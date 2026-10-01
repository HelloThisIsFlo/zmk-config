import re, sys
KEEP = re.compile(r"Row: .*pressed: true|Row: .*pressed: false|capturing position event|releasing position event|reraising position event|remaining_candidates|layer_id:|hid_listener_keycode_(pressed|released): (usage|unregistering)|layer_changed|Exiting")
def extract(path, lo, hi):
    out = []
    for line in open(path):
        m = re.match(r"\[00:00:(\d\d)\.(\d{3}),000\]", line)
        if not m: continue
        ms = int(m.group(1))*1000 + int(m.group(2))
        if lo <= ms <= hi and KEEP.search(line):
            out.append(line.rstrip().replace("<dbg> zmk: ", ""))
    return out
if __name__ == "__main__":
    p, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    print("\n".join(extract(p, lo, hi)))
