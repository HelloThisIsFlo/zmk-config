#!/usr/bin/env python3
"""AK-pair sweep: enumerate every compiled adaptive-key pair on NAQUADAH and derive its failure band.

Sources (read-only):
  - compiled devicetree of an R2 (real keymap, hack ON) build: combos + keymap (ground truth for what is compiled)
  - expanded_symbolic.dts (preprocessed zmk-config) for readable binding names (cross-checked against the compiled keymap)
Output: sweep_pairs.json + sweep_pairs.md (tables) next to this script.
"""
import json, re, sys
from pathlib import Path

INV = Path(__file__).resolve().parent
ZEPHYR_DTS = Path('/Users/flo/Work/Private/Dev/Keyboard/zmk/app/build/tests/ak-truth/T-23-a-MT-d5/zephyr/zephyr.dts')
SYMB = INV / 'tmp-cpp' / 'expanded_symbolic.dts'

NAMES = {4:'LT0',3:'LT1',2:'LT2',1:'LT3',0:'LT4',5:'RT0',6:'RT1',7:'RT2',8:'RT3',9:'RT4',
         14:'LM0',13:'LM1',12:'LM2',11:'LM3',10:'LM4',15:'RM0',16:'RM1',17:'RM2',18:'RM3',19:'RM4',
         24:'LB0',23:'LB1',22:'LB2',21:'LB3',20:'LB4',25:'RB0',26:'RB1',27:'RB2',28:'RB3',29:'RB4',
         32:'LH0',31:'LH1',30:'LH2',33:'RH0',34:'RH1',35:'RH2'}
POS = {v: k for k, v in NAMES.items()}
hand = lambda p: NAMES[p][0]
LAYER = {0:'l_alpha',1:'l_alpha_linwin',2:'l_akA',3:'l_akB',4:'l_akC',5:'l_akD',6:'l_akE',7:'l_akF',8:'l_akG',
         9:'l_akH',10:'l_akhE',11:'l_akK',12:'l_akL',13:'l_akM',14:'l_akN',15:'l_akO',16:'l_akP',17:'l_akR',
         18:'l_akS',19:'l_akT',20:'l_akU',21:'l_akV',22:'l_akW',23:'l_akX',24:'l_akY'}

# ---------- compiled combos ----------
dts = ZEPHYR_DTS.read_text()
cblk = dts[dts.index('combos {'):dts.index('keymap {')]
combos = []
for m in re.finditer(r'(combo_\w+) \{(.*?)\};', cblk, re.S):
    body = m.group(2)
    kp = [int(x, 16) for x in re.search(r'key-positions = <([^>]*)>', body).group(1).split()]
    to = int(re.search(r'timeout-ms = <([^>]*)>', body).group(1).strip(), 16)
    ly = [int(x, 16) for x in re.search(r'layers = <([^>]*)>', body).group(1).split()]
    bd = ' '.join(re.search(r'bindings = <([^>]*)>', body).group(1).split())
    combos.append(dict(name=m.group(1)[6:], kp=kp, timeout=to, layers=ly, binding=bd))
assert len(combos) == 28, len(combos)
HACK = [c for c in combos if c['name'] == 'ak_consistency_hack'][0]
REAL = [c for c in combos if c is not HACK]

def real_on(pos, layer):
    return [c for c in REAL if pos in c['kp'] and layer in c['layers']]

def kmax(pos, layer):
    return max((c['timeout'] for c in real_on(pos, layer)), default=0)

# ---------- compiled keymap ----------
kblk = dts[dts.index('keymap {'):]
def split_bindings(s):
    parts = re.split(r'(?=&)', ' '.join(s.split()))
    return [p.strip() for p in parts if p.strip()]
compiled = {}
for m in re.finditer(r'\n\t\t(\d+) \{\s*label = "[^"]*";\s*bindings = <(.*?)>;', kblk, re.S):
    compiled[int(m.group(1))] = split_bindings(m.group(2))
# symbolic keymap (readable)
sy = SYMB.read_text()
skm = sy[sy.index('keymap {'):]
symbolic = {}
for m in re.finditer(r'^\s*(\d+)\s*\{\s*label\s*=\s*"[^"]*";\s*bindings\s*=\s*<(.*?)>;', skm, re.M | re.S):
    symbolic[int(m.group(1))] = split_bindings(m.group(2))
