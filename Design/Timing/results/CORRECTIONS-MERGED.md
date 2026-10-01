# 🧾 CORRECTIONS-MERGED: A + B corrections to MODEL.md / CLAIMS.md

> Inputs: `results/CORRECTIONS-A.md` (54 items: MC/MR/NF/SA/HW) · `results/CORRECTIONS-B.md` (53 items: B/H/S/W).
> Merger re-checked every single-source item, and single-source sub-claims inside agreed items, against the raw logs in `results/*.raw.log` and `results/CORR-B/*.raw.log`.
> Extra corroboration neither extractor cited: `PAIRS.md` and the sweep logs `results/S-*.raw.log` (21 R2 cases on the 7 shared or near-boundary pairs, run 2026-10-01). They turn several INFERRED rows in item 1 into PROVEN on native.
> Status tags: **PROVEN(T-xx)** = native_posix log · **SRC** = file:line · **INF** = inferred.
> Board = native − 1 ms per relative timer crossed (+δ). An `&ak` delivered by a combo rung crosses two timers.

## 🎯 Result first

| section | count |
|---|---|
| ✅ AGREED by both extractors (one merged statement each) | 42 |
| ⬆️ SINGLE-SOURCE promoted to AGREED after log check | 9 (A: MR-02, NF-10, NF-11, NF-12, NF-13, HW-12 · B: B-25, S-10, S-11) |
| ❌ SINGLE-SOURCE dropped | 0 |
| ⚠️ FLAGGED (not resolved here) | 5 |
| **Final AGREED total** | **51** |

- Single-source **sub-claims** inside agreed items were checked as well. All passed, and each is tagged ✔︎ in its row.
- The FLAGGED items are three substance differences (board tie bias, RM1+RM3 stall exit, dead-window bound) and two kind mismatches (correction vs refinement on a headline claim).

---

## ✅ 1. AGREED

### 🧨 Model corrections (page must change)

**1 · Shared-combo pairs break theorem (d)**: A MC-01 · B B-01 + B-02
- Statement:
  - (d) holds only when trigger A and follower B share **no** real combo.
  - If they share one (S = longest timeout among the real combos that contain both), B's press does not empty A's set. Both keys leave at A's rung T_A+S (native +1).
  - B is re-raised with its old timestamp and bypassed (R8) iff T_B ≤ now_flush − 2 → base layer.
  - Hack ON and hack OFF behave identically. For Δ ≤ 9 the flush is at T_A+S, not T_A+11.
  - Native: MISS Δ ≤ S−1, HIT from Δ = S.
  - Board (INF): MISS Δ ≤ S−2, STALL at Δ = S−1 (R9 strand → delivered at next event, adapted if the layer is still alive), HIT from S.
  - CLAIMS contradictions 2 and 3 hold only for non-shared pairs. "Hack rescues 12 / breaks all 23 for Δ ≤ 10" must exclude these pairs.
- 6 compiled pairs:

| pair | shared combo | S | native band | status |
|---|---|---|---|---|
| L (LB2) → LB3 | magicCloseQuitCb, 3-key | 16 | MISS ≤ 15, HIT 16 | PROVEN(T-23-d5/d6/e5, S-L_LB3-d14/d17) |
| H (RM4) → RM2 | capsWord, 4-key | 18 | MISS ≤ 17, HIT 18 | ⬆️ PROVEN(S-H_RM2-d16/d17/d18, d17-nohack). Both extractors had it INF |
| M (LT2) → LT3, W (LT3) → LT2 | typeZ, 2-key | 16 | combo **Z** for Δ ≤ 15 (hack on and off), HIT 16 | ⬆️ PROVEN for M→LT3 (S-M_LT3-d5/d14/d15/d15-nohack/d16). W→LT2 INF. Both extractors had it INF |
| D (LB1) → LB0, V (LB0) → LB1 | tab, 2-key | 16 | combo Tab for Δ ≤ 15 | INF (PAIRS.md) |

- Evidence:
  - A: T-23-e5 `[00:00:00.030,000] … remaining_candidates=0 timestamp=29` → `layer_id: 0 position: 21` → `[00:00:00.041,000] … keycode 0x0A`; T-23-d6 `[00:00:00.049,000] … layer_id: 12 position: 21, binding name: flo,behavior-buffered-key`.
  - B: T-23-d2 `[00:00:00.017,000] … remaining_candidates=1 timestamp=16` then `[00:00:00.022,000] … remaining_candidates=0 timestamp=21`; T-23-e1 (hack off Δ = 20) `[00:00:00.057,000] … layer_id: 12 position: 21`.
  - Merger: S-H_RM2-d17 `[00:00:00.036,000] … layer_id: 0 position: 17, binding name: flo,behavior-adaptive-key`; S-H_RM2-d18 `[00:00:00.055,000] … layer_id: 9 position: 17`; S-M_LT3-d15 `[00:00:00.030,000] … keycode 0x1D`; S-M_LT3-d16 `[00:00:00.049,000] … layer_id: 13 position: 1, binding name: flo,behavior-buffered-key`.
- Note: A adds "board STALL cell MISS ~5 %". B is silent on this. Not a conflict.

**2 · `htm` mod goes down at delivery; `htls` interrupt re-enters the combo engine on `l_mod`**: A MC-02 · B B-04
- Statement:
  - The `htm` mod goes down at the key's **delivery** (hold-tap creation, hold-while-undecided). Delivery = press + the longest combo candidate live on the then-highest layer (+δ board, +1 native), or the key-up if that comes earlier.
  - Reword: "never absent between press and consumption" → "between delivery and consumption".
  - `htls` hold-interrupt: decision + `&mo l_mod` happen in the interrupting key's ms. The interrupting key is then re-raised (ht:235) and passes combos again with `l_mod` highest.
  - On Flo's `l_mod` only LM1 (`entr <13 14>`) and RM1 (`entr2 <15 16>`) have a live combo. Shift lands at ts_key+16 (native +17). LM4/LM3/LM2/RM2/RM3/RM4 → mod in the decision ms. RM1 is INF.
