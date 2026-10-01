# 🔎 REVIEW-FABLE-MODEL — correctness gate on MODEL.md (+ README.md)

> Reviewer: Fable 5.1 · 2026-10-01 · targets `Design/Timing/MODEL.md` (primary), `Design/Timing/README.md` (secondary: ten things, six lines, 10 ms cell)
> Method: every `case [hh:mm:ss.mmm,uuu] … text` citation parsed and matched against `tests/timing/logs/*.raw.log` (script `scratchpad/fable-check/cite_check.py`); every 📜 `file:line` opened in the fork, the config, the dev container's Zephyr and the upstream checkout; every board-from-native translation recomputed; Δ tables, E_b table and the four Mermaid diagrams read against the text

## 🎯 Result first

- **~400 statements checked**: 219 timestamped log citations · 61 source `file:line` citations · ~85 Δ / E_b table cells · ~36 README statements in the three named sections
- **Logs: no fabricated or mis-timed citation.** Every cited `[timestamp]` exists in its raw log and says what is claimed; same-ms ordering claims (timer before key, layer before key, sticky OFF before rung) hold line by line
- **Source: every cited line says what the statement says**, including the Zephyr kernel lines read through the container and the upstream `combo.c:100-101` / `:263-279`
- **Tables and diagrams: no cell contradicts the rules**; the diagrams say nothing the text does not
- **23 edits** (12 in MODEL.md, 11 in README.md): 2 flagged tensions settled, 1 tag upgraded (🧮 → 📜), 0 tags downgraded, 5 README statements that contradicted MODEL.md's refuted list or its rules, the rest precision fixes (literal log quotes, page-clock vs board-clock, missing preconditions)
- **Nothing unresolved.** Two figures were not re-derived (debounce 4–6 ms, BLE 7.5 ms interval); both are tagged 📜/🧮 and cite report C, so they stand as tagged

## ⚖️ Tension 1 — status of the one-workqueue claim

- **Was**: ⏱️ Time convention tagged 🧮 "src", 🚚 Pipeline tagged 📜 for the same fact
- **Settled: 📜 in both places**
  - Every hop is a bare `k_work_submit` / `k_work_schedule` / `k_work_reschedule`; Zephyr routes those to `k_sys_work_q`
    - `kernel/work.c:405-409` (`k_work_submit` → `k_work_submit_to_queue(&k_sys_work_q, …)`), `:978-983` (`k_work_schedule` → `_for_queue(&k_sys_work_q, …)`), `:1014-1019` (reschedule); `system_work_q.c:20-32`; build `.config` `CONFIG_SYSTEM_WORKQUEUE_PRIORITY=-1`
  - Callers: `physical_layouts.c:159` (key), `central.c:266` (BLE key), `combo.c:417` (rung), `behavior_queue.c:46` (tick), `behavior_sticky_key.c:186` (sticky OFF), `behavior_hold_tap.c:620` (term), `kscan_gpio_matrix.c:200` (scan)
  - Only the BLE HID send has its own queue (`hog.c:259-274`), which is the "except the radio" clause
- **Edits**: Time convention bullet → 📜 with citations; Pipeline bullet → citations added; the `[!warning]` → one `[!note]`

## ⚖️ Tension 2 — #9 "RM1 types the base letter 'a'" vs the refuted "lowercase a"

- **Was**: #9 said the late Shift "types the base letter: LM1 "t", RM1 "a""; the ⛔ list struck "The late key types lowercase 'a'" (T-18-f); RVA-callum-close245 logs `keycode 0x04` + `Modifiers set to 0x02`
- **Settled: both are true at different levels, and the doc now says so in one voice**
  - The key resolves on **base** as `&ak A` (keycode 0x04, the base letter) and is parked to R+260
  - The **host** sees whatever modifiers are armed at R+260: in the page scenario the earlier LM1 Shift tap's sticky `skm` is still pending (`Modifiers set to 0x02` since `[00:00:00.215,000]`), it is consumed by that keycode → shifted "A", released with the key's kp↑ at `[00:00:00.494,000]`, before `layer 2 state 1`
  - So "base letter" (keycode) and "never lowercase a" (host output in that scenario) are the same event; "lowercase a" stays ⛔
