#!/usr/bin/env python3
"""Print verbatim raw log lines (with [prefix]) that matter for T-23, dropping known noise."""
import re, sys
NOISE = ("USB endpoint is not supported", "Failed to send key report", "Modifiers set to",
         "zmk_endpoints_send_report", "Listener handled", "Listener captured", "no undecided hold_tap active",
         "Ignore upstroke", "delaying next keypress", "macro mode set", "macro tap time", "macro wait time",
         "macro param", "Precalculate", "kscan_mock_work_handler_0: ev")
KEEP = re.compile(r"Row:|capturing position|releasing position|reraising position|filter_timed_out|layer_id:|"
                  r"hid_listener_keycode|layer_changed|Invoking|Processing next queued|new sticky_key|"
                  r"Iterating macro|Exiting|mo_keymap_binding|decided|new undecided")
for line in open(sys.argv[1], errors="replace"):
    line = line.rstrip("\n")
    if not line.startswith("[") or line.startswith("[00:00:00.000,000]"):
        continue
    if any(n in line for n in NOISE):
        continue
    if KEEP.search(line):
        print(line)
