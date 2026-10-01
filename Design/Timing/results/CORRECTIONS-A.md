# 🧾 CORRECTIONS-A — what T-02…T-23 changed or added relative to MODEL.md

> Extractor A. Inputs read in full: `MODEL.md`, `CLAIMS.md` (contradictions 1–16), `results/T-02.md` … `results/T-23.md` (incl. every Deviations list and the Reconciliation sections of T-02, T-10, T-16, T-17, T-18).
> Extra evidence used (flagged per entry): 11 **undocumented reconciliation probes** whose case dirs exist under `zmk/app/tests/ak-truth/*-fix-*` but whose results never made it into a T-xx.md. 7 had raw logs in `results/`; 4 I ran myself (`zmk.exe --no-rt`, no rebuild) → `investigation/corrA-logs/` (md5 listed in §8).
> Legend
> - **Kind**: `model-correction` (a MODEL rule predicted the wrong outcome) · `model-refinement` (rule right, incomplete/over-broad) · `new-fact` (MODEL silent) · `spec-arithmetic` (CLAIMS spec slip, MODEL unchanged) · `harness` · `wording`.
> - **Status**: PROVEN(T-xx) = observed in a native_posix log · SOURCE = file:line reading · INFERRED = derived, not executed.
> - **Board translation rule**: board = native − 1 ms per relative timer crossed (+δ, δ ∈ (0.03, 1.05] ms each); an `&ak` key delivered by a combo timer crosses two (rung, then 10 ms queue tick); key-driven instants carry no offset.

---

## 🎯 Lead: what the page must change