- Evidence:
  - A and B both cite: T-17-a4 `[00:00:00.062,000] … capturing position event 13` → `[00:00:00.079,000] … keycode 0xE1`; T-17-a3 `[00:00:00.062,000] … keycode 0xE0`.
  - T-19-a `[00:00:00.081,000] … 0xE0` vs T-19-fix-a-nocombo `[00:00:00.062,000] … 0xE0`.

**3 · Linger TAP: captured raw `&kp` follower emits at the decision, before tap↑**: A MC-03 · B B-03
- Statement:
  - Only queued followers (`&ak`/`&bk`/macros/morph) wait for the next queue tick after tap↑ (decision+10+δ board, +11 native).
  - A captured raw `&kp` is emitted synchronously at the decision instant → report order Y↓ D↓ Y↑ D↑ (overlap, text unchanged).
  - HOLD path: hold binding, then captured keys, in the same instant. Board order is the same.
- Evidence (both): T-15-d `[00:00:00.123,000] … keycode 0x1C` → `[00:00:00.123,000] … keycode 0x07` → `[00:00:00.134,000] … released … 0x1C`; T-15-f / T-15-fix-a-bk-follower `[00:00:00.134,000]`.

**4 · Behaviour queue FIFO is per queued item (nested replace macro)**: A MC-04 · B B-15
- Statement:
  - REPLACE_CHAR_WITH_BIGRAM = 8 outer + 4 nested items. The nested `&ak` enqueues its steps only when its outer item runs.
  - Board / native timeline (F = replace delivery):

| step | board | native |
|---|---|---|
| ⌫↓ | F | F |
| ⌫↑ + L↓ | F+10 | F+11 |
| L↑ + no-op Shift releases + ak↓ | F+20 | F+22 |
| B↓ | F+30 | F+33 |
| B↑ + new AK layer ON | F+40 | F+44 |
| new AK layer OFF | F+140 | F+145 |

  - A `&bk` follower delivered in (F, F+20) lands **before** B ("LDB"). One delivered after F+20 lands after B.
  - Raw `&kp` emits at delivery, ahead of all queued output (PROVEN T-21-d/h).
- Evidence: T-21-c `[00:00:00.111,000] … 0x07` before `[00:00:00.122,000] … 0x05`; T-21-f `[00:00:00.107,000] … 0x0F` before B `[00:00:00.118,000]`; T-21-e B `[00:00:00.114,000]` then D `[00:00:00.125,000]`.
- ⚠️ Kind differs (A correction / B refinement) → see FLAG F4.

**5 · AK-layer pin by modifiers (CLAIMS contradiction 16 / E-60)**: A MR-07 · B B-06 + B-14 + B-26
- Statement:
  - Only a keycode, modifiers included, whose DOWN is delivered **after** aksl arms consumes or pins the layer.
  - A Shift already held when the AK letter is typed does not pin: the layer times out at D+110 (native D+112).
  - A key down before arming neither consumes the layer nor releases it with its UP (T-07-d5 timeout at `[00:00:00.117,000]`).
  - While a held modifier pins the layer, **every** follower resolves on the AK layer until the modifier's UP ("aKK"). A follower's own UP does not release a Shift pin.
  - An `skms` pin ends at the next letter's key-up (at most one adapted letter).
  - Board pin condition (INF): modifier delivered (after its own 11–18 ms combo wait or hold-tap decision) before ≈ D_A+110+δ.
  - INF: a held `htm` mod pins the same way.
  - MODEL (c) wording "first keycode DOWN after arming" is exact. MODEL (a) "or pinned by a held modifier" and (c) "a held/sticky Shift pins" need the after-arming condition.
  - ✔︎ B-only sub-claim checked: `ignore-modifiers` removes the pin. T-20-b: Shift `[00:00:00.119,000] … 0xE1` yet `[00:00:00.180,000] … layer 1 state 0`.
- Evidence: T-20-d `[00:00:00.211,000] … layer 1 state 0` (Shift up only `[00:00:00.346,000]`); T-20-e second K `[00:00:00.446,000] … layer_id: 1 position: 1`, OFF `[00:00:00.477,000]`; T-20-c `[00:00:00.377,000]`.
- ⚠️ Kind differs for CLAIMS 16 (A refinement / B correction) → see FLAG F5.

### 🔧 Model refinements

**6 · R6 release-while-buffered with an `&ak` key 1**: A MR-01 · B B-09
- Statement:
  - The release flushes all at T_rel, key-driven, with no +1.
  - `&ak` key 1's kp↓ is queue-stamped at T_rel, so key 2 (T_B ≤ T_rel−2) is bypassed (R8). It resolves on base at T_rel with no re-capture and no dupe cleanup.
  - Key 2's HID↓ queues behind key 1's tap (native T_rel+11, board T_rel+10+δ) → MISS "AB", and key 2's keycode consumes key 1's layer.
  - Re-capture + dupe cleanup applies only to a raw `&kp` key 1 or to T_B ≥ T_rel−1. The outcome is the same.
  - ✔︎ A-only sub-claim checked: releasing key 2 first also flushes key 1. T-08-b `[00:00:00.016,000] … Row: 0, col: 1 … pressed: false` → `releasing position event 0` → `layer_id: 0 position: 0`.