- **Evidence**
  - `RVA-callum-close245.raw.log`: `[00:00:00.345,000] … capturing position event 16` → `[00:00:00.352,000] … layer 26 state 0` → `[00:00:00.362,000] … layer_id: 0 position: 16, binding name: flo,behavior-adaptive-key` → `[00:00:00.483,000] … keycode 0x04` + `zmk_hid_implicit_modifiers_press: Modifiers set to 0x02` → `[00:00:00.494,000] … keycode_released … 0x04`, `… 0xE1`, `Modifiers set to 0x00`, `layer 2 state 1`
  - `T-18-f-r2-page.raw.log`: same shape, RM1 pressed `[00:00:00.362,000]`, delivered `[00:00:00.381,000] … layer_id: 0 position: 16`, `[00:00:00.483,000] … keycode 0x04` + `Modifiers set to 0x02`
  - T-18-g (LM1 held past R+130, no prior sticky): `[00:00:00.504,000] … keycode 0x17` with no Shift → plain "t"; the capital is the sticky's doing, not the key's
- **Edits**: #9 bullet rewritten; `[!warning]` → `[!note]`; 🧲 table rows and the ⛔ lines say "`&ak A` on base, shifted by the pending sticky Shift"; README #9 aligned

## 📋 MODEL.md changes

| # | location | what was wrong | evidence | fix |
|---|---|---|---|---|
| 1 | 🎯 #9, "Shift pressed in the buffer's last ~16 ms" | "types the base letter … RM1 "a"" read as lowercase output; contradicted the ⛔ list | close245 `[00:00:00.483,000] … keycode 0x04` + `Modifiers set to 0x02`; T-18-f same | resolves on base as `&ak T` / `&ak A`, parked to R+260; host sees it shifted when the sticky is pending, never lowercase |
| 2 | `[!warning]` after the ten things | flagged tension 2 | as above | replaced by a `[!note]` with the resolution and both log lines |
| 3 | ⏱️ Workqueue blocking, first bullet | tagged 🧮 for a fact the source states directly | `work.c:405-409, 978-983`; callers listed above | 📜 with citations |
| 4 | ⏱️ Native offset, "T-02 reconciliation" | `T-02` is ambiguous (five T-02 logs); the lines are T-02-a's | `T-02-a-spec.raw.log` `[00:00:00.018,000] … in 10ms`, `[00:00:00.029,000] … layer 1 state 1` | `T-02-a reconciliation` |
| 5 | 🚚 Same-thread guarantee | 📜 with no citation | same as #3 + `kscan_gpio_matrix.c:200`, `hog.c:259-274` | citations added |
| 6 | `[!warning]` after the Pipeline bullets | flagged tension 1 | as above | replaced by a `[!note]` |
| 7 | ✋ Linger, TAP path, T-15-d quote | `… released 0x1C` is not a substring of any log line | `T-15-d-interrupt.raw.log:` `[00:00:00.134,000] … hid_listener_keycode_released: usage_page 0x07 keycode 0x1C` | quote made literal: `… keycode_released: … keycode 0x1C` |
| 8 | 🎚️ htm, "`kp_released 0xE0` is logged" | no such log text | T-19-a `[00:00:00.113,000] … hid_listener_keycode_released: … keycode 0xE0` | `keycode_released … 0xE0` |
| 9 | 🧲 Sticky Shift, T-18-f quote | `… released 0xE1` not literal | T-18-f `[00:00:00.494,000] … hid_listener_keycode_released: … keycode 0xE1` | made literal; added the one-line "letter is base `&ak A`, capital from the sticky" |
| 10 | 🧲 table, "late" and "close" rows | "board 380" reads as a board-clock instant; 380 is the page's own clock (R = 120) | T-18-f board R+260 = 481 absolute (R = 221); CORRECTIONS item 22 "release 120 + 260" | "page clock 380, R = 120" |
| 11 | 🧲 ⛔ "Late key types lowercase 'a'" | unexplained next to #9 | as tension 2 | parenthetical "`&ak A` on base, shifted by the pending sticky Shift" |
| 12 | 🔍 ⛔ list, same item | same | same | killing cases named (T-18-f, RVA-callum-close245) with the same parenthetical |

## 📋 README.md changes

