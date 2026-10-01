#!/usr/bin/env python3
"""Create the T-07 case directories from the _rig_R1_nohack template (never edits the template)."""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "cases"  # tests/timing/cases (was zmk/app/tests/ak-truth in the fork)
TEMPLATE = ROOT / "_rig_R1_nohack"

# name -> (e0.ms, comment).  Key 1 = pos 1 (0,1) `&ak 2 B`; key 2 = pos 3 (0,3) `&kp D` / akB `&bk Q`.
# mock rule (RIG): t(e0) = e0.ms + 1 ; t(e1) = t(e0) + e0.ms + 1  → key 2 at t + (e0.ms + 1) = t + Δ
CASES = {
    "T-07-d5":  (4,  "Δ = 5  : key 2 position event at t+5  (spec: MISS → D on base)"),
    "T-07-d6":  (5,  "Δ = 6  : spec's literal 'D at t+6' reading (mock ms 5) — supplementary MISS check"),
    "T-07-d11": (10, "Δ = 11 : key 2 at t+11 = same tick as `layer 2 state 1` (spec: TIE band, expected D)"),
    "T-07-d12": (11, "Δ = 12 : key 2 at t+12, one tick after layer 2 ON (spec: HIT → Q)"),
}

BLOCK = """
/* T-07 — key 1 with no real combo (k1 = 0), hack OFF (template _rig_R1_nohack: no combo_hack node).
 * {comment}
 * key 1 = pos 1 (0,1) `&ak 2 B`  (no candidate at all with the hack off → bubbles)
 * key 2 = pos 3 (0,3) `&kp D` on base / `&bk Q` on akB (layer 2)  (no candidate either)
 */
&kscan {{
    events = <
        ZMK_MOCK_PRESS(0,1,{ms})
        ZMK_MOCK_PRESS(0,3,60)
        ZMK_MOCK_RELEASE(0,1,40)
        ZMK_MOCK_RELEASE(0,3,300)
    >;
}};
"""

for name, (ms, comment) in CASES.items():
    dst = ROOT / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(TEMPLATE, dst)
    km = dst / "native_posix_64.keymap"
    with km.open("a", encoding="utf-8") as fh:
        fh.write(BLOCK.format(comment=comment, ms=ms))
    print(f"created {dst}  (e0.ms = {ms})")
