#!/usr/bin/env python3
"""Per case: t (first press), HID down/up sequence with rel ms, layer on/off, delivery layer per position."""
import re, sys, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")  # tests/timing/logs (raw logs used to sit next to this script)
HID = {**{0x04 + i: chr(65 + i) for i in range(26)}, 0x2A: "BSPC", 0x2D: "MINUS", 0x2E: "EQUAL", 0x2B: "TAB", 0xE1: "LSHIFT", 0xE5: "RSHIFT"}
P = re.compile(r"^\[00:00:(\d\d)\.(\d{3}),000\] <dbg> zmk: (\S+): (.*)$")
for c in sys.argv[1:]:
    t0 = None; downs = []; ev = []
    for line in open(os.path.join(R, c + ".raw.log"), errors="replace"):
        m = P.match(line.rstrip())
        if not m: continue
        ms = int(m.group(1)) * 1000 + int(m.group(2)); f, msg = m.group(3), m.group(4)
        if f == "zmk_physical_layouts_kscan_process_msgq" and "pressed: true" in msg and t0 is None: t0 = ms
        if t0 is None: continue
        r = ms - t0
        if f.startswith("hid_listener_keycode_") and "keycode 0x" in msg:
            k = int(re.search(r"keycode 0x(\w+)", msg).group(1), 16)
            ev.append(f"{'↓' if f.endswith('pressed') else '↑'}{HID.get(k, hex(k))}@+{r}")
            if f.endswith("pressed"): downs.append(HID.get(k, hex(k)))
        elif f == "set_layer_state":
            mm = re.search(r"layer (\d+) state (\d)", msg); ev.append(f"L{mm.group(1)}{'on' if mm.group(2)=='1' else 'off'}@+{r}")
        elif f == "zmk_keymap_apply_position_state":
            mm = re.search(r"layer_id: (\d+) position: (\d+)", msg); ev.append(f"[pos{mm.group(2)}→layer{mm.group(1)}@+{r}]")
    print(f"{c}: t=abs {t0} | HID downs: {' '.join(downs)}\n   {' '.join(ev)}")
