#!/usr/bin/env python3
"""Create the T-23 case directories from _rig_R2 (copy, then append events / hack deletion)."""
import os, shutil

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cases")  # tests/timing/cases (was zmk/app/tests/ak-truth in the fork)
RIG = os.path.join(BASE, "_rig_R2")
NOHACK = "\n/* T-23: hack OFF (RIG.md R2 idiom; the real combo has no label) */\n/ { combos { /delete-node/ combo_ak_consistency_hack; }; };\n"

# (case, k1 (r,c), k2 (r,c), delta, hack_on, comment)
CASES = [
    ("T-23-a-MT-d5",            (0, 3), (1, 4), 5,  True,  "LT2 M then LM1 T, delta 5, hack on"),
    ("T-23-b-CP-d6",            (1, 1), (0, 4), 6,  True,  "LM4 C then LT1 P, delta 6, hack on"),
    ("T-23-c-CP-d6-nohack",     (1, 1), (0, 4), 6,  False, "LM4 C then LT1 P, delta 6, hack off"),
    ("T-23-d1-LG-d13",          (2, 3), (2, 2), 13, True,  "LB2 L then LB3 G, delta 13, hack on"),
    ("T-23-d2-LG-d5",           (2, 3), (2, 2), 5,  True,  "LB2 L then LB3 G, delta 5, hack on"),
    ("T-23-e1-LG-d20-nohack",   (2, 3), (2, 2), 20, False, "LB2 L then LB3 G, delta 20, hack off"),
    ("T-23-e2-LG-d28-nohack",   (2, 3), (2, 2), 28, False, "LB2 L then LB3 G, delta 28, hack off"),
    ("T-23-d3-LX-d13",          (2, 3), (0, 1), 13, True,  "LB2 L then LT4 X-key (akL: &bk G), delta 13, hack on"),
    ("T-23-d4-LX-d5",           (2, 3), (0, 1), 5,  True,  "LB2 L then LT4 X-key (akL: &bk G), delta 5, hack on"),
    ("T-23-e3-LX-d20-nohack",   (2, 3), (0, 1), 20, False, "LB2 L then LT4 X-key (akL: &bk G), delta 20, hack off"),
    ("T-23-e4-LX-d28-nohack",   (2, 3), (0, 1), 28, False, "LB2 L then LT4 X-key (akL: &bk G), delta 28, hack off"),
    # bracket cases added after d1/d2 showed LB2+LB3 share magicCloseQuitCb (16 ms, <21 22 23>)
    ("T-23-d5-LG-d15",          (2, 3), (2, 2), 15, True,  "LB2 L then LB3 G, delta 15, hack on (bypass edge, native)"),
    ("T-23-d6-LG-d16",          (2, 3), (2, 2), 16, True,  "LB2 L then LB3 G, delta 16, hack on (key-first flush)"),
    ("T-23-e5-LG-d13-nohack",   (2, 3), (2, 2), 13, False, "LB2 L then LB3 G, delta 13, hack off (shared real combo)"),
]

for name, (r1, c1), (r2, c2), d, hack, comment in CASES:
    dst = os.path.join(BASE, name)
    if os.path.exists(dst):
        print("exists, skipping:", name)
        continue
    shutil.copytree(RIG, dst)
    km = os.path.join(dst, "native_posix_64.keymap")
    with open(km, "a") as f:
        f.write(f"\n/* ===== T-23 case {name}: {comment} ===== */\n")
        if not hack:
            f.write(NOHACK)
        f.write(
            "\n&kscan {\n    events = <\n"
            f"        ZMK_MOCK_PRESS({r1},{c1},{d-1})\n"
            f"        ZMK_MOCK_PRESS({r2},{c2},60)\n"
            f"        ZMK_MOCK_RELEASE({r1},{c1},40)\n"
            f"        ZMK_MOCK_RELEASE({r2},{c2},300)\n"
            "    >;\n};\n"
        )
    print("created", name)
