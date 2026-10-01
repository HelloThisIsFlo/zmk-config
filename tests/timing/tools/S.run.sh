#!/bin/bash
# Build + run each sweep case, then capture the timestamped --no-rt log.
# Paths are relative to tests/timing: cases/ for the case dirs, logs/ for the evidence.
# ../run.sh replaces the fork's run-test.sh (first run of a new case: ZMK_TESTS_AUTO_ACCEPT=1 writes its snapshot).
H="$(cd "$(dirname "$0")/.." && pwd)"
R=$H/logs
for c in "$@"; do
  echo "=== $c"
  ZMK_TESTS_AUTO_ACCEPT=1 "$H/run.sh" "$c" 2>&1 | tail -2
  "$H/run.sh" "$c" --raw > $R/$c.raw.log
  echo "raw: $(wc -l < $R/$c.raw.log) lines md5 $(md5 -q $R/$c.raw.log)"
  cp $H/cases/$c/keycode_events.snapshot $R/$c.snapshot 2>/dev/null
done
echo ALLDONE
