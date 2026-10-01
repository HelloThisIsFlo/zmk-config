# 🔎 REVIEW-B — adversarial review of `MODEL_v2.md` + `PAGE_FACTS.md`

> Reviewer B. Inputs: `MODEL_v2.md` (566 l.), `PAGE_FACTS.md` (622 l.), `PAIRS.md`, `RIG.md`, `results/CORRECTIONS-FINAL.md`, `results/T-*.md`, every cited `results/*.raw.log`, `results/CORR-B/*.raw.log`, fork source under `zmk/app/src`.
> Status tags: **PROVEN(case `[prefix]`)** = native_posix log line · **SRC** `file:line` · **INF** = inferred.
> Five new native cases run (own dirs `zmk/app/tests/ak-truth/RVB-*`, templates untouched). Each raw log's `sed 's/.*> //'` md5 equals the build's `keycode_events_full.log` md5.

## 🎯 Result first

- 🧱 **No blocker.** The page's core story holds: hack trade-off, bypass mechanism, 45/6/3 pair classes, `&ak` offsets, Callum park numbers, dead window, all re-derived and matching their logs.
- 🧨 **10 major, 10 minor defects.** Five of them are now PROVEN by new runs:
  - 📌 A modifier pin ends at the first `&ak`-bound follower (its `aksl↓` releases the pinned position-0 sticky), not at the modifier's UP → PAGE §3 fact 8 false for most letters. RVB-pin-akfollower.
  - ⌫ `bspc`/`del` fire at the 18 ms sibling deadline, hack ON or OFF, never "at the completing press" / "at completion". RVB-bspc-d12, RVB-bspc-d5-nohack.
  - ⏸ A strand is NOT ended by a press that shares a live candidate (the stranded key's own fresh hack): that press joins the timer-less set. RVB-strand-join.
  - 🎛️ Two letters parked by `moAndBuffer`: 2nd at R+270, and both were resolved on base before any AK layer existed → no adaptation inside the park. RVB-park-two.
- ⏱️ **Board-transfer lens:** the "≤ 0.061 ms" timer bound is per relative `K_MSEC(n)` only. Absolute-target timers (rungs, sticky OFF, hold-tap term) fire at the integer target **+ the arming instant's sub-ms phase** (MODEL's own line 124) → up to ~1.06 ms for left-hand-armed timers; USB `hid_sem` and `k_msleep(10)` block the same thread. The struck "≈5 % / ≈0.05 %" figures are the same mechanism MODEL keeps OPEN.

## 🧪 New evidence (native_posix, this review)