| # | location | what was wrong | evidence | fix |
|---|---|---|---|---|
| 13 | ten things #4 | margin "1 ms for hack-only followers" without the BLE exception MODEL #4 carries | MODEL 📐 (BLE-stamped follower → `K_MSEC(10)`, same tick as the layer tick, armed after it) | "(a BLE-stamped hack-only follower can shrink to ≈ 0 ms, still ✅ 🧮)" |
| 14 | ten things #5 | "fragile to 14–16 ms" hid the board ⏸ cells at 15 / 17; H→E misses to 16 and stalls at 17 | MODEL Δ table (S3 rows), PAIRS.md l.66-67 | header "fragile past 10 ms"; "⏸ at 15" / "⏸ at 17" on the two S3 lines |
| 15 | ten things #6, "Adds latency only on the 8 hack-only keys; everything else was held 16/18 ms anyway" | this is in MODEL's ⛔ list | T-02-a pos 0 (R16) `[00:00:00.018,000] … keycode 0x04` = t+12 vs T-02-b-nohack `[00:00:00.012,000]` = t+6; T-23-a `[00:00:00.017,000]` = t+12 | lone-key +11 only on 8 keys; in any roll ≤ 10 ms key 1 waits to `t+11` on every position; fast 2-key combos wait for their deadline |
| 16 | ten things #6, "Costs the 34 ordinary pairs every roll ≤ 9 ms" | board Δ = 10 is a ⏸ stall, missing | MODEL #6 | "and a ⏸ stall at 10" |
| 17 | ten things #7 | "fires at its own deadline" omits the next-event exit (R7) | T-10-e `[00:00:00.129,000] … 0x1A` at first release; ARB-F2 | "(or your next key event)" |
| 18 | ten things #9 | "in the buffer's last 16 ms it types `t` / `a`" lacked "still held at R+130" (a tap released before R+130 stays Shift) and read as lowercase output | T-18-f LM1 delivered at key-up `[00:00:00.215,000]` → Shift; close245 / T-18-f `keycode 0x04` + `Modifiers set to 0x02` | "pressed in the last ~16 ms and still held at R+130 → `&ak T` / `&ak A` on base, parked to R+260 (shifted "A" when the sticky is pending, never lowercase)" |
| 19 | ten things #10 | "(10–200 µs firmware latencies …)" is MODEL's right-hand statement only; left-left ⚖️ cells are BLE-phase races up to ~1 ms (F1, RVB-03) | MODEL ⚖️ Same-tick ordering | both bands named |
| 20 | six lines, line 1, "every press is held at least 11 ms" | in MODEL's ⛔ list ("Every press is held 11 ms"; R6 key-up flush) | T-08-b `[00:00:00.016,000]` release flush; T-11 | "captured and held 11 ms, unless a key-up or a non-sharing press flushes it earlier" |
| 21 | six lines, line 3 | "Follower ≥ 11 ms … ✅" without the no-shared-combo precondition or the window edge (RVA-06 defect, re-introduced) | T-23-d1 `[00:00:00.030,000] … layer_id: 0 position: 21` (Δ 13 MISS, shared combo); T-12-b-d112 edge | precondition and "up to the window edge" added |
| 22 | six lines, line 5 | S2 pairs do not get "the same story": the 2-key combo itself fires | S-M_LT3-d5/d14/d15 `… keycode 0x1D` | clause added |
| 23 | 10 ms cell, "until your next key event (any press or release)" and "On the board the rung runs on time" | a press inside the follower's fresh hack window joins the stall (RVB-05); "runs on time" holds for right-hand triggers on BLE only (F1 / Time convention) | RVB-strand-join `[00:00:00.020,000] … capturing position event 0`, no rung at `[00:00:00.024,000]`, flush `[00:00:00.073,000]`; MODEL 📐 "Board now_flush" | exits restated; left-hand caveat added |

## 🏷️ Tag changes

- **Upgraded**: ⏱️ Time convention "Key stamps, rungs and ticks all run on `k_sys_work_q`" 🧮 → 📜
- **Downgraded**: none. Every 🧪 names an observation that exists in its raw log; every 📜 names lines that say what is claimed

## ✅ Checks that passed (so the next reader can skip them)

