#!/usr/bin/env python3
"""Per-position combo candidate analysis from the compiled right-half devicetree."""
import re
from collections import defaultdict

SRC = "/private/tmp/claude-501/-Users-flo-Work-Private-Dev-Keyboard-zmk-config/56bdead7-aa9e-4bbc-b13e-b1255ed79094/scratchpad/combos_node.dts"
NAMES = {4:"LT0",3:"LT1",2:"LT2",1:"LT3",0:"LT4",5:"RT0",6:"RT1",7:"RT2",8:"RT3",9:"RT4",
         14:"LM0",13:"LM1",12:"LM2",11:"LM3",10:"LM4",15:"RM0",16:"RM1",17:"RM2",18:"RM3",19:"RM4",
         24:"LB0",23:"LB1",22:"LB2",21:"LB3",20:"LB4",25:"RB0",26:"RB1",27:"RB2",28:"RB3",29:"RB4",
         32:"LH0",31:"LH1",30:"LH2",33:"RH0",34:"RH1",35:"RH2"}

text = open(SRC).read()
combos = []
for m in re.finditer(r"(combo_\w+) \{(.*?)\n\t\t\};", text, re.S):
    name, body = m.group(1), m.group(2)
    kp = [int(x,16) for x in re.search(r"key-positions = <([^>]*)>", body).group(1).split()]
    tm = re.search(r"timeout-ms = <([^>]*)>", body)
    timeout = int(tm.group(1).strip(),16) if tm else 50
    ly = re.search(r"layers = <([^>]*)>", body)
    layers = [int(x,16) for x in ly.group(1).split()] if ly else [-1]
    layers = [l if l < 0x80000000 else l - 0x100000000 for l in layers]
    bind = re.search(r"bindings = <([^>]*)>", body).group(1).strip()
    combos.append(dict(idx=len(combos), name=name, kp=kp, timeout=timeout, layers=layers, bind=bind))

print(f"total combos: {len(combos)}")
print("definition order (= virtual key position order, = tie-break order):")
for c in combos:
    print(f"  #{c['idx']:2d} {c['name']:28s} len={len(c['kp'])} timeout={c['timeout']:3d} "
          f"keys={[NAMES[k] for k in c['kp']] if len(c['kp'])<8 else 'ALL36'} layers={'0-24' if c['layers']==list(range(25)) else ('all32' if c['layers']==list(range(32)) else c['layers'])}")

per_pos = defaultdict(list)
for c in combos:
    for k in c["kp"]:
        per_pos[k].append(c)

def lookup_order(cs):
    return sorted(cs, key=lambda c: (len(c["kp"]), c["idx"]))

print("\nper-position combo_lookup order (shortest first, then definition order) with timeouts:")
for k in range(36):
    cs = lookup_order(per_pos[k])
    on_alpha = [c for c in cs if 0 in c["layers"]]
    on_nav = [c for c in cs if 25 in c["layers"]]
    print(f"  pos {k:2d} {NAMES[k]}: n={len(cs):2d}  alpha: n={len(on_alpha)} maxT={max((c['timeout'] for c in on_alpha), default=0):3d} "
          f"[{', '.join(f'{c['name'][6:]}({c['timeout']})' for c in on_alpha)}]")
    if on_nav != on_alpha:
        print(f"           nav(25): n={len(on_nav)} maxT={max((c['timeout'] for c in on_nav), default=0):3d} "
              f"[{', '.join(f'{c['name'][6:]}({c['timeout']})' for c in on_nav)}]")

print("\nmax combos on any single position:", max(len(v) for v in per_pos.values()), "(limit CONFIG_ZMK_COMBO_MAX_COMBOS_PER_KEY=30)")
print("max keys in a combo:", max(len(c['kp']) for c in combos), "(limit CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO=36)")
hack_only_alpha = [NAMES[k] for k in range(36) if [c for c in per_pos[k] if 0 in c['layers']] == [c for c in per_pos[k] if c['name']=='combo_ak_consistency_hack']]
print("positions whose ONLY alpha-layer combo is the hack (solo delay = 11ms):", hack_only_alpha)
