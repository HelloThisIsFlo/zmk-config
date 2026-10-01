#!/usr/bin/env python3
"""Verbatim evidence lines for PAIRS.md: presses, combo capture/filter/flush, delivery layer, HID downs, layer changes, hold-tap decisions (up to the first physical release)."""
import re, sys
KEEP = re.compile(r"pressed: true|capturing position|releasing position|reraising position|filter_timed_out|layer_id:|"
                  r"hid_listener_keycode_pressed|layer_changed|decided")
for c in sys.argv[1:]:
    print(f"#### {c}")
    print("```")
    for line in open(f"{c}.raw.log", errors="replace"):
        line = line.rstrip("\n")
        if "pressed: false" in line:
            break
        if "bubble (no undecided" in line:
            continue
        if line.startswith("[") and not line.startswith("[00:00:00.000,000]") and KEEP.search(line):
            print(line)
    print("```")