- **Log citations (219)**: all timestamps present; fragments literal except the three paraphrases fixed above. Ordering claims verified in-ms: T-07-d11 `layer 2 state 1` before `Row: 0, col: 3`; T-04-d12 `timestamp=23` before `Row:`; T-12-b-d112 `layer 19 state 0` before `remaining_candidates=0 timestamp=178`; T-15-c `decided hold-timer` before `pressed: false`; T-12-c `layer 13 state 0` → `layer 3 state 1` in one ms; RVB-pin-akfollower `mo_keymap_binding_released: position 0 layer 1` before `0 new sticky_key`; T-14-c R↓, R↑, `layer 17 state 1` all at `[00:00:00.102,000]`, two `zmk_endpoints_send_report` in T-14-a
- **Arithmetic**: T-12-a +17/+28/+129 from press `[00:00:00.101,000]`; T-01-r2-map +19 from `[00:00:01.107,000]`; T-11 sweep +12/+17/+19 (hack) vs 0/+17/+19 (no hack) recomputed over all 12 positions; T-17-c T+12 / T+91 from `[00:00:00.121,000]`; T-16-d-d11 created ts+12, HOLD ts+101; T-15-a/b/c key-ups at +99/+100/+101 → TAP/TAP/HOLD; T-09-b t+13, T-10-a t+16, T-09-a t+17, S-M_LT3-d5 t+17, RVB-bspc t+19; T-18-a / RVB-park-two R+131 / R+262 / R+273; T-21-a F+11/+22/+33/+44/+145; E_b for all five groups and the hack-OFF edges (94/110/112/108/126)
- **Source**: `bq:35` (`timestamp = k_uptime_get()`), `sk:85-92, 147-151, 181-186`, `combo.c:141-143, 145-161, 198, 273-289, 349, 407-418, 422-433, 448-452, 473-475, 498`, `keymap.c:142-145, 651-654, 665-666`, `ht:142-149, 220-222, 232-235, 619-620, 636, 642-645`, `physical_layouts.c:147-160, 178-182`, `central.c:130-131, 259-266`, `usb_hid.c:25-27, 139`, `hog.c:259-274`, `endpoints.c:123-127`, `app/Kconfig:142-143`, `kscan_gpio_matrix.c:194-200`, Zephyr `timeout.c:120, 122, 125-131`, `work.c:277, 492-511, 966-968`, `cfg/corne.conf:39-49`, `cfg/corne.keymap:86-87`, `hands_down/combos.dtsi:26, 34, 55`, `layers_C_extra.dtsi:41-43`, `adaptive_keys/behaviors.dtsi:1-9`, `mods/behaviors.dtsi:45-55`, `zmk.map:4612-4635` (activity → hold_tap → sticky_key → combo → hid_listener → keymap), compiled `zephyr.dts` (22 × 16, 5 × 18, 1 × 11 = 28), `zmk,combos.yaml` `require-prior-idle-ms` default −1, upstream `combo.c:100-101` (`LISTIFY(20, …)`) and `:263-279`
- **R11 board path re-traced**: `k_work_schedule` returns 0 when refused, and `0 >= 0` records the phantom deadline (`combo.c:417-418`) — as written
- **Tables**: hack-ON Δ table (5 columns × 10 rows), hack-OFF table, E_b table, board-timeline table, per-pair class table (34/11/2/4/1/2, 42 L-L / 12 R-R) all consistent with the rules, PAIRS.md and the cited cases
- **Diagrams**: pipeline notes (stamp points, "modifier pin: its UP or the next aksl↓"), state machine (R8–R10 edges incl. `Dead --> Dead` join), class flowchart (45 / 6 / 3), hack-mechanism sequence (Δ ≤ 9 / 10 / 11 ≤ Δ < dA) — each says only what the text says; lint 0 errors before and after
- **README counts**: 181 cases (184 dirs − 3 rig templates), 181 raw logs, 58 cases on the real keymap (59 keymaps reference NAQUADAH incl. the `_rig_R2` template)

## 🧾 Not re-derived (stand as tagged)

- Debounce "+4.0–6.0 ms" and BLE "0–7.5 ms + stack, median ≈ 4.5" (📜/🧮, report C §3); BLE 7.5 ms connection interval (🧮)
- README "180 PASS, 1 never had a snapshot" and "24 open items in FACTS.md" (outside the three sections in scope)