- Evidence: T-08-a `[00:00:00.016,000] … reraising position event 1` → `layer_id: 0 position: 1, binding name: flo,behavior-adaptive-key`, B `[00:00:00.027,000]`; T-08-fix-boundary-rel1/rel2 (both).

**7 · R10 stall mechanism**: A MR-03 · B B-07
- Statement:
  - `k_work_schedule` is refused while the combo delayable is DELAYED, QUEUED or CANCELING. Only RUNNING may re-arm (work.c:967). This leaves a phantom `timeout_task_timeout_at` (combo.c:417-418).
  - When a later key removes the candidate that owns the armed deadline and a later-deadline candidate survives, the old timer early-returns (combo.c:473-475). The set is timer-less until the next position event.
  - QUEUED case: a fresh MIN deadline already in the past → K_MSEC(<0) = K_NO_WAIT → a second re-raise is refused → stranded.
  - Exits:
    1. A press completing the only survivor → fires at that press.
    2. A press completing candidates[0] with ≥ 2 alive → fires at the first release.
    3. A press sharing no live candidate, or after all deadlines → flush at that press.
    4. Any release → flush.
  - Hack-on band: 2nd key at Δ ≥ 11 and before the shortest survivor's deadline. Hack-off (nav/num) layers stall likewise (INF).
  - Flo: RM1, RM3@+12, RM2 → delWord only at the first release (capsWord alive).
- Evidence: T-10-e `[00:00:00.129,000] … 0x1A`; T-10-c no line in [.025]–[.128]; T-10-fix-lateF-d13 `[00:00:00.037,000] … 0x08`, G/F stranded to `[00:00:00.138,000]`.
- ⚠️ RM1+RM3 without RM2: exit wording differs → see FLAG F2.

**8 · Out-of-order 3-key combo stall needs a live sibling**: A MR-04 · B B-08
- Statement:
  - A completed out-of-order combo waits for the first release only if ≥ 2 candidates are alive at completion. As the sole survivor it fires at the completing press (R7).
  - Flo's RM1–RM3 example keeps capsWord alive, so MODEL's Flo claim stands. The general wording needs the condition.
- Evidence: T-10-a `[00:00:00.028,000] … remaining_candidates=1 timestamp=28` + `… 0x1A` (t+16); T-10-e `[00:00:00.129,000] … 0x1A`.

**9 · Hack-off, k2 = 0 boundary (native table)**: A MR-05 · B B-05 + B-18
- Statement:
  - Board is unchanged: MISS ≤ k1+9, sub-ms TIE at k1+10, HIT ≥ k1+11.
  - Native: layer ON at D_A+11 (D_A = 0 for k1 = 0, k1+1 otherwise). The tie at Δ = D_A+11 resolves HIT (layer first).
  - k1 = 0: MISS ≤ 10, HIT ≥ 11. k1 = 16: MISS ≤ 27, HIT ≥ 28.
  - The parenthetical in CLAIMS contradiction 14 ("no exact-ms tie in the 2-key model") is wrong. MODEL's ⚖️ cells were right for board.
- Evidence: T-07-d11 `[00:00:00.022,000] … layer 2 state 1` precedes `… Row: 0, col: 3 … pressed: true` → `layer_id: 2 position: 3`; T-07-fix-d10 `[00:00:00.020,000] … layer_id: 0 position: 3` then `[00:00:00.021,000] … layer 2 state 1`; T-23-e4 `[00:00:00.056,000]`.

**10 · AK window upper edge**: A MR-06 · B B-16
- Statement:
  - Native (16/16 pair): adapted through Δ = 111. At Δ = 112 the earlier-armed sticky OFF timer runs first in the same ms → base.
  - Board (INF): Δ ≤ 109 adapted, Δ = 110 sub-ms race, Δ ≥ 111 base. The OFF path crosses 3 timers, the follower 1.
  - The native window is 2 ms wider. D_A+110−max(11,k2) is the race cell, not a safe HIT. Page numbers must name the target.
  - A consuming follower keeps the layer on past D+110 until its kp↑ (B).
- Evidence: T-12-b-d111 `[00:00:00.178,000] … layer_id: 19 position: 21`; T-12-b-d112 `[00:00:00.179,000] … layer 19 state 0` → `remaining_candidates=0 timestamp=178` → `layer_id: 0 position: 21`.
- Confidence: A high / B medium (board side INF).

**11 · R-thumb `blt_akR`: PROVEN + queue park**: A MR-08 · B B-10
- Statement:
  - Tap → H↓, H↑, `l_akR` ON in the thumb-up handler. The captured key is re-raised after that onto `l_akR` (T7b refuted).
  - The nested process_next schedules the 10 ms delayable → queue parked to thumb-up+10+δ (native +11). Any queued output resolved in that window emits HID↓ only at the tick. The leftover `&ak↑` is a no-op at the tick.
  - A follower pressed after the window (+15) emits in its own ms (T-13-fix-f-nopark `[00:00:00.077,000]`).
  - ✔︎ A-only sub-claim checked: the `l_akR` window is decision → decision+100+δ (native +101) with no +10. T-14-c ON `[00:00:00.102,000] … layer 17 state 1`, OFF `[00:00:00.203,000] … layer 17 state 0`.
  - ✔︎ A-only sub-claim checked: a hold-tap whose tap is a direct `&ak` behaves like a normal `&ak`. The captured key resolves on base and consumes/wastes the layer. T-13-c `[00:00:00.093,000] … layer_id: 0 position: 1, binding name: flo,behavior-adaptive-key`, `[00:00:00.104,000] … layer 3 state 1` then `… keycode 0x05`.
