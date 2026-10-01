#!/usr/bin/env python3
"""Create the T-05 case directories from the R1 template (never edits the template)."""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "cases"  # tests/timing/cases (was zmk/app/tests/ak-truth in the fork)
TEMPLATE = ROOT / "_rig_R1"

# name -> (e0.ms, comment)   e0.ms = boot delay AND the A→D gap (both +1 on native) → Δ = e0.ms + 1
CASES = {
    "T-05":     (12, "spec run: Δ = 13 (11 ≤ Δ < 16 band, middle)"),
    "T-05-d11": (10, "band edge: Δ = 11 (hack deadline == D's timestamp → key-first hack drop)"),
    "T-05-d15": (14, "band edge: Δ = 15 (last Δ strictly inside R16's 16 ms window)"),
    "T-05-d16": (15, "one past the band: Δ = 16 (R16 deadline == D's timestamp; native ladder would fire at t+17)"),
}

BLOCK = """

/* ===== {name}: T-05 — key 1 (pos 0 = A, &ak 1 A, in R16 <0 2> + hack) then a hack-only key 2 (pos 3 = D, &kp D)
 * {comment}
 * Mock rule (RIG §headline): t(A) = e0.ms + 1 ; t(D) = t(A) + e0.ms + 1  → Δ = {delta}
 * ===== */
&kscan {{
    events = <
        ZMK_MOCK_PRESS(0,0,{e0})      /* pos 0 = A (0x04): &ak 1 A ; candidates R16(16) + hack(11) */
        ZMK_MOCK_PRESS(0,3,60)      /* pos 3 = D (0x07): &kp D on base, &bk L (0x0F) on akA ; hack-only */
        ZMK_MOCK_RELEASE(0,0,40)    /* A↑ */
        ZMK_MOCK_RELEASE(0,3,300)   /* D↑ ; 300 ms tail so the 100 ms aksl timer is observed */
    >;
}};
"""

for name, (e0, comment) in CASES.items():
    dst = ROOT / name
    if dst.exists():
        print(f"exists, leaving alone: {dst}")
        continue
    shutil.copytree(TEMPLATE, dst)
    km = dst / "native_posix_64.keymap"
    with km.open("a", encoding="utf-8") as fh:
        fh.write(BLOCK.format(name=name, comment=comment, e0=e0, delta=e0 + 1))
    print(f"created {dst} (e0.ms={e0}, Δ={e0 + 1})")
