# REVIEW-FABLE-TESTS — correctness gate for `TESTS.md`, `tests/timing/README.md`, `run.sh` usage

Reviewed 2026-10-01 against the raw logs in `tests/timing/logs/`, the case dirs, the fork source (`zmk/app/src/**`, `module/`, `keymap-module/`), Zephyr `kernel/timeout.c` / `work.c` in the devcontainer, `MODEL.md`, `PAIRS.md`, `results/T-02.md`, and the investigation's `RIG.md`, `FIX-LOG.md`, `CORRECTIONS-FINAL.md`.

> [!note] The short version
>
> - **16 fixes** across `TESTS.md` (13) and `README.md` (3); `run.sh` untouched, its usage text matched the docs
> - **3 tensions settled**, the flagged `[!warning]` on board δ replaced by a `[!note]`
> - **2 retags** — one 📜 → 🧪 (now proven by observation), one untagged fact → 🧮
> - **Index**: 184 / 184 dirs present, no duplicates, every link resolves; 41 rows re-derived from raw logs, all match
> - **Harness arithmetic**: every rule recomputed from a raw log; every cited `[hh:mm:ss.mmm,uuu]` exists
> - **Live runs**: `run.sh T-12-a-alone` → PASS; `--raw | md5` = the stored log; real-time vs `--no-rt` byte-identical
> - **Mermaid lint**: 2 diagrams, 0 errors

## 🔧 Changes