- Evidence: T-13-b `[00:00:00.093,000] … layer 3 state 1` → `Releasing key position event for position 1` → `layer_id: 3 position: 1` → `[00:00:00.104,000] … 0x17`; T-13-fix-e-park `[00:00:00.067,000] … layer_id: 3 position: 1` → `[00:00:00.073,000] … 0x17` (A and B both ran it).

**12 · Linger key forced TAP after an `&ak` alpha**: A MR-09 · B B-11
- Statement:
  - PROVEN native. A linger key ≤ 10 ms after an `&ak` alpha is re-raised at D, bypasses the combo engine, and is decided "tap (… quick-tap)" at D. It never lingers.
  - The `&bk` Y queues behind the `&ak`: Y↓ at D+10+δ (native +11), right after A↑ + AK layer ON. Y↑ at D+20. The AK layer lives only (D+10, D+20]. The term timer fires as a no-op.
  - Combo bypass and the quick-tap flip happen at the same Δ.
  - Native Δ = 11 → re-captured, normal HOLD at T_L+100+δ. Board Δ ≤ 9 forced TAP. Board Δ = 10 (INF) → stranded to the next event, then HOLD (term expired).
  - ✔︎ A-only sub-claim checked: with a `&kp` tap, Y↓ lands at the decision and the AK layer goes unconsumed (overlapped roll). T-16-fix-a-kptap `[00:00:00.018,000] … 0x1C`, `[00:00:00.029,000] … layer 2 state 1`, `[00:00:00.130,000] … layer 2 state 0`.
- Evidence: T-16-a `[00:00:00.018,000] … decided tap (tap-preferred decision moment quick-tap)`, `[00:00:00.029,000] … 0x1C`, `[00:00:00.040,000] … layer 2 state 0`; T-16-c-d10 `[00:00:00.022,000]`; T-16-d-d11 `[00:00:00.123,000] … decided hold-timer`.

**13 · moAndBuffer closing edge**: A MR-11 · B B-12
- Statement:
  - A key pressed inside the 130 ms buffer resolves on `l_mod` iff its DELIVERY precedes layer OFF (release+130+δ, native +131).
  - Delivery = min(own key-up, press + k), with k = the longest combo live on `l_mod` for that position.
  - Effective edge = release+130−k for a held key, release+130 if released earlier or if there is no `l_mod` combo.
  - Flo: LM1/RM1 Shift (k = 16) lose the last ≈ 16 ms. They resolve on base as the `&ak` letter, parked to release+260 (LM1 → "t"). LM4/RM4 keep 130 (INF).
- Evidence: T-18-g `[00:00:00.373,000] … layer 26 state 0` → `[00:00:00.378,000] … layer_id: 0 position: 13` → `[00:00:00.504,000] … 0x17`; T-18-fix-b-htm232 `[00:00:00.372,000] … layer_id: 4 position: 5, binding name: hold_tap_mod`.

**14 · Key-driven 1 ms margin is phase-independent**: A MR-12 · B B-17
- Statement:
  - For 11 ≤ Δ < dA, the layer's K_MSEC(10) (329 ticks) and B's K_MSEC(11) (362 ticks) are armed in the same handler → board margin ≈ 1.01 ms at any phase.
  - The 0.05 % sub-ms caveat applies only to Δ ≥ dA.
  - The same ~1 ms holds after a replace macro (⌫↑ vs a re-captured key; B-22 says the same).
  - SRC arithmetic, board-only.
- Evidence: T-05 `[00:00:00.037,000] … layer 1 state 1` / `[00:00:00.038,000] … 0x0F`; T-21-a `[00:00:00.089,000]` / `[00:00:00.090,000]`. Confidence medium in both.

**15 · Combo acceptance bar + near-miss cost**: A MR-13 · B B-28
- Statement:
  - Combo iff ts2 − ts1 ≤ T−1 (combo.c:228 strict `>`). PROVEN at T = 16 and 30.
  - A same-combo key 2 at gap ≥ T starts a fresh set, delivered at ts2+T (+1 native).
  - A non-member key at gap T bubbles at once (B; T-22-fix-g `[00:00:00.032,000] … 0x04` + `… 0x07`, checked).
  - Board bar is identical.
- Evidence: T-22-b `[00:00:00.032,000] … timestamp=32`, then `[00:00:00.049,000] … timestamp=48` + `… 0x06`; T-22-f `[00:00:00.091,000] … timestamp=90`.

**16 · Captured keys re-enter the combo engine after any hold-tap decision**: A MR-14 · B B-24
- Statement:
  - Each captured key is re-raised at the hold-tap listener (ht:232-235) with its original timestamp. It passes R1 on the then-active layer, with the deadline anchored at the original timestamp (a past deadline → immediate flush).
  - It is re-captured unless R8 bypasses it. Bypass happens when the decision emitted a non-modifier keycode ≥ 2 ms after the captured key's timestamp (linger tap, R-thumb H↓).
  - A modifier-only or layer-only decision (`htm` HOLD, `htls` `&mo`) → re-capture.
- ⬆️ The bypass cause is now **PROVEN**. A had it "inferred by elimination", confidence medium. B's own case CB-T15-noquicktap was checked: keymap sets `require-prior-idle-ms = <(-1000)>`, and the log shows `[00:00:00.123,000] … capturing position event 3` → `remaining_candidates=0 timestamp=93` → `… keycode 0x07`. T-15-d at the same point has no capture line (`[00:00:00.123,000] … layer_id: 0 position: 3, binding name: key_press`).
- Evidence (A): T-19-b `[00:00:00.193,000] … capturing position event 2` + `timestamp=129`; T-17-a `[00:00:00.062,000] … capturing position event 5`.

### 🆕 New facts

