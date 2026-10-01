#!/usr/bin/env bash
# Out-of-tree runner for the AK timing proof cases (native_posix_64).
# Does what ZMK's app/run-test.sh does, for cases that live in this repo instead of app/tests.
#
#   ./run.sh <case>          build, run, diff against keycode_events.snapshot -> PASS / FAIL
#   ./run.sh <case> --raw    build, then print the timestamped `zmk.exe --no-rt` log on stdout
#   ./run.sh all             every case under cases/ except the _rig_* templates, then a summary
#                            (J=8 ./run.sh all runs 8 cases in parallel; default 4)
#   ZMK_TESTS_AUTO_ACCEPT=1 ./run.sh <case>   first run of a new case: write its snapshot
set -uo pipefail

CONTAINER=zmk-devcontainer
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
C_CASES=/workspaces/zmk-config/tests/timing/cases  # cases/ as the container sees it (repo bind mount)
C_APP=/workspaces/zmk/app                          # the ZMK fork's app/ (west source dir + cwd)
C_BUILD=build/zmk-config-timing                    # relative to app/; app/build is gitignored in the fork

box() { docker exec -w "$C_APP" "$CONTAINER" bash -c "$1"; }

# Build one case. Output is swallowed (as in run-test.sh); rerun the printed line to see errors.
build() {
  local cmd="west build -s $C_APP -d $C_BUILD/$1 -b native_posix_64 -- -DCONFIG_ASSERT=y -DZMK_CONFIG=$C_CASES/$1"
  box "$cmd" >/dev/null 2>&1 || { echo "FAIL: $1 (did not build; to see why: docker exec -w $C_APP $CONTAINER $cmd)"; return 1; }
}

# Run one case the run-test.sh way: real-time exe, strip the "[time] <lvl> " prefix,
# keep the full log, filter with events.patterns, diff against the snapshot.
# ZMK_TESTS_AUTO_ACCEPT=1 (as in run-test.sh) writes the snapshot instead of failing.
check() {
  local c=$1 b=$C_BUILD/$1 d=$C_CASES/$1 accept=${ZMK_TESTS_AUTO_ACCEPT:-}
  [ -f "$HERE/cases/$c/keycode_events.snapshot" ] || [ -n "$accept" ] \
    || { echo "NO-SNAPSHOT: $c (raw-only case; use --raw)"; return 2; }
  build "$c" || return 1
  box "./$b/zephyr/zmk.exe | sed -e 's/.*> //' | tee $b/keycode_events_full.log | sed -n -f $d/events.patterns > $b/keycode_events.log"
  if box "diff -auZ $d/keycode_events.snapshot $b/keycode_events.log" >"${QUIET:-/dev/stdout}" 2>&1; then
    echo "PASS: $c"
  elif [ -n "$accept" ]; then
    box "cp $b/keycode_events.log $d/keycode_events.snapshot" && echo "ACCEPTED: $c (snapshot written)"
  else
    echo "FAIL: $c (filtered log kept at zmk/app/$b/keycode_events.log)"; return 1
  fi
}

# Start the devcontainer if it is not running (same check as ../zmk/build_and_flash.sh).
if [ "$(docker inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null)" != "true" ]; then
  echo "Starting $CONTAINER" >&2
  docker start "$CONTAINER" >/dev/null || exit 1
fi

case "${1:-}" in
  "" | -h | --help)
    sed -n '2,9p' "$0"; exit 1 ;;
  all)
    # Templates have no &kscan events and do not build; skip them. Diffs are muted, logs are kept.
    out=$(ls "$HERE/cases" | grep -v '^_rig_' | QUIET=/dev/null xargs -P "${J:-4}" -I{} "$0" __check {})
    echo "$out" | sort -k2
    echo "---"
    for s in PASS FAIL NO-SNAPSHOT ACCEPTED; do printf '%-12s %s\n' "$s" "$(echo "$out" | grep -c "^$s:")"; done
    ! echo "$out" | grep -q '^FAIL:' ;;
  __check)                                   # internal: one case inside an `all` run
    check "$2" ;;
  *)
    [ -d "$HERE/cases/$1" ] || { echo "No such case: cases/$1" >&2; exit 1; }
    if [ "${2:-}" = "--raw" ]; then
      # stdout = exactly what `zmk.exe --no-rt > x.raw.log 2>&1` wrote, so md5s compare with logs/
      build "$1" >&2 && box "./$C_BUILD/$1/zephyr/zmk.exe --no-rt 2>&1"
    else
      check "$1"
    fi ;;
esac