for lid in range(0, 25):
    assert len(compiled[lid]) == 36 and len(symbolic[lid]) == 36, lid
    cx = [p for p in range(36) if compiled[lid][p] != '&trans']
    sx = [p for p in range(36) if symbolic[lid][p] != '&trans']
    assert cx == sx, (lid, cx, sx)
    for p in range(36):  # behaviour names must agree
        assert compiled[lid][p].split()[0] == symbolic[lid][p].split()[0], (lid, p, compiled[lid][p], symbolic[lid][p])

base_c, base_s = compiled[0], symbolic[0]

# ---------- triggers ----------
trig = {}  # layer -> (pos, letter, note, trigger_layer)
for p, b in enumerate(base_s):
    m = re.match(r'&ak (\d+) (\w+)$', b)
    if m and int(m.group(1)) in LAYER:
        trig[int(m.group(1))] = (p, m.group(2), '', 0)
assert base_s[POS['LH0']].startswith('&blt_akR 25')
trig[17] = (POS['LH0'], 'R', 'thumb hold-tap &blt_akR (tap-preferred 200 ms) -> ak_R_macro -> &ak 17 R', 0)
# l_akhE (10) is armed only by RM2 resolved on l_akH (9): `&ak 10 E`
assert symbolic[9][POS['RM2']] == '&ak 10 E'
trig[10] = (POS['RM2'], 'E', 'E resolved on l_akH (&ak 10 E) = 2nd key of H,E', 9)
assert sorted(trig) == list(range(2, 25)), sorted(trig)

def letter_of(b):
    m = re.match(r'&(?:ak \d+|bk) (\w+)$', b)
    return m.group(1) if m else None

def describe(b):
    m = re.match(r'&replace_char_with_bigram_(\w\w)$', b)
    if m: return f'BSPC+{m.group(1)} (replace…{m.group(1)})'
    return b

# ---------- pairs ----------
pairs = []
for lid in range(2, 25):
    tp, tl, tnote, tlayer = trig[lid]
    k1 = kmax(tp, tlayer)
    for fp in range(36):
        b = symbolic[lid][fp]
        if b == '&trans':
            continue
        if compiled[lid][fp] == base_c[fp]:
            continue  # same binding as base (the trigger's own repeat key) -> not an adaptation
        k2 = kmax(fp, tlayer)
        k2_ak = kmax(fp, lid)  # follower captured fresh while the AK layer is already on
        shared = [] if tp == fp else [c for c in real_on(tp, tlayer) if fp in c['kp']]  # a repeat key cannot co-press with itself
        shared2 = [c for c in shared if len(c['kp']) == 2]
        pairs.append(dict(
            layer=lid, layer_name=LAYER[lid], trig_pos=NAMES[tp], trig_letter=tl, trig_note=tnote,
            trig_layer=tlayer, fol_pos=NAMES[fp], fol_base=base_s[fp], fol_ak=b, fol_ak_desc=describe(b),
            k1=k1, k2=k2, k2_on_ak_layer=k2_ak,
            shared=[f"{c['name']}({'/'.join(NAMES[k] for k in c['kp'])},{c['timeout']}ms,{len(c['kp'])}-key)" for c in shared],
            shared_max=max((c['timeout'] for c in shared), default=0),
            shared_2key=[c['name'] for c in shared2],
            shared_2key_binding=[c['binding'] for c in shared2],
            trig_hack_only=(k1 == 0), fol_hack_only=(k2 == 0),
            hands=hand(tp) + hand(fp), repeat=(tp == fp),
        ))

