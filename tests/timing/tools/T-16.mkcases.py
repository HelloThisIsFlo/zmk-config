#!/usr/bin/env python3
"""Create T-16 case dirs from _rig_R1 (copy, then append the &kscan events block)."""
import shutil, pathlib
BASE = pathlib.Path(__file__).resolve().parents[1] / "cases"  # tests/timing/cases (was zmk/app/tests/ak-truth in the fork)
TPL = BASE / "_rig_R1"
CASES = {
    # name: (delta, comment)
    "T-16-a-d6":  (6,  "spec: B (pos 1 &ak 2 B) at t, linger (pos 9 &lk X Y) at t+6"),
    "T-16-b-d12": (12, "control: linger at t+12"),
    "T-16-c-d10": (10, "extra boundary probe: linger at t+10"),
    "T-16-d-d11": (11, "extra boundary probe: linger at t+11"),
}
for name, (d, comment) in CASES.items():
    dst = BASE / name
    if dst.exists():
        print("exists, skip", dst); continue
    shutil.copytree(TPL, dst)
    km = dst / "native_posix_64.keymap"
    km.write_text(km.read_text() + f"""
/* T-16 {comment} */
&kscan {{
    events = <
        ZMK_MOCK_PRESS(0,1,{d-1})       // pos 1 (&ak 2 B) at t = {d} ms after boot; gap to next = {d}
        ZMK_MOCK_PRESS(2,1,300)     // pos 9 (&lk X Y) at t+{d}
        ZMK_MOCK_RELEASE(0,1,10)    // pos 1 up at t+{d}+301
        ZMK_MOCK_RELEASE(2,1,300)   // pos 9 up 11 ms later; exit +301
    >;
}};
""")
    print("created", dst)