| # | File · location | What was wrong | Evidence | Fix |
|---|---|---|---|---|
| 1 | TESTS § Combo-engine log arithmetic | `candidate->timeout_at > timestamp` cited as `combo.c:231` | `grep -n` → `combo.c:228`; PAIRS.md also cites `:228` | `:231` → `:228` |
| 2 | TESTS § Combo-engine log arithmetic | "prints the intended deadline when the timer calls it" cited `combo.c:472` (the handler's first line) | the call `filter_timed_out_candidates(timeout_task_timeout_at)` is `combo.c:477` | `:472` → `:477` |
| 3 | TESTS § `run.sh` | "📜 `--no-rt` output is byte-identical to real-time output" carried a source tag with no source line | ran the same `zmk.exe` real-time and `--no-rt` (T-12-a-alone): both md5 `cc322d4bffa71872f568c422361baf0d` = `logs/T-12-a-alone.raw.log` | retag 🧪 with the observation |
| 4 | TESTS § Harness gotchas | "auto-accept turns any output into a PASS" | `run.sh:37-38` prints `ACCEPTED: <c> (snapshot written)`; only ZMK's `run-test.sh` prints `PASS` | reworded |
| 5 | TESTS § `run.sh` table | `./run.sh <case>` row omitted `NO-SNAPSHOT` (checked before the build, `run.sh:31-32`) and `ACCEPTED`; `all` row omitted `ACCEPTED` and the `J=N` override | `run.sh:30-41, 55-58` | both rows completed |
| 6 | TESTS § Making a new case · README § tools | generators listed as `*.mkcases.py` only | `tools/` also holds `mk_T05_cases.py` and `T-10.mkfix.py`, both write case dirs | both named |
| 7 | TESTS § R2 conf | "Without `MAX_KEYS_PER_COMBO=36` the 36-key hack fails at boot" stated as fact, untagged | never run; `combo.c:30` sizes `key_positions[]`, `:521-522` fill it from DT, `:97` / `:120` are the boot errors; G-test-harness §4 derives it from source | tagged 🧮, source lines cited, "never run that way" |
| 8 | TESTS § What native cannot show | "hardware adds ≈5 ms to every press and release; relative gaps between keys survive" | MODEL 🛣️: 4–6 ms debounce (both halves); MODEL 📡: left-left gaps quantised to ~7.5 ms (🧮) | "4–6 ms", scoped to same-half pairs; BLE quantisation sub-bullet added under "No split" |
| 9 | TESTS § What native cannot show | section listed only the Δ = 10 cell; MODEL also marks the S−1 cell 🔮 and every same-ms tie ⚖️ | MODEL truth 5 + 🟥 S3 ("Board ❌ ≤ S−2 · ⏸ S−1 · Native ❌ ≤ S−1"); PAIRS.md "board Δ = S−1 is not a quick tap → re-captured, R9 strand"; CORRECTIONS-FINAL F1 | two bullets added (S−1 cell, ⚖️ ties with the five cases) |
| 10 | TESTS § Translating to board time | `[!warning]` left the v1 "δ ∈ (0.03, 1.05] ms" convention standing next to the struck one | see 🧭 Tensions below | replaced by a `[!note]` with the reading rule and its evidence |
| 11 | TESTS § Case index legend | "⚖️ tie on the board" read as a fifth outcome; nothing said the glyphs are native observations | 41 rows re-derived from raw logs are native outcomes; ⚖️ appears only as "✅ native · ⚖️ board" | "**Out** = the native observation …; ⚖️ marks a same-ms tie that native resolved timer-first and the board leaves undetermined" |
| 12 | TESTS § T-19 | rows use `t` = htm press while the legend says `t` = the first key's press | all 7 T-19 logs: pos 3 (`&mo 4`) at `.031`, htm pos 5 at `.062`; T-19.md: "htm ↓ t+0 (62)"; `0xE0↓` at `.081` = htm + 19 | section note: pos 3 pressed first, `t` = the htm press |
| 13 | TESTS § Verifier probes | "the fork's `app/tests/ak-truth/` holds no `V-*` directory" — the directory itself no longer exists | `ls zmk/app/tests/ak-truth` → No such file | reworded: no `V-*` case was ever written; the dir is gone |
| 14 | README § What is here | `logs/` described as `<case>.raw.log + <case>.snapshot` for every case | 181 raw logs (180 cases + `T-02-a-spec.rerun`), 153 snapshots; the 28 follow-up cases (`*-fix-*`, ARB, CB, FIX, RV*) have only the raw log there (their snapshot lives in `cases/`) | counts stated |
| 15 | README § run.sh | "`app/run-test.sh` only discovers cases under `app/tests`" | `run-test.sh` takes any path relative to `app/` (`-DZMK_CONFIG="$(pwd)/$testcase"`); `all` = `tests` | "only takes a case path relative to `app/` (it cannot reach this repo's `cases/`)" |
| 16 | README § tools | "they … **replace** an existing dir of the same name" | only `S`, `T-07`, `T-07-fix` `rmtree` first; the other 10 `copytree(tpl, d)` and raise on an existing dir | split into the two behaviours |

- Clarification, not an error: the Harness-rules intro now says `T-12-a-alone` is the same events as `T-01-r2` with an md5-identical log (`cc322d4b…`), since the table cites T-12-a while the diagram is T-01-r2

## 🧭 Tensions settled

### Board δ convention (the flagged `[!warning]`)

- **Resolution** — the `results/T-xx.md` board columns are read as native − 1 per timer hop; their integer instants stand; the sub-ms phrasing in them is superseded
- **Evidence**
  - FIX-LOG RVB-03 (APPLY): "v1 δ ∈ (0.03, 1.05] = target + arming phase + ε … F1 conflated the two" → MODEL 🎲 split into two quantities
  - CORRECTIONS-FINAL F1 side note: "MODEL's δ ∈ (0.03, 1.05] is wrong by C §4's own SRC table (δ ≤ 0.061 ms per hop). The 1.05 figure must not reach the page"
  - MODEL 🎲: per hop `K_MSEC(n)` fires n + 0.005–0.061 ms after arming (📜 `timeout.c:122`, read in the container: `to->dticks = timeout.ticks + 1 + elapsed();`); right-hand φ ≈ 0.01–0.15 ms on the scan grid; left-hand φ ∈ [0, 1) from BLE receipt, magnitude ❓
  - F1: board ties are undetermined — not "leans to the timer", not a coin flip
- **Result in TESTS.md** — the struck figure now appears once, inside the `[!note]`, marked ⛔; no statement repeats it as fact (`grep 1.05|95 %|0.05 %|coin flip|leans` → only the note and the ⚖️ negation)

### Index `t` convention vs the T-19 rows

- **Resolution** — a one-line note on the T-19 section (pos 3 held first, `t` = the htm press)
- **Evidence** — the seven T-19 raw logs and T-19.md's own timeline (above, fix 12)

### "What native cannot show" vs MODEL.md

- **Resolution** — the section now carries all three board-only cells: Δ = 10 ⏸ (🔮), S−1 ⏸ (🔮), ⚖️ ties undetermined
- **Evidence** — MODEL truths 3 and 5, 🟥 S3, 📡 target bullets; CORRECTIONS-FINAL F1; PAIRS.md S3 sequence note

## 🏷️ Tags changed

| Statement | Was | Now | Why |
|---|---|---|---|
| `--no-rt` output byte-identical to real-time | 📜 (no source cited) | 🧪 T-12-a-alone, md5 `cc322d4b…` both ways | proven by observation on 2026-10-01 |
| 36-key hack without `MAX_KEYS_PER_COMBO=36` fails at boot | untagged fact | 🧮 `combo.c:30, :97, :120, :521-522` | never executed; the failure mode is read from source |

## 🧪 What was verified and held

- **Harness arithmetic** (each rule recomputed from a raw log)
  - +1 per relative timer: T-01-r1 `delaying 100` → `Row` at `[.101]`; T-12-a 10 ms tick `[.118]` → `[.129]`; sticky 100 → `[.129]` → `[.230]`
  - Mock schedule, e0 applied twice, gap = ms + 1: T-01-r1 D↓ `.101`, D↑ `.202`, C↓ `.213`, C↑ `.264`, exit `.275` (md5 `8d51067c…` = RIG's original)
  - `ms = 0` → same ms: T-08-fix-boundary-rel1 press + release at `[.012]` (events `PRESS(0,1,0)`)
  - Two hops for a rung-delivered `&ak`: T-02-a-spec t = 6, rung `[.018]` (t+12), `… in 10ms` → `[.029]` (t+23) — matches T-02.md's reconciliation
  - Chained `K_MSEC(130)` ×2: T-18-a release `[.242]` → `[.373]` → B↓ `[.504]` = +262
  - Lone-key ladder: T-11-c +17/+12/+17/+12/+19/+19/+19/+31/+31/+12/+12/+17 (hold-tap positions 9, 10 created at +12, HID at key-up); T-01-r2-map RM1 `[00:00:01.126,000]` = +19
  - Same-tick ordering: T-07-d11 `[.022]` layer before `Row`; T-04-d12 `[.024] timestamp=23` before `Row`; T-15-c `[.202]` hold-timer before the release; T-12-b-d112 `[.179]` sticky OFF before `timestamp=178`; T-23-e4 `[.056]`
  - Deadline-vs-prefix: `117@[.118]` (T-22-d), `33@[.034]`, `50@[.051]` (T-22-c), `48@[.049]` (T-22-b), `90@[.091]` (T-22-f), key path `30@[.030]` (T-22-a); `remaining_candidates=2 timestamp=24` at `[.024]` in T-10-a with only Q18 surviving
  - Window edge: gap 15 fires / 16 does not (T-22-a/b), 29 fires / 30 does not (T-22-e/f)
- **Source lines** (fork + container): `timeout.c:117-122, 125-131`, `work.c:277`, `physical_layouts.c:147-160`, `central.c:125-131, 259-266`, `behavior_queue.c:53`, `combo.c:430-431`, `kscan_mock.c:52-73, :61, :68`, `kscan_mock.h:9-14`, `modules.cmake:26-35` — all as cited
- **Log-format section**: every example line exists verbatim (`Row:`, `capturing`, `remaining_candidates=1 timestamp=112`, `releasing`, `layer_id:`, `hid_listener_keycode_pressed … 0x17`, `layer 19 state 1`, `Invoking key_press: 0x70017 0x00`, `Iterating macro bindings - starting: 0, count: 7` / `starting: 7, count: 0`, `0 new sticky_key`, `31 decided tap (hold-preferred decision moment key-up)`, `Exiting`); all four `decide_hold_tap` status strings occur in the logs; T-18-d `[.381]` shows `explicit_mods 0x00` + `Modifiers set to 0x02`; T-14-a `[.102]` has `… in 10ms` between H↓ and H↑; `Ignore upstroke` and `-95` noise are R2-only; `events.patterns` identical across the three rigs and matches the snapshot vocabulary
- **Rigs**: R1/R2 confs as quoted; R2 includes and transforms as quoted; `-DZMK_CONFIG` bind mount `type=none, o=bind, device=/Users/flo/…/zmk-config`; `corne.conf` / `corne.keymap` / `CONFIG.h` md5 identical host vs container; `combos.dtsi` working-tree diff = 6 comment lines
- **Faithful move**: the six md5s in the table match `logs/`; `T-01-r1-delhack` = `T-01-r1-nohack` = `848cbcfd…`; `T-02-fix-a-spec` and `T-02-a-spec.rerun` = `T-02-a-spec`; all 181 `logs/*.raw.log` md5-identical to the investigation's originals (`scratchpad/investigation/results/`, incl. `CORR-B/`)
- **Index**: 184 rows = 184 dirs; 41 rows re-derived (`T-03`, `T-04-d9/d11`, `T-05`, `T-05-d16`, `T-06a/b/c`, `T-08-a`, `T-09-a`, `T-10-a/c/e`, `T-11-b`, `T-12-b-d111/d112`, `T-12-c`, `T-13-b/d`, `T-15-d/e`, `T-16-a/b`, `T-17-a/b2`, `T-18-fix-b`, `T-19-a`, `T-20-a/b/c/e`, `T-21-a/f`, `T-23-a/c/d3/d6`, `S-N_LT4-d11`, `S-O_RT3-d10`, `S-A_RT2-d11`, `S-M_LT3-d16`, `S-H_RM2-d17`, `RVA-ex33-cpn`, `RVB-pin-akfollower`, `RVB-park-two`, `ARB-F3-c`, `FIX-R13-eqmin`) — outcome glyph and quoted times match in every one
- **Commands**: `tests/timing/run.sh T-12-a-alone` → `PASS: T-12-a-alone`; `… --raw | md5` = `cc322d4b…` = `logs/T-12-a-alone.raw.log`; `tl.py` runs on a raw log and its flags are `--all --abs --t0 --grep` as documented; `J=6 tests/timing/run.sh all` → see below
- `run.sh` usage text (lines 2-9) matches the script and both docs; the script was not changed

## ❓ Not settled here

- The sweep count in TESTS.md "Faithful move" (180 PASS · 0 FAIL · 1 NO-SNAPSHOT) — re-run result recorded in the final line below
- The provenance split "23 cases through `run.sh --raw` itself; the rest by `zmk.exe --no-rt`" is historical and not re-checkable; the md5 identity it claims is re-checked (181 / 181)
- `results/T-xx.md` still contain the v1 δ wording and "coin flip" / "≈ 97 %" phrasing (e.g. T-02.md §Board translation, T-05.md §Board translation); they are outside this review's scope — TESTS.md now tells the reader how to read them
- The `MAX_KEYS_PER_COMBO` boot-failure mode stays 🧮 (would need a deliberate failing build to become 🧪)

## 🧾 Sweep result (2026-10-01)

- `J=6 tests/timing/run.sh all` was stopped by the review harness's 20-minute cap after **78 of 181** cases (≈ 15 s per case: real-time `zmk.exe` runs plus three `docker exec`s each; a full sweep needs ≈ 45 min)
  - The `all` mode buffers its output until the end, so the per-case lines were lost; the 78 fresh `keycode_events.log` files were graded by hand against `cases/<c>/keycode_events.snapshot` (trailing whitespace ignored, as `diff -Z` does)
  - **78 PASS · 0 FAIL · 0 NO-SNAPSHOT** — families covered: ARB ×7, CB ×1, FIX ×2, RVA ×4, RVB ×5, all 21 `S-*`, T-01 ×7, T-02 ×4, T-03 ×2, T-04 ×4, T-05 ×4, T-06 ×3, T-07 ×6, T-08 ×6, T-09-a, T-12-a
- TESTS.md's "180 PASS · 0 FAIL · 1 NO-SNAPSHOT" therefore stands as the investigation's own tally; this review re-confirms 78 of the 180 passes, every case's snapshot presence (all but `T-15-fix-b-hack-noquicktap`), and 181 / 181 raw-log md5 identity with the originals