# ---------- band derivation ----------
def bands(p):
    k1, k2, S = p['k1'], p['k2'], p['shared_max']
    dA = max(11, k1)
    d2 = max(11, k2)
    r = {}
    if p['trig_pos'] == 'LH0' and not p['repeat']:  # R thumb trigger: hold-tap path, timed from thumb release
        r['cls'] = 'R-thumb'
        r['native_on'] = 'no Δ band: HIT for follower↓ anywhere in [thumb↓, thumb↑+88] (thumb↑ < 200 = tap)'
        r['board_on'] = 'no Δ band: HIT for follower↓ in [thumb↓, thumb↑+88], ⚖️ thumb↑+89'
        r['native_off'] = 'no Δ band: HIT for follower↓ in [thumb↓, thumb↑+100]'
        r['board_off'] = 'no Δ band: HIT for follower↓ in [thumb↓, thumb↑+99], ⚖️ thumb↑+100'
        r['worst_board_on'] = -1
        r['edge_b_on'] = 'thumb↑ + 100 − 11'
        r['edge_b_off'] = 'thumb↑ + 100'
        return r
    if p['repeat']:
        r['cls'] = 'repeat'
        r['native_on'] = r['board_on'] = f'no Δ band (same key: 2nd↓ after 1st↑; 1st flushed at its ↑ or at {dA}, layer ≤ +10; 2nd held ≥ 11) → HIT to edge'
        r['native_off'] = r['board_off'] = r['native_on'] if k2 else 'no Δ band (0 ms tap: layer on at 1st↑, before any 2nd↓) → HIT to edge'
        if p['trig_pos'] == 'LH0':
            r['native_on'] = r['board_on'] = 'no Δ band (thumb tap = 0 ms nested &ak → layer on at 1st↑; 2nd↓ held ≥ 11 by the hack) → HIT to edge'
        r['worst_board_on'] = -2
        r['edge_b_on'] = dA + 110 - d2
        r['edge_b_off'] = k1 + 110 - k2
        return r
    if p['shared_2key']:
        r['cls'] = 'S2'
        r['native_on'] = f'COMBO Δ≤{S-1} · HIT {S}…{dA+111-d2}'
        r['board_on'] = f'COMBO Δ≤{S-1} · HIT {S}…{dA+109-d2} · ⚖️{dA+110-d2}'
        r['native_off'] = r['native_on'] if k1 else '?'
        r['board_off'] = f'COMBO Δ≤{S-1} · HIT {S}…{k1+109-k2} · ⚖️{k1+110-k2}'
        r['worst_board_on'] = S - 1
    elif S:
        r['cls'] = 'S3'
        r['native_on'] = f'MISS Δ≤{S-1} · HIT {S}…{dA+111-d2}'
        r['board_on'] = f'MISS Δ≤{S-2} · STALL {S-1} · HIT {S}…{dA+109-d2} · ⚖️{dA+110-d2}'
        r['native_off'] = f'MISS Δ≤{S-1} · HIT {S}…{k1+111-k2}'
        r['board_off'] = f'MISS Δ≤{S-2} · STALL {S-1} · HIT {S}…{k1+109-k2} · ⚖️{k1+110-k2}'
        r['worst_board_on'] = S - 1
    else:
        r['cls'] = 'N' if k2 else 'H0'
        r['native_on'] = f'MISS Δ≤10 · HIT 11…{dA+111-d2}'
        r['board_on'] = f'MISS Δ≤9 · STALL 10 · HIT 11…{dA+109-d2} · ⚖️{dA+110-d2}'
        if k2:
            e_off_n = (k1 + 1 if k1 else 0) + 111 - (k2 + 1) + 1  # native: off = D_A+112, B = Δ+k2+1, strict <
            r['native_off'] = f'HIT 0…{e_off_n}'
            r['board_off'] = f'HIT 0…{k1+109-k2} · ⚖️{k1+110-k2}'
        else:
            e_off_n = (k1 + 1 if k1 else 0) + 111  # native: B immediate (Δ), off = D_A+112
            r['native_off'] = f'MISS Δ≤{k1+11 if k1 else 10} · ⚖️{k1+12 if k1 else 11} (native order) · HIT …{e_off_n}'
            r['board_off'] = f'MISS Δ≤{k1+9} · ⚖️{k1+10} · HIT {k1+11}…{k1+109} · ⚖️{k1+110}'
        r['worst_board_on'] = 10
    r['edge_b_on'] = dA + 110 - d2
    r['edge_b_off'] = k1 + 110 - k2
    return r

for p in pairs:
    p.update(bands(p))

order = {'S3': 0, 'S2': 1, 'N': 2, 'H0': 3, 'R-thumb': 4, 'repeat': 5}
pairs.sort(key=lambda p: (-p['worst_board_on'], order.get(p['cls'], 9), -p['shared_max'], p['layer'], POS[p['fol_pos']]))

json.dump(dict(combos=combos, pairs=pairs), open(INV / 'sweep_pairs.json', 'w'), indent=1)

# summary
from collections import Counter
print('pairs total', len(pairs))
print('by class', Counter(p['cls'] for p in pairs))
print('hands', Counter(p['hands'] for p in pairs))
print('repeat', [f"{p['trig_letter']}→{p['fol_pos']}" for p in pairs if p['repeat']])
for p in pairs:
    print(f"{p['cls']:7s} {p['layer_name']:7s} {p['trig_pos']} {p['trig_letter']:1s} k1={p['k1']:2d} -> {p['fol_pos']} base={p['fol_base']:22s} ak={p['fol_ak']:30s} k2={p['k2']:2d}/{p['k2_on_ak_layer']:2d} shared={p['shared']} | ON n:{p['native_on']} | b:{p['board_on']} | OFF b:{p['board_off']} | edge {p['edge_b_on']}/{p['edge_b_off']}")
