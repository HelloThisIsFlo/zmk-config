# 🔍 REVIEW-FABLE-PAIRS — correctness gate on `PAIRS.md`

> [!note] Result
>
> - **Target:** `Design/Timing/PAIRS.md` (1149 → 1151 lines)
> - **≈ 300 statements re-checked** against the compiled devicetree, `sweep_pairs.json`, the 21 raw logs, the cited `combo.c` / `behavior_queue.c` / `behavior_hold_tap.c` lines and the T-12 / T-13 / T-14 / T-23 / FIX-R13-eqmin logs
> - **14 errors fixed, 2 flagged-tension callouts replaced by their resolution, 0 tags downgraded**
> - Mermaid: `@mermaid-lint/cli@0.53.1 --no-semantic` → 2 diagrams, 0 errors, 0 warnings

## 🧪 What was verified, and how

- **54-pair table** → every row's class, k1, k2, S, shared combos, hack-only flags, hand and band profile re-derived from the 28 compiled combos
  - Combos read from `zmk/app/build/zmk-config-timing/T-23-a-MT-d5/zephyr/zephyr.dts` (28 nodes, timeouts 16/18/11) = `research/sweep_pairs.json` `combos`
  - Re-derivation = JSON = doc on all 54 rows; profile counts 1/1/4/11/23/6/1/4/3 = 54; hands 42 L-L / 12 R-R; k2 identical on layer 0, layer 1 and the AK layer for all 54
