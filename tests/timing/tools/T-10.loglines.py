#!/usr/bin/env python3
"""Print the noise-filtered raw log lines of one T-10 case (for T-10.md)."""
import re, sys
DROP = re.compile(r"USB endpoint|Modifiers set|zmk_endpoints_send_report|Listener (captured|handled)|"
                  r"bubble \(no undecided|delaying next keypress|behavior_macro_init|handle_control_binding|"
                  r"Booting|get_selected_transport|Welcome|kscan_mock_work_handler_0")
keep_mock = "--mock" in sys.argv
for line in open(sys.argv[1]):
    line = line.rstrip("\n")
    if not line.strip():
        continue
    if keep_mock and "kscan_mock_work_handler_0" in line and "ev 1 row 1 column 0 state 0" not in line:
        print(line); continue
    if DROP.search(line):
        continue
    print(line)
