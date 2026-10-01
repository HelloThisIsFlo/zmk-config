#!/usr/bin/env python3
import pathlib, sys
R = pathlib.Path(__file__).resolve().parents[3] / "Design" / "Timing" / "results"  # reads CORRECTIONS-MERGED.md, REWRITES CORRECTIONS-FINAL.md there
src = (R/"CORRECTIONS-MERGED.md").read_text()

def rep(s, old, new):
    assert s.count(old) == 1, ("not unique/missing:", old[:80])
    return s.replace(old, new)

s = src
s = rep(s, "# 🧾 CORRECTIONS-MERGED: A + B corrections to MODEL.md / CLAIMS.md",
           "# 🧾 CORRECTIONS-FINAL: A + B corrections to MODEL.md / CLAIMS.md, five flags resolved")
s = rep(s, "> Board = native − 1 ms per relative timer crossed (+δ). An `&ak` delivered by a combo rung crosses two timers.",
           "> Board = native − 1 ms per relative timer crossed (+δ). An `&ak` delivered by a combo rung crosses two timers.\n"
           "> Arbitration 2026-10-01: the five FLAGGED items are RESOLVED in §3. Seven new native cases `zmk/app/tests/ak-truth/ARB-*` (3 on R2 = Flo's keymap, 4 on R1 / R1_nohack), logs `results/ARB-*.raw.log`, index at the end of §3. Body items 4, 5, 7, 17, 18 carry the outcome inline.")
s = rep(s, "| ⚠️ FLAGGED (not resolved here) | 5 |", "| ✅ RESOLVED by arbitration (§3) | 5 (F1 source · F2 new R2 cases · F3 new R1 cases · F4, F5 literal reading of the targets) |")
s = rep(s, "- The FLAGGED items are three substance differences (board tie bias, RM1+RM3 stall exit, dead-window bound) and two kind mismatches (correction vs refinement on a headline claim).",
           "- The five formerly FLAGGED items: board tie bias (no direction claimable, and the cell is not a coin flip either), RM1+RM3 stall exit (next event, press or release, PROVEN), dead-window bound (open on the board; native brackets depend on the delivery mechanism, PROVEN), ONE-queue kind (refinement), pin kind (correction for every \"held modifier\" sentence).")
s = rep(s, "- ⚠️ Kind differs (A correction / B refinement) → see FLAG F4.",
           "- ✅ Kind settled: **refinement** of the headline; the refuted prediction lived in CLAIMS T-21 / E-67 (RESOLVED F4).")
s = rep(s, "- ⚠️ Kind differs for CLAIMS 16 (A refinement / B correction) → see FLAG F5.",
           "- ✅ Kind settled: **correction** for every sentence that says a *held* modifier pins (MODEL (a) note, CLAIMS 16); **refinement** for MODEL (c) and E-60, whose wording already carries \"DOWN after arming\" (RESOLVED F5).")
s = rep(s, "- ⚠️ RM1+RM3 without RM2: exit wording differs → see FLAG F2.",
           "- ✅ RM1+RM3 without RM2: both letters leave at the **next position event, press or release** (exits 3 and 4). PROVEN on Flo's keymap: ARB-F2-press40 `[00:00:00.052,000] … keycode 0x04` at the unrelated press, ARB-F2-press14, ARB-F2-release40 (RESOLVED F2).")
s = rep(s, "- ⚠️ Board-tie direction differs → see FLAG F1.",
           "- ✅ Board-tie direction: **not claimable** from source; print ⚖️ cells as unresolved on hardware, not \"leans to the timer\" and not \"≈ 50/50\" (RESOLVED F1).")
s = rep(s, "- ⚠️ Upper-bound bracket and the \"[F, F+10) sees old layer\" sub-claim → see FLAG F3.",
           "- ✅ Brackets settled by four new cases: board **(F+10, F+40)** with both ends ⚖️; native key-driven **[F+11, F+44)**, rung-driven **(F+11, F+44]**; **[F, F+10) resolves on the old AK layer** (PROVEN T-21-f at F, ARB-F3-c at F+5) (RESOLVED F3).")

