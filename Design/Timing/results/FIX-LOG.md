# 🛠️ FIX-LOG — REVIEW-A + REVIEW-B applied to MODEL_v2.md and PAGE_FACTS.md

> Targets edited in place: `MODEL_v2.md` (566 → ~645 l.), `PAGE_FACTS.md` (622 → ~650 l.). Pre-fix copies: `fixwork/MODEL_v2.pre-fix.md`, `fixwork/PAGE_FACTS.pre-fix.md`. Edit scripts: `fixwork/m1–m8.py`, `fixwork/p1–p6.py` (exact-string replace, each asserted unique).
> Tags: **PROVEN(case `[prefix]`)** native_posix log · **SRC** `file:line` · **INF** inferred.

## 🎯 Result first

- **40 findings → 39 applied, 1 split (RVB-08: applied for PAGE §1 fact 10, rejected for the R13 Δ = 0 ⏸ cell), 0 uncertain.**
- **Disputed truths settled:** #3 = confirmed core + B's refinement (strand-join) applied; #7 = B right, clause "fires at its own 16/18 ms deadline" partly refuted (bspc/del) and rewritten.
- **2 new native cases** (own dirs, templates untouched, both `run-test.sh` PASS with auto-accept):

| case | rig | events (abs ms) | decisive lines | md5 (raw log) | settles |
|---|---|---|---|---|---|
| `FIX-R13-eqmin` | `_rig_R1_nohack` | A = pos 7 (`&ak 3 H`, only W30) ↓14 · B = pos 2 (`&kp C`, only R16, shares nothing) ↓28 · B↑129 · A↑140 → both MIN = 44 | `[00:00:00.028,000] … remaining_candidates=1 timestamp=28` → `releasing position event 7` → `reraising position event 2` → `capturing position event 2` → **`[00:00:00.045,000] … remaining_candidates=0 timestamp=44`** → `releasing position event 2` → `keycode 0x06` | `c3e3f148973be01e44b4547027d0cbc4` | MODEL R13 refuted (equal MIN does not strand) |
| `FIX-linger-hold-akfollower` | `_rig_R1` | lk pos 9 ↓41 ↑192 (HOLD) · pos 1 `&ak 2 B` ↓82 ↑203 | `[00:00:00.142,000] … decided hold-timer` → `keycode 0x1B` (linger X↓) → `Releasing key position event for position 1` → `layer_id: 0 position: 1, binding name: flo,behavior-adaptive-key` → **`[00:00:00.153,000]` X↑ + `keycode 0x05`** | `bc0c72b310cb2b7e0a3fc5eea7017113` | RVA-13: queued follower on HOLD path emits at linger↑ (+10 board) |

- **Side correction (not raised by a reviewer, forced by RVB-08):** MODEL R13 "hack-off equal-deadline strand" struck as REFUTED.
  - SRC: B's press calls `update_timeout_task()` with 0 candidates **before** `cleanup()` (`combo.c:429-433`). That resets `timeout_task_timeout_at`: native → `LLONG_MAX` branch → 0 (`:412-414`); board → schedule refused (A's timer DELAYED) → phantom `LONG_MAX` (`:417-418`). No stale equality survives to B's re-raise.
  - PROVEN(FIX-R13-eqmin) at Δ = 14 with equal MIN. Δ = 0 unreachable on the mock (min gap 1 ms); same code path.
  - PAIRS.md l.279-282 (origin of R13) listed in the new erratum.

## ⚖️ Disputed truth verdicts

| truth | A | B | settled | evidence |
|---|---|---|---|---|
| #3 fast-roll failure | confirmed | weakened | **confirmed + refined (B's refinement applied)**. Native bands PROVEN; board STALL stays BOARD-ONLY; ⏸ exit rewritten: next release or next non-sharing press, a press inside the follower's fresh hack window joins | T-23-a `[00:00:00.017,000] … layer_id: 0 position: 13`; T-04-d10 `[00:00:00.022,000]`; RVB-strand-join `[00:00:00.020,000] … capturing position event 0`, no rung `[00:00:00.024,000]`, flush `[00:00:00.073,000]` |
| #7 real combos under the hack | confirmed (nit) | partly refuted | **partly refuted → rewritten.** "Fires at its own 16/18 ms deadline" false for `bspc`/`del` (t+18 via siblings, hack ON or OFF); A's nit (deadline OR next release/unrelated press) also applied | RVB-bspc-d12 `[00:00:00.029,000] … timestamp=28` → `[00:00:00.031,000] … remaining_candidates=0 timestamp=30` + `keycode 0x2A` (t+19 native); RVB-bspc-d5-nohack `[00:00:00.024,000] … keycode 0x2A` (t+19 native); SRC `combo.c:448-452` |