**17 · Native same-tick order: timer before key**: A NF-01 · B B-18 (+ B-05)
- Statement:
  - The kscan callback only does `k_msgq_put` + `k_work_submit` (physical_layouts.c:147-160). The key's work item is queued behind every delayable expiring on the same tick, and equal deadlines run in arming order (timeout.c:125-131).
  - Native consequences, all observed:
    - Layer ON beats a same-tick key (T-07-d11, T-23-e4 → HIT).
    - A combo rung beats a same-tick key (T-04-d12, T-22-fix-h).
    - The hold-tap term beats a same-tick release → HOLD (T-15-c `[00:00:00.202,000] … decided hold-timer` before `… Row: 2, col: 1 … pressed: false`, checked).
    - Two timers on one tick run in arming order (T-12-b-d112 → base).
  - Do not print native tie outcomes as board outcomes.
- Evidence: T-07-d11 `[00:00:00.022,000] … kscan_mock_work_handler_0` → `layer 2 state 1` → `Row: 0, col: 3`; T-04-d12 `[00:00:00.024,000] … timestamp=23` before `Row: 0, col: 3`.
- ⚠️ Board-tie direction differs → see FLAG F1.

**18 · Replace-macro dead window**: A NF-02 · B B-22
- Statement:
  - ⌫↓ at F is the first keycode after the old aksl armed → it consumes that layer. The old layer drops at ⌫↑ (board F+10 / native F+11).
  - The nested `&ak`'s new layer comes ON at F+40 / F+44. Keys delivered between those points resolve on base.
  - Queue items: 8 outer + 4 nested (E-98 confirmed, B).
- Evidence: T-21-a `[00:00:00.089,000] … layer 1 state 0` → `[00:00:00.090,000] … layer_id: 0 position: 3, binding name: key_press`, new layer `[00:00:00.122,000] … layer 3 state 1`; T-21-d `[00:00:00.108,000] … layer_id: 0 position: 3`.
- ⚠️ Upper-bound bracket and the "[F, F+10) sees old layer" sub-claim → see FLAG F3.

**19 · Raw `&kp` of the macro's own letter is pre-released, not dropped**: A NF-03 · B B-23
- Statement:
  - `hid_listener` pre-releases the already-pressed keycode, so the host sees two L key-downs ("LLB"). The macro's L↑ releases the physically held follower early.
  - ✔︎ A-only sub-claim checked: about 295 ms early. Macro L↑ `[00:00:00.096,000]` vs follower Row up `[00:00:00.391,000]`.
  - ✔︎ B-only sub-claim checked: a different raw letter overtakes even the macro's own letter. T-21-h M `[00:00:00.074,000] … 0x10` before L `[00:00:00.085,000] … 0x0F`.
  - The native −95 on the pre-release report is transport noise.
- Evidence: T-21-g `[00:00:00.085,000] … unregistering usage_page 0x07 keycode 0x0F since it was already pressed` → `… 0x0F` → `[00:00:00.096,000] … released 0x0F`.

**20 · Park scope + park numbers**: A NF-04 + SA-06 · B B-13 + S-06
- Statement:
  - The moAndBuffer park holds only queue-routed output (`&ak`, `&bk`, macros, morph). A raw `&kp` emits at its normal delivery (T-18-c `[00:00:00.402,000] … 0x09`, t+281, ≈ 100 ms before park end).
  - "Raw `&kp` overtakes parked `&ak`" is INF (not mixed-tested).
  - Park end = native release+262 (two chained K_MSEC(130), +1 each), board release+260+δ1+δ2. Layer OFF = native release+131, board release+130+δ1.
  - ✔︎ B-only sub-claim checked: every parked `&ak` emits HID↓ at park end, whenever it reached the keymap. T-18-a2 delivered `[00:00:00.395,000]`, HID `[00:00:00.504,000]`, same as T-18-a.
  - B also notes (INF, SRC): the park is anchored to the central's stamp of the thumb-up (left thumb adds debounce + BLE).
- Evidence: T-18-a `[00:00:00.242,000] … in 130ms` → `[00:00:00.373,000] … layer 4 state 0` → `[00:00:00.504,000] … 0x05`.

**21 · `htm` HOLD double release cancels a co-held same mod**: A NF-05 · B B-20
- Statement:
  - HOLD key-up calls release_hold_binding twice (ht:642, ht:644-645).
  - Alone: `<err> Tried to unregister modifier 0 too often`, no HID effect.
  - With a second holder (a same-mod sticky armed by an earlier `htm` tap) the count drops 2→0 → the sticky is cancelled early → the next key is unmodified, and the sticky's later release logs the error.
  - Same code on board.
- Evidence: T-19-b `[00:00:00.225,000] <err> …`; T-19-fix-c-hold-refcount2 `[00:00:00.325,000] … Modifier 0 released` → `[00:00:00.543,000] … 0x06` + `Modifiers set to 0x00` → `[00:00:00.577,000] <err> …`.

**22 · Sticky Shift survives the park**: A NF-06 · B B-21
- Statement:
  - It is consumed by the parked `&ak`'s queued kp↓ (report 0x02) and released in the same ms as that key's kp↑, before the key's aksl layer ON.
  - "A" is shifted at release+262 native. Board ≈ 380 in MODEL's page "late" scenario (release 120 + 260; MODEL.md:224, checked).
- Evidence: T-18-f `[00:00:00.483,000] … 0x04` + `Modifiers set to 0x02` → `[00:00:00.494,000] … released 0xE1` → `layer 2 state 1`.

**23 · 0 ms R tap = two HID reports**: A NF-07 · B B-30
- Statement:
  - Press and release are separate reports in one ms. ZMK merges or drops nothing.
  - USB: usb_hid.c:139 30 ms semaphore forces a host poll between them (SRC). BLE may share a connection event (INF).
  - Host acceptance is hardware-only.