head, _, _ = s.partition("## ⚠️ 3. FLAGGED (not resolved)")

resolved = r'''## ✅ 3. RESOLVED (arbitration, 2026-10-01)

> Method: existing logs and the firmware source first; where they could not settle a flag, the smallest native case that does. New cases: `zmk/app/tests/ak-truth/ARB-*` (templates copied, never edited), logs `results/ARB-*.raw.log`, builds `zmk/app/build/tests/ak-truth/ARB-*`. Line prefixes quoted exactly.
> Tags: **PROVEN(case: line)** = native_posix log · **SRC** file:line · **INF** = inferred. Board = native − 1 ms per relative timer hop (+δ, δ ∈ (0.005, 0.061] ms per hop, `C-timestamps-transport.md` §4).

| flag | decision | one line |
|---|---|---|
| F1 board tie direction | **A's rule (no direction), sharpened** | The board cell is decided by three µs-scale firmware latencies that pull in opposite directions and that native cannot measure. Print ⚖️ as "unresolved on hardware". Not "leans to the timer" (B), and not "≈ 50/50" either (the 1 ms scan grid erases the typist's phase). |
| F2 RM1 + RM3 stall exit | **A: next position event, press or release** | PROVEN on R2: an unrelated press at t+14 or t+40 flushes both letters at that press; a release flushes too. B-08's "first release" is the no-further-press special case. |
| F3 dead window | **B's open board bracket + A's early sub-window; native brackets by delivery mechanism** | Board (F+10, F+40), both ends ⚖️. Native: key-driven [F+11, F+44), rung-driven (F+11, F+44]. [F, F+10) still resolves on the old AK layer (PROVEN). |
| F4 "ONE queue" kind | **B: refinement** | The headline's two literal claims hold. The refuted order prediction was CLAIMS T-21's (item 32) and E-67's "strict ordering between macros". |
| F5 pin kind | **B: correction** for "held modifier" sentences; **refinement** for MODEL (c) / E-60 | A pre-held Shift does not pin (T-20-d). Any sentence whose literal reading covers a pre-held modifier is wrong, not under-specified. |

### F1 · Board same-tick ties → no direction, and not a coin flip

- **Decision**: no board direction. Every board ⚖️ cell (hack-off k1+10, window edge Δ = 110, combo gap = T, forced-TAP Δ = 10) is printed as *unresolved on hardware*, with both neighbours certain. Native's timer-first outcomes stay harness notes.
- **Why B's "biases toward the timer" is not safe** (SRC, board = nRF52840, `CONFIG_SYS_CLOCK_TICKS_PER_SEC=32768`):
  - B's mechanism is real but 30 µs wide. Timeouts expiring on one tick are submitted FIFO in deadline-then-arming order (`timeout.c:122-135` insertion keeps equal deadlines in arming order, `:209-239` announce loop), and a key reaches the keymap only through a second work item: scan work → `data->callback` (`kscan_gpio_matrix.c:274`) → `k_msgq_put` + `k_work_submit(&msg_processor.work)` (`physical_layouts.c:158-159`; left half `central.c:130-131`). So a timer expiring on the **same 30.5 µs tick** as the key's scan always runs first.
  - Against it, every relative timer is late by (0, 1] tick: `to->dticks = timeout.ticks + 1 + elapsed()` (`timeout.c:122`). `K_MSEC(10)` fires 10.010–10.040 ms after arming, `K_MSEC(16)` 16.021–16.052 ms (C §4 table). A chain of m hops is late by m × (5–61 µs). This pulls a nominal tie toward the **key**.
  - Also against it, key 1's arming latency: key 1's first timer is armed inside its listener chain (combo `k_work_schedule`, or for a bare `&ak` only after the HID report was sent), tens to hundreds of µs after key 1's scan; key 2 is resolved ~10–100 µs after its own scan (C §2 "Position event follows the flip by ~10–100 µs").
  - Also unknown in sign: the two keys' order inside the matrix read loop (`kscan_gpio_matrix.c:222-262`), tens of µs either way.
- **Why A's "sub-ms coin flip" is not safe either** (SRC): while any key is held the matrix is polled on an **absolute 1 ms grid** (`kscan_gpio_matrix.c:194-200`: `scan_time += 1; k_work_reschedule(&work, K_TIMEOUT_ABS_MS(scan_time))`; absolute timeouts carry no +1, `timeout.c:120`), and the stamp is floor-ms taken within the same ms (`physical_layouts.c:182`). For a same-half roll the stamp gap Δ is an exact scan count; the typist's sub-ms phase is erased. A whole 1 ms band of physical gaps maps onto Δ = N, and the whole band is resolved the same way by the latencies above (modulo ≤ 61 µs tick-phase jitter and workqueue backlog). So a board ⚖️ cell is probably consistent for a given key pair, in a direction nobody has measured.
- Left-hand keys are stamped at BLE receipt (`central.c:263-266`) and L→L gaps are quantised to the 7.5 ms connection interval (C §5, INF), so the k1+10 / Δ = 10 cells are rarely populated for left-hand pairs; L↔R ties are genuine phase races. All 23 compiled AK pairs are same-hand (MODEL headline 10).
- **Net**: three source-backed effects of comparable size (10–200 µs) with opposite signs, summed with hardware latencies native cannot measure → INF either way → hardware only (T-24 scope).
- **Page-safe wording**: "⚖️ = on the board a key event and a timer fall within about 0.1 ms of each other. The firmware's own latencies, not your timing, decide which runs first, and this investigation could not determine which way (native_posix resolves such ties timer-first; do not read that as the board's answer). The cells on either side are certain."
- Side note, not a flagged item: MODEL's "δ ∈ (0.03, 1.05]" is wrong by C §4's own SRC table (δ ≤ 0.061 ms per hop). The 1.05 figure must not reach the page; it is what made both extractors frame board ties as broad sub-ms races.

### F2 · RM1 + RM3 (no RM2), 11 ≤ Δ ≤ 15 → both letters leave at the next position event, press or release

- **Decision**: A (MR-03) and the exit list in item 7. B-08's "until the first release" is the special case where nothing else is pressed first.
- **Cases** (R2 = Flo's keymap, hack ON; RM1 = pos 16 mock (1,7), RM3 = pos 18 mock (1,9), LM1 = pos 13 mock (1,4); t = abs 12):

| case | events (abs ms) | what ends the stall | A (0x04) | I (0x0C) |
|---|---|---|---|---|
| `ARB-F2-press40` | RM1 12 · RM3 24 · LM1 52 · ups 153 / 164 / 175 | unrelated press at t+40, after both deadlines | `[00:00:00.052,000]` | `[00:00:00.063,000]` |
| `ARB-F2-press14` | RM1 12 · RM3 24 · LM1 26 · ups 127 / 138 / 149 | unrelated press at t+14, candidates still alive | `[00:00:00.026,000]` | `[00:00:00.037,000]` |
| `ARB-F2-release40` | RM1 12 · RM3 24 · RM1↑ 52 · RM3↑ 153 | first release at t+40 | `[00:00:00.052,000]` | `[00:00:00.063,000]` |

- **PROVEN, the stall** (identical in all three logs): `[00:00:00.024,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=4 timestamp=23` (hack rung, re-arms t+16) → `[00:00:00.024,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 1, col: 9, position: 18, pressed: true` → `[00:00:00.024,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=4 timestamp=24` → `[00:00:00.024,000] <dbg> zmk: position_state_down: combo: capturing position event 18` → **no log line at t+17 or t+19**; the next line is the next mock event. R10 reproduced on Flo's real RM1/RM3 (delWord + capsWord survive, their t+18 deadline is never armed).
- **PROVEN, exit at an unrelated press** (`ARB-F2-press40`): `[00:00:00.052,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 1, col: 4, position: 13, pressed: true` → `[00:00:00.052,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=52` → `[00:00:00.052,000] <dbg> zmk: position_state_down: combo: capturing position event 13` → `[00:00:00.052,000] <dbg> zmk: release_pressed_keys: combo: releasing position event 16` → `[00:00:00.052,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 16, binding name: flo,behavior-adaptive-key` → `[00:00:00.052,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x04 implicit_mods 0x00 explicit_mods 0x00` → `[00:00:00.052,000] <dbg> zmk: release_pressed_keys: combo: reraising position event 18` → `[00:00:00.052,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 18, binding name: flo,behavior-adaptive-key` (R8 bypass, no capture) → `[00:00:00.063,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x0C implicit_mods 0x00 explicit_mods 0x00`. The unrelated key is itself re-captured (`[00:00:00.052,000] … capturing position event 13`), delivered by its entr rung `[00:00:00.069,000]`, T↓ `[00:00:00.074,000] … keycode 0x17`.
- **PROVEN, exit at a press before the deadlines** (`ARB-F2-press14`): `[00:00:00.026,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=2 timestamp=26` (delWord + capsWord alive) → `[00:00:00.026,000] <dbg> zmk: position_state_down: combo: capturing position event 13` → `[00:00:00.026,000] <dbg> zmk: release_pressed_keys: combo: releasing position event 16` → `[00:00:00.026,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x04 implicit_mods 0x00 explicit_mods 0x00` → `[00:00:00.037,000] … keycode 0x0C`. Exit (3), first clause: a press sharing no live candidate empties the set (`combo.c` `filter_candidates` → 0 → `cleanup()`).
- **PROVEN, exit at the first release** (`ARB-F2-release40`): `[00:00:00.052,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 1, col: 7, position: 16, pressed: false` → `[00:00:00.052,000] <dbg> zmk: release_pressed_keys: combo: releasing position event 16` → `[00:00:00.052,000] … keycode 0x04` → `[00:00:00.063,000] … keycode 0x0C`. Exit (4) = B-08's case.
- **Board**: the flush is key-driven (no timer) → A at the next event's stamp, I at +10 + δ (queue tick; native +11). Stall band on the board: Δ ∈ [11, 15]; Δ = 16 is a ⚖️ cell (RM3's press vs the t+16 rung); Δ ≤ 10 → RM3 lands before the hack rung, the MIN does not move, no stall (T-10-d pattern).
- **Page-safe wording**: "RM1 then RM3 12 ms later with no RM2: nothing is typed until your next key event, whichever comes first — the next letter's press or the first key-up. At that instant A is typed, I follows 10 ms later on the base layer, and the next letter is processed normally. A fast typist sees at most a one-keystroke hiccup, never a hang."

### F3 · Replace-macro dead window → open board bracket; native brackets depend on who delivers the key; [F, F+10) sees the old layer

- **Decision**: the page prints B's open board bracket **(F+10, F+40)** with both ends as ⚖️ cells, plus A's sub-window: a key delivered in **[F, F+10)** resolves on the **old** AK layer. A's native bracket "(F+11, F+44]" is right only for rung-delivered keys; for key-driven deliveries both ends flip: **[F+11, F+44)**.
- **Cases** (R1; A-key pos 0 at abs 31, E-key pos 4 at abs 62 delivered by its own Q18 rung at abs 81 = F; native replace ticks: ⌫↓ 81 · ⌫↑ + layer 1 OFF + L↓ 92 (F+11) · L↑ + ak↓ 103 (F+22) · B↓ 114 (F+33) · B↑ + layer 3 ON 125 (F+44); akH pos 3 set to `&kp Z` so a resolution on the new layer is visible as 0x1D):

| delivery of the follower (pos 3) | case | decisive lines | resolved on |
|---|---|---|---|
| key-driven at F (re-raised in the flush burst) | T-21-f (existing) | `[00:00:00.074,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 1 position: 3, binding name: flo,behavior-buffered-key` | **old** AK layer 1 |
| key-driven at F+5 | `ARB-F3-c-key-F5` (R1_nohack, D at abs 86) | `[00:00:00.086,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 3, position: 3, pressed: true` → `[00:00:00.086,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 1 position: 3, binding name: flo,behavior-buffered-key`; its L↓ `[00:00:00.114,000] … keycode 0x0F` lands before B `[00:00:00.125,000] … keycode 0x05` (item 4) | **old** AK layer 1 |
| key-driven at exactly F+11 | `ARB-F3-d-key-F11` (R1_nohack, D at abs 92) | `[00:00:00.092,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0x2A implicit_mods 0x00 explicit_mods 0x00` → `[00:00:00.092,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 0` → `[00:00:00.092,000] … keycode 0x0F` → `[00:00:00.092,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 3, position: 3, pressed: true` → `[00:00:00.092,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 3, binding name: key_press` → `… keycode 0x07` | **base** (timer first) |
| key-driven, F+12 … F+43 | T-21-a `[00:00:00.090,000]`, T-21-d `[00:00:00.108,000]` (item 18) | | base |
| key-driven at exactly F+44 | `ARB-F3-b-key-F44` (R1_nohack, D at abs 125) | `[00:00:00.125,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0x05 implicit_mods 0x00 explicit_mods 0x00` → `[00:00:00.125,000] <dbg> zmk: set_layer_state: layer_changed: layer 3 state 1` → `[00:00:00.125,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 3, position: 3, pressed: true` → `[00:00:00.125,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 3 position: 3, binding name: key_press` → `[00:00:00.125,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x1D implicit_mods 0x00 explicit_mods 0x00` | **new** AK layer 3 (timer first) |
| rung-driven at exactly F+44 (hack rung armed at abs 113 = F+32; B↑ tick armed at 114 = F+33) | `ARB-F3-a-rung-F44` (R1, D at abs 113) | `[00:00:00.113,000] <dbg> zmk: position_state_down: combo: capturing position event 3` → `[00:00:00.114,000] … keycode 0x05` (B↓) → `[00:00:00.125,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=124` → `[00:00:00.125,000] <dbg> zmk: release_pressed_keys: combo: releasing position event 3` → `[00:00:00.125,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 3, binding name: key_press` → `[00:00:00.125,000] … keycode 0x07` → then `[00:00:00.125,000] <dbg> zmk: set_layer_state: layer_changed: layer 3 state 1` | **base** (earlier-armed timer first) |

- **Native rule** (item 17 applied): a key-driven delivery on a tick where a queue timer also expires runs after that timer; a rung-driven delivery runs in arming order against it. Hence native key-driven **[F+11, F+44)** → base, rung-driven **(F+11, F+44]** → base (the rung end at F+11 is INF by the same rule, not run). Old layer: key-driven [F, F+11), rung-driven [F, F+11].
- **Board**: the interior **(F+10, F+40)** → base (same logs minus one +1 per hop; inside the interval the margins are ≥ 1 ms, item 14). The two endpoints are ⚖️ cells (F1). Old layer: **[F, F+10)**, the F+10 end ⚖️.
- Worth a page sentence: a key at the F+40 edge that resolves on the *new* layer still adapts (in Flo's keymap that layer is the nested `&ak`'s, e.g. `l_akB` after `REPLACE_CHAR_WITH_BIGRAM(L, B)`).
- **Page-safe wording**: "When a replace macro starts at F, its ⌫ is the keycode that consumes the old AK layer, which drops at F+10; the new layer (from the nested `&ak`) comes on at F+40. A key delivered before F+10 still sees the old layer; one delivered between F+10 and F+40 resolves on base and sees neither bigram layer; both edges are ⚖️." Native numbers (F+11 / F+44) belong in the harness notes only.

### F4 · "ONE queue" headline → refinement; the refuted prediction was CLAIMS T-21's and E-67's

- **Decision**: **model-refinement** of MODEL headline 8 (MODEL.md:19). Keep "one queue", add the per-item FIFO sentence. Correction tags go to CLAIMS T-21's expected HID order (already item 32) and to E-67 (DEEP:120, "events within and between macros maintain strict ordering"), which the logs refute for a nested macro.
- **Basis**: read literally, the headline claims (i) one FIFO behaviour queue and (ii) moAndBuffer's park emits in-window letters at thumb-release + 260. (i) holds (`bq`); (ii) holds for queue-routed keys (T-18-a `[00:00:00.504,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x05 implicit_mods 0x00 explicit_mods 0x00`) and is already refined for raw `&kp` by item 20. It says nothing about where a `&bk` lands relative to a macro's not-yet-enqueued nested items. The order prediction "`&bk` build → A, BSPC, L, B, L" is CLAIMS T-21's own derivation. What the logs refute is E-67's "between macros" clause: T-21-f `[00:00:00.107,000] … keycode 0x0F` before `[00:00:00.118,000] … keycode 0x05`; ARB-F3-c `[00:00:00.114,000] … keycode 0x0F` before `[00:00:00.125,000] … keycode 0x05`; T-21-e (delivered after `ak↓`) `[00:00:00.125,000] … keycode 0x07` after B `[00:00:00.114,000] … keycode 0x05`.
- **Page-safe wording**: "Every macro key goes through one FIFO queue, and FIFO is per queued item: a macro nested inside a macro (the `&ak` at the end of a replace) adds its own steps only when its own item runs, F+20 on the board. A `&bk` that reaches the keymap before that lands before the B; one that reaches it after lands after. A raw `&kp` never enters the queue and overtakes everything in it."

### F5 · Modifier pin → correction for every "held modifier" sentence; refinement where the text already says "DOWN after arming"

- **Decision**:
  - **model-correction**: MODEL (a) diagram note "or pinned by a held modifier" (MODEL.md:69) and CLAIMS contradiction 16 "pinned by any held modifier" (CLAIMS.md:25). Their literal reading includes a modifier already down when the AK letter is typed; that case is refuted. The page's pin sentence, if it says "held", is wrong, not under-specified.
  - **model-refinement**: MODEL (c) Consumption (MODEL.md:147). Its first clause "the first keycode DOWN after arming stops the 100 ms timer and pins the layer until that keycode's UP" is exact; its consequence "so a held/sticky Shift pins the AK layer" needs "pressed inside the window". E-60's verdict "pinned by any keycode down incl. modifiers" → add "whose DOWN is delivered after arming".
- **PROVEN**:
  - A pre-held Shift does **not** pin (T-20-d): Shift↓ `[00:00:00.058,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0xE1 implicit_mods 0x00 explicit_mods 0x00` → A's layer `[00:00:00.110,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 1` → timeout `[00:00:00.211,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 0` (ON + 101) while Shift is down until `[00:00:00.346,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0xE1 implicit_mods 0x00 explicit_mods 0x00`.
  - A Shift pressed inside the window pins (T-20-a): layer ON `[00:00:00.079,000] … layer 1 state 1` → Shift↓ delivered `[00:00:00.119,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0xE1 implicit_mods 0x00 explicit_mods 0x00` → no OFF at +129 → K adapted `[00:00:00.414,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 1 position: 1, binding name: flo,behavior-buffered-key` → OFF only with Shift↑ `[00:00:00.465,000] … released … keycode 0xE1` → `[00:00:00.465,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 0`.
- **Page-safe wording**: "The AK layer is pinned by the first keycode whose press reaches the keymap after the layer came on: a letter, or a modifier pressed inside the window. A modifier you were already holding when you typed the trigger does not pin it; the layer still times out after 100 ms. While a modifier pins it, every following key resolves on the AK layer until that modifier is released."

### 🗂️ ARB evidence index

| case (`zmk/app/tests/ak-truth/…`) | template | overlay | events (abs ms) | log (`results/…`) | md5 |
|---|---|---|---|---|---|
| `ARB-F2-press40` | `_rig_R2` | events only | `PRESS(1,7,11) PRESS(1,9,27) PRESS(1,4,100) RELEASE(1,7,10) RELEASE(1,9,10) RELEASE(1,4,300)` → RM1 12 · RM3 24 · LM1 52 · ups 153 / 164 / 175 · exit 476 | `ARB-F2-press40.raw.log` | `46601b833effa7c6e7c276919405ad85` |
| `ARB-F2-press14` | `_rig_R2` | events only | `PRESS(1,7,11) PRESS(1,9,1) PRESS(1,4,100) RELEASE(1,7,10) RELEASE(1,9,10) RELEASE(1,4,300)` → RM1 12 · RM3 24 · LM1 26 · ups 127 / 138 / 149 · exit 450 | `ARB-F2-press14.raw.log` | `d19367c6e7ee148a7050b3ffe380d2e1` |
| `ARB-F2-release40` | `_rig_R2` | events only | `PRESS(1,7,11) PRESS(1,9,27) RELEASE(1,7,100) RELEASE(1,9,300)` → RM1 12 · RM3 24 · RM1↑ 52 · RM3↑ 153 · exit 454 | `ARB-F2-release40.raw.log` | `e3fe2128a69c405be122e836a718d18f` |
| `ARB-F3-a-rung-F44` | `_rig_R1` | T-21 replace macro on akA pos 4, akA pos 3 `&bk L`, akH pos 3 `&kp Z` | `PRESS(0,0,30) PRESS(1,0,50) PRESS(0,3,300) RELEASE(0,0,10) RELEASE(1,0,10) RELEASE(0,3,300)` → A 31 · E 62 · D 113 (F+32, rung at 125 = F+44) | `ARB-F3-a-rung-F44.raw.log` | `d651a8d34c41322d379b28ac2e55f809` |
| `ARB-F3-b-key-F44` | `_rig_R1_nohack` | same overlay | `… PRESS(1,0,62) …` → D 125 = F+44, key-driven (no combos) | `ARB-F3-b-key-F44.raw.log` | `000e647ff7e7b45d8c64f532a382bd93` |
| `ARB-F3-c-key-F5` | `_rig_R1_nohack` | same overlay | `… PRESS(1,0,23) …` → D 86 = F+5, key-driven | `ARB-F3-c-key-F5.raw.log` | `4b3d499ae213a7d55ffc1f1633774cab` |
| `ARB-F3-d-key-F11` | `_rig_R1_nohack` | same overlay | `… PRESS(1,0,29) …` → D 92 = F+11, key-driven | `ARB-F3-d-key-F11.raw.log` | `437bfa69a4117f2cb23cef1c7f9729dc` |

- Generator: `results/ARB.mkcases.py`. All seven built and ran (`run-test.sh` PASS after auto-accept); the `--no-rt` logs are the evidence. F = abs 81 in every F3 case (`[00:00:00.081,000] … layer_id: 1 position: 4, binding name: flo-macro-replace-char-with-bigram-LB`), identical in the hack-ON and hack-OFF rigs because the Q18 rung outlasts the hack.
- Source citations used in §3 and verified this run: `kscan_gpio_matrix.c:188` (`scan_time = k_uptime_get()` in the ISR), `:194-200` (absolute 1 ms re-arm), `:274` (callback inside the scan work); `physical_layouts.c:147-159` (callback → msgq + submit), `:182` (stamp); `central.c:130-131`, `:263-266`; Zephyr `kernel/timeout.c:120` (absolute, `MAX(1, ticks)`), `:122` (relative `+1`), `:126-135` (insertion after equal deadlines), `:209-239` (`sys_clock_announce`); `kernel/work.c:810-830` (`work_timeout` → `submit_to_queue_locked`), `:277` (`sys_slist_append` FIFO), `:966-967` (`k_work_schedule` only when idle or RUNNING).
'''

(R/"CORRECTIONS-FINAL.md").write_text(head + resolved)
print("written", R/"CORRECTIONS-FINAL.md", len((head+resolved).splitlines()), "lines")
