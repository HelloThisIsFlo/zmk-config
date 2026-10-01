import re, sys
P = re.compile(r"^\[(\d\d):(\d\d):(\d\d)\.(\d{3}),\d{3}\]\s+<\w+>\s+zmk:\s+(?:(\S+?):\s+)?(.*)$")
def ms(m): return ((int(m.group(1))*60+int(m.group(2)))*60+int(m.group(3)))*1000+int(m.group(4))
def run(path):
    keys=[]; cur=None
    for line in open(path, errors="replace"):
        m=P.match(line.strip())
        if not m: continue
        t=ms(m); f=m.group(5); msg=m.group(6)
        r=re.match(r"Row: \d+, col: \d+, position: (\d+), pressed: (\w+)", msg) if f=="zmk_physical_layouts_kscan_process_msgq" else None
        if r and r.group(2)=="true":
            cur=dict(pos=int(r.group(1)),t=t,cap=False,rungs=[],deliver=None,hid=None,layer_on=None,layer_off=None,ht=None); keys.append(cur); continue
        if cur is None: continue
        if "capturing position event" in msg and cur["deliver"] is None: cur["cap"]=True
        if "remaining_candidates" in msg and cur["deliver"] is None:
            a=re.search(r"remaining_candidates=(\d+) timestamp=(\d+)",msg); cur["rungs"].append((t-cur["t"],int(a.group(1)),int(a.group(2))-cur["t"]))
        if f=="zmk_keymap_apply_position_state" and cur["deliver"] is None: cur["deliver"]=t-cur["t"]; cur["binding"]=msg.split("binding name: ")[1]
        if "new undecided hold_tap" in msg and cur["ht"] is None: cur["ht"]=t-cur["t"]
        if f=="hid_listener_keycode_pressed" and cur["hid"] is None: cur["hid"]=(t-cur["t"],int(re.search(r"keycode 0x(\w+)",msg).group(1),16))
        if "layer_changed" in msg:
            s=re.search(r"layer (\d+) state (\d)",msg)
            if s.group(2)=="1" and cur["layer_on"] is None: cur["layer_on"]=(int(s.group(1)),t-cur["t"])
            if s.group(2)=="0" and cur["layer_off"] is None: cur["layer_off"]=(int(s.group(1)),t-cur["t"])
    for k in keys:
        hid=f"+{k['hid'][0]} {chr(ord('A')+k['hid'][1]-4) if 4<=k['hid'][1]<=0x1d else hex(k['hid'][1])}" if k["hid"] else "-"
        rungs=" ".join(f"[+{a}] rem={b} ts=t+{c}" for a,b,c in k["rungs"]) or "(none)"
        lo=f"L{k['layer_on'][0]} ON +{k['layer_on'][1]}" if k["layer_on"] else ""
        lf=f"OFF +{k['layer_off'][1]}" if k["layer_off"] else ""
        print(f"pos {k['pos']:>2} t={k['t']:>5} cap={'Y' if k['cap'] else 'N'} deliver=+{k['deliver']} ({k['binding']}) ht={('+'+str(k['ht'])) if k['ht'] is not None else '-'} HID↓ {hid} | rungs: {rungs} | {lo} {lf}")
for p in sys.argv[1:]:
    print("##", p.split('/')[-1]); run(p)
