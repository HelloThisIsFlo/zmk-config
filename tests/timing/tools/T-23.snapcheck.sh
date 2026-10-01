#!/bin/bash
# Re-derive the harness snapshot from each timestamped raw log (run-test.sh:35 pipeline) and compare.
H="$(cd "$(dirname "$0")/.." && pwd)"   # tests/timing
R=$H/logs
T=$H/cases
for c in T-23-a-MT-d5 T-23-b-CP-d6 T-23-c-CP-d6-nohack T-23-d1-LG-d13 T-23-d2-LG-d5 T-23-e1-LG-d20-nohack T-23-e2-LG-d28-nohack T-23-d3-LX-d13 T-23-d4-LX-d5 T-23-e3-LX-d20-nohack T-23-e4-LX-d28-nohack T-23-d5-LG-d15 T-23-d6-LG-d16 T-23-e5-LG-d13-nohack; do
  a=$(sed -e "s/.*> //" "$R/$c.raw.log" | sed -n -f "$T/$c/events.patterns" | sed -e 's/[[:space:]]*$//')
  b=$(sed -e 's/[[:space:]]*$//' "$T/$c/keycode_events.snapshot")
  if [ "$a" = "$b" ]; then echo "$c: raw log (filtered) == snapshot ($(echo "$b" | wc -l | tr -d ' ') lines)"; else echo "$c: MISMATCH"; fi
done