- Evidence: T-14-a two `zmk_endpoints_send_report: usage page 0x07` at `[00:00:00.102,000]` around `… pressed 0x0B` / `… released 0x0B`. Confidence A high / B medium.

**24 · Layer chosen at delivery; release dispatched on the press-time layer**: A NF-08 · B B-27
- Statement:
  - The binding layer is chosen when the event reaches the keymap, after any combo or hold-tap hold.
  - The release resolves on the layer stored at press, even after that layer is OFF (keymap.c:651-654, 665-666).
  - Combo holds can therefore move a key across a layer edge.
- Evidence: T-12-b-d110 `[00:00:00.211,000] … layer_id: 19 position: 21` (layer 19 OFF since `[00:00:00.188,000]`); T-18-b2 `[00:00:00.391,000] … decided tap` after `[00:00:00.373,000]` OFF; T-18-b `[00:00:00.380,000] … layer_id: 0 position: 5`.

**25 · Combo ladder does not drift**: A NF-09 · B B-29
- Statement: each re-arm is K_MSEC(first_timeout − k_uptime_get()) (combo.c:417), so each rung fires at deadline+1 native / deadline+δ_i board.
- Evidence: T-11-a pos 4 `[00:00:00.797,000] … timestamp=796`, `[00:00:00.802,000] … timestamp=801`, `[00:00:00.804,000] … timestamp=803`.

### 🧮 Spec arithmetic (CLAIMS slips, MODEL unchanged)

| # | topic | merged statement | A | B | evidence |
|---|---|---|---|---|---|
| 26 | rung-delivered `&ak` chain | Native D = t+max(11,k)+1. kp↑ / layer ON / next queued keycode at D+11 → follower t+23, not t+22. Board t+21. A key-delivered `&ak` at D = Δ → layer at Δ+11. | SA-01 | S-01, H-03 | T-02-a `[00:00:00.018,000] … in 10ms` → `[00:00:00.029,000] … layer 1 state 1`; T-23-a `[00:00:00.028,000] … 0x17` |
| 27 | key-driven deliveries carry no +1 | T-06c A t+6 / layer t+17 / O t+37 · T-23c C t+0 · T-07 Δ = 5 → D at t+5 | SA-02, SA-03, SA-08 | S-02 | T-06-c `[00:00:00.012,000]`/`[.023]`/`[.043]`; T-23-c `[00:00:00.006,000] … 0x06`; T-07-d5 `[00:00:00.010,000]` |
| 28 | T-15 mock gap | PRESS(2,1,98/99/100) for +99/+100/+101. Interrupt Y↓ t+82, Y↑ t+93 | SA-04 | S-04 | T-15-d `[00:00:00.123,000]` / `[00:00:00.134,000]` |
| 29 | T-16 control | HOLD X at t+113 native (term t+112 +1), board t+112+δ. Forced-TAP Y↓ t+23 (B adds) | SA-05 | S-05 | T-16-b `[00:00:00.125,000] … 0x1B`; T-16-a `[00:00:00.029,000]` |
| 30 | T-18(a) | B held 11 ms → delivered by its key-up t+273 (held ≥ 12 → rung t+274). HID↓ at release+262 = t+383 | SA-06 | S-06 | T-18-a `[00:00:00.394,000] … releasing position event 1`, `[00:00:00.504,000] … 0x05` |
| 31 | T-20(a) | K at t+363 (B↑ at t+352 +10 +1). Rig fix: akA pos 11 = `&trans` (B; ✔︎ T-20.md:25 + keymap.diff) | SA-07 | S-07 | T-20-a `[00:00:00.414,000] … 0x0E` |
| 32 | T-21 | The E-key is held by its S16/Q18 (k = 18) candidates. The replace starts at D's press t+47 or its own rung t+50, not t+31. The follower lands in the dead window on base. `&bk` and `&kp` spec builds give identical logs (B) | SA-09 | S-08 | T-21-a `[00:00:00.078,000] … releasing position event 4`; `[00:00:00.090,000] … layer_id: 0 position: 3` |
| 33 | T-10(a) | Stock R1: G leaves Q18 as the lone candidate → F's press fires W at t+16. The stall needs a longer sibling or no completion | SA-11 | S-03 | T-10-a `[00:00:00.028,000] … 0x1A` |

### 🔬 Harness / log reading / wording