## 📋 Findings — REVIEW-A

| id | decision | evidence checked | edits |
|---|---|---|---|
| RVA-01 | ✅ APPLY | T-04-d10 `[00:00:00.022,000] … layer_id: 0 position: 3` is a native MISS (supports, cannot kill a board claim); T-02-c/T-03 prove the strand only under altered quick-tap / raw `&kp` key 1 | PAGE §1 must-NOT "At 10 ms the board types the base letter" removed → merged into caveat ("print neither it nor its negation"); OPEN #1 adds MISS paths |
| RVA-02 | ✅ APPLY | RVA-callum-relaxed180 `[00:00:00.297,000] … layer_id: 26 position: 16, binding name: hold_tap_mod`, 0 × `keycode 0x04`; RVA-callum-close245 `[00:00:00.352,000] layer 26 state 0` → `[00:00:00.362,000] … layer_id: 0 position: 16` → `[00:00:00.483,000] … 0x04` + `Modifiers set to 0x02`; old page `index.html:2036-2045, 2057, 2078` | MODEL (g) close/relaxed bullets + strike; PAGE §2 facts 14, 18, Ex 2.2 notes, must-NOT, Concept 2 table (4 rows) |
| RVA-03 | ✅ APPLY | RVA-htls-forcedtap-d5 `[00:00:00.017,000] … 31 decided tap (hold-preferred decision moment quick-tap)` → `keycode 0xE1`; LH1↑ `[00:00:00.260,000]`; `grep -c 'layer 26'` = 0; SRC `mods/behaviors.dtsi` htls has no `require-prior-idle-ms`; `ht:142-149`. RH0 = `&blt 29 SPACE` (tap-preferred, default) → INF | MODEL (g) forced-TAP bullet, (i) scope; PAGE §2 facts 1, 17, must-NOT; §4 fact 7; OPEN #22 |
| RVA-04 | ✅ APPLY | SRC `behavior_queue.c:34-35` (`.timestamp = k_uptime_get()`), `behavior_sticky_key.c:181-186`; T-12-a OFF `[00:00:00.230,000]` = ON `[00:00:00.129,000]` + 101 | MODEL truth 9 rewritten; PAGE §6 fact 7; MODEL (n) REFUTED + SRC lists |
| RVA-05 | ✅ APPLY | sweep_pairs.json l_akA RT2 `fol_ak: "&bk U"`; SRC `ht:619-620` term = ts + term − now, `K_MSEC(≤0)` → immediate; T-16-d-d11 created `[00:00:00.034,000]`, HOLD `[00:00:00.123,000]` | MODEL (i) Δ = 10 outcome by E (3 cases, LH0 term 210); (k) forced-TAP Δ = 10 removed from ⚖️ list; (n) BOARD-ONLY row; PAGE Ex 4.2 note, §4 caveat, OPEN #14 |
| RVA-06 | ✅ APPLY | T-23-d1 `[00:00:00.030,000] … layer_id: 0 position: 21` (Δ 13); `combos.dtsi:26` entr2 = RM0 RM1 (RM0 = comsemi linger), `:55` magicBracketsL = RB0 RB1 (RB0 = MagicUnder, RB1 = U) | PAGE §1 facts 4, 10; §4 fact 6 exception; MODEL (i) exception; MODEL truth 4 precondition |
| RVA-07 | ✅ APPLY | S-M_LT3-d5 `[00:00:00.022,000] … 0x1D` (t+17 native) vs T-09-c `[00:00:00.012,000]`; T-02-a vs T-02-b-nohack | MODEL truths 6, 7, (d) S2 heading + hack-OFF line; PAGE §1 facts 3, 12, 13, 14 |
| RVA-08 | ✅ APPLY | S-S_LH0-d10 R↓ `[00:00:00.033,000] … keycode 0x15`, R↑ + `layer 17 state 1` `[00:00:00.044,000]` | MODEL (c) idle-queue precondition + busy-queue bullet, (d) caveat, (e) R-thumb row; PAGE §3 facts 15, 16, 18; §7 fact 9; OPEN #24 |
| RVA-09 | ✅ APPLY | T-20-a pos 11 = `&kp LSHIFT` (`[00:00:00.119,000] … layer_id: 0 position: 11, binding name: key_press`); RIG R1 | MODEL (h) rig bullet; PAGE §3 fact 8 rig caveat |
| RVA-10 | ✅ APPLY | T-18-f LM1 delivered at key-up `[00:00:00.215,000]`; T-18-g held to `[.391]`; T-08-b release flush `[00:00:00.016,000]` | MODEL truths 1, 9, (g) delivery bullet; PAGE §1 fact 2, §2 facts 5, 12, must-NOT "Order matters" |
| RVA-11 | ✅ APPLY | RVA-callum-relaxed180 `[00:00:00.280,000]` → `[00:00:00.297,000] … remaining_candidates=0 timestamp=296`; RVA-callum-close245 `[00:00:00.362,000]`; RVA-ex33-cpn: P `[00:00:00.057,000] … layer_id: 4 position: 3 … bigram-TP`, N `[00:00:00.082,000] … layer_id: 0 position: 12`, p↓ `[00:00:00.090,000] … 0x13`, `[00:00:00.101,000] layer 16 state 1` + `0x11`, `[00:00:00.112,000]` | MODEL landscape, (g), (n); PAGE §2 fact 10, caveat; Ex 3.3 now PROVEN with a native column (all 12 rows = native − hops, re-derived); OPEN #7, #15 → RESOLVED |
| RVA-12 | ✅ APPLY | PAIRS.md l.70, l.77, rows S-H_RM2-d17 / S-N_LT4-d10 / S-A_RT2-d10 ("≈5 % MISS"), S-N_LT4-d11 ("no sub-ms risk") | Erratum block in MODEL (e) + PAGE source header. PAIRS.md itself not edited |
| RVA-13 | ✅ APPLY (upgraded to PROVEN) | T-15-e follower = raw `&kp` (`[00:00:00.142,000] … key_press`); new FIX-linger-hold-akfollower `[00:00:00.153,000] … keycode 0x05` | MODEL (f) HOLD path split; PAGE §4 fact 5 |
| RVA-14 | ✅ APPLY | T-18-fix-b-htm232 rungs `[00:00:00.370,000]`/`[00:00:00.372,000]` → `layer_id: 4` (combo-held, R+130−k); T-18-b2 `[00:00:00.361,000]` (R+119, mid-window) | MODEL (g) Ctrl/Alt/Gui bullet reworded ("not run at the edge"); PAGE §2 caveat + must-NOT |
| RVA-15 | ✅ APPLY | T-04-d11 `[00:00:00.033,000]` layer / `[00:00:00.034,000] … 0x14`; RIG R1 pos 1 hack-only, Δ 11 = dA | PAGE Ex 1.4 proof pointer |
| RVA-16 | ✅ APPLY | C §1/§3: anchor wait 0–7.5 ms + stack → 0.5–9 ms total (median 4.5); MODEL (m) left stamp moved upstream | MODEL time convention + diagram note; PAGE header, §6 facts 3, 10 |
| RVA-17 | ✅ APPLY | SRC `central.c:263` (stamp in BT RX callback), `combo.c:417` (`K_MSEC(first_timeout − k_uptime_get())`), `behavior_queue.c:61-62` (layer tick armed synchronously, before B's re-raise) | MODEL (d) margin split (right ≈ 1.01 ms; BLE follower ≈ 0, still HIT), truth 4 exception; PAGE §1 fact 4 |
| RVA-18 | ✅ APPLY | `combos.dtsi:55` magicBracketsL = combo RB0 RB1; morph = `MagicUnder` | MODEL (f) naming |
| RVA-19 | ✅ APPLY | SRC `combo.c:198` `LONG_MAX`, `:412-418` `LLONG_MAX` compare; work.c:967 (in container `/workspaces/zmk/zephyr/kernel/work.c`) "Schedule … if it's idle or running"; `cleanup()` cancels (`combo.c:398`) → CANCELING | MODEL R11 split into board path / native path |
| RVA-20 | ✅ APPLY | D-config §6.2 rows 12 (del `<17 18>`), 13 (delWord `<16 17 18>`), 25 (capsWord); ARB-F2 event lists have no pos 17 (raw logs: positions 16, 18, 13 only) | PAGE key map adds I/RM3; MODEL R10 delWord bullet → INFERRED |

## 📋 Findings — REVIEW-B

| id | decision | evidence checked | edits |
|---|---|---|---|
| RVB-01 | ✅ APPLY | RVB-pin-akfollower `[00:00:00.162,000] … layer_id: 1 position: 7, binding name: transparent` → base `&ak` → `[00:00:00.173,000] … mo_keymap_binding_released: position 0 layer 1` → `layer 1 state 0` → `0 new sticky_key` → `layer 3 state 1`; Shift↑ `[00:00:00.263,000]`; SRC `behavior_sticky_key.c:85-92, 147-151` | MODEL (h) pin bullet, (c) position-0 bullet ("Moot" struck), diagram note, truth 9; PAGE §3 fact 8, must-NOT, Concept 3 row, DEEP doc-fix line |
| RVB-02 | ✅ APPLY | see disputed #7 | MODEL truth 7, R7 Flo bullet, (l); PAGE §1 fact 13, §5 facts 4, 5, Concept 5 row |
| RVB-03 | ✅ APPLY | SRC `combo.c:417`, `sk:182-186`, `ht:619-620`, `central.c:263`; C §4 table = lateness after arming; MODEL v2 old l.25 vs l.124 contradiction confirmed. v1 δ ∈ (0.03, 1.05] = target + arming phase + ε, i.e. the absolute-target quantity; F1 conflated the two | MODEL time convention (two quantities), (d) struck items reworded "basis restated, left-hand OPEN", (k) L-L phase race, (n) REFUTED line rescoped; PAGE §6 fact 6, must-NOT ×2 rescoped to right-hand, caveat, OPEN #3 |
| RVB-04 | ✅ APPLY (as INF) | SRC `physical_layouts.c:147-160` (callback = put + submit), `:178-182` (stamp `k_uptime_get()` in the work item); `usb_hid.c:25-27` (`hid_sem` 1/1), `:139` (`k_sem_take(&hid_sem, K_MSEC(30))`), `in_ready_cb` gives it; `app/Kconfig:142-143` poll 1 ms; `endpoints.c:123-127` synchronous; `hog.c:259-274` msgq + own workqueue (non-blocking); `behavior_hold_tap.c:220-221` `k_msleep(10)` when `undecided_hold_tap != NULL` | MODEL time convention, (a) bullets, (d) now_flush caveat; PAGE §1 caveat, §6 caveat, OPEN #1, #20 |
| RVB-05 | ✅ APPLY | see disputed #3; SRC `combo.c:407-411` early return on equal MIN, `:422-433` | MODEL state diagram (`Dead --> Dead` join), R9 join + board trigram INF, (d) Δ = 10, legend, truth 3; PAGE glyph, §1 fact 7, caveat, OPEN #19 |
| RVB-06 | ✅ APPLY | T-02-a `[00:00:00.018,000] … keycode 0x04` (t+12) vs T-02-b-nohack `[00:00:00.012,000] … keycode 0x04` (t+6), same events; T-23-a `[00:00:00.017,000]`; T-08-b `[00:00:00.016,000]` | MODEL truths 1, 6, (n) REFUTED; PAGE §1 facts 2, 3, slider must-NOT |
| RVB-07 | ✅ APPLY | T-23-d1 `[00:00:00.030,000]`; S-H_RM2-d16 `[00:00:00.035,000]`; S-M_LT3-d14 `[00:00:00.028,000] … 0x1D` | PAGE §1 fact 4 (same edit as RVA-06/17) |
| RVB-08 | ✅ APPLY (fact 10, window edge) · ❌ REJECT (R13 ⏸ cell) | fact 10 vs must-NOT confirmed (T-23-e5 `[00:00:00.030,000]`; S-H_RM2-d17-nohack `[00:00:00.036,000]`; S-M_LT3-d15-nohack `[00:00:00.030,000]`). R13 mechanism does not exist: SRC `combo.c:429-433` + FIX-R13-eqmin `[00:00:00.045,000] … timestamp=44` | PAGE §1 fact 10, §7 fact 10; MODEL truth 6 "below the window edge"; hack-OFF Δ = 0 cell kept ✅; R13 struck (see side correction) |
| RVB-09 | ✅ APPLY | same as RVA-01 | same edit |
| RVB-10 | ✅ APPLY | RVB-park-two B `[00:00:00.394,000] … layer_id: 0 position: 1`, A `[00:00:00.426,000] … layer_id: 0 position: 0`, B↓ `[00:00:00.504,000]`, `layer 2 state 1` + A↓ `[00:00:00.515,000]` (R+273 native = board R+270); T-18-a/a2/e/f/g each park one key | MODEL (g) park bullets ×3; PAGE §2 facts 5, 19, must-NOT, Concept 2 row |
| RVB-11 | ✅ APPLY | same as RVA-05; PAIRS rows 15/18 + sweep: every hold-tap-follower pair's AK cell is `&bk` (A/U→RT2, E/hE/O→RT1, S→LH0) | same edits as RVA-05 |
| RVB-12 | ✅ APPLY | same as RVA-08 | same edits |
| RVB-13 | ✅ APPLY | same as RVA-04; T-17-b2 `[00:00:00.051,000]` → `[00:00:01.552,000]` (hold-tap-invoked sticky does count from the press) | MODEL truth 9 |
| RVB-14 | ✅ APPLY | CORRECTIONS-FINAL F2 case table + ARB-F2-press40 raw log: positions 16, 18, 13 only; MODEL R10 exit 3 ("unrelated press also ends it") | MODEL R10 Flo bullets split (PROVEN / INF), RM2-after-t+18 branch; PAGE §5 fact 9 |
| RVB-15 | ✅ APPLY (as INF) | SRC `layers_C_extra.dtsi:41-43` (LT1 LG(V), LT0 LG(K), LM0 LG(A), LB3 LS(LG(Z)), LB2 LG(W), LB1 `________`, LB0 LG(S), RM0 `________`); `preprocessor_macros.c:41-47` COMBO_ANY_* = `l_all`; `combos.dtsi:24-27, 29, 45, 72` (space, entr, entr2, tab, esc2, magicCloseQuitCb, settings) | MODEL landscape new `l_mod` row, (g) closing-edge + LM0 bullets, truth 1; PAGE §2 fact 20, Ex 2.1 note tagged INF, must-NOT buffer; OPEN #21 |
| RVB-16 | ✅ APPLY (as INF) | `combos.dtsi:27` tab = `tabCmdtab`; `linger_keys/behaviors.dtsi:32` `&lk LG(TAB) TAB`; LK = tap-preferred, `linger_term` 100 | MODEL (d) S2 bullets + board timeline; PAGE §5 caveat; OPEN #23 |
| RVB-17 | ✅ APPLY | T-21-h `[00:00:00.074,000] … 0x10` before `[00:00:00.085,000] … 0x0F` = ordering only; native has no host | PAGE §3 must-NOT removed → caveat; Concept 3 row reworded |
| RVB-18 | ✅ APPLY | PAIRS row 1 H RM4 (18) → RM2 (18); E_b = 18 + 110 − 18 = 110 | MODEL E_b table label |
| RVB-19 | ✅ APPLY | PAGE Ex 5.1 rows = M→W only | PAGE §5 caveat rewritten |
| RVB-20 | ✅ APPLY | RIG.md l.10; T-01-r2-map `[00:00:01.126,000]` (+19); T-11-c `[00:00:01.159,000]` (+12) | PAGE §5 facts 6, 8 |

## 🧾 What the next agent should know

- New PROVEN facts now in the docs: RM1 `l_mod` lag/edge; page relaxed/close outcomes; LH1 forced TAP; Ex 3.3 "tpn"; pin ends at next `aksl↓`; `bspc`/`del` at t+18; strand join; park = one letter per tick, no adaptation; equal-MIN no strand; queued follower on linger HOLD path at +10.
- Still INFERRED/OPEN (PAGE OPEN #19–#24 added): board trigram join, USB workqueue blocking, `l_mod` ⌘-key combos, RH0 forced TAP + letter/linger 2-key combos, `tab` hold-tap timing, busy-queue R thumb.
- PAIRS.md is NOT edited; its stale lines are covered by the erratum in MODEL_v2 §(e) and the PAGE_FACTS header.
- Numbering kept stable: PAGE OPEN #7 and #15 marked ✅ RESOLVED rather than removed (caveats reference OPEN #3/#8/#10).
