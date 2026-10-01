#!/usr/bin/env python3
"""Verbatim key lines (with [prefix]) for a T-23 case: position events, combo, delivery, HID, layers, exit."""
import re, sys, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")  # tests/timing/logs (raw logs used to sit next to this script)
KEEP = re.compile(r"Row:|capturing position|releasing position|reraising position|filter_timed_out|layer_id:|"
                  r"hid_listener_keycode_(pressed|released): usage|layer_changed|Exiting")
for line in open(os.path.join(R, sys.argv[1] + ".raw.log"), errors="replace"):
    line = line.rstrip("\n")
    if line.startswith("[00:00:00.000,000]") or not line.startswith("["):
        continue
    if KEEP.search(line):
        print(line)
