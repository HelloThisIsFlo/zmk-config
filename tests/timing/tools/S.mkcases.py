#!/usr/bin/env python3
"""Generate the AK-pair sweep validation cases (R2 = Flo's real keymap) from _rig_R2.

Event schedule (RIG mock rule: t(e0) = e0.ms+1, each later gap = previous ms + 1):
  PRESS(A, Δ-1)   A↓ abs Δ            (t)
  PRESS(B, h1)    B↓ abs 2Δ           (t+Δ)
  RELEASE(A, h2)  A↑ abs 2Δ+h1+1      (t+Δ+h1+1)
  RELEASE(B, 300) B↑ abs 2Δ+h1+h2+2   exit +301 later
"""
import shutil, sys
from pathlib import Path

TESTS = Path(__file__).resolve().parents[1] / 'cases'  # tests/timing/cases (was zmk/app/tests/ak-truth in the fork)
RIG = TESTS / '_rig_R2'

def mock(pos):
    return (pos // 10, pos % 10 + 1) if pos < 30 else (3, pos - 27)

P = dict(LT4=0, LT3=1, LT2=2, LT1=3, LT0=4, RT0=5, RT1=6, RT2=7, RT3=8, RT4=9,
         LM4=10, LM3=11, LM2=12, LM1=13, LM0=14, RM0=15, RM1=16, RM2=17, RM3=18, RM4=19,
         LB4=20, LB3=21, LB2=22, LB1=23, LB0=24, RB0=25, RB1=26, RB2=27, RB3=28, RB4=29,
         LH2=30, LH1=31, LH0=32, RH0=33, RH1=34, RH2=35)

# (pair tag, trigger pos, follower pos, [Δ...], hack, h1, h2)
CASES = [
    ('L_LB3', 'LB2', 'LB3', [14, 17], True, 60, 40),          # S3 16 ms (magicCloseQuitCb), complements T-23 d1/d5/d6
    ('M_LT3', 'LT2', 'LT3', [5, 14, 15, 16, 17], True, 60, 40),  # S2 16 ms (typeZ)
    ('M_LT3', 'LT2', 'LT3', [15], False, 60, 40),
    ('H_RM2', 'RM4', 'RM2', [16, 17, 18, 19], True, 60, 40),  # S3 18 ms (capsWord)
    ('H_RM2', 'RM4', 'RM2', [17], False, 60, 40),
    ('N_LT4', 'LM2', 'LT4', [10, 11], True, 60, 40),          # H0 (hack-only follower)
    ('O_RT3', 'RB2', 'RT3', [10, 11], True, 60, 40),          # N (ordinary, right hand)
    ('A_RT2', 'RM1', 'RT2', [10, 11], True, 30, 28),          # N, k1 = 18, hold-tap base follower
    ('S_LH0', 'LM3', 'LH0', [10, 11], True, 30, 28),          # H0, thumb follower (base = blt_akR)
]

made = []
for tag, a, b, deltas, hack, h1, h2 in CASES:
    ra, ca = mock(P[a]); rb, cb = mock(P[b])
    for d in deltas:
        name = f'S-{tag}-d{d}' + ('' if hack else '-nohack')
        dst = TESTS / name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(RIG, dst)
        tA, tB = d, 2 * d
        aup = tB + h1 + 1
        bup = aup + h2 + 1
        txt = f"\n/* ===== AK-pair sweep case {name}: {a} -> {b}, Δ = {d}, hack {'ON' if hack else 'OFF'} ===== */\n"
        if not hack:
            txt += "/* hack OFF (RIG.md R2 idiom; the real combo has no label) */\n"
            txt += "/ { combos { /delete-node/ combo_ak_consistency_hack; }; };\n"
        txt += f"""
&kscan {{
    events = <
        ZMK_MOCK_PRESS({ra},{ca},{d-1})      /* {a} down  abs {tA} (t)        */
        ZMK_MOCK_PRESS({rb},{cb},{h1})     /* {b} down  abs {tB} (t+{d})     */
        ZMK_MOCK_RELEASE({ra},{ca},{h2})   /* {a} up    abs {aup} (t+{aup-tA}) */
        ZMK_MOCK_RELEASE({rb},{cb},300)  /* {b} up    abs {bup} (t+{bup-tA}) */
    >;
}};
"""
        with open(dst / 'native_posix_64.keymap', 'a') as f:
            f.write(txt)
        made.append(name)
print('\n'.join(made))
