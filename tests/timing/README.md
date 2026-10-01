# AK timing tests (native_posix)

The `native_posix_64` cases that proved how the adaptive-key timing really works. They run in ZMK's own test harness, out of tree, from this repo.

> [!tip] What the cases prove, and how to read their logs
>
> [`Design/Timing/TESTS.md`](../../Design/Timing/TESTS.md) has:
>
> - The two rigs and the position → mock-coordinate maps
> - The harness arithmetic (native +1 ms per timer, mock gaps) and how to translate to board time
> - An index of every case: what it establishes, its outcome, its write-up

## What is here

```
tests/timing/
├── run.sh      runner: build + run + snapshot diff, or the raw timestamped log
├── cases/      184 dirs: 3 rig templates (_rig_*) + 181 runnable cases
│   └── <case>/ native_posix_64.keymap · native_posix_64.conf · events.patterns · keycode_events.snapshot
├── logs/       <case>.raw.log for all 180 run cases (timestamped evidence) + <case>.snapshot copies for 153 of them, as produced during the investigation
└── tools/      tl.py (timeline printer), case generators (*.mkcases.py), excerpt / check helpers
```

- `_rig_R1`, `_rig_R1_nohack`, `_rig_R2` are **templates**
  - No `&kscan events` → they do not build
  - Copy one, append an `events` block, never edit them in place
- R2 cases `#include "/workspaces/zmk-config/config/corne.keymap"`
  - That path exists only inside the container, where this repo is bind-mounted
  - It is the **live** keymap: a binding change can change an R2 case's output

## run.sh

```sh
./run.sh <case>          # build, run, diff against keycode_events.snapshot → PASS / FAIL
./run.sh <case> --raw    # build, then print the timestamped `zmk.exe --no-rt` log on stdout
./run.sh all             # every case except _rig_*, then a PASS / FAIL / NO-SNAPSHOT summary (J=4 parallel)
ZMK_TESTS_AUTO_ACCEPT=1 ./run.sh <case>   # first run of a new case: write its snapshot
```

- Host side; it `docker exec`s into `zmk-devcontainer` and starts it if it is stopped
- Builds go to the fork's gitignored `zmk/app/build/zmk-config-timing/<case>/`
  - `keycode_events_full.log` (prefix-stripped) and `keycode_events.log` (filtered) stay next to the build
- Same pipeline as ZMK's `app/run-test.sh`, which only takes a case path relative to `app/` (it cannot reach this repo's `cases/`)
- `T-15-fix-b-hack-noquicktap` has no snapshot (never built during the investigation) → `NO-SNAPSHOT`

## logs/

- `<case>.raw.log` = stdout of `zmk.exe --no-rt` for that case; the timestamps are the evidence
  - Regenerate any of them with `./run.sh <case> --raw > logs/<case>.raw.log`
- **Deterministic**: 1 ms tick, one thread, no real time → a re-run is byte-identical
  - The move into this repo was checked by md5 against these files
- `<case>.snapshot` = the harness's filtered, untimestamped view (ordering only)
- `T-02-a-spec.rerun.raw.log` is a second run of the same binary, kept as the determinism check

## tools/

- `tl.py <raw.log>` → one line per event, `+rel  abs  event`, relative to the first key press
- `*.mkcases.py` (+ `mk_T05_cases.py`, `T-10.mkfix.py`) → the generators that wrote the case dirs
  - They now write into `cases/`, each dir a `copytree` of a template
  - `S`, `T-07`, `T-07-fix` delete an existing dir of the same name first; the others stop on one
- Paths inside the tools are relative to this folder
  - Exception: `ARB.mkfinal.py` rewrites `Design/Timing/results/CORRECTIONS-FINAL.md`; `mk_T11_md.py` reads `*.key.txt` extracts that were not kept
