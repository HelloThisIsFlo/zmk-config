#!/usr/bin/env python3
"""T-10 reconciliation fix case: spec shape (stock R1, no sibling) but F delayed past Q18's
deadline so the stall's end is a NON-completing press. Never edits the template."""
import shutil, os
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cases")  # tests/timing/cases (was zmk/app/tests/ak-truth in the fork)
TPL = os.path.join(BASE, "_rig_R1")
CASES = {
    # E t, G t+12 (MIN 16 -> 18, schedule refused), F t+25 (after Q18's t+18 deadline);
    # E^ t+126, F^ t+137, G^ t+148
    "T-10-fix-lateF-d13": ["PRESS(1,0,11)", "PRESS(1,2,12)", "PRESS(1,1,100)",
                           "RELEASE(1,0,10)", "RELEASE(1,1,10)", "RELEASE(1,2,300)"],
}
for case, evs in CASES.items():
    dst = os.path.join(BASE, case)
    if os.path.exists(dst):
        print("exists, skipping:", dst); continue
    shutil.copytree(TPL, dst)
    with open(os.path.join(dst, "native_posix_64.keymap"), "a") as f:
        f.write("\n/* T-10-fix: spec shape, F moved to t+25 (> Q18 deadline t+18). */\n")
        f.write("&kscan {\n    events = <\n")
        for e in evs:
            f.write(f"        ZMK_MOCK_{e}\n")
        f.write("    >;\n};\n")
    print("created", dst)
