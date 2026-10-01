#!/usr/bin/env python3
"""Create the T-10 case directories from the R1 template (never edits the template)."""
import shutil, os
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cases")  # tests/timing/cases (was zmk/app/tests/ak-truth in the fork)
TPL = os.path.join(BASE, "_rig_R1")

SIB = """
/* T-10 case-only tweak: a 4-key 18 ms sibling of Q18 (stand-in for Flo's capsWord RM1-RM4
 * next to delWord RM1-RM3), so a completed Q18 still has a live longer candidate. */
&combos {
    combo_X18: combo_X18 {
        bindings = <&bk X>;
        key-positions = <4 5 6 7>;
        layers = <0 1 2 3 4 5>;
        timeout-ms = <18>;
    };
};
"""

CASES = {
    # spec verbatim: E t, G t+12, F t+16; E^ t+117, F^ t+128, G^ t+139
    "T-10-a-spec": (False, ["PRESS(1,0,11)", "PRESS(1,2,3)", "PRESS(1,1,100)",
                            "RELEASE(1,0,10)", "RELEASE(1,1,10)", "RELEASE(1,2,300)"]),
    # control: E t, F t+4, G t+8 (all inside 11 ms)
    "T-10-b-ctrl": (False, ["PRESS(1,0,3)", "PRESS(1,1,3)", "PRESS(1,2,100)",
                            "RELEASE(1,0,10)", "RELEASE(1,1,10)", "RELEASE(1,2,300)"]),
    # R10 direct: E t, G t+12 (moves MIN 16 -> 18), no F; E^ t+117, G^ t+128
    "T-10-c-noF-d12": (False, ["PRESS(1,0,11)", "PRESS(1,2,104)",
                               "RELEASE(1,0,10)", "RELEASE(1,2,300)"]),
    # control for c: E t, G t+5 (before the hack rung, MIN unchanged), no F; E^ t+117
    "T-10-d-noF-d5": (False, ["PRESS(1,0,4)", "PRESS(1,2,111)",
                              "RELEASE(1,0,10)", "RELEASE(1,2,300)"]),
    # spec events + 4-key 18 ms sibling (faithful R10 example: completed combo with a live sibling)
    "T-10-e-sib-spec": (True, ["PRESS(1,0,11)", "PRESS(1,2,3)", "PRESS(1,1,100)",
                               "RELEASE(1,0,10)", "RELEASE(1,1,10)", "RELEASE(1,2,300)"]),
    # control for e: sibling keymap, E t, F t+4, G t+8
    "T-10-f-sib-ctrl": (True, ["PRESS(1,0,3)", "PRESS(1,1,3)", "PRESS(1,2,100)",
                               "RELEASE(1,0,10)", "RELEASE(1,1,10)", "RELEASE(1,2,300)"]),
}

for case, (sib, evs) in CASES.items():
    dst = os.path.join(BASE, case)
    if os.path.exists(dst):
        print("exists, skipping:", dst)
        continue
    shutil.copytree(TPL, dst)
    with open(os.path.join(dst, "native_posix_64.keymap"), "a") as f:
        if sib:
            f.write(SIB)
        f.write("\n&kscan {\n    events = <\n")
        for e in evs:
            f.write(f"        ZMK_MOCK_{e}\n")
        f.write("    >;\n};\n")
    print("created", dst)
