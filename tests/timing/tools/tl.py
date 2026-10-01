#!/usr/bin/env python3
"""tl.py — compact timeline from a timestamped native_posix ZMK log.

Usage:
    python3 tl.py <raw.log> [--all] [--abs] [--t0 MS] [--grep REGEX]

Input:  the stdout of `zmk.exe --no-rt` (lines prefixed `[hh:mm:ss.mmm,uuu] <lvl> zmk: func: msg`).
        The prefix-stripped `keycode_events_full.log` written by run-test.sh has NO timestamps
        and cannot be used.
Output: one line per interesting event: `+<rel ms>  <abs ms>  <event>`.
        rel ms is relative to the first `Row: … pressed: true` line (first physical position event)
        unless --t0 is given; --abs drops the relative column.
        --all prints every log line (still with the rel-ms column); --grep keeps only matching lines.
"""
import re
import sys

PREFIX = re.compile(r"^\[(\d\d):(\d\d):(\d\d)\.(\d{3}),(\d{3})\]\s+<(\w+)>\s+zmk:\s+(?:(\S+?):\s+)?(.*)$")

HID = {
    **{0x04 + i: chr(ord("A") + i) for i in range(26)},
    **{0x1E + i: str(i + 1) for i in range(9)}, 0x27: "0",
    0x28: "RET", 0x29: "ESC", 0x2A: "BSPC", 0x2B: "TAB", 0x2C: "SPACE", 0x2D: "MINUS", 0x2E: "EQUAL",
    0x2F: "LBKT", 0x30: "RBKT", 0x31: "BSLH", 0x33: "SEMI", 0x34: "SQT", 0x35: "GRAVE", 0x36: "COMMA",
    0x37: "DOT", 0x38: "SLASH", 0x39: "CAPS", 0x4C: "DEL", 0x4F: "RIGHT", 0x50: "LEFT", 0x51: "DOWN", 0x52: "UP",
    0xE0: "LCTRL", 0xE1: "LSHIFT", 0xE2: "LALT", 0xE3: "LGUI", 0xE4: "RCTRL", 0xE5: "RSHIFT", 0xE6: "RALT", 0xE7: "RGUI",
}


def name(code):
    return HID.get(code, "?")


def interesting(func, msg):
    """Return a compact event string, or None to skip the line."""
    if func == "zmk_physical_layouts_kscan_process_msgq":
        m = re.match(r"Row: (\d+), col: (\d+), position: (-?\d+), pressed: (\w+)", msg)
        if m:
            r, c, p, pr = m.groups()
            return f"POS {'↓' if pr == 'true' else '↑'} {p:>3}  (mock {r},{c})"
    if func == "zmk_keymap_apply_position_state":
        m = re.match(r"layer_id: (\d+) position: (\d+), binding name: (.*)", msg)
        if m:
            return f"deliver pos {m.group(2)} on layer {m.group(1)} → {m.group(3)}"
    if func in ("hid_listener_keycode_pressed", "hid_listener_keycode_released"):
        m = re.match(r"usage_page 0x(\w+) keycode 0x(\w+) implicit_mods 0x(\w+) explicit_mods 0x(\w+)", msg)
        if m:
            page, code, im, em = (int(x, 16) for x in m.groups())
            arrow = "↓" if func.endswith("pressed") else "↑"
            mods = ""
            if im or em:
                mods = f"  mods imp=0x{im:02X} exp=0x{em:02X}"
            return f"HID {arrow} 0x{code:02X} {name(code) if page == 7 else f'page{page:#x}'}{mods}"
    if func == "set_layer_state":
        m = re.match(r"layer_changed: layer (\d+) state (\d)", msg)
        if m:
            return f"LAYER {m.group(1)} {'ON ' if m.group(2) == '1' else 'OFF'}"
    if func == "filter_timed_out_candidates":
        m = re.search(r"remaining_candidates=(\d+) timestamp=(\d+)", msg)
        if m:
            return f"combo filter: remaining={m.group(1)} (timestamp={m.group(2)})"
    if msg.startswith("combo: "):
        return "combo " + msg[len("combo: "):]
    if func == "on_hold_tap_binding_pressed" or func == "decide_hold_tap" or func == "on_hold_tap_binding_released":
        return "ht " + msg
    if func == "position_state_changed_listener":
        if "no undecided hold_tap active" in msg:
            return None
        return "ht " + msg
    if func == "keycode_state_changed_listener" or func == "release_captured_events":
        return "ht " + msg
    if func in ("on_sticky_key_binding_pressed", "on_sticky_key_binding_released"):
        return "sk " + msg
    if func == "queue_macro":
        return "macro " + msg
    if func == "behavior_queue_process_next":
        if msg.startswith("Invoking "):
            return "queue invoke " + msg[len("Invoking "):]
        m = re.match(r"Processing next queued behavior in (\d+)ms", msg)
        if m:
            return f"queue wait {m.group(1)}ms"
    if func and func.startswith("kscan_mock_work_handler"):
        m = re.match(r"ev \d+ row (\d+) column (\d+) state (\d)", msg)
        if m:
            return f"mock {'press' if m.group(3) == '1' else 'release'} ({m.group(1)},{m.group(2)})"
    if func and func.startswith("kscan_mock_schedule_next_event") and msg.strip() == "Exiting":
        return "EXIT"
    if func == "mo_keymap_binding_pressed" or func == "mo_keymap_binding_released":
        return f"mo {'↓' if func.endswith('pressed') else '↑'} {msg}"
    return None


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 2
    path = argv[1]
    show_all = "--all" in argv
    absolute = "--abs" in argv
    t0 = None
    grep = None
    if "--t0" in argv:
        t0 = int(argv[argv.index("--t0") + 1])
    if "--grep" in argv:
        grep = re.compile(argv[argv.index("--grep") + 1])

    rows = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            m = PREFIX.match(line)
            if not m:
                continue
            hh, mm, ss, ms, us, lvl, func, msg = m.groups()
            t = ((int(hh) * 60 + int(mm)) * 60 + int(ss)) * 1000 + int(ms)
            ev = interesting(func, msg)
            if ev is None:
                if not show_all:
                    continue
                ev = f"[{lvl}] {func + ': ' if func else ''}{msg}"
            rows.append((t, ev))
            if t0 is None and func == "zmk_physical_layouts_kscan_process_msgq" and "pressed: true" in msg:
                t0 = t

    if not rows:
        print("no timestamped lines found — feed the raw `zmk.exe --no-rt` output, not keycode_events_full.log", file=sys.stderr)
        return 1
    if t0 is None:
        t0 = rows[0][0]
    for t, ev in rows:
        if grep and not grep.search(ev):
            continue
        if absolute:
            print(f"{t:>6}  {ev}")
        else:
            print(f"{t - t0:+5d}  {t:>6}  {ev}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