- **Window edges** → `dA + 110 − d2` / `k1 + 110 − k2` recomputed for the 5 groups (110, 112, 108, 105/94, 115/126) ✓
- **21 validation blocks** → every cited `[hh:mm:ss.mmm]`, keycode and layer id found in `tests/timing/logs/S-*.raw.log`; every `t+N` recomputed from the case's `&kscan events` (generator `S.mkcases.py` rule) ✓
  - The 21 verbatim ```log blocks are byte-identical to `S.excerpt.py` over the raw logs
  - Integrity: `sed 's/.*> //' raw.log | md5` = build `keycode_events_full.log` md5 for all 21; raw md5 of S-H_RM2-d17 = `13915840…` ✓; `-nohack` builds carry 0 hack nodes, the rest 1 ✓; each case's `keycode_events.snapshot` = its build's `keycode_events.log` (the `PASS` criterion) ✓
- **Source cites** → `combo.c:141-143, 163-195, 228, 397-405, 407-420, 429-433, 442-447, 448-452, 472-481, 496-502`, `behavior_queue.c:35`, `ht:142-147` all point at the stated code in the fork ✓; combo `require-prior-idle-ms` default −1 (`zmk,combos.yaml`) ✓
- **Earlier tests cited** → T-12-b-d111 HIT / d112 MISS, T-13-d re-raise onto layer 17, T-14-c layer 17 ON in the tap-decision ms, T-23-e3 MISS / e4 same-ms HIT, FIX-R13-eqmin `[00:00:00.045,000] … timestamp=44` ✓
- **Live keymap caveat** → the uncommitted change to `adaptive_keys/combos.dtsi` is comment-only, so the 28 compiled combos still hold for the R2 cases

## 🛠️ Changes

| # | location | what was wrong | evidence | fix |
|---|---|---|---|---|
| 1 | 🔢 54 pairs, 6 classes | "D §10's 77 non-`&trans` cells include 23 repeat cells that equal the base binding" — both numbers wrong (the difference, 54, was right) | Compiled `zephyr.dts` layers 2–24: 75 non-`&trans` cells, 21 equal to layer 0; D §10's own table lists 75 cells; the trigger cells on l_akhE (`&ak 10 E`) and l_akR (`&ak 17 R`) differ from base and are pairs #53/#54 | 75 / 21, with the 2 differing trigger cells named as the repeat pairs |
| 2 | 🌳 Which class is a pair? (flowchart) | Thumb test came before the same-key test → R→LH0 (#54) would land in R-thumb, the table says repeat | Pair table #54 = 👍 repeat; `sweep_pairs.py` l.136 (`repeat` wins); MODEL.md's class flowchart tests same-key first | Decision order swapped: same key → thumb → shared combo |
| 3 | 📏 Bands per class, 🟪 S2 board cell | "same" as native, i.e. HIT S…E_n — but the board edge is E_b − 1 with ⚖️ at E_b (tension 1) | From Δ = S the S2 pair follows the N path (🧪 S-M_LT3-d16 key-first flush + fresh set); edge 🧪 T-12-b-d110/d111/d112 (HIT 110, 111, MISS 112 → E_b 110, E_n 111); 📊 Band profiles already had 16…109 · ⚖️110 | Cell now reads `🟪 COMBO Δ ≤ S−1 · ✅ HIT S…E_b−1 · ⚖️ E_b` |
| 4 | 📏 Bands per class, `[!warning] Two source statements disagree` | Flagged tension, unresolved (tensions 1 + 2) | #3 above; R13 refuted by 📜 `combo.c:429-433` + 🧪 FIX-R13-eqmin; Δ = 0 unreachable on the mock | Replaced by a `[!note]` stating both resolutions with their evidence; "HIT Δ ≥ 0" kept, its Δ = 0 cell marked 🧮 |
| 5 | 🪟 Upper window edge | "⚖️ sub-ms coin flip" (tension 5) | CORRECTIONS-FINAL F1: board ties undetermined, neither "coin flip" nor "leans to the timer"; native timer-first is a harness fact | "⚖️ unresolved on hardware (F1)" + two bullets on why, native noted as harness-only |
| 6 | 📋 Band notation | "⚖️ = sub-ms tie" (tension 5) | F1 | "⚖️ = tie, unresolved on hardware (F1)" |
| 7 | 🗂️ S-M_LT3-d16 board line | "key vs rung = sub-ms order" (tension 5) | F1; outcome is order-independent | "key vs rung at t+16 is a board tie, F1; either order gives B a fresh set" |
| 8 | 🧾 Corrections, upper edge bullet | "that exact Δ is a sub-ms tie on the board" (tension 5) | F1 | "a ⚖️ tie on the board, unresolved on hardware (F1)" |
| 9 | ⚠️ Deviations item 3 | "All 21 … match the prediction to the ms" contradicts items 1–2 (tension 3) | S-A_RT2-d10 `[00:00:00.033,000] … keycode 0x2E`, S-S_LH0-d10 `[00:00:00.033,000] … keycode 0x15` = t+23, predicted at B↑ = t+70; the other 19 match to the ms; all 21 HID sequences / delivery layers / layer ids match | "The other 19 cases match to the ms; all 21 HID sequences, delivery layers and layer ids match; only the char time of items 1–2 differs" |
| 10 | ⚠️ Deviations, `[!warning] Item 3 vs items 1–2` | Flagged tension (tension 3) | #9 | Replaced by a `[!note]`: one deviation (forced TAP), 2 cases, outcome unchanged |
| 11 | 📋 Sources | `build/tests/ak-truth/T-23-a-MT-d5/zephyr/zephyr.dts` no longer exists; `tmp-cpp/*` is investigation scratch (tension 6) | Build now at `zmk/app/build/zmk-config-timing/T-23-a-MT-d5/zephyr/zephyr.dts` (present, 28 combos re-read from it); `tmp-cpp` lives only in the scratchpad | Paths re-pointed; `tmp-cpp` labelled scratch, not in the repo |
| 12 | 🛠️ Rig, Cases | `zmk/app/tests/ak-truth/S-*`, `results/S.mkcases.py` (tension 6) | Cases in `tests/timing/cases/S-*`, generator in `tests/timing/tools/` | Linked to `tests/timing/cases/`, generator path fixed; original run location kept in parentheses |
| 13 | 🛠️ Rig, Integrity | `build/…` unlocated; `run-test.sh` is ZMK's runner; the cited md5 is the raw log's, not the stripped one (ambiguous as written) | Builds under `zmk/app/build/zmk-config-timing/<case>/`; `md5 -q S-H_RM2-d17.raw.log` = `13915840…` | Build path, runner (today `tests/timing/run.sh`) and "raw-log md5" made explicit |
| 14 | 🗂️ Per-case evidence, Filter + Full logs | `results/S.excerpt.py`, `results/S-*.raw.log` (tension 6) | Files in `tests/timing/tools/` and `tests/timing/logs/` | Paths re-pointed, logs linked |
| 15 | Footer | `results/S.*`, `zmk/app/tests/ak-truth/S-*` (tension 6) | as above | Footer lists the `tests/timing/` locations, original location in parentheses |

## ⚖️ Tensions

| # | tension | resolution | evidence |
|---|---|---|---|
| 1 | S2 board "same as native" vs `HIT 16…109 · ⚖️110` | Pair/profile table right; "same" was shorthand for the combo band only. Board = 🟪 ≤ S−1 · ✅ S…E_b−1 · ⚖️ E_b | 🧪 S-M_LT3-d16 (N path from Δ = S) · 🧪 T-12-b-d110/d111/d112 (E_b 110, E_n 111) · 🧮 `dA + 110 − d2` |
| 2 | N hack-OFF "HIT Δ ≥ 0" vs the 🧮 Δ = 0 equal-deadline strand | "HIT Δ ≥ 0" stands; the strand (R13) is ⛔ refuted; Δ = 0 cell is 🧮 (mock cannot reach it) | 📜 `combo.c:429-433` · 🧪 FIX-R13-eqmin `[00:00:00.045,000] … remaining_candidates=0 timestamp=44` → `releasing position event 2` |
| 3 | Deviations item 3 "all 21 to the ms" vs items 1–2 | 19/21 to the ms; the 2 hold-tap-base followers differ only in the char time; all 21 outcomes, letters, delivery layers, layer ids match | 🧪 S-A_RT2-d10 / S-S_LH0-d10 `[00:00:00.033,000]` = t+23 vs predicted t+70 |
| 4 | Erratum's stale line numbers (l.70, l.77, l.279-282) | **Nothing to re-anchor in PAIRS.md**: its erratum already locates the † lines by section (🔣 Symbols, 📏 Bands per class, 🗂️ Per-case evidence, 🧾 Corrections); checked, all five anchors exist and carry †. The stale numbers live in `MODEL.md` "Erratum for PAIRS.md" and `FIX-LOG.md` RVA-12, outside this document | `grep -n 'l\.[0-9]' PAIRS.md` → none |
| 5 | "sub-ms coin flip" / "⚖️ = sub-ms tie" vs F1 | Reworded at all 4 sites to "unresolved on hardware (F1)"; the two remaining "sub-ms" strings are inside † lines the erratum keeps verbatim on purpose | CORRECTIONS-FINAL F1 |
| 6 | In-body `results/S.*`, `zmk/app/tests/ak-truth` paths | Re-pointed to `tests/timing/{tools,logs,cases}`; build output to `zmk/app/build/zmk-config-timing/` | directory listings |

## ❓ Left as is

- `MODEL.md` "Erratum for PAIRS.md" cites investigation-copy line numbers (l.70, l.77, l.279-282) → for MODEL.md's reviewer
- The † lines (δ ∈ (0.03, 1.05], ≈95 %/5 %, "≈5 % MISS", "no sub-ms risk") stay verbatim with † by the erratum's design; the left-hand phase effect stays ❓ OPEN
- D→LB0 / V→LB1 (`tab`) and W→LT2 are 🧮, never executed — stated as such in the document
- No 🧪 tag needed downgrading: every one names a line that exists in a raw log