| # | id | kind | one line |
|---|---|---|---|
| 1 | MC-01 | model-correction | Pairs whose trigger and follower **share a real combo** miss up to Δ ≤ S−1 (native) **with or without the hack**; "every follower in a real combo adapts for all Δ without the hack" is false for them (6 compiled pairs). |
| 2 | MC-02 | model-correction | `htm` mod is down from the key's **delivery**, not its press; after an `htls` interrupt the key re-enters the combo engine on `l_mod` → LM1/RM1 Shift lands **+16 ms** (+17 native). |
| 3 | MC-03 | model-correction | A captured **raw `&kp`** follower of a hold-tap is emitted **at the decision instant, before tap↑**; only queued followers wait for the next tick. |
| 4 | MC-04 | model-correction | The behaviour queue is FIFO **per item**: a nested `&ak` inside a replace macro enqueues its B only at F+20, so a `&bk` follower delivered in (F, F+20) lands **before** B. |
| 5 | NF-01 | new-fact | Native same-tick order: every timer work item of a tick runs **before** that tick's position event (msgq + 2nd work item) → native ties resolve layer-first / timer-first (T-07 Δ=11 = HIT). |
| 6 | NF-02 | new-fact | Dead window after a replace macro: keys delivered in (F+10, F+40] (board) resolve on **base** — old AK layer consumed by ⌫, new one not on yet. |
| 7 | NF-05 | new-fact | `htm` HOLD release unregisters the mod **twice**; with a same-mod sticky armed it **cancels the sticky** (next key unmodified) — PROVEN by an undocumented probe. |
| 8 | MR-06 | model-refinement | AK window upper edge: native adapts through Δ=111, base at 112 (tie, sticky first); board ≤109 adapt, **110 = sub-ms race**, ≥111 base (16/16 pair). |
| 9 | MR-07 | model-refinement | A modifier pins the AK layer only if its keycode DOWN arrives **after** arming; while pinned, **every** follower adapts until the modifier's UP. |
| 10 | MR-11 | model-refinement | Callum buffer closing edge = release + 130 − k (k = key's longest `l_mod` combo): a Shift on LM1/RM1 pressed in the last ≈16 ms becomes the base `&ak` letter. |

- Counts: model-correction 4 · model-refinement 14 · new-fact 13 · spec-arithmetic 11 · harness 7 · wording 5 (HW table mixes both).

---

## 1. 🔴 Model corrections

### MC-01 — shared-combo pairs fail regardless of the hack
- **Target**: MODEL 🎯 headline bullet 6 (🔁 "every follower that is in a real combo … adapted for ALL Δ"); (d) Hack OFF line "`k2 > 0` → HIT for every Δ ≥ 0"; (d) Hack ON line "Δ ≤ 9 … both wait for the hack rung at T_A + 11"; (d) Failure-region summary; CLAIMS contradiction 4.
- **Corrected statement**
  - The (d) theorem holds only under its own precondition "A and B share no real combo". Page must state it.
  - If A and B are both members of a real combo live on the alpha layer (S = longest timeout among combos containing both):
    - B's press does **not** empty A's set (R2 keeps the shared combo) → both leave together at A's shared rung `T_A + S` (native `T_A + S + 1`), A first; B is re-raised with its old timestamp.
    - A's `&ak` kp↓ is queue-stamped at the flush → B bypasses (R8) iff `T_B ≤ now_flush − 2`.
    - **Native**: MISS for Δ ≤ S − 1, HIT from Δ = S (B's press lands at/after A's deadline → key-first flush, B re-captured fresh, delivered `T_B + S (+1)`).
    - **Board** (INFERRED, R8/R9): MISS Δ ≤ S − 2; Δ = S − 1 → B re-captured inside the timer handler → R9 strand → delivered at the next press/release (adapted if the AK layer is still alive, ≈ hold-time late; MISS only in the ≈5 % where `now_flush = T_A + S + 1`); HIT from Δ = S.
    - Identical with the hack on or off (the hack adds only a no-op rung). For Δ ≤ 9 the flush is at `T_A + S`, not `T_A + 11`.
    - L→LB3 (S = 16): native MISS Δ ≤ 15, HIT 16; board MISS ≤ 14, STALL 15, HIT 16.
  - Static scan (not executed) of compiled pairs sharing a real combo with the trigger:

    | trigger → follower | follower binding | shared combo | status |
    |---|---|---|---|
    | L (LB2) → LB3 | `&bk L` | magicCloseQuitCb LB3 LB2 LB1, 16, 3-key | PROVEN T-23 |
    | H (RM4) → RM2 | `ak_hE` | capsWord RM1–RM4, 18, 4-key | INFERRED (band Δ ≤ 17 native) |
    | M (LT2) → LT3 | `&bk M` | typeZ LT3 LT2, 16, **2-key** | INFERRED: follower completes the combo → likely Z, not an AK |
    | W (LT3) → LT2 | `WM_to_LM` | typeZ, 2-key | INFERRED: likely Z |
    | D (LB1) → LB0 | `DV_to_LV` | tab LB1 LB0, 16, 2-key | INFERRED: likely Tab |
    | V (LB0) → LB1 | `&bk L` | tab, 2-key | INFERRED: likely Tab |

- **Evidence**
  - T-23-e5 (hack OFF, Δ = 13, L→LB3): `[00:00:00.030,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=29` → `[00:00:00.030,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 21, binding name: flo,behavior-adaptive-key` → `[00:00:00.041,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x0A implicit_mods 0x00 explicit_mods 0x00` ("LG" MISS).
  - T-23-d5 (hack ON, Δ = 15): `[00:00:00.032,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=31` → `[00:00:00.032,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 21, binding name: flo,behavior-adaptive-key`.
  - T-23-d6 (Δ = 16, first HIT): `[00:00:00.049,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 12 position: 21, binding name: flo,behavior-buffered-key`.
  - T-23-d2 (Δ = 5, flush at t+17 not t+12): `[00:00:00.017,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=1 timestamp=16` then `[00:00:00.022,000] … remaining_candidates=0 timestamp=21`.
  - T-23-e1 (hack OFF, Δ = 20, HIT): `[00:00:00.057,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 12 position: 21, binding name: flo,behavior-buffered-key`.
- **Confidence**: high (L→LB3 native band); medium (board band, H→RM2); low (2-key pairs → proposed test in §7).

### MC-02 — `htm` mod down at delivery; interrupting key re-enters the combo engine on `l_mod`
- **Target**: MODEL (e) `htm` bullet "the modifier is DOWN from the key press (HID report immediately) … the mod is never absent between press and consumption"; (e) `htls` interrupt bullet (silent on the re-raise); CLAIMS contradiction 10 "(mod down from press, `ht:522-526`)".
- **Corrected statement**
  - `htls` interrupt: other key DOWN while undecided → `decided hold-interrupt` in that key's ms (event-driven) → `&mo l_mod` runs synchronously (queue idle) → `layer 26 state 1` same ms. **Then** the interrupting key is re-raised AT the hold-tap listener (`ht:232-235`, `event_manager.c:65-71`) and passes the combo engine again with `l_mod` highest (`combo.c:147`).
  - ≥ 1 candidate live on `l_mod` → captured, delivered at `ts_key + longest candidate` (board `+δ`, native `+1`), deadline anchored at the key's original timestamp; 0 candidates → delivered in the decision ms.
  - `htm` modifier goes DOWN at the key's **delivery** (hold-tap creation → hold-while-undecided, `ht:523`), i.e. press + combo hold on the layer active at capture, or at its key-up if earlier. "Never absent between delivery and consumption" stays true.
  - Flo's `l_mod` (26): only **LM1 (`entr` <13 14>, 16 ms, layers 0–31)** and **RM1 (`entr2` <15 16>)** have a combo live on 26 → Shift at `ts + 16` (native +17). LM4/LM3/LM2, RM2/RM3/RM4 → 0 ms. Same delay applies when an `htm` is pressed directly while `l_mod` is held.
  - Consequence (INFERRED, untested): a letter pressed on another key during LM1/RM1's 16 ms hold is not an `entr` member → it flushes LM1 at its own press.
- **Evidence**
  - T-17-a4 (real keymap, LH1 + LM1): `[00:00:00.062,000] <dbg> zmk: position_state_down: combo: capturing position event 13` → `[00:00:00.079,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=78` → `[00:00:00.079,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0xE1 implicit_mods 0x00 explicit_mods 0x00` (t+48 native = decision t+31 + 17).
  - T-17-a3 (LH1 + LM4, no `l_mod` combo): `[00:00:00.062,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0xE0 implicit_mods 0x00 explicit_mods 0x00` (decision ms).
  - T-17-fix-a-tiers-alpha-only (R1 pos 5 with S16/Q18 moved off layer 4): `[00:00:00.062,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0xE0 implicit_mods 0x00 explicit_mods 0x00` (vs T-17-a `[00:00:00.081,000] … keycode 0xE0` = t+50).
  - T-19-a (htm pressed on layer 4, rig combos): `[00:00:00.081,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0xE0 implicit_mods 0x00 explicit_mods 0x00` (t+19); **undocumented** T-19-fix-a-nocombo (S16/Q18 deleted): `[00:00:00.062,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0xE0 implicit_mods 0x00 explicit_mods 0x00` (t+0).
  - T-18-f (LM1 tapped 15 ms on `l_mod`, flushed by its own key-up): `[00:00:00.215,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0xE1 implicit_mods 0x00 explicit_mods 0x00` (Shift at key-up, not at press t+100).
- **Confidence**: high (LM1, LM4 observed on R2); RM1 INFERRED from D-config §6.2 → test in §7.

### MC-03 — captured raw `&kp` follower jumps ahead of `tap↑`
- **Target**: MODEL (e) Linger keys: "TAP path: `tap↓`, captured keys delivered, `tap↑` … with `&bk` as tap the follower's HID down lands after `tap↑` at the next 10 ms tick".
- **Corrected statement**
  - Order at the decision instant = `tap↓` (queue idle → synchronous) → `release_captured_events` → each captured key resolved.
  - **Raw `&kp` follower**: HID↓ in the same handler, **before** `tap↑` → HID `Y↓ D↓ Y↑ D↑` (overlapped roll; text unchanged "yd").
  - **Queued follower** (`&ak`/`&bk`/morph): enqueued behind `tap↑` → HID↓ at the next queue tick = decision + 10 + δ (native +11), right after `tap↑`.
  - Same for HOLD (`X↓ D↓ X↑`). Board order identical (event-driven); only `tap↑` time is +10+δ.
- **Evidence**
  - T-15-d: `[00:00:00.123,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x1C implicit_mods 0x00 explicit_mods 0x00` → `[00:00:00.123,000] <dbg> zmk: release_captured_events: Releasing key position event for position 3 pressed` → `[00:00:00.123,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x07 implicit_mods 0x00 explicit_mods 0x00` → `[00:00:00.134,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0x1C implicit_mods 0x00 explicit_mods 0x00`.
  - T-15-e (HOLD): `[00:00:00.142,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x1B …` then `[00:00:00.142,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x07 …`, X↑ at `[00:00:00.153,000]`.
  - Queued controls: T-15-f `[00:00:00.134,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0x1C …` then `[00:00:00.134,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x05 …`; **undocumented** T-15-fix-a-bk-follower (`&bk D`): `[00:00:00.134,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0x1C implicit_mods 0x00 explicit_mods 0x00` then `[00:00:00.134,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x07 implicit_mods 0x00 explicit_mods 0x00`.
- **Confidence**: high.

### MC-04 — queue FIFO is per item; nested macros enqueue late
- **Target**: MODEL 🎯 headline 🧵 "Every macro key (`&ak`, `&bk`, morphs) is serialised through ONE queue"; CLAIMS contradiction 13 / E-72 ("`&bk` keeps order behind an in-flight macro").
- **Corrected statement**
  - One FIFO, but ordered **per queued item**. `REPLACE_CHAR_WITH_BIGRAM` = 8 outer items (⌫↓ ⌫↑ L↓ L↑ LSHFT↑ RSHFT↑ `ak↓` `ak↑`) + 4 nested (B↓ B↑ aksl↓ aksl↑); the nested 4 are enqueued only when the outer `ak↓` item executes.
  - Replace timeline (F = replace delivery), board / native: ⌫↓ F / F · ⌫↑ + L↓ F+10 / F+11 · L↑ + shift releases + `ak↓` F+20 / F+22 · B↓ F+30 / F+33 · B↑ + new AK layer ON F+40 / F+44 · layer OFF F+140 / F+145.
  - `&bk` follower delivered in (F, F+20) → its items sit before B's → emitted before B (text "LDB" not "LBD"). Delivered after F+20 → after B. Raw `&kp` → emitted at delivery, ahead of all queued output (E-68 holds).
- **Evidence** (T-21 quotes have the `<dbg> zmk:` prefix stripped by the runner)
  - T-21-c (`&bk D` delivered t+59): `[00:00:00.111,000] hid_listener_keycode_pressed: usage_page 0x07 keycode 0x07 implicit_mods 0x00 explicit_mods 0x00` before `[00:00:00.122,000] hid_listener_keycode_pressed: usage_page 0x07 keycode 0x05 implicit_mods 0x00 explicit_mods 0x00`.
  - T-21-f (in-window `&bk L`): follower `[00:00:00.107,000] hid_listener_keycode_pressed: usage_page 0x07 keycode 0x0F …` before B `[00:00:00.118,000] hid_listener_keycode_pressed: usage_page 0x07 keycode 0x05 …`.
  - T-21-e (delivered after `ak↓`): B `[00:00:00.114,000] hid_listener_keycode_pressed: usage_page 0x07 keycode 0x05 …` then D `[00:00:00.125,000] hid_listener_keycode_pressed: usage_page 0x07 keycode 0x07 …`.
  - T-21-d (raw ahead): D `[00:00:00.108,000] hid_listener_keycode_pressed: usage_page 0x07 keycode 0x07 …` before B `[00:00:00.114,000] … keycode 0x05`.
- **Confidence**: high.

---

## 2. 🟠 Model refinements

### MR-01 — R6 release-while-buffered with an `&ak` key 1: bypass, no dupe cleanup
- **Target**: MODEL R6 ("the re-raised B is immediately re-flushed by the dupe's own `cleanup()`"), state-diagram RELEASE edge.
- **Statement**
  - Any release flushes the whole buffer at the release's timestamp (key-driven: no +1 on either target). ✅ unchanged.
  - Key 1 = `&ak`: its kp↓ is queue-stamped at `T_rel` → re-raised key 2 (`T_B ≤ T_rel − 2`) is a quick tap (R8) → 0 candidates → resolves on base at `T_rel`; **no re-capture, no `releasing position event` for key 2**; the dupe release hits an empty buffer.
  - Key 2's HID↓ is queued behind key 1's tap: native `T_rel + 11`, board `T_rel + 10 + δ`, after key 1↑ and the AK layer ON in the same tick → MISS "AB".
  - R6's re-capture + dupe-cleanup path applies when key 1 is raw `&kp` (position-stamped) or `T_B ≥ T_rel − 1`; outcome identical (key 2 at the release, on base).
  - Releasing key 2 first also flushes key 1 (51 ms before its own release).
- **Evidence**
  - T-08-a-spec: `[00:00:00.016,000] <dbg> zmk: release_pressed_keys: combo: reraising position event 1` → `[00:00:00.016,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 1, binding name: flo,behavior-adaptive-key`; no `releasing position event 1`; `[00:00:00.027,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x05 implicit_mods 0x00 explicit_mods 0x00`.
  - T-08-c (raw `&kp` key 1): `[00:00:00.016,000] <dbg> zmk: position_state_down: combo: capturing position event 1` → `[00:00:00.016,000] <dbg> zmk: release_pressed_keys: combo: releasing position event 1`.
  - **Undocumented** T-08-fix-boundary-rel1 (`T_B = T_rel`, same ms): `[00:00:00.012,000] <dbg> zmk: position_state_down: combo: capturing position event 1` → `[00:00:00.012,000] <dbg> zmk: release_pressed_keys: combo: releasing position event 1` (re-capture). T-08-fix-boundary-rel2 (`T_rel = T_B + 2`): `[00:00:00.014,000] <dbg> zmk: release_pressed_keys: combo: reraising position event 1` → `[00:00:00.014,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 1, binding name: flo,behavior-adaptive-key` (bypass).
  - `T_B = T_rel − 1` itself is not producible by the mock (HW-01); SOURCE: `(T_rel − 1) > T_rel − 1` false → re-capture.
- **Confidence**: high.

### MR-02 — raw `&kp` key 1 never bypasses: key 2 strands for the whole Δ ≤ 10 band
- **Target**: MODEL R8/R9 scope; (d) is stated only for `&ak` key 1.
- **Statement**: with a position-stamped key 1 (raw `&kp`), `is_quick_tap = (T_1 − 1) > T_2` is false for every Δ ≥ 0 → a key 2 flushed in the hack-rung burst is always re-captured inside the timer handler → R9 strand (no timer) until the next press/release; target-independent (no +1 involved). Output unchanged letters, key 2 late by the hold time. Contrast: same events with `&bk` key 1 → R8 bypass.
- **Evidence**: T-03 `[00:00:00.018,000] <dbg> zmk: position_state_down: combo: capturing position event 1` (after `reraising`), nothing until `[00:00:00.073,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x05 implicit_mods 0x00 explicit_mods 0x00` (= D↑); T-03-bk `[00:00:00.018,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 1, binding name: flo,behavior-adaptive-key` (no capture). Also T-10-d `[00:00:00.024,000] <dbg> zmk: position_state_down: combo: capturing position event 6`, next line `[00:00:00.122,000]`.
- **Confidence**: high (mechanism); which of Flo's layer 0–24 positions are raw `&kp` not enumerated here.

### MR-03 — R10 sharpened: only RUNNING may re-arm; four exits
- **Target**: MODEL R10.
- **Statement** (replaces R10 text)
  - `k_work_schedule` is refused whenever the combo delayable is DELAYED, QUEUED or CANCELING (`work.c:967`; only RUNNING may re-arm), yet `combo.c:417-418` records the wanted deadline → phantom `timeout_task_timeout_at`. When a later key removes the candidate owning the armed deadline and a later-deadline candidate survives, the old timer fires, `combo.c:473-475` early-returns, no re-arm → timer-less until the next position event.
  - Exits: (1) press completing the **only** surviving candidate → fires at that press (stall invisible); (2) press completing `candidates[0]` with ≥ 2 alive → marked, fires at the first release; (3) press sharing no live candidate, or after every deadline passed → flush at that press (first key late vs its unarmed deadline); (4) any release → flush.
  - Hack on: needs key 2 at Δ ≥ 11 (hack already dropped) and before the shortest survivor's deadline. Δ < 11 → MIN unchanged, no stall (then R9 may strand the re-raised key instead).
  - Also QUEUED (SOURCE `work.c:894`, `sys_clock.h:127`, outcome PROVEN): a fresh set whose MIN is already past → `K_MSEC(<0)` clamps to 0 → item QUEUED → a second re-raised key's schedule is refused → both stranded until the next event.
  - Flo: RM1, RM3 at +12, RM2 → delWord only at the first release (capsWord alive) ✅; RM1 + RM3 at 11–15 ms with no RM2 → both letters held until the next press/release instead of +18 (INFERRED from T-10-c).
  - Hack off (nav/num layers): any key dropping the shortest candidate while a longer survives stalls the same way (INFERRED).
- **Evidence**
  - T-10-e: `[00:00:00.129,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x1A implicit_mods 0x00 explicit_mods 0x00` (W at E↑, t+117; no rung at t+17/t+19).
  - T-10-c: no line of any kind in `[.025]`–`[.128]`; `[00:00:00.129,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x08 …` then `… keycode 0x0A`.
  - T-10-fix-lateF-d13: `[00:00:00.037,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x08 implicit_mods 0x00 explicit_mods 0x00` (E at F's press t+25, not rung t+19); then G, F stranded to `[00:00:00.138,000]`.
  - T-10-a (exit 1): `[00:00:00.028,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x1A …` (t+16).
- **Confidence**: high (observed exits); QUEUED refusal mechanism SOURCE.

### MR-04 — scope of "3-key combos typed out of order stall until a release"
- **Target**: MODEL (e) Combo tiers bullet; CLAIMS contradiction 7 / E-25; CLAIMS T-10 spec.
- **Statement**: a completed out-of-order 3-key combo waits for a release only if ≥ 2 candidates are alive at completion. As the sole surviving candidate it fires at the completing press. Flo's RM1–RM3 example always has capsWord alive → the MODEL example stands; the general wording must carry the condition. The stall itself (MR-03) does not need completion.
- **Evidence**: T-10-a `[00:00:00.028,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=1 timestamp=28` + `[00:00:00.028,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x1A …`; T-10-e as MR-03.
- **Confidence**: high.

### MR-05 — hack-off, `k2 = 0` column on native (tie resolves HIT)
- **Target**: MODEL (d) table columns "OFF, k2 = 0, …" and the ⚖️ legend "deterministic on native".
- **Statement**
  - Board unchanged: MISS Δ ≤ k1 + 9, TIE Δ = k1 + 10 (sub-ms), HIT Δ ≥ k1 + 11.
  - Native: layer ON at `D_A + 11` with `D_A = 0` (k1 = 0) or `k1 + 1` (timer-delivered) → MISS for Δ < D_A + 11, **tie at Δ = D_A + 11 resolves HIT** (layer first, NF-01), HIT beyond. k1 = 0: MISS ≤ 10, HIT ≥ 11. k1 = 16: MISS ≤ 27, HIT ≥ 28.
- **Evidence**
  - T-07-d11: `[00:00:00.022,000] <dbg> zmk: set_layer_state: layer_changed: layer 2 state 1` precedes `[00:00:00.022,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 3, position: 3, pressed: true` → `[00:00:00.022,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 2 position: 3, binding name: flo,behavior-buffered-key`.
  - **Undocumented** T-07-fix-d10 (my run): `[00:00:00.020,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 3, binding name: key_press` then `[00:00:00.021,000] <dbg> zmk: set_layer_state: layer_changed: layer 2 state 1` (Δ = 10 MISS).
  - T-23-e4 (k1 = 16, Δ = 28): `[00:00:00.056,000] <dbg> zmk: set_layer_state: layer_changed: layer 12 state 1` → `[00:00:00.056,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 1, position: 0, pressed: true` → `[00:00:00.056,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 12 position: 0, binding name: flo,behavior-buffered-key`; T-23-e3 (Δ = 20) `[00:00:00.040,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 0, binding name: flo,behavior-adaptive-key`.
- **Confidence**: high (native); board TIE cell untested (T-24).

### MR-06 — AK window upper edge
- **Target**: MODEL (c) "Window seen from the next key-down … ≈ 105–110 ms"; (d) "Upper window edge … 110 (M→T, L→G)".
- **Statement**
  - Native (k1 = k2 = 16): adapted through Δ = 111; Δ = 112 = same-ms tie between the sticky OFF timer (armed at D+11) and the follower's last rung; the earlier-armed sticky runs first → base. Native window 2 ms wider than the board's.
  - Board: OFF path carries three timer offsets (rung, queue tick, sticky; `≈ T + 126 + Σδ`), follower delivery one (`T + Δ + 16 + δ`) → Δ ≤ 109 adapted, **Δ = 110 sub-ms race**, Δ ≥ 111 base (rare δ exceptions). So `D_A + 110 − max(11,k2)` is the race cell, not a safe HIT. INFERRED.
  - Consumption keeps the layer past +110 until the consuming follower's UP (unchanged).
- **Evidence**: T-12-b-d111 `[00:00:00.178,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 19 position: 21, binding name: flo,behavior-buffered-key`; T-12-b-d112 `[00:00:00.179,000] <dbg> zmk: set_layer_state: layer_changed: layer 19 state 0` → `[00:00:00.179,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=178` → `[00:00:00.179,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 21, binding name: flo,behavior-adaptive-key`.
- **Confidence**: high native; medium board.

### MR-07 — modifier pin scope; pinned layer adapts every follower
- **Target**: MODEL (a) diagram note "OFF … or pinned by a held modifier"; (c) Consumption "a held/sticky Shift pins the AK layer until Shift up"; CLAIMS contradiction 16 / E-60 "pinned by any held modifier".
- **Statement**
  - Only a keycode whose DOWN is **delivered after `aksl` arms** consumes/pins (MODEL's "first keycode DOWN after arming" is exact). A Shift already held when the AK letter is typed does **not** pin; the layer times out at D+110 (native D+112). A key already down before arming does not consume, and its later UP does not release the layer either.
  - While a held modifier pins the layer, **every** follower resolves on the AK layer until the modifier's UP (text "aKK"). With `skms` the pin ends at the next letter's key-up (sticky releases there) → at most one extra letter on Flo's LH1 path.
  - Pin condition on the board (INFERRED): the modifier's keycode must be *delivered* before ≈ `D_A + 110 + δ` — after its own combo wait (11–18 ms) or the hold-tap decision. INFERRED: an `htm` home-row mod held on `l_mod` pins the same way.
- **Evidence**
  - T-20-d (Shift first): `[00:00:00.211,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 0` with Shift still down (Shift↑ `[00:00:00.346,000]`).
  - T-20-e (two followers): second K `[00:00:00.446,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 1 position: 1, binding name: flo,behavior-buffered-key`; OFF only at `[00:00:00.477,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 0` (Shift↑).
  - T-20-c (`skms`): `[00:00:00.377,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 0` right after K↑ and LSHIFT↑.
  - T-07-d5 (pre-held D): D↓ `[00:00:00.010,000]`, layer ON `[00:00:00.016,000]`, OFF `[00:00:00.117,000] <dbg> zmk: set_layer_state: layer_changed: layer 2 state 0` (timer).
- **Confidence**: high.

### MR-08 — R thumb: 0 ms tap PROVEN, but the queue stays parked 10 ms
- **Target**: MODEL (c) "R thumb … INFERRED, T-14" bullet; (g) INFERRED list "R thumb 0 ms tap + immediate layer; captured key adapted".
- **Statement**
  - PROVEN: `blt_akR` tap → `ak_R_macro` → nested `&ak`: R↓, R↑, `l_akR` ON in the thumb-up handler (event-driven, same instant on the board); a key captured by the thumb hold-tap is re-raised after that → resolves on `l_akR` (D's T7b refuted on R2).
  - Addition: the nested inner `process_next` scheduled the 10 ms delayable → queue parked until thumb-up + 10 + δ (native +11). Any macro key resolved in that window (the captured follower's `&bk`, or a follower pressed ≤ 10 ms after thumb-up) emits HID↓ at thumb-up + 10 (+δ), though resolved on `l_akR` at delivery. The leftover `&ak↑` runs at that tick (no-op).
  - `l_akR` window = decision → decision + 100 + δ (native +101) — no +10 as for other `&ak`.
  - Control: a hold-tap tap = direct `&ak` program → normal 10 ms tap, layer at +10, captured key on base, and its kp consumes/wastes the new layer.
- **Evidence**
  - T-13-b: `[00:00:00.093,000] <dbg> zmk: set_layer_state: layer_changed: layer 3 state 1` → `[00:00:00.093,000] <dbg> zmk: release_captured_events: Releasing key position event for position 1 pressed` → `[00:00:00.093,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 3 position: 1, binding name: flo,behavior-buffered-key` → `[00:00:00.104,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x17 implicit_mods 0x00 explicit_mods 0x00`.
  - T-13-d (real LH0): `[00:00:00.093,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 17 position: 0, binding name: flo,behavior-buffered-key`, HID `[00:00:00.104,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x15 …`.
  - T-14-a / T-14-c: R/H ↓, ↑ and layer ON all `[00:00:00.102,000]`; `[00:00:00.203,000] <dbg> zmk: set_layer_state: layer_changed: layer 17 state 0` (c).
  - **Undocumented** T-13-fix-e-park (my run; hack off, follower at thumb-up + 5): `[00:00:00.067,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 3 position: 1, binding name: flo,behavior-buffered-key` → `[00:00:00.073,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x17 implicit_mods 0x00 explicit_mods 0x00`. Control T-13-fix-f-nopark (thumb-up + 15): `[00:00:00.077,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 3 position: 1, binding name: flo,behavior-buffered-key` → `[00:00:00.077,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x17 implicit_mods 0x00 explicit_mods 0x00`.
  - T-13-c control: `[00:00:00.093,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 1, binding name: flo,behavior-adaptive-key`; layer `[00:00:00.104,000] … layer 3 state 1`.
- **Confidence**: high.

### MR-09 — linger forced TAP: full rule
- **Target**: MODEL (e) "A linger key pressed ≤ 9 ms after an `&ak` alpha is force-decided TAP at delivery … INFERRED → T-16".
- **Statement** (PROVEN on native; board band INFERRED)
  - Linger key (`&lk`, tap-preferred 100, tap `&bk`) pressed ≤ 9 ms (board; ≤ 10 native) after an `&ak` alpha: re-raised at the `&ak`'s delivery D with its old timestamp, bypasses the combo engine (R8), hold-tap created and `decided tap (… quick-tap)` at D (`ht:611-612`, `last_tapped` = the `&ak`'s queue-stamped kp↓).
  - `&bk Y` is enqueued behind the running `&ak` → Y↓ at D + 10 (+δ; native +11) right after `A↑` + AK layer ON; Y↑ at D + 20. Y is the first keycode after arming → the AK layer lives only (D+10, D+20]. Term timer still fires at `T_L + 100` as a no-op. Never lingers however long held.
  - The combo bypass and the hold-tap quick-tap flip at the same Δ (both compare the same kp↓ stamp).
  - Δ ≥ 11 (both targets): not quick-tap → re-captured by a fresh hack set → decides normally (HOLD at `T_L + 100 + δ`, native +1).
  - Board Δ = 10 (INFERRED, R9): linger key stranded until the next position event; hold-tap then created with ts `t+10`, not quick-tap, term already expired → `K_MSEC(<0)` → **HOLD (X)** at ≈ that event → T-24a.
  - With a queue-free tap (`&kp Y`): Y↓ at the decision instant, AK layer not consumed (expires by timer), HID overlapped `B↓ Y↓ B↑ … Y↑`.
  - Flo's linger keys sit in 16 ms combos → reach on the real keymap untested.
- **Evidence**: T-16-a `[00:00:00.018,000] <dbg> zmk: decide_hold_tap: 9 decided tap (tap-preferred decision moment quick-tap)`, `[00:00:00.029,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x1C implicit_mods 0x00 explicit_mods 0x00`, `[00:00:00.040,000] <dbg> zmk: set_layer_state: layer_changed: layer 2 state 0`; T-16-c-d10 `[00:00:00.022,000] <dbg> zmk: decide_hold_tap: 9 decided tap (tap-preferred decision moment quick-tap)`; T-16-d-d11 `[00:00:00.123,000] <dbg> zmk: decide_hold_tap: 9 decided hold-timer (tap-preferred decision moment timer)`; T-16-fix-a-kptap `[00:00:00.018,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x1C implicit_mods 0x00 explicit_mods 0x00` + `[00:00:00.130,000] <dbg> zmk: set_layer_state: layer_changed: layer 2 state 0`.
- **Confidence**: high (native); board Δ ≤ 9 medium; board Δ = 10 low.

### MR-10 — sticky mod window anchored at the key's PRESS
- **Target**: MODEL (e) `htls` "skms LSHIFT (sticky 1500 ms …)"; `htm` "mod stays until … 1500 ms". (Headline 🎯 "sticky windows … count from" the original timestamp covers it.)
- **Statement**: `release_at = event.timestamp + 1500` with the hold-tap's original press timestamp (`sk:182`, `ht:410-413`, `ht:433-436`) → sticky expires at **press + 1500** (+δ board, +1 native); effective window after key-up = 1500 − hold time. Applies to `skms` (htls tap) and `skm` (htm tap).
- **Evidence**: T-17-b2 `[00:00:01.552,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0xE1 implicit_mods 0x00 explicit_mods 0x00` (thumb press `.051` + 1501; tap decided `.102`); T-19-d `[00:00:01.563,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0xE0 implicit_mods 0x00 explicit_mods 0x00` (htm press `.062` + 1501, although the hold-tap was created at `.081`).
- **Confidence**: high.

### MR-11 — Callum buffer closing edge for combo-held keys
- **Target**: MODEL (e) Callum mods `moAndBuffer` release bullet.
- **Statement**
  - A key pressed inside the 130 ms buffer resolves on `l_mod` iff its **delivery** precedes layer OFF (release + 130 + δ; native +131). Delivery = min(own key-up, press + k (+δ)), k = longest combo candidate live on `l_mod` for that position at press time (the candidate set is fixed at press; the keymap resolves on the live layer at delivery, `keymap.c:651-654`).
  - Effective closing edge: **release + 130 − k** for a key still held at its deadline; **release + 130** for a key released earlier or with no `l_mod` combo.
  - Flo: LM1/RM1 (Shift, `entr`/`entr2` 16 ms) → the last ≈ 16 ms turn a held Shift into the base `&ak` letter (observed "t", parked to release + 260). LM4/RM4 (Ctrl, no `l_mod` combo) keep the full 130 (INFERRED from T-17-a3 + table).
  - It is the OFF-edge twin of (c) "Visibility to the next key".
- **Evidence**: T-18-g `[00:00:00.373,000] <dbg> zmk: set_layer_state: layer_changed: layer 26 state 0` → `[00:00:00.378,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=377` → `[00:00:00.378,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 13, binding name: flo,behavior-adaptive-key` → `[00:00:00.504,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x17 implicit_mods 0x00 explicit_mods 0x00`; T-18-b `[00:00:00.380,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 5, binding name: key_press`; T-18-fix-b-htm232 `[00:00:00.372,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 4 position: 5, binding name: hold_tap_mod` + `[00:00:00.372,000] … keycode 0xE0`, OFF `[00:00:00.373,000]`; T-18-b3 (key-up first) `[00:00:00.371,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 4 position: 5, binding name: hold_tap_mod`.
- **Confidence**: high (mechanism, LM1); medium (exact board edge).

### MR-12 — board margin is robust when the delivery is key-driven
- **Target**: MODEL (d) caveat "Nominal 1 ms margin at Δ = 11 with k2 = 0 can be eaten by sub-ms phase … ≈ 0.05 %".
- **Statement**: in the band 11 ≤ Δ < dA (A flushed by B's press), the layer's `K_MSEC(10)` (329 ticks = 10.04 ms) and B's `K_MSEC(11)` (362 ticks = 11.05 ms) are scheduled in the same handler → layer leads B by ≈ 1.01 ms regardless of phase. The sub-ms caveat applies only when A's delivery is timer-driven (Δ ≥ dA). Same 1 ms robust margin on the OFF side after a replace macro (⌫↑ at F+10.04 vs a re-captured hack-only key at F+11.05, T-21-a/b/c). SOURCE + arithmetic; unobservable on native.
- **Evidence**: T-05 native `[00:00:00.037,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 1` / `[00:00:00.038,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x0F …` (1 ms) + T-05 board-translation arithmetic; T-21-a `[00:00:00.089,000] set_layer_state: layer_changed: layer 1 state 0` / `[00:00:00.090,000] zmk_keymap_apply_position_state: layer_id: 0 position: 3, binding name: key_press`.
- **Confidence**: medium (board-only).

### MR-13 — near-miss combo: key 2 waits its own full timeout
- **Target**: MODEL (e) Combo tiers (acceptance bar) — consequence of R3.
- **Statement**: combo iff `ts2 − ts1 ≤ T − 1` (strict `>` at `combo.c:228`), proven at 16 and 30. A key 2 at gap ≥ T that belongs to the same combo starts a fresh set and is delivered only at `ts2 + T` (native +1) — a near-miss costs key 2 a full extra T (16 → +16, 30 → +30). Board: the bar is identical (integer timestamps); at gap = T key path vs rung is a sub-ms flip with the same output.
- **Evidence**: T-22-b `[00:00:00.032,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=32` → C re-captured → `[00:00:00.049,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=48` + `[00:00:00.049,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x06 …`; T-22-f `[00:00:00.091,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=90`; T-22-a/e (gap 15 / 29 fire).
- **Confidence**: high.

### MR-14 — captured keys re-enter the combo engine; bypass depends on what the decision emitted
- **Target**: MODEL (e) "captured keys delivered" (linger, htls, htm); T-17 reconciliation's generalisation.
- **Statement**
  - PROVEN: after any hold-tap decision each captured key is re-raised AT the hold-tap listener and passes the combo engine with the layer active then, deadlines anchored at its original timestamp (T-17-a, T-19-b). A deadline already past → `K_MSEC(<0)` = immediate flush in the same ms (T-19-b).
  - Whether it is captured again follows R8: if the decision emitted a non-modifier keycode (linger tap/hold `&bk`/`&kp`, R-thumb `&ak`) stamped ≥ 2 ms after the captured key's timestamp → quick tap → bypass (no capture line in T-13-b, T-15-d, T-16-a); if it emitted only `&mo` (htls HOLD) or a modifier (htm; modifiers don't update `last_tapped`) → re-captured (T-17-a, T-19-b).
  - Timing effect of a capture only when the captured key's deadline has not yet passed at the decision.
  - Status: T-15-d/T-13-b bypass cause INFERRED by elimination → proving test §7 (T-15-fix-b exists, never built).
- **Evidence**: T-19-b `[00:00:00.193,000] <dbg> zmk: position_state_down: combo: capturing position event 2` + `[00:00:00.193,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=129`; T-17-a `[00:00:00.062,000] <dbg> zmk: position_state_down: combo: capturing position event 5`; T-15-d `[00:00:00.123,000] <dbg> zmk: position_state_changed_listener: 3 bubble (no undecided hold_tap active)` → `[00:00:00.123,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 3, binding name: key_press` (no capture line).
- **Confidence**: high (re-entry); medium (bypass split).

---

## 3. 🟢 New facts

### NF-01 — native same-tick ordering: timers before position events
- **Target**: MODEL (a) same-thread guarantee; (c) "A key delivered at exactly D+10 is a same-tick ordering question"; (d) ⚖️ cells; CLAIMS T-07 expectation ("mock-timer-first → D").
- **Statement**
  - The kscan callback does only `k_msgq_put` + `k_work_submit(&msg_processor.work)` (`physical_layouts.c:147-160`) → a position event is a **later work item** than every delayable that expired on the same tick (all expiring timeouts submit FIFO, `work.c:810-828`, `sys_slist_append` `:277`; equal deadlines keep arming order, `timeout.c:125-131`).
  - Native consequences (all observed): layer-ON beats a same-tick key (T-07-d11 → HIT; T-23-e4 → HIT); combo rung beats a same-tick key (T-04-d12, T-10-a, T-22-c, T-22-fix-h); hold-tap term timer beats a same-tick release → HOLD (T-15-c); two timers on one tick run in arming order (T-12-b-d112: sticky OFF before the follower's rung → base).
  - Board: no shared 1 ms tick; order = which work item is submitted first at sub-ms phase; the msgq hop adds only µs → board ties stay sub-ms coin flips (INFERRED). Native tie outcomes must not be printed as board outcomes.
- **Evidence**: T-07-d11 `[00:00:00.022,000] <dbg> zmk: kscan_mock_work_handler_0: ev 2151416576 row 0 column 3 state 1` → `[00:00:00.022,000] <dbg> zmk: set_layer_state: layer_changed: layer 2 state 1` → `[00:00:00.022,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 3, position: 3, pressed: true`; T-04-d12 `[00:00:00.024,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=23` before `[00:00:00.024,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 3, position: 3, pressed: true`; T-15-c `[00:00:00.202,000] <dbg> zmk: decide_hold_tap: 9 decided hold-timer (tap-preferred decision moment timer)` before `[00:00:00.202,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 2, col: 1, position: 9, pressed: false`; T-12-b-d112 as MR-06; **undocumented** T-22-fix-h `[00:00:00.034,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=33` before `[00:00:00.034,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 3, position: 3, pressed: true`.
- **Confidence**: high (native); low (board bias) — do not claim a board direction.

### NF-02 — dead window after a replace macro
- **Target**: MODEL (c) (silent on replace macros); page AK timelines.
- **Statement**: the replace macro's ⌫↓ at F is the first keycode after the old `aksl` armed → consumes it; the old AK layer drops at ⌫↑ (F+10 board / F+11 native). The new AK layer (nested `&ak`) comes on only at F+40 / F+44. Keys delivered in (F+10, F+40] board / (F+11, F+44] native resolve on **base**; keys delivered in [F, F+10) still see the old AK layer.
- **Evidence** (prefix stripped by runner): T-21-a `[00:00:00.089,000] set_layer_state: layer_changed: layer 1 state 0` → `[00:00:00.090,000] zmk_keymap_apply_position_state: layer_id: 0 position: 3, binding name: key_press`; new layer `[00:00:00.122,000] set_layer_state: layer_changed: layer 3 state 1`; T-21-d `[00:00:00.108,000] zmk_keymap_apply_position_state: layer_id: 0 position: 3, binding name: key_press`.
- **Confidence**: high.

### NF-03 — raw `&kp` of the macro's own letter: not dropped, doubled, released early
- **Target**: CLAIMS E-71 ("out of order or dropped").
- **Statement**: `hid_listener` pre-releases an already-pressed keycode → the host sees two L key-downs (text "LLB"); the macro's own L↑ then releases the physically held follower key (≈ 295 ms before its key-up). Nothing dropped. Native `-95` on the pre-release report is transport noise.
- **Evidence**: T-21-g `[00:00:00.085,000] hid_listener_keycode_pressed: unregistering usage_page 0x07 keycode 0x0F since it was already pressed` → `[00:00:00.085,000] hid_listener_keycode_pressed: usage_page 0x07 keycode 0x0F …` → `[00:00:00.096,000] hid_listener_keycode_released: usage_page 0x07 keycode 0x0F …`.
- **Confidence**: high.

### NF-04 — raw `&kp` is not parked by `moAndBuffer`
- **Target**: MODEL (e) `moAndBuffer` "every `&ak`/`&bk`/morph delivered in (release, release+260) is emitted at release + 260".
- **Statement**: a raw `&kp` reached during the park is emitted at its delivery (press + combo hold), ≈ 100 ms before the queue resumes. INFERRED (not mixed-tested): a raw `&kp` during the park overtakes parked `&ak` output.
- **Evidence**: T-18-c `[00:00:00.402,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x09 implicit_mods 0x00 explicit_mods 0x00` (t+281; the same thumb release parks the queue to t+383, cf. T-18-a `[00:00:00.504,000]`).
- **Confidence**: high (not parked); INFERRED (overtaking).

### NF-05 — `htm` HOLD release double-unregisters the modifier
- **Target**: MODEL (e) `htm` bullet (silent).
- **Statement**
  - On key-up after a HOLD, `on_hold_tap_binding_released` calls `release_binding()` and then, because `hold-while-undecided` + `hold-while-undecided-linger`, `release_hold_binding()` again (`ht:642`, `:644-645`) → the mod is unregistered twice.
  - Alone: second release logs `<err> zmk: Tried to unregister modifier 0 too often` (no HID effect).
  - With another holder of the same mod (e.g. a same-mod sticky armed by an earlier `htm` tap, refcount 2): the HOLD release drops the count 2 → 0 → **the sticky mod is cancelled early**; the next key is unmodified; the sticky's own later release logs the error. PROVEN.
  - Board: same code; `<err>` only visible with logging.
- **Evidence**: T-19-b `[00:00:00.225,000] <err> zmk: Tried to unregister modifier 0 too often`; **undocumented** T-19-fix-c-hold-refcount2: `[00:00:00.255,000] <dbg> zmk: decide_hold_tap: 5 decided hold-timer (tap-preferred decision moment timer)` → at key-up `[00:00:00.325,000] <dbg> zmk: zmk_hid_unregister_mod: Modifier 0 count: 1` then `[00:00:00.325,000] <dbg> zmk: zmk_hid_unregister_mod: Modifier 0 count: 0` / `Modifier 0 released` / `Modifiers set to 0x00` → C `[00:00:00.543,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x06 implicit_mods 0x00 explicit_mods 0x00` + `[00:00:00.543,000] <dbg> zmk: zmk_hid_implicit_modifiers_press: Modifiers set to 0x00` → `[00:00:00.577,000] <err> zmk: Tried to unregister modifier 0 too often`.
- **Confidence**: high.

### NF-06 — sticky Shift survives the 260 ms park and is consumed by the parked key
- **Target**: MODEL (e) "Page 'late' scenario … 'A' shifted".
- **Statement**: the `skm` Shift armed before the park stays in the report through it; the parked `&ak`'s queued kp↓ consumes it; LSHIFT↑ in the same ms as that key's queued kp↑, **before** the `aksl` layer ON. Confirms "A" shifted at release + 260 (native +262).
- **Evidence**: T-18-f `[00:00:00.483,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x04 implicit_mods 0x00 explicit_mods 0x00` + `[00:00:00.483,000] <dbg> zmk: zmk_hid_implicit_modifiers_press: Modifiers set to 0x02` → `[00:00:00.494,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0xE1 …` → `[00:00:00.494,000] <dbg> zmk: set_layer_state: layer_changed: layer 2 state 1`.
- **Confidence**: high.

### NF-07 — 0 ms R tap = two distinct HID reports in one ms
- **Target**: MODEL (a) HID note; CLAIMS T-14 purpose (host-drop).
- **Statement**: press and release are two separate `zmk_endpoints_send_report` calls in the same ms, in order; nothing merged inside ZMK. USB: `usb_hid.c:139` sem (30 ms) forces one host poll between them (SOURCE). BLE: two `bt_gatt_notify_cb`, may share a connection event (INFERRED). Host acceptance → hardware (T-24).
- **Evidence**: T-14-a: two `zmk_endpoints_send_report: usage page 0x07` lines at `[00:00:00.102,000]`, one after `[00:00:00.102,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x0B …`, one after `[00:00:00.102,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0x0B …`.
- **Confidence**: high (ZMK side).

### NF-08 — keymap releases on the press-time layer snapshot
- **Target**: MODEL (a)/(c) "layer resolved NOW".
- **Statement**: `zmk_keymap_active_behavior_layer[position]` is written at delivery (`keymap.c:651-654`); the key-up resolves on that snapshot (`:665-666`) even after the layer turned off. Harmless for `&ak`/`&bk` (empty release branches); lets an `htm` resolved on `l_mod` finish its tap after `l_mod` OFF.
- **Evidence**: T-12-b-d110 `[00:00:00.211,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 19 position: 21, binding name: flo,behavior-buffered-key` (layer 19 off since `[00:00:00.188,000]`); T-18-b2 key-up at t+270 decided tap on layer 4 (`[00:00:00.391,000] <dbg> zmk: decide_hold_tap: 3 decided tap (tap-preferred decision moment key-up)`).
- **Confidence**: high.

### NF-09 — combo ladder does not drift
- **Target**: MODEL R4.
- **Statement**: each re-arm is `K_MSEC(first_timeout − k_uptime_get())` (`combo.c:417`), i.e. relative to the absolute deadline → every rung at `deadline + 1` native / `deadline + δ_i` board, never cumulative.
- **Evidence**: T-11-a pos 4: `[00:00:00.797,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=2 timestamp=796`, `[00:00:00.802,000] … remaining_candidates=1 timestamp=801`, `[00:00:00.804,000] … remaining_candidates=0 timestamp=803`.
- **Confidence**: high.

### NF-10 — hack cost for a real 2-key combo = T − Δ
- **Target**: MODEL headline 🕰️ (quantifies it).
- **Statement**: a 2-key combo completed at Δ < 11 under the hack fires at `t + T (+δ)` instead of `t + Δ` → extra latency T − Δ (10 ms + δ at Δ = 6 for 16 ms). Hack off → fires at completion.
- **Evidence**: T-09-a `[00:00:00.023,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=22` + `[00:00:00.023,000] … keycode 0x06` (t+17 native); T-09-c `[00:00:00.012,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x06 …` (t+6).
- **Confidence**: high.

### NF-11 — hack delay on hack-only hold-taps moves only the creation
- **Target**: MODEL (e) "the combo delay is NOT added" to terms.
- **Statement**: on hack-only positions the hack delays hold-tap creation by 11 ms (+1) but not the term (T+100 / T+90 from the press) nor a tap released after creation (output at key-up either way).
- **Evidence**: T-11-c pos 9 `[00:00:03.331,000] <dbg> zmk: on_hold_tap_binding_pressed: 9 new undecided hold_tap` vs T-11-d `[00:00:03.319,000] <dbg> zmk: on_hold_tap_binding_pressed: 9 new undecided hold_tap`, Y at +61 in both; T-15-c created `[00:00:00.113,000]`, decided `[00:00:00.202,000]` (t+101 not t+112).
- **Confidence**: high.

### NF-12 — `htm` tap followed by a captured key: sticky release ordered before the key
- **Target**: MODEL (e) htm "key-up after a captured key".
- **Statement**: the captured key is re-captured by the combo engine and reaches the keymap after the sticky's press handler ran → the sticky treats it as its consumer → mod held until that key's UP (not the "act like a normal key" path).
- **Evidence**: T-19-c `[00:00:00.144,000] <dbg> zmk: on_sticky_key_binding_pressed: 5 new sticky_key` → `[00:00:00.144,000] <dbg> zmk: position_state_down: combo: capturing position event 2` → `[00:00:00.144,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x06 …` → `[00:00:00.165,000] … keycode 0xE0` released with `Modifier 0 released`.
- **Confidence**: high.

### NF-13 — key buffered with the `htls` thumb also forces HOLD (and maps on `l_mod`)
- **Target**: MODEL (e) htls "(also for keys that were buffered with it and flushed together)" → now PROVEN; plus board note.
- **Statement**: Δ = 6 key flushed with the thumb at the hack rung → thumb delivered, hold-tap created, re-raised key captured by the hold-tap → `hold-interrupt` in the same ms → key resolves on `l_mod`. Board Δ = 10: the hold-tap listener runs before the combo listener, so the R9 strand does not apply to the key the hold-tap captures (INFERRED).
- **Evidence**: T-17-d `[00:00:00.018,000] <dbg> zmk: decide_hold_tap: 10 decided hold-interrupt (hold-preferred decision moment other-key-down)` → `[00:00:00.018,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 4 position: 3, binding name: hold_tap_mod`.
- **Confidence**: high (native).

---

## 4. 🟡 Spec-arithmetic (CLAIMS slips; MODEL unchanged)

| id | test / sub-case | spec said | observed (verbatim) | cause |
|---|---|---|---|---|
| SA-01 | T-02-a; T-06-b; T-23-a/b | follower HID↓ + layer at t+22 | `[00:00:00.029,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 1` (T-02) = t+23; T-23-a `[00:00:00.028,000] … keycode 0x17` = t+23 | spec added +1 to the rung but not to the 10 ms queue tick; native `D = t + max(11,k) + 1`, layer `D + 11`; board T+21 |
| SA-02 | T-06-c | A t+7, layer t+18, O t+38 | `[00:00:00.012,000] … keycode 0x04`, `[00:00:00.023,000] … layer 1 state 1`, `[00:00:00.043,000] … keycode 0x12` = t+6/17/37 | spec put key 2 at t+7; key-driven flush has no +1 |
| SA-03 | T-07 | Δ = 5 → D at t+6 | `[00:00:00.010,000] … Row: 0, col: 3` (t = .005) = t+5 | reading of Δ |
| SA-04 | T-15 | `PRESS(2,1,99/100/101)` for releases +99/+100/+101; interrupt t+81/t+91 | needed n = 98/99/100; interrupt Y↓ `[00:00:00.123,000]` = t+82, Y↑ `[00:00:00.134,000]` = t+93 | mock gap = ms + 1 |
| SA-05 | T-16-b control | X at t+112 | `[00:00:00.125,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x1B …` = t+113 | term timer +1 native (board t+112+δ) |
| SA-06 | T-18-a | B delivered t+274; HID at `[t+382]` | `[00:00:00.394,000] <dbg> zmk: release_pressed_keys: combo: releasing position event 1` = t+273 (B's key-up, 11 ms hold); `[00:00:00.504,000] … keycode 0x05` = t+383 | mock gap ms+1 puts B↑ before the hack rung; park = two chained `K_MSEC(130)` → +2 native (board release + 260 + δ1 + δ2) |
| SA-07 | T-20-a | K at ~t+362 | `[00:00:00.414,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x0E …` = t+363 | mock gap +1 on the 10 ms B hold |
| SA-08 | T-23-c | C at t+1 | `[00:00:00.006,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x06 …` = t+0 | no combo on LM4 without the hack; no mechanism for +1 |
| SA-09 | T-21-a/b | E-key at +31 triggers the replace; follower resolves on layer 1 | `[00:00:00.078,000] release_pressed_keys: combo: releasing position event 4` (t+47, flushed by D's press); D on `layer_id: 0` at `[00:00:00.090,000]` | spec ignored R4 (E is in S16/Q18, k = 18) and NF-02 |
| SA-10 | T-22-b | gap 16 → `remaining_candidates=0 timestamp=t+16` at `[t+17]` | `[00:00:00.032,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=32` = `[t+16]`, key path | native key-first at gap = T (HW-09); the predicted timer line appears at gap 17 / alone |
| SA-11 | T-10-a | W only at `[t+117]` | `[00:00:00.028,000] … keycode 0x1A` = t+16 | spec moved Flo's example onto R1 without a longer sibling (MR-04) |

---

## 5. ⚙️ Harness / wording

| id | kind | statement | evidence |
|---|---|---|---|
| HW-01 | harness | Mock `ms = 0` → next event in the **same ms** (`K_NO_WAIT`), not +1; RIG's "gap = ms + 1" holds only for ms ≥ 1 → **1 ms gaps are not producible** (0, 2, 3, …). Explains why T-08-fix-rel1 tested `T_B = T_rel` (not −1) and why T-07-fix-d11-rev ran Δ = 10, not 11 (its reversed-order goal was never tested). | T-08-fix-boundary-rel1 (`PRESS(0,1,0)`): `[00:00:00.012,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 1, position: 1, pressed: true` then `[00:00:00.012,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 0, position: 0, pressed: false`; rel2 (`PRESS(0,1,1)`) release at `[00:00:00.014,000]`; T-07-fix-d11-rev (my run) `[00:00:00.042,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 1, position: 1, pressed: true` then `[00:00:00.042,000] <dbg> zmk: kscan_mock_work_handler_0: ev 590336 row 0 column 2 state 0`, key 2 at `[00:00:00.052,000]` |
| HW-02 | harness | `remaining_candidates=` is printed **before** the position filter (`combo.c:430` then `:431`) → counts include candidates the new key will drop. | T-10-a `[00:00:00.024,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=2 timestamp=24` (Q18 only survives) |
| HW-03 | harness | Timer-driven filter lines print the deadline, prefix = deadline + 1; key-driven lines print the key's own timestamp = prefix. | T-22-d `[00:00:00.118,000] … timestamp=117`; T-22-a `[00:00:00.030,000] … remaining_candidates=1 timestamp=30` |
| HW-04 | harness | Native key-first at gap = T / Δ = dA (key at t+T, rung at t+T+1); board = sub-ms flip; delivery times identical. | T-05-d16 `[00:00:00.032,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=32`; T-22-b same; **undocumented** T-22-fix-g (non-member key) `[00:00:00.032,000] … remaining_candidates=0 timestamp=32` + `[00:00:00.032,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x07 …` |
| HW-05 | wording | Hold-tap log strings are status words: `decided hold-interrupt (…)`, `decided hold-timer (…)`, `decided tap (…)`, `decided tap (tap-preferred decision moment quick-tap)`. | T-17-a `[00:00:00.062,000] <dbg> zmk: decide_hold_tap: 10 decided hold-interrupt (hold-preferred decision moment other-key-down)`; T-16-b `[00:00:00.125,000] <dbg> zmk: decide_hold_tap: 9 decided hold-timer (tap-preferred decision moment timer)` |
| HW-06 | harness | A 0 ms nested tap still logs `Processing next queued behavior in 10ms` between H↓ and H↑ (nested loop scheduled the tick; outer loop drains). | T-14-a `[00:00:00.102,000] <dbg> zmk: behavior_queue_process_next: Processing next queued behavior in 10ms` between the 0x0B press/release lines |
| HW-07 | harness | `hid_listener_keycode_*` prints the event's own `explicit_mods`; a held/sticky mod shows only as `Modifiers set to 0x0N` (report byte). | T-18-d `[00:00:00.381,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x09 implicit_mods 0x00 explicit_mods 0x00` + `[00:00:00.381,000] <dbg> zmk: zmk_hid_implicit_modifiers_press: Modifiers set to 0x02` |
| HW-08 | wording | `htm` tap end logs a `kp_released 0xE0` (refcount 2 → 1) although the report byte never drops. On `l_mod` the sticky Shift is `htm → skm` (ignore-modifiers), not `skms`. | T-19-a `[00:00:00.113,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0xE0 …` + `[00:00:00.113,000] <dbg> zmk: zmk_hid_unregister_mod: Modifier 0 count: 1` |
| HW-09 | wording | "no `capturing position event N`" must read "none after the re-raise": key 2's own press is captured into the live hack set. | T-04-d9 `[00:00:00.018,000] <dbg> zmk: position_state_down: combo: capturing position event 3`; T-02-a `[00:00:00.012,000] … capturing position event 1` |
| HW-10 | harness | Queue-driven keycodes log `position 0`; combo-press timestamp ("press stamped t") is never log-observable. Replace-macro `&macro_release &kp LSHFT/RSHFT` with no shift held logs `<err> … too often` (no HID effect); native `-95` on pre-release reports. | T-09-a `[00:00:00.023,000] <dbg> zmk: on_keymap_binding_pressed: position 0 keycode 0x70006`; T-21-a `<err> zmk: Tried to unregister modifier 1 too often` at `[.100]` |
| HW-11 | wording | T-23 spec mixed two `l_akL` followers: LT4 = `&bk G` (k2 = 0, the timings used), LB3 = `&bk L` (the binding named). | T-23-d3 `[00:00:00.038,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 12 position: 0, binding name: flo,behavior-buffered-key` + `keycode 0x0A` |
| HW-12 | wording | R2 hack-off idiom must be `/ { combos { /delete-node/ combo_ak_consistency_hack; }; };` (real node has no label). | T-23 corrections list; `-nohack` `zephyr.dts` has 0 hack nodes |

---

## 6. ✅ MODEL statements CONFIRMED verbatim (mark PROVEN)

| MODEL statement (section) | test(s) |
|---|---|
| 🧱 Lone key held for its LONGEST candidate: 11 / 16 / 18 ms; not a flat 11; hack adds latency only to hack-only positions | T-11-a/b/c/d (all 12 R1 positions), T-12-a |
| ⏱️ `&ak` = kp↓ at D, one 10 ms tick: kp↑ + AK layer ON + sticky armed; gone at D+110 | T-12-a (native +17/+28/+129), T-11-a, T-22-d |
| 🧨 Two `&ak` keys ≤ 9 ms apart leave at key 1 + 11, key 2 on base; mechanism = quick-tap bypass (R8) — *precondition: share only the hack (MC-01)* | T-02-a + control T-02-c, T-04-d9/d10 (native ≤ 10), T-06-b, T-23-a/b, T-23-d4 |
| 🪤 R9 CANCELING strand (re-capture inside the handler, no timer until next event) | T-02-c (`&ak` key 1), T-03 (`&kp` key 1), T-10-d |
| ✅ 11 ≤ Δ < dA: A at Δ, layer at Δ+10, B at Δ + max(11,k2), margin max(11,k2) − 10 ≥ 1 | T-05 (Δ = 11/13/15/16), T-04-d11, T-23-d3 (L@13, layer@24, G@25 native) |
| ✅ dA ≤ Δ: A at dA by the ladder, B fresh | T-04-d12, T-06-a, T-12-b-d110 |
| (d) native: now_flush = T_A+12 → bypass Δ ≤ 10; Δ = 11 key-first HIT | T-04-d10/d11, T-16-c/d |
| (d) Hack ON Δ ≤ 9 board HID `A↓@11, A↑@21, B↓@21, B↑@31` (native 12/23/23/34) | T-02-a |
| (d) Hack OFF, k2 = 0: MISS ≤ k1+9 (board); k2 > 0: HIT (for non-shared pairs) | T-02-b, T-07-d5/d6, T-23-e3; T-06-c (k2 = 30), T-23-c |
| (d) Examples L(16)→G(0)@13 and C(0)→P(16) hack-off | T-23-d3, T-23-c |
| 🕰️ Combo completed under the hack fires at its own deadline or next event; 11 ≤ Δ < T with a single survivor fires at Δ | T-09-a/a2/b/c, T-10-b/f |
| 🧵 `moAndBuffer`: layer OFF at release + 130, queue parked to release + 260, parked `&ak`/`&bk` emitted in order at the park end | T-18-a/a2/e/f/g (native +131/+262) |
| 🎯 Timestamps never move: hold-tap terms, sticky windows, combo deadlines count from the original timestamp | T-15-c, T-16-b, T-17-c, T-19-b (term 130 from press), T-17-b2/T-19-d (sticky), T-17-a4 (combo deadline at key ts) |
| R1 candidates fixed at first key from highest active layer | T-17-a/a4, T-18-b |
| R2 strict `>` (`combo.c:228`): 2nd key at exactly ts1 + T is OUT; acceptance `ts2 − ts1 ≤ T − 1` (16 and 30) | T-22-a/b/e/f, T-04-d11, T-05-d16 |
| R2 a key sharing nothing is captured, then `cleanup()` flushes all | T-04-d11, T-05, T-06-c |
| R3 re-raised key starts a fresh set anchored at its own timestamp | T-04-d11, T-05, T-22-b, T-23-d6 |
| R4 ladder: MIN armed, lone key leaves at longest deadline | T-11 |
| R5 element 0 RELEASE (skips hold-tap), others RAISE, original timestamps, press order | T-02-a, T-05, T-17-d (re-raised key hits the hold-tap) |
| R6 any release flushes the whole buffer; fired-combo behaviour released on the FIRST key up (either key), 2nd up swallowed | T-08 (a–d), T-09-a/a2, T-10-a, T-18-a |
| R7 only candidates[0] tested; ≥ 2 alive → marked, fires at ladder end / next event | T-10-b/e/f, T-09-a |
| R8 quick-tap bypass; `last_tapped` = last **non-modifier** keycode | T-02-c (flip with −100), T-03 vs T-03-bk, T-19-b (modifier doesn't count → re-captured) |
| (c) Visibility: key flushed in the same burst as key 1 resolves before D+10 → base | T-02-a, T-13-a |
| (c) Consumption: first keycode DOWN after arming stops the timer, pins until that keycode's UP (after HID); `&ak` follower chains gaplessly (kp↑ → old OFF → new ON, same tick) | T-12-b/c, T-20-a/b/c, T-05, T-06-b |
| (c) Position-0 collision moot: old layer released by consumption, `0 new sticky_key` | T-12-c |
| (c) native offsets: delivery T + max(11,k) + 1, layer D + 11, off D + 112 | T-12-a, T-11, T-22-d |
| (c) `&ak` release phase empty, holding never repeats | T-02-a (`starting: 7, count: 0`), T-12-a |
| (c) R thumb 0 ms tap, layer ON at decision, captured key re-raised onto `l_akR` (now PROVEN; see MR-08 addition) | T-13-b/d, T-14-a/c |
| (e) Linger: term from original timestamp, combo delay not added; ≤ T+100 TAP, ≥ T+101 HOLD, exactly 100 TAP on native; captured keys never decide | T-15-a/b/c/d/e |
| (e) Linger forced TAP after `&ak` within 9 ms (native ≤ 10) — now PROVEN (MR-09 completes it) | T-16-a/c |
| (e) `htls`: alone → `l_mod` at T + 90 (+δ), hack not added; other key DOWN → HOLD immediately; tap alone → `skms` LSHIFT; buffered keys also force HOLD | T-17-a/a2/a3/a4/b/c/d, T-18-a |
| (e) `htm` tap: `skm` count 2 → 1, mod stays until next non-mod key's UP or 1500; captured keys delivered with the mod down | T-19-a/b/c/d |
| (e) Page late scenario: `l_mod` off at 250, RM1 at 260 → `&ak A`, shifted, HID at 380 (native 252/383) | T-18-f |
| (g) Refuted D T7b ("R thumb then held key → not adapted") | T-13-b, T-13-d |
| (g) Refuted B §4.4 "queue parked 130" (it is 260) | T-18-a |
| (g) Refuted E simulator Case B (`d2 = Δ + max(k2,11)` for Δ < 11) | T-02-a, T-04-d9/d10, T-06-b |
| CLAIMS E-98 `REPLACE_CHAR_WITH_BIGRAM` = 8 queue items + 4 nested | T-21-a |
| CLAIMS E-124 key 2's own 30 ms combo ignored with the hack at Δ = 6, honoured without | T-06-b/c |

---

## 7. 🔬 Still INFERRED → test that would prove it

| claim | status | proving test |
|---|---|---|
| Re-raised captured key after a linger TAP bypasses the combo engine by quick-tap (T-15-d, T-13-b) | INFERRED by elimination | Build/run the existing but never-built `tests/ak-truth/T-15-fix-b-hack-noquicktap` (hack `require-prior-idle-ms = <(-1000)>`): expect `capturing position event 3` after `Releasing key position event for position 3` (+ immediate flush, deadline past) |
| MC-01 board band (MISS Δ ≤ S−2, STALL S−1) | INFERRED | hardware T-24 (L→LB3 rolls at 13–16 ms) |
| MC-01 2-key shared pairs output the combo (Z/Tab) | INFERRED | R2: M (LT2) → LT3 at Δ = 5/13/20, hack on/off; D (LB1) → LB0 same |
| MC-01 H (RM4) → RM2 band Δ ≤ 17 native | INFERRED | R2: RM4 then RM2 at Δ = 13/17/18 |
| MC-02 RM1 (`entr2`) Shift +16 after `htls` interrupt | INFERRED (table) | R2: LH1 held + RM1 at +31 → expect `keycode 0xE1` at t+48 |
| MR-02 which Flo layer 0–24 positions are raw `&kp` | not enumerated | static scan of D-config §6 |
| MR-03 QUEUED-state refusal | SOURCE (outcome observed) | none needed beyond T-10-fix; instrumentation would need a debug log in `update_timeout_task` |
| MR-03 stall on hack-off layers (nav/num) | INFERRED | R1 hack-off with S16/Q18 on layer 0: E, then G at +5 (drops S16) → expect no rung until E↑ |
| MR-05 / NF-01 board TIE direction | not observable | hardware only |
| MR-06 board window edge (110 = race) | INFERRED | hardware T-24 |
| MR-09 board Δ = 10 linger → stranded → HOLD | INFERRED (R9) | hardware T-24a |
| MR-11 exact edge for LM4/RM4 = 130 | INFERRED | R2: LH1 hold-release, LM4 pressed at release + 125, held 30 → expect LCTRL |
| MR-12 robust ≈ 1.01 ms board margin | SOURCE | hardware only |
| MR-07 `htm` home-row mod pins the AK layer | INFERRED | R2: `&ak` letter, then LH1 hold + LM4 held across +100 → expect layer pinned to LM4↑ |
| NF-04 raw `&kp` overtakes parked `&ak` | INFERRED | R1: `htls` hold/release, `&ak B` at +140, `&kp D` at +160 → expect D↓ before B↓ |
| NF-07 host accepts a 0 ms tap | hardware | T-24 |
| Δ = 10 board STALL with `&ak` key 1 (headline 🪤) | INFERRED (native shows bypass) | hardware T-24a |
| CLAIMS E-20 (M→T at Δ = 5 without the hack) | not covered | R2: T-23-a events with the hack deleted |

---

## 8. 📂 Undocumented reconciliation probes (found, used above)

| case dir (`zmk/app/tests/ak-truth/…`) | log | what it shows | used in |
|---|---|---|---|
| `T-07-fix-d10` | `investigation/corrA-logs/T-07-fix-d10.raw.log` (my run, md5 `fd97f40a0bc72169d1e0a6242f3409b2`) | hack off, k1 = 0, Δ = 10 → D on base, layer at t+11 → MISS | MR-05 |
| `T-07-fix-d11-rev` | `corrA-logs/T-07-fix-d11-rev.raw.log` (md5 `03d4fc8a85f66cc08636b5be0d94bb62`) | intended reversed timeout order at Δ = 11; `ms = 0` gave gap 0 → ran Δ = 10 (MISS); goal untested | HW-01 |
| `T-08-fix-boundary-rel1` / `-rel2` | `results/…raw.log` (md5 `9544fc5d…` / `afbe1cdd…`) | `T_B = T_rel` → re-capture + dupe cleanup; `T_rel = T_B + 2` → bypass | MR-01, HW-01 |
| `T-13-fix-e-park` / `-f-nopark` | `corrA-logs/…raw.log` (md5 `df7fdf64ec26c0f4dca07ea664ce1955` / `e9e42d4c0292fc7a96afd0c01b547094`) | follower at thumb-up + 5 → HID at thumb-up + 11 (parked); at + 15 → immediate | MR-08 |
| `T-15-fix-a-bk-follower` | `results/…raw.log` (md5 `d5b61c1c…`) | captured `&bk D` → D↓ after Y↑ (queued) | MC-03 |
| `T-15-fix-b-hack-noquicktap` | **never built** (no build dir, no snapshot) | — | §7 |
| `T-19-fix-a-nocombo` | `results/…raw.log` (md5 `8b123e20…`) | htm without rig combos → 0xE0 at t+0 | MC-02 |
| `T-19-fix-b-hold-refcount2` | `results/…raw.log` (md5 `96348d29…`) | mis-timed (2nd press held 101 ms → TAP): 2nd tap replaces the 1st sticky, C still Ctrl'd; no error | — (superseded by fix-c) |
| `T-19-fix-c-hold-refcount2` | `results/…raw.log` (md5 `9b9cc668…`) | sticky Ctrl armed, htm HOLD release drops count 2 → 0, C plain, later `<err> … too often` | NF-05 |
| `T-22-fix-g-gap16-nonsib` / `-h-gap17-nonsib` | `results/…raw.log` (md5 `87a18c6b…` / `1c009ae4…`) | non-member key at gap = T → key-path expiry; at T+1 → timer first | HW-04, NF-01 |