| # | topic | merged statement | A | B | evidence |
|---|---|---|---|---|---|
| 34 | `filter_timed_out_candidates` line origin | Key path prints the key's own timestamp at its own ms. The timer path prints the deadline at deadline+1 (native). The count is printed **before** the position filter (combo.c:430 then :431). At gap = T native, the key beats the +1-late rung → logged from the key path, `[t+16] timestamp=t+16`. Board: sub-ms flip, same output. Kinds: A SA-10 = spec-arithmetic, B H-01 = harness; same content | SA-10, HW-02, HW-03, HW-04 | H-01 | T-22-b `[00:00:00.032,000] … timestamp=32`; T-22-d `[00:00:00.118,000] … timestamp=117`; T-10-a `[00:00:00.024,000] … remaining_candidates=2 timestamp=24`; T-05-d16 `[00:00:00.032,000]` |
| 35 | mock ms = 0 | `ZMK_MOCK_*(…, 0)` → K_NO_WAIT, a 0 ms gap. "gap = ms+1" holds only for ms ≥ 1. T-08-fix-rel1 tested T_B = T_rel, and T-07-fix-d11-rev tested Δ = 10, so its reversed-order goal stays untested | HW-01 | H-02 | T-08-fix-boundary-rel1 `[00:00:00.012,000]` press + release; T-07-fix-d11-rev `[00:00:00.042,000]` ×2 |
| 36 | hold-tap status strings | `decided hold-interrupt (…)`, `decided hold-timer (…)`, `decided tap (… key-up / quick-tap)` | HW-05 | W-01 | T-17-a `[00:00:00.062,000]`; T-16-b `[00:00:00.125,000]` |
| 37 | nested 0 ms tap logs a 10 ms wait | `Processing next queued behavior in 10ms` appears between H↓ and H↑ in the same ms (the tick parks the queue, item 11) | HW-06 | W-03 | T-14-a / T-13-b `[00:00:00.102,000]` / `[00:00:00.093,000]` |
| 38 | explicit_mods | `hid_listener_*` prints the event's own mods (0x00). A held or sticky mod appears only as `Modifiers set to 0x0N` | HW-07 | W-04 | T-18-d `[00:00:00.381,000]` |
| 39 | `htm` tap end | `kp_released 0xE0` IS logged (refcount 2→1) and the report stays 0x01. The `l_mod` Shift is `htm` → `skm` (ignore-modifiers), not `skms` (A; ✔︎ D-config.md:323-326) | HW-08 | W-05 | T-19-a `[00:00:00.113,000] … released 0xE0` + `Modifier 0 count: 1` |
| 40 | "no capturing" assertions | Key 2's own press IS captured into the hack set. Assert "no capture after the re-raise" | HW-09 | W-02 | T-04-d9 `[00:00:00.018,000]`; T-02-a `[00:00:00.012,000]` |
| 41 | log noise | Queue-invoked keycodes (incl. combo `&bk`, aksl) log `position 0`; use the queue `Invoking` line. The combo-press timestamp is never log-observable (combo.c:349). Replace-macro `&macro_release &kp LSHFT/RSHFT` with no Shift held → `<err> Tried to unregister modifier 1/5 too often` + `Unable to release keycode`, no HID effect, not the item-21 bug. Native −95 = transport noise | HW-10 | W-08, W-06, B-31 | T-09-a `[00:00:00.023,000] … position 0 keycode 0x70006`; T-21-a `[00:00:00.100,000] <err>`; T-21-g `[00:00:00.085,000] … (-95)` |
| 42 | `l_akL` followers | LT4 (X key) = `&bk G` (k2 = 0, MODEL's example) · LB3 (G key) = `&bk L` (shares magicCloseQuitCb, item 1). Specify both. The page must not call LB3 "L→G" | HW-11 | S-09, W-07 | T-23-d3 `[00:00:00.038,000] … layer_id: 12 position: 0` HIT vs T-23-d1 MISS at Δ = 13 |

---

## ⬆️ 2. SINGLE-SOURCE: verified and promoted to AGREED

| # | id | statement (as kept) | merger's log check |
|---|---|---|---|
| 43 | A MR-02 | A position-stamped (raw `&kp`) key 1 never makes key 2 a quick tap (T1−1 > T2 is false for every Δ ≥ 0). A key 2 flushed in the hack-rung burst is re-captured inside the handler → R9 strand until the next press/release. A queue-stamped key 1 (`&bk`) with the same events → R8 bypass. Native PROVEN. "Both targets" = SRC/INF for board | ✔︎ T-03 `[00:00:00.018,000] … reraising position event 1` → `[00:00:00.018,000] … capturing position event 1`, next delivery `[00:00:00.073,000] … keycode 0x05` at D↑ · T-03-bk `[00:00:00.018,000] … layer_id: 0 position: 1, binding name: flo,behavior-adaptive-key` → `[00:00:00.029,000] … 0x05` · T-10-d `[00:00:00.024,000] … capturing position event 6` → nothing until `[00:00:00.122,000] … releasing position event 6` |
| 44 | A NF-10 | Hack cost for a real 2-key combo completed at Δ < 11 is T − Δ: it fires at t+T (+δ) instead of t+Δ. Hack off → fires at completion | ✔︎ T-09-a key 1 `[00:00:00.006,000]`, fires `[00:00:00.023,000] … remaining_candidates=0 timestamp=22` + `… 0x06` (t+17) · T-09-c `[00:00:00.012,000] … 0x06` (t+6) |
| 45 | A NF-11 | On hack-only positions the hack delays hold-tap **creation** by 11 ms (+1 native), but not the term (counted from press) nor a tap released after creation | ✔︎ T-11-c Row `[00:00:03.319,000]`, created `[00:00:03.331,000]` vs T-11-d created `[00:00:03.319,000]`; both decided tap + Y at `[00:00:03.380,000]` · T-15-c press `[00:00:00.101,000]`, created `[00:00:00.113,000]`, `decided hold-timer` `[00:00:00.202,000]` (= press+101) |
| 46 | A NF-12 | After an `htm` TAP with a captured key, that key is re-captured and reaches the keymap after the sticky's press handler. The sticky treats it as its consumer → mod held until that key's UP | ✔︎ T-19-c `[00:00:00.144,000] … 5 new sticky_key` → `… capturing position event 2` → `… 0x06` pressed; `[00:00:00.165,000]` C up → `… released 0xE0` → `Modifier 0 released` |
| 47 | A NF-13 | A key buffered with the `htls` thumb by the hack (Δ = 6) is re-raised into the new hold-tap at the flush → hold-interrupt in the same ms → resolves on `l_mod`. Board Δ = 10: hold-tap listener runs before the combo listener → no R9 strand for it (INF) | ✔︎ T-17-d `[00:00:00.018,000] … 10 new undecided hold_tap` → `reraising position event 3` → `10 capturing 3 down event` → `decided hold-interrupt` → `layer_id: 4 position: 3, binding name: hold_tap_mod` |
| 48 | A HW-12 | On R2 the hack node has no label. Use `/ { combos { /delete-node/ combo_ak_consistency_hack; }; };` | ✔︎ zephyr.dts `combo_ak_consistency_hack {` (no label) · T-23-c/e1 keymaps line 91 use the node-path form · all 6 `T-23-*-nohack` builds: 0 occurrences in zephyr.dts |
| 49 | B B-25 | In a bypass MISS, key 2's base keycode (dequeued right after aksl↓) is the first keycode after arming → it consumes key 1's AK layer, which drops at key 2's kp↑. Key 1's layer serves no key. Same for a hold-tap captured key resolved on base (T-13-c) and for ⌫ in a replace macro (item 18) | ✔︎ T-06-b `[00:00:00.029,000] … layer 1 state 1` + `… 0x0B` → `[00:00:00.040,000] … released 0x0B` → `layer 1 state 0` · T-02-a same at `[00:00:00.040,000]` · T-08-a `[00:00:00.027,000]` ON → `[00:00:00.038,000]` OFF |
| 50 | B S-10 | R1 pos 5 sits in `l_all` S16/Q18, live on layer 4, so the key is combo-held 18 ms on the mod layer (LCTRL t+50 / F at 240 / 0xE0 at t+19). Spec derivation slip. Consequences are in items 2 and 13 | ✔︎ T-17-a `[00:00:00.079,000] … remaining_candidates=1 timestamp=78` → `[00:00:00.081,000] … remaining_candidates=0 timestamp=80` → `5 new undecided hold_tap` |
| 51 | B S-11 | T-08(a) spec described the raw-`&kp` re-capture path with HID at t+10. With an `&ak` key 1 the path is the bypass, and B↓ is at t+21 (queue). "Immediate, on base" holds (item 6) | ✔︎ T-08-a key 1 `[00:00:00.006,000]`, `[00:00:00.016,000] … reraising position event 1`, `[00:00:00.027,000] … keycode 0x05` |

- ❌ Dropped: none. Every single-source item and sub-claim was supported by its cited log, or by MODEL/D-config arithmetic for B-21's ≈ 380 and B-13's anchoring note (INF as stated).

---

## ⚠️ 3. FLAGGED (not resolved)

**F1 · Board same-tick ties: neutral or timer-biased?** (A NF-01 vs B B-18)
- A says:
  - The msgq hop adds only µs, so board ties "stay sub-ms coin flips (INFERRED)".
  - Confidence low for any board bias. "Do not claim a board direction."
- B says:
  - Board ties at k1+10 "remain sub-ms races; the same msgq hop biases toward the timer (INF)".
- Why it matters:
  - Affects every board ⚖️ cell: hack-off k1+10, window edge Δ = 110, combo gap = T, forced-TAP Δ = 10.
  - The page either prints "≈ 50/50" or "leans to the timer outcome (HIT / HOLD / base)".
  - Both are INF and native cannot test it. Hardware only.

**F2 · RM1 + RM3 (no RM2) at +11…15: what ends the stall?** (A MR-03 vs B B-08)
- A says: "both held until **next event**" (INF). This matches the exit list in A and in B-07: a press sharing no live candidate flushes at that press.
- B says (B-08): "both letters are held **until the first release** instead of leaving at t+18".
- Why it matters:
  - The page's Flo example for the stall.
  - If the next press flushes, a fast typist sees the letters at the next keystroke. If only a release flushes, they appear at the first key-up.
  - B-07's own exit (3) suggests B-08 is shorthand, but neither extractor ran this case. A one-off R2 case would settle it: RM1, RM3 +12, then an unrelated press.

**F3 · Replace-macro dead window: upper bound and the early sub-window** (A NF-02 vs B B-22)
- A says:
  - Keys delivered in **(F+10, F+40]** board / **(F+11, F+44]** native resolve on base (closed upper bound).
  - Adds: keys delivered in [F, F+10) still see the old AK layer.
- B says:
  - **(F+10, F+40)** (open upper bound). No native bracket given, and nothing about [F, F+10).
- Why it matters:
  - The endpoint is the tie cell where the new layer comes ON at the same instant as the key.
  - Per item 17, native runs the layer timer before a same-ms key → a key-driven delivery at exactly F+44 would see the **new** layer, contradicting A's closed bracket for that case. Board = sub-ms.
  - A's [F, F+10) sub-claim has no direct test: T-21-f delivers a follower inside (F, F+20) but checks ordering, not the layer it resolved on. Not verified from logs.

**F4 · Kind mismatch: "ONE queue" headline** (A MC-04 vs B B-15)
- A says: **model-correction**. The headline "every macro key … serialised through ONE queue" predicted the wrong order: a `&bk` follower lands before B.
- B says: **model-refinement**. The headline is right but incomplete (FIFO is per item).
- Substance (timeline, F+20 boundary, raw `&kp` overtaking) is identical (item 4).
- Why it matters: decides whether the page's queue headline is rewritten (correction) or caveated (refinement).

**F5 · Kind mismatch: modifier pin / CLAIMS 16** (A MR-07 vs B B-06 + B-14)
- A says: **model-refinement** of MODEL (a) "or pinned by a held modifier", (c) "a held/sticky Shift pins", and CLAIMS 16 / E-60.
- B says: CLAIMS 16 / E-60 is a **model-correction** ("pinned by any held modifier" is wrong). MODEL (c) "first keycode DOWN after arming" is exact. MODEL (c) Consumption needs only a refinement (B-14).
- Substance is identical (item 5).
- Why it matters: whether the page's pin sentence (MODEL (a) diagram note) is treated as wrong (pre-held Shift shown as pinning) or as under-specified.