| case | rig + overlay | events (abs ms) | decisive lines |
|---|---|---|---|
| `RVB-pin-akfollower` | R1; base pos 11 = `&kp LSHIFT`; akA pos 7, 11 = `&trans` (so pos 7 → base `&ak 3 H`) | A↓ 51 · Shift↓ 102 · H-key↓ 151 ↑ 162 · Shift↑ 263 · A↑ 274 | `[00:00:00.119,000] … keycode 0xE1` (Shift pins layer 1) → `[00:00:00.162,000] … layer_id: 1 position: 7, binding name: transparent` → base `&ak` → `[00:00:00.173,000] … mo_keymap_binding_released: position 0 layer 1` → `layer 1 state 0` → `layer 3 state 1`; Shift↑ only `[00:00:00.263,000]` |
| `RVB-bspc-d12` | R2 (Flo), hack ON | RM1↓ 12 · RM2↓ 24 · ↑ 85 / 126 | `[00:00:00.024,000] … remaining_candidates=4 timestamp=24` (RM2 press) → `[00:00:00.029,000] … remaining_candidates=2 timestamp=28` → `[00:00:00.031,000] … remaining_candidates=0 timestamp=30` + `keycode 0x2A` = t+19 native (board t+18), not t+12 |
| `RVB-bspc-d5-nohack` | R2, hack node deleted (0 nodes in zephyr.dts) | RM1↓ 5 · RM2↓ 10 | `[00:00:00.022,000] … remaining_candidates=2 timestamp=21` → `[00:00:00.024,000] … remaining_candidates=0 timestamp=23` + `keycode 0x2A` = t+19 native, not "at completion" t+5 |
| `RVB-strand-join` | R1 (T-03 pattern: raw `&kp D` key 1 → key 2 stranded in the rung handler) + 3rd press | D↓ 6 · B↓ 12 · A↓ 20 · D↑ 73 | strand `[00:00:00.018,000] … reraising position event 1` → `capturing position event 1`; 3rd press `[00:00:00.020,000] … remaining_candidates=1 timestamp=20` → `capturing position event 0` (no flush); **no line at `[00:00:00.024,000]`** (B's fresh hack deadline 23); flush only at `[00:00:00.073,000] … releasing position event 1` → `reraising position event 0` → `layer_id: 0 position: 0` (bypassed) → A↓ `[00:00:00.084,000]` |
| `RVB-park-two` | R1 + T-18 `&htls 4 LSHIFT` overlay | thumb 121–242 (R=242) · B 383–394 · A 415–426 | B `[00:00:00.394,000] … layer_id: 0 position: 1`, A `[00:00:00.426,000] … layer_id: 0 position: 0`; B↓ `[00:00:00.504,000]` (R+262) · A↓ `[00:00:00.515,000]` (R+273 = board R+270) · `layer 2 state 1` only at `[00:00:00.515,000]` → A never saw l_akB (akB pos 0 `&bk P` unused) |

## 🎯 Ten truths — verdicts

| # | verdict | evidence / note |
|---|---|---|
| 1 longest candidate | ✅ confirmed | T-12-a `[00:00:00.118,000]` +17; T-01-r2-map `[00:00:01.126,000]` +19; T-11-c `[00:00:01.159,000]` +12; T-17-a3 `[00:00:00.062,000] … 0xE0`; T-17-a4 `[00:00:00.079,000] … 0xE1`. l_mod landscape row incomplete → RVB-15 |
| 2 `&ak` D / D+10 / D+110 | ✅ confirmed | T-12-a `[00:00:00.118,000]` / `[00:00:00.129,000] … layer 19 state 1` / `[00:00:00.230,000] … state 0` = +17/+28/+129 → board +16/+26/+126 (1/2/3 hops) |
| 3 fast-roll failure | ⚠️ weakened | Native bands PROVEN (T-23-a `[00:00:00.017,000] … layer_id: 0 position: 13`; T-23-b `[00:00:00.018,000] … position: 3`; T-04-d10 `[00:00:00.022,000]`; S-*-d10). Board ⏸ at 10 is described as "waits for the next event"; RVB-strand-join shows a press inside the follower's fresh hack window joins the strand → RVB-05 |
| 4 band 11 … E_b−1, E_b 105–115 | ✅ confirmed (numbers) | T-04-d11 `[00:00:00.033,000]`/`[00:00:00.034,000]`; S-N_LT4-d11 same; T-12-b-d111 `[00:00:00.178,000] … layer_id: 19`; d112 `[00:00:00.179,000] … layer 19 state 0` first; E_b arithmetic re-derived for all 5 groups. "⚖️ = firmware µs tie" wrong for L-L pairs → RVB-03 |
| 5 six fragile pairs | ✅ confirmed | T-23-d1 `[00:00:00.030,000] … remaining_candidates=0 timestamp=29`; T-23-d6 `[00:00:00.049,000] … layer_id: 12 position: 21`; S-H_RM2-d17 `[00:00:00.036,000] … layer_id: 0 position: 17`; S-M_LT3-d15 `[00:00:00.030,000] … 0x1D`. W→M, D↔V INFERRED as stated |
| 6 hack is a trade | ⚠️ weakened | "Latency cost: +11 ms on the 8 hack-only positions only" refuted: T-02-a A (R16 position) `[00:00:00.018,000] … 0x04` = t+12 vs T-02-b-nohack `[00:00:00.012,000] … 0x04` = t+6 → RVB-06. "OFF they never miss" ignores R13 Δ=0 → RVB-08 |
| 7 real combos under the hack | ❌ partly refuted | "fires at its own 16/18 ms deadline" false for `bspc`/`del` (fire at 18 via delWord/capsWord): RVB-bspc-d12 `[00:00:00.031,000]`; "stalls until the next press or release" refined by RVB-strand-join → RVB-02, RVB-05 |
| 8 one queue, FIFO per item | ✅ confirmed | T-21-c `[00:00:00.111,000]` before `[00:00:00.122,000]`; T-18-a `[00:00:00.504,000]`; T-13-b `[00:00:00.104,000]`. Park consequence wording → RVB-10 |
| 9 timestamps never move | ⚠️ weakened | Layer-at-delivery + press-time release PROVEN (T-12-b-d110 `[00:00:00.211,000] … layer_id: 19`). "sticky windows count from the original press" false for AK stickies (count from aksl's queue stamp) → RVB-13. "pinned only by a keycode delivered after arming" true but incomplete (pin ends at next `aksl↓`) → RVB-01 |
| 10 targets & transport | ✅ confirmed | native +1/hop, timer-first ties (T-07-d11 `[00:00:00.022,000]`, T-12-b-d112, T-15-c `[00:00:00.202,000]`); 42 L-L / 12 R-R re-counted from PAIRS (24+11+1+4+1+1 / 10+1+1) |

## 🧾 Re-derived and matching (no defect; listed so the next agent can skip them)

- Ex 1.1 (T-23-a), 1.2 (T-23-b), 1.3 (T-23-c, all 9 rows incl. F+145), 1.4 arithmetic, 2.1 (T-18-g), 2.2 (T-18-f), 2.3 (T-17-a3/a4), 3.1 (T-12-c), 3.2 (T-13-d), 3.3 arithmetic, 4.2 (S-A_RT2-d10), 5.1 (S-M_LT3-d5/14/15/16), 5.2 (ARB-F2-press40 incl. `[00:00:00.069,000]`/`[00:00:00.074,000]`), 6.1 (T-12-a), 7.1/7.2/7.3 (T-23-d1/d6/d3): every native prefix exists at the cited ms and every board cell = native − hops.
- PAIRS ↔ MODEL (e)/E_b table ↔ PAGE §7: class counts, hands, S values, E_b ON/OFF, native last HIT = E_b+1 all consistent.

---

## 🧨 Findings

### RVB-01 · major · 📌 pin ends at the next `aksl↓`, not at the modifier's UP
- **Where:**
  - `PAGE_FACTS.md:224` §3 fact 8 "A modifier pressed inside the window pins the AK layer until the modifier is released; every key typed meanwhile adapts."
  - `MODEL_v2.md:418` (h) "pins until its UP; every follower in between resolves on the AK layer."
  - `MODEL_v2.md:239` "a new `aksl↓` releases a still-armed one. Moot in practice."
  - `MODEL_v2.md:116` diagram "OFF at the UP of the first keycode delivered after arming, else at +100".
- **Problem:** every queued `aksl` sits at position 0; `on_sticky_key_binding_pressed` releases any active sticky found at that position, pinned or not. So the first follower whose resolved binding runs an `&ak` (adapted `&ak`, replace macro, or `&trans` → base `&ak` letter, i.e. most of Flo's AK-layer cells) turns the pinned layer OFF while the modifier is still held. T-20-a/e only used `&bk` followers.
- **Evidence:** PROVEN(RVB-pin-akfollower `[00:00:00.173,000] … mo_keymap_binding_released: position 0 layer 1` → `layer 1 state 0`, Shift↑ only `[00:00:00.263,000]`); T-20-e followers both `flo,behavior-buffered-key` (`[00:00:00.414,000]`, `[00:00:00.446,000]`); SRC `behavior_sticky_key.c:85-92, 147-151`.
- **Fix:** "pins until the modifier's UP or until the next `&ak`-type key arms its own layer, whichever is first; only `&bk`-adapted followers keep it"; strike "Moot in practice".

### RVB-02 · major · ⌫ `bspc`/`del` never fire at completion
- **Where:**
  - `PAGE_FACTS.md:364` §5 fact 5 "Completed between 11 ms and T − 1, it fires at the completing press".
  - `PAGE_FACTS.md:363` fact 4 "waits for its own deadline"; `PAGE_FACTS.md:55` §1 fact 13 "to its own 16/18 ms deadline (cost 16 − gap)".
  - `MODEL_v2.md:57` truth 7 "fires at its own 16/18 ms deadline"; `MODEL_v2.md:486` (l) "hack OFF → fires at completion".
- **Problem:** `bspc` (RM1 RM2) and `del` (RM2 RM3) always complete with `delWord`/`capsWord` (18 ms) still alive → pending (R7) → fire when the last sibling expires (t+18) or at the next event. The hack is irrelevant for them; MODEL's own "iff it is the only survivor" (line 58) is right, PAGE drops it.
- **Evidence:** PROVEN(RVB-bspc-d12 `[00:00:00.031,000] … remaining_candidates=0 timestamp=30` + `keycode 0x2A` = t+19 native / board t+18, gap 12); PROVEN(RVB-bspc-d5-nohack `[00:00:00.024,000] … keycode 0x2A` = t+19 native, gap 5, hack absent). SRC `combo.c:448-452` (default branch: complete + ≥ 2 alive → `fully_pressed_combo`, no cleanup); D §6.2 #11-13, #25.
- **Fix:** facts 4/5/13 need "when it is the only live candidate"; add "`bspc`/`del`: always t+18 (or first key-up), hack or not".

### RVB-03 · major · ⏱️ "timers ≤ 0.061 ms late" ignores the arming phase; REFUTED list overbroad
- **Where:**
  - `MODEL_v2.md:25` "Board timer lateness per hop: 0.005–0.061 ms after the integer target." vs `MODEL_v2.md:124` "fire at the integer target + the sub-ms phase of the arming instant + ≤ 61 µs".
  - `PAGE_FACTS.md:422` §6 fact 6 "Firmware timers on the board are late by at most 0.061 ms."
  - `PAGE_FACTS.md:443` must-NOT "~~Board timers are up to ~1 ms late~~ — ≤ 0.061 ms. Killed by src C §4 (F1)."
  - `MODEL_v2.md:26, 283-284, 545` strike "δ ∈ (0.03, 1.05]", "≈95 %/5 %", "≈0.05 %" as REFUTED.
  - `MODEL_v2.md:474` (k) "Every ⚖️ cell … is decided by firmware latencies of 10–200 µs".
- **Problem:**
  - C §4's 0.005–0.061 ms is lateness after **arming** for relative `K_MSEC(n)` (queue ticks). Rungs, sticky OFF and hold-tap terms are `K_MSEC(target − k_uptime_get())`: relative to the integer instants the page prints they fire φ + ε late, φ = sub-ms phase of the arming instant ∈ [0, 1) for left-hand (BLE-stamped) keys → up to ~1.06 ms. The must-NOT is therefore not killed for left-hand keys.
  - v1's δ ∈ (0.03, 1.05] and "≈5 % floor to deadline+1" are exactly this φ effect; v2 strikes them as REFUTED yet keeps the same mechanism as INFERRED/OPEN at lines 282, 284 and PAGE OPEN 3. "≈0.05 %" ≈ P(φ_A − φ_B > 1 − ε) for the H0 Δ = dA margin, also kept OPEN at line 284.
  - For L-L pairs (42/54, all 11 H0 pairs) a ⚖️ cell compares a timer carrying φ_A with a key carrying φ_B: a BLE-phase race up to 1 ms wide, not a 10–200 µs firmware tie, and its neighbours are not strictly certain (e.g. H0 hack-OFF Δ = 27 MISS iff φ_A − φ_B > 1 − ε).
- **Evidence:** SRC `combo.c:417`, `behavior_sticky_key.c:182-186`, `behavior_hold_tap.c:619-620`, `central.c:259-266`; C §4 table header "fires after" (from arming); MODEL_v2.md:124 itself.
- **Fix:** state two quantities (per-hop relative ≤ 0.061 ms; absolute-target timers +φ, φ ≈ 0.01–0.2 ms right-hand, 0–1 ms left-hand); move the struck items from REFUTED to "basis restated, left-hand only, OPEN"; drop or rescope the §6 must-NOT.

### RVB-04 · major · 🧵 workqueue blocking (USB `hid_sem`, `k_msleep(10)`) not modelled
- **Where:**
  - `MODEL_v2.md:125` "Right-hand stamps sit ~0.01–0.15 ms after an integer ms, so right-hand timelines are integer-ms in practice."
  - `MODEL_v2.md:282` "Right-hand trigger → the rung floors to its integer deadline → STALL cells as stated" (deterministic).
  - `MODEL_v2.md:127` same-thread guarantee; `MODEL_v2.md:242` "R↓, R↑ and `l_akR` ON all in the thumb-up ms U"; `PAGE_FACTS.md:422`.
- **Problem:**
  - The key timestamp is `k_uptime_get()` taken inside the msgq **work item**, not in the kscan callback. Anything that holds `k_sys_work_q` delays stamps, rungs and ticks.
  - Over USB every report send does `k_sem_take(&hid_sem, K_MSEC(30))` on the calling (system workqueue) thread, released only when the host polls (1 ms interval). So two reports < 1 ms apart block the thread for ≤ ~1 ms: R↓R↑ of the 0 ms R tap, A↑ + B↓ in one tick, separate mod-release reports.
  - `release_captured_events` sleeps 10 ms per further captured event once a re-raised event created a new undecided hold-tap. Possible on Flo's keymap: e.g. a linger key or R thumb undecided while `RH0` (`&blt` space) and a letter are pressed.
  - Reader report B had both blockers (`B-behavior-pipeline.md:29`); v2 dropped them.
- **Evidence:** SRC `physical_layouts.c:147-160` (callback = msgq put + submit) and `:178-182` (stamp in work item); `usb_hid.c:25-27, 139`; `app/Kconfig:142-143` (`USB_HID_POLL_INTERVAL_MS` default 1); `endpoints.c:123-127` (synchronous); `behavior_hold_tap.c:220-222` (`k_msleep(10)` at :221); BLE path non-blocking via `hog.c:259-274`.
- **Fix:** qualify "deterministic right-hand" and "integer-ms in practice" with "on BLE; on USB, cells adjacent to a double report can slip 1 ms"; add the `k_msleep(10)` corner to OPEN.

### RVB-05 · major · ⏸ a strand is not ended by "the next press"
- **Where:**
  - `PAGE_FACTS.md:12` glyph "⏸ STALL (follower waits for the next key event)"; `PAGE_FACTS.md:49` §1 fact 7.
  - `MODEL_v2.md:154` "Dead --> Idle : NEXT position event (press or release) → flush"; `MODEL_v2.md:188` R9 "It waits for the next position event"; `MODEL_v2.md:261` "Adapted iff T+21 ≤ E ≤ ~T+121".
- **Problem:** the stranded key B owns a fresh set incl. its own hack candidate (live until ts_B + 11 = T+21 at Δ = 10). A press C before that shares the hack → captured into the same set; `update_timeout_task` sees the unchanged MIN = phantom → still no timer. C joins the stall; both leave at the next non-sharing press or a release. At that flush B is adapted late, and C is re-raised behind B's keycode, quick-tap-bypassed, and resolves on A's still-held AK layer or base (not B's layer). INF for the board. A fast trigram at ~10 ms spacing is exactly this case.
- **Evidence:** PROVEN(RVB-strand-join `[00:00:00.020,000] … capturing position event 0`, no rung at `[00:00:00.024,000]`, flush `[00:00:00.073,000]`, 3rd key `layer_id: 0 position: 0`); SRC `combo.c:407-411, 422-433`.
- **Fix:** add a "join" exit to R9/R10 and the state diagram (`Dead --> Dead : PRESS sharing a live candidate`), redefine ⏸, and add a trigram OPEN item (A, B@10, C@≤20).

### RVB-06 · major · 🐢 "hack adds latency only to 8 positions" refuted by existing logs
- **Where:**
  - `PAGE_FACTS.md:45` §1 fact 3 "The hack adds latency only to the 8 hack-only positions … every other key is unchanged".
  - `MODEL_v2.md:54` "Latency cost: +11 ms on the 8 hack-only positions only."
  - `PAGE_FACTS.md:118` must-NOT "applies only to the 8 hack-only positions".
  - `PAGE_FACTS.md:44` "It holds every press for at least 11 ms".
- **Problem:**
  - In any roll with Δ ≤ 10 the hack holds key 1 to t+11 even on 16/18 ms positions. Without the hack, key 1 leaves at key 2's press (t+Δ). The cost is 11 − Δ on every position.
  - Separately, a key released before 11 ms is flushed at its key-up (R6), so "at least 11 ms" is false.
- **Evidence:** PROVEN(T-02-a pos 0 (R16) `[00:00:00.018,000] … keycode 0x04` = t+12 vs T-02-b-nohack `[00:00:00.012,000] … keycode 0x04` = t+6, same events); T-23-a M (16 ms LT2) `[00:00:00.017,000] … keycode 0x10` (t+12); T-08-b release flush `[00:00:00.016,000]`.
- **Fix:** "lone-key latency +11 only on 8 positions; in rolls < 11 ms, key 1 waits until 11 on every position".

### RVB-07 · major · 🛡️ §1 fact 4 "guarantees" drops the precondition
- **Where:** `PAGE_FACTS.md:46` "If the follower is pressed 11 ms or later after the trigger, the hack guarantees the AK layer is on before the follower lands: margin … ≥ 1 ms."
- **Problem:**
  - It is false for the 6 shared-combo pairs, which §7 of the same file lists: L→G key MISS at 11–14, H→E key MISS at 11–16, S2 pairs give Z/Tab at 11–15.
  - "≥ 1 ms" is OPEN for the 11 L-L H0 pairs at Δ = dA (MODEL_v2.md:284).
- **Evidence:** T-23-d1 `[00:00:00.030,000] … layer_id: 0 position: 21` (Δ 13 MISS); S-H_RM2-d16 `[00:00:00.035,000]`; S-M_LT3-d14 `[00:00:00.028,000] … 0x1D`; MODEL_v2.md:284.
- **Fix:** prefix "for the 45 pairs that share no combo"; add "left-hand H0 at Δ = 16: nominal 1 ms, phase-dependent".

### RVB-08 · major · 🔁 §1 fact 10 restates the killed claim; R13 contradicts the hack-OFF table
- **Where:**
  - `PAGE_FACTS.md:52` "Without the hack, every follower that has its own combo (34 pairs) adapts at every gap." vs `PAGE_FACTS.md:116` must-NOT "Every follower that is in a real combo adapts at any gap without the hack".
  - `MODEL_v2.md:315` hack-OFF row "0–25 | ✅ · ✅" vs `MODEL_v2.md:200` R13 (hack OFF, Δ = 0 → strand); `MODEL_v2.md:52` "OFF they never miss".
- **Problem:**
  - S2/S3 followers also "have their own combo" (k2 16/18) and miss hack-off. The parenthetical does not fix the sentence.
  - "Every gap" ignores the window edge (94–112).
  - R13 makes Δ = 0 a STALL for N pairs with k1 = k2 = 16. PAIRS line 120 says L-L Δ ≈ 0–1 when both presses share one connection event, so this matters on upstream.
- **Evidence:** T-23-e5 `[00:00:00.030,000]` → `layer_id: 0 position: 21` → `[00:00:00.041,000] … 0x0A`; S-H_RM2-d17-nohack `[00:00:00.036,000]`; S-M_LT3-d15-nohack `[00:00:00.030,000] … 0x1D`; MODEL_v2.md:200.
- **Fix:** "followers whose combos are not shared with the trigger"; mark the N hack-OFF Δ = 0 cell ⏸ (INF/OPEN).

### RVB-09 · major · 🚫 must-NOT "At 10 ms the board types the base letter" is not killed by any test
- **Where:** `PAGE_FACTS.md:119` "Killed by T-04-d10 (native) + R9 source (T-02-c, T-03)".
- **Problem:**
  - T-04-d10 shows a native MISS at 10 (`[00:00:00.022,000] … layer_id: 0 position: 3`). It supports the statement, it does not kill it.
  - T-02-c/T-03 prove the strand only under altered conditions: `require-prior-idle −100`, or a raw `&kp` key 1.
  - The board ⏸ is BOARD-ONLY and OPEN (T-24a). PAGE :124 itself says a left-hand trigger's 10 ms cell can come out as a MISS. RVB-03 and RVB-04 add further MISS paths.
- **Fix:** demote to an honest caveat ("predicted to stall; unmeasured; can miss on left-hand triggers / USB").

### RVB-10 · major · 🎛️ park emits one letter per 10 ms tick, and no adaptation happens inside it
- **Where:**
  - `PAGE_FACTS.md:138` §2 fact 5 "any letter typed in (R, R+260) appears at R+260, in order".
  - `MODEL_v2.md:400` "Every queued key delivered in (R, R+260) emits HID↓ at R+260, in order. PROVEN(T-18-a, a2, e, f, g …)". Each of those cases parks exactly one key.
- **Problem:**
  - The 2nd parked `&ak` emits at R+270, the 3rd at R+280, etc.
  - Each parked letter's layer is chosen at its delivery, while every earlier letter's `aksl` is still parked. So AK pairs typed inside the park never adapt (missing page fact).
  - A letter pressed after ≈R+244 (16 ms combos) is delivered after R+260 and is not "at R+260".
- **Evidence:** PROVEN(RVB-park-two A `[00:00:00.426,000] … layer_id: 0 position: 0` before `[00:00:00.515,000] … layer 2 state 1`; A↓ `[00:00:00.515,000]` = R+273 native / board R+270).
- **Fix:** "first parked letter at R+260, then one per 10 ms; letters typed during the park are resolved on base (no adaptation among them)".

### RVB-11 · minor · 🔨 board forced-TAP Δ = 10 "then HOLD (term already expired)" is wrong
- **Where:**
  - `MODEL_v2.md:435` "Board Δ = 10: stranded to the next event, then HOLD (term already expired)"; also `MODEL_v2.md:526` and `PAGE_FACTS.md:618` OPEN 14 "strand → HOLD".
  - `MODEL_v2.md:474` lists "forced-TAP Δ = 10" as a ⚖️ tie.
- **Problem:**
  - The term counts from the follower's ts (T+10), so it expires at T+110. Delivered at E < T+110, the hold-tap is created undecided and decides normally. This is what PAGE :351 says ("then decides normally"), and the two docs disagree.
  - On Flo's two hold-tap-follower pairs, the strand resolves on the AK layer as `&bk U` / `&bk W`, not a hold-tap (PAGE :339 "late u").
  - It is a strand, not a ⚖️ tie: the comparison is integer-deterministic.
- **Evidence:** T-16-d-d11 created `[00:00:00.034,000]`, HOLD only `[00:00:00.123,000]` (= ts + 101 native); PAIRS rows 18, 15.

### RVB-12 · minor · 👍 R-thumb "0 ms tap" needs an idle queue
- **Where:** `PAGE_FACTS.md:231` fact 15 "(0 ms tap, no +10)", `:234` fact 18 "thumb-up to thumb-up + 100", `MODEL_v2.md:242-243`.
- **Problem:** when the queue is busy (forced-TAP after a letter), the nested `&ak R` queues normally: `l_akR` comes ON 10 ms after R↓.
- **Evidence:** S-S_LH0-d10 R↓ `[00:00:00.033,000] … keycode 0x15`, `layer 17 state 1` `[00:00:00.044,000]` (PAIRS deviation 2).

### RVB-13 · minor · 🕰️ truth 9 "sticky windows count from the original press"
- **Where:** `MODEL_v2.md:68`.
- **Problem:** AK stickies count from `aksl`'s queue stamp (D+10), which contradicts truth 2. The statement is true only for hold-tap-invoked stickies (`skms`/`skm`).
- **Evidence:** T-12-a ON `[00:00:00.129,000]` → OFF `[00:00:00.230,000]` (+101); T-17-b2 `[00:00:00.051,000]` → `[00:00:01.552,000]`.

### RVB-14 · minor · 🧩 delWord exit over-tagged and over-stated
- **Where:**
  - `MODEL_v2.md:195` "Flo: RM1, RM3 @+12, RM2 → delWord only at the first release … PROVEN(ARB-F2 …)".
  - `PAGE_FACTS.md:368` "fires only at the first key-up".
- **Problem:**
  - ARB-F2 had no RM2 press (cases: LM1 press, RM1↑), so the delWord half is INFERRED.
  - "Only" contradicts `MODEL_v2.md:192` ("an unrelated press would also end it").
  - It holds only if RM2 comes before t+18; after that, RM2 flushes "a i e".
- **Evidence:** CORRECTIONS-FINAL F2 case table.

### RVB-15 · minor · 🗺️ l_mod landscape lists only the 8 mod keys
- **Where:** `MODEL_v2.md:210-211`; `PAGE_FACTS.md:203`; `PAGE_FACTS.md:166` "Ctrl on LM4 … would have landed on `l_mod`" (untagged INF).
- **Problem:**
  - `l_mod` keys inside `l_all` combos are also held 16 ms and lose the last 16 ms of the 130 ms buffer. They are: LT1 `LG(V)` and LT0 `LG(K)` (`space`), LM0 `LG(A)` (`entr`), LB3 `LS(LG(Z))`, LB2 `LG(W)`, LB1 and LB0 `LG(S)` (`magicCloseQuitCb`/`esc2`/`tab`), plus `&trans` RM0 (`entr2`).
  - Rolled pairs fire combos: ⌘V→⌘K < 16 ms → space; LM1 Shift→LM0 ⌘A → Enter.
- **Evidence:** SRC `layers_C_extra.dtsi:41-43`; D §6.2 layers 0–31 for `space`/`entr`/`entr2`/`tab`/`esc2`/`magicCloseQuitCb`. INF.

### RVB-16 · minor · ⇥ S2 "Tab at t+Δ"
- **Where:** `MODEL_v2.md:309` "S2: Z/Tab at t+16 (Δ ≤ 10) or t+Δ (11–15)".
- **Problem:** `tab` = `&lk LG(TAB) TAB`, a tap-preferred 100 ms hold-tap. At t+16 / t+Δ it is only created; Tab is emitted at the first key-up, ⌘Tab at press+100.
- **Evidence:** D §6.2 #9, D §7. INF.

### RVB-17 · minor · 🚫 must-NOT about `&bk` "10 ms prevents dropped keys" not killable on native
- **Where:** `PAGE_FACTS.md:292` "Killed by T-21-h, T-15-d"; `PAGE_FACTS.md:562`.
- **Problem:** those logs show ordering (raw `&kp` overtakes the queue). They say nothing about host-side drops, and native has no host.
- **Fix:** relabel as an unverified rationale.

### RVB-18 · minor · 🏷️ E_b table label
- **Where:** `MODEL_v2.md:327` "16/16 pairs (most N, all S3/S2)".
- **Problem:** H→E key is 18/18 (S3). The value 110 is still right; the label is wrong.

### RVB-19 · minor · 📝 dangling caveat
- **Where:** `PAGE_FACTS.md:409` "Example 5.1 rows W→M, D→V, V→D follow the same rule but were not run."
- **Problem:** Ex 5.1 has no such rows; only M→W is shown.

### RVB-20 · minor · 📏 §5 facts 6 and 8 hard-code "+ T" / "16 or 18"
- **Where:**
  - `PAGE_FACTS.md:365` "it is typed at its own press + T".
  - `PAGE_FACTS.md:367` "A key held alone waits for its longest combo: 16 ms, or 18 ms on A E I H".
- **Problem:** the wait is the late key's own longest live candidate, not the combo's T: E/A/I/H late keys wait 18, and the 8 hack-only keys wait 11.
- **Evidence:** RIG.md:10; T-01-r2-map `[00:00:01.126,000]`.
