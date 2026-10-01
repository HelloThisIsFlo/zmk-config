#!/usr/bin/env python3
"""Render sweep_pairs.json as the PAIRS.md pair table (markdown on stdout)."""
import json, re
from pathlib import Path

INV = Path(__file__).resolve().parent
d = json.load(open(INV / 'sweep_pairs.json'))
pairs = d['pairs']

KEYLET = dict(LT4='X', LT3='W', LT2='M', LT1='P', LT0='K', RT0='/', RT1='.', RT2='=', RT3='-', RT4="'",
              LM4='C', LM3='S', LM2='N', LM1='T', LM0='B', RM0=',', RM1='A', RM2='E', RM3='I', RM4='H',
              LB4='F', LB3='G', LB2='L', LB1='D', LB0='V', RB0='_', RB1='U', RB2='O', RB3='Y', RB4='J',
              LH2='num', LH1='⇧', LH0='R', RH0='␣', RH1='sym', RH2='OS')

def out(b):
    m = re.match(r'&ak (\d+) (\w+)$', b)
    if m: return m.group(2) + ('' if m.group(1) == '999' else f'·ak{m.group(1)}')
    m = re.match(r'&bk (\w+)$', b)
    if m: return {'MINUS': '-', 'EQUAL': '='}.get(m.group(1), m.group(1))
    m = re.match(r'&replace_char_with_bigram_(\w\w)$', b)
    if m: return f'⌫{m.group(1)}'
    return {'&lk COLON DOT': '. (tap) / : (linger)', '&lk_bk MINUS EQUAL': '= (tap) / - (linger)',
            '&blt_akR 25 0': 'R (tap) / nav (hold)'}.get(b, b)

COMBO_OUT = {'typeZ': 'Z', 'tab': 'Tab (tap) / ⌘Tab (linger)'}

def worst_off(p):
    if p['cls'] in ('S3', 'S2'): return p['shared_max'] - 1
    if p['cls'] == 'H0': return p['k1'] + 10
    return -1

order = {'S3': 0, 'S2': 1, 'H0': 2, 'N': 3, 'R-thumb': 4, 'repeat': 5}
pairs.sort(key=lambda p: (-p['worst_board_on'], -worst_off(p), order[p['cls']], p['layer'], p['fol_pos']))

print('| # | class | layer | trigger (k1) | follower pos (base key) | k2 | real combos shared by BOTH | hack-only | miss → adapted output | native, hack ON | board, hack ON | board, hack OFF | board window edge ON / OFF | hand |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for i, p in enumerate(pairs, 1):
    trig = f"{p['trig_letter']} {p['trig_pos']} ({p['k1']})" + (' via l_akH' if p['trig_layer'] == 9 else '')
    fol = f"{p['fol_pos']} ({KEYLET[p['fol_pos']]})"
    shared = ', '.join(p['shared']) or '—'
    flags = ' '.join(x for x, on in (('T0', p['trig_hack_only']), ('F0', p['fol_hack_only']), ('rep', p['repeat'])) if on) or '—'
    if p['cls'] == 'S2':
        mo = f"**{', '.join(COMBO_OUT[n] for n in p['shared_2key'] if n in COMBO_OUT)}** (combo, Δ<16) · {out(p['fol_base'])} → {out(p['fol_ak'])}"
    else:
        mo = f"{out(p['fol_base'])} → {out(p['fol_ak'])}"
    edge = f"{p['edge_b_on']} / {p['edge_b_off']}" if p['cls'] not in ('R-thumb',) else 'thumb↑+89 / thumb↑+100'
    hand = 'L-L (both via BLE)' if p['hands'] == 'LL' else 'R-R (central)'
    print(f"| {i} | {p['cls']} | {p['layer_name']} | {trig} | {fol} | {p['k2']} | {shared} | {flags} | {mo} | {p['native_on']} | {p['board_on']} | {p['board_off']} | {edge} | {hand} |")
