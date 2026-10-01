#!/usr/bin/env python3
"""Create the T-20 case directories from the R1 template (template is only read, never edited)."""
import shutil, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1] / "cases"  # tests/timing/cases (was zmk/app/tests/ak-truth in the fork)
TPL = ROOT / "_rig_R1"

BASE_OLD = "&kp I       &lk X Y     &blt_akR 5 0    &kp J"
AKA_OLD = "&trans      &trans      &trans          &bk M"

def make(name, base_new, aka_new, overlay, events):
    d = ROOT / name
    if d.exists():
        raise SystemExit(f"{d} exists - refusing to overwrite")
    shutil.copytree(TPL, d)
    km = d / "native_posix_64.keymap"
    s = km.read_text()
    assert s.count(BASE_OLD) == 1 and s.count(AKA_OLD) == 1
    s = s.replace(BASE_OLD, base_new).replace(AKA_OLD, aka_new)
    s += "\n/* ---- T-20 case overlay ---- */\n" + overlay + "\n&kscan {\n    events = <\n" + \
         "".join(f"        {e}\n" for e in events) + "    >;\n};\n"
    km.write_text(s)
    print("created", d)

# pos 11 = held LSHIFT on base; akA pos 11 made &trans so a Shift delivered while akA is up
# still resolves to the base &kp LSHIFT (template has &bk M there).
BASE_SHIFT = "&kp I       &lk X Y     &blt_akR 5 0    &kp LSHIFT"
AKA_TRANS = "&trans      &trans      &trans          &trans"

SPEC_EVENTS = [
    "ZMK_MOCK_PRESS(0,0,50)",     # A (pos 0, &ak 1 A)          t
    "ZMK_MOCK_PRESS(2,3,300)",    # Shift (pos 11, &kp LSHIFT)  t+51
    "ZMK_MOCK_PRESS(0,1,10)",     # B-key (pos 1)               t+352
    "ZMK_MOCK_RELEASE(0,1,50)",   # B-key up                    t+363
    "ZMK_MOCK_RELEASE(2,3,10)",   # Shift up                    t+414
    "ZMK_MOCK_RELEASE(0,0,300)",  # A up                        t+425, exit t+726
]

make("T-20-a-spec", BASE_SHIFT, AKA_TRANS, "", SPEC_EVENTS)

make("T-20-b-ignoremods", BASE_SHIFT, AKA_TRANS,
     "&aksl {\n    ignore-modifiers;\n};\n", SPEC_EVENTS)

# extra c: sticky shift (skms via htls tap on pos 10) armed AFTER the AK layer -> pins it
make("T-20-c-stickyshift",
     "&kp I       &lk X Y     &htls 4 LSHIFT  &kp J", "&trans      &trans      &trans          &bk M", "",
     [
        "ZMK_MOCK_PRESS(0,0,50)",     # A                 t      (abs 51)
        "ZMK_MOCK_RELEASE(0,0,20)",   # A up              t+51   (abs 102)
        "ZMK_MOCK_PRESS(2,2,30)",     # thumb htls down   t+72   (abs 123)
        "ZMK_MOCK_RELEASE(2,2,200)",  # thumb up (tap)    t+103  (abs 154)
        "ZMK_MOCK_PRESS(0,1,10)",     # B-key             t+304  (abs 355)
        "ZMK_MOCK_RELEASE(0,1,300)",  # B-key up          t+315  (abs 366), exit t+616
     ])

# extra d: Shift pressed BEFORE A and held -> arming happens after the mod down -> no pin
make("T-20-d-shiftfirst", BASE_SHIFT, AKA_TRANS, "",
     [
        "ZMK_MOCK_PRESS(2,3,40)",     # Shift down        abs 41
        "ZMK_MOCK_PRESS(0,0,50)",     # A                 abs 82  = t
        "ZMK_MOCK_RELEASE(0,0,150)",  # A up              abs 133 = t+51
        "ZMK_MOCK_PRESS(0,1,10)",     # B-key             abs 284 = t+202
        "ZMK_MOCK_RELEASE(0,1,50)",   # B-key up          abs 295 = t+213
        "ZMK_MOCK_RELEASE(2,3,300)",  # Shift up          abs 346 = t+264, exit abs 647
     ])

# ---- appended after the first four ran: extra e ----
# while the pinning Shift is still held, a SECOND follower tap: does it also resolve on akA?
if __name__ == "__main__" and not (ROOT / "T-20-e-twokeys").exists():
    make("T-20-e-twokeys", BASE_SHIFT, AKA_TRANS, "",
         [
            "ZMK_MOCK_PRESS(0,0,50)",     # A                 t      (abs 51)
            "ZMK_MOCK_PRESS(2,3,300)",    # Shift down        t+51   (abs 102)
            "ZMK_MOCK_PRESS(0,1,10)",     # B-key #1          t+352  (abs 403)
            "ZMK_MOCK_RELEASE(0,1,20)",   # B-key #1 up       t+363  (abs 414)
            "ZMK_MOCK_PRESS(0,1,10)",     # B-key #2          t+384  (abs 435)
            "ZMK_MOCK_RELEASE(0,1,30)",   # B-key #2 up       t+395  (abs 446)
            "ZMK_MOCK_RELEASE(2,3,10)",   # Shift up          t+426  (abs 477)
            "ZMK_MOCK_RELEASE(0,0,300)",  # A up              t+437  (abs 488), exit t+738
         ])
