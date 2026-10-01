#!/usr/bin/env python3
"""T-07 reconciliation cases — copies of _rig_R1_nohack (never edits the template).

T-07-fix-d10     : Δ = 10 (mock ms 9). Key 2 at t+10, layer 2 ON at t+11 → expected D on base (MISS).
                   Pins the native band boundary: MISS ≤ 10, HIT ≥ 11.
T-07-fix-d11-rev : Δ = 11 with the TIMEOUT ORDER REVERSED. A harmless dummy event (release of a never-pressed
                   key, pos 2) sits 1 ms after key 1, so the mock's K_MSEC(9) for key 2 is scheduled at t+1,
                   i.e. AFTER the behaviour queue's K_MSEC(10) scheduled at t. Both expire on tick t+11, but now
                   the queue timeout is first in Zephyr's timeout list. Expected: still layer-first → Q (HIT).
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "cases"  # tests/timing/cases (was zmk/app/tests/ak-truth in the fork)
TEMPLATE = ROOT / "_rig_R1_nohack"

CASES = {
    "T-07-fix-d10": """
/* T-07-fix-d10 — key 1 with no real combo (k1 = 0), hack OFF. Δ = 10: key 2 at t+10, one tick BEFORE
 * `layer 2 state 1` (t+11). Expected: D (0x07) on layer 0 → MISS. Pins the native boundary of the
 * corrected rule (MISS ≤ 10, HIT ≥ 11).
 * key 1 = pos 1 (0,1) `&ak 2 B`; key 2 = pos 3 (0,3) `&kp D` base / `&bk Q` on akB (layer 2).
 */
&kscan {
    events = <
        ZMK_MOCK_PRESS(0,1,9)
        ZMK_MOCK_PRESS(0,3,60)
        ZMK_MOCK_RELEASE(0,1,40)
        ZMK_MOCK_RELEASE(0,3,300)
    >;
};
""",
    "T-07-fix-d11-rev": """
/* T-07-fix-d11-rev — Δ = 11 same-tick case with the Zephyr timeout-list order REVERSED.
 * e0 RELEASE(0,2,20): dummy (pos 2 = `&kp C`, never pressed → no-op release) at 21; gap after = 21
 * e1 PRESS(0,1,0)   : key 1 (B) at t = 42; queue K_MSEC(10) scheduled at 42 → fires 53; gap after = 1
 * e2 RELEASE(0,2,9) : dummy at 43 → the mock's K_MSEC(9) for e3 is scheduled at 43 → fires 53,
 *                     inserted AFTER the queue timeout (equal dticks) → queue work is submitted first.
 * e3 PRESS(0,3,60)  : key 2 (pos 3) at 53 = t+11.
 * Expected: `layer 2 state 1` → mock handler → `Row: 0, col: 3` on layer_id 2 → Q (HIT).
 */
&kscan {
    events = <
        ZMK_MOCK_RELEASE(0,2,20)
        ZMK_MOCK_PRESS(0,1,0)
        ZMK_MOCK_RELEASE(0,2,9)
        ZMK_MOCK_PRESS(0,3,60)
        ZMK_MOCK_RELEASE(0,1,40)
        ZMK_MOCK_RELEASE(0,3,300)
    >;
};
""",
}

for name, block in CASES.items():
    dst = ROOT / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(TEMPLATE, dst)
    with (dst / "native_posix_64.keymap").open("a", encoding="utf-8") as fh:
        fh.write(block)
    print(f"created {dst}")
