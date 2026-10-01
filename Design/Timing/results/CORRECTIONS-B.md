# 🧾 CORRECTIONS-B — what T-02 … T-23 changed or added relative to MODEL.md (extractor B)

> Input read in full: MODEL.md, CLAIMS.md (contradictions + test plan), RIG.md offsets, T-02.md … T-23.md incl. every deviation list and every Reconciliation section.
> Also read (no runner write-up exists for them): raw logs `T-08-fix-boundary-rel{1,2}`, `T-15-fix-a-bk-follower`, `T-19-fix-{a,b,c}-*`, `T-22-fix-{g,h}-*`. Timestamped logs I generated from already-built exes (read-only run): `results/CORR-B/T-07-fix-d10.raw.log`, `T-07-fix-d11-rev.raw.log`, `T-13-fix-e-park.raw.log`, `T-13-fix-f-nopark.raw.log`. One new case of my own: `zmk/app/tests/ak-truth/CB-T15-noquicktap/` → `results/CORR-B/CB-T15-noquicktap.raw.log` (PASS, auto-accepted).
> Status tags: **PROVEN(T-xx)** = observed in a native_posix log · **SRC** = source-backed (file:line) · **INF** = inferred, not executed. Board = native minus 1 ms per relative timer crossed (an `&ak` key delivered by a combo timer crosses two: rung, then the 10 ms queue tick), plus δ ∈ (0.03, 1.05] ms per timer.
> Kinds: **model-correction** (rule predicted the wrong outcome) · **model-refinement** (right but incomplete) · **new-fact** (MODEL never said it) · **spec-arithmetic** (CLAIMS/spec slip; MODEL unchanged) · **harness** · **wording**.

---

## 🎯 Result first — what actually changes in MODEL

- ❌ **Shared-combo pairs break the theorem's headline claims** (B-01, B-02). A trigger/follower pair that shares a real combo of timeout S misses for Δ ≤ S−1 (native) **with or without the hack**. Six compiled pairs do this (L→LB3 observed).
- ❌ **Linger TAP path**: a raw `&kp` captured key is emitted at the decision instant, *before* `tap↑`. Only queued followers wait for the next tick (B-03).
- ❌ **Callum `htls` interrupt / `htm` mod-down**: the interrupting key re-enters the combo engine on `l_mod`. LM1/RM1 Shift (in `entr`/`entr2`) lands 16 ms after the decision; `htm` mods are down from *delivery*, not press (B-04).
- ❌ **CLAIMS-only**: contradiction 14 ("no exact-ms tie") and contradiction 16 / E-60 ("pinned by any held modifier") are wrong (B-05, B-06).
- 🔧 **Refinements** with numbers: native same-tick order (timer beats key), R10 sharpened, R6 with an `&ak` key 1, R-thumb queue park, forced-TAP timeline + bands, Callum closing edge, park scope, AK-layer pin rules, nested-macro FIFO, window upper edge tie, key-driven margin.
- 🆕 **New facts**: sticky expiry anchored at press, double modifier release (proven to cancel a sticky Ctrl), sticky Shift survives the park, replace-macro dead window, duplicate raw `&kp` pre-release, hold-tap captured keys re-enter the combo engine (quick-tap bypass proven by my own case).
- 🧮 **Spec/harness only** (no MODEL change): every "t+22 vs t+23" slip, key-driven deliveries carry no +1, mock `ms = 0` → 0 ms gap, log-line origin rules.

---

## ❌ Model corrections

### B-01 · model-correction · target: MODEL (d) theorem precondition + "Hack OFF k2 > 0 → HIT for every Δ" + headline 5 ("every compiled AK pair adapts for 11 ≤ Δ") + headline 6 ("every follower in a real combo … adapted for ALL Δ") + CLAIMS contradiction 4

- **Corrected statement**
  - The (d) theorem holds only when trigger A and follower B share **no real combo**.
  - If they share a real combo, let S = the longest shared real-combo timeout (> 11). B's press never empties A's set, so both leave together at A's rung `T_A + S`; B is re-raised with its old timestamp and hits the quick-tap bypass (R8) → base layer.
  - **Native (PROVEN, L=LB2 → LB3, S = 16 `magicCloseQuitCb`)**: MISS for Δ ≤ S−1 = 15, HIT from Δ = S = 16 (key-first flush, B starts a fresh set). **Identical with the hack on or off** (the hack only adds a no-op rung).
  - **Board (INF from R8/R9, `now_flush = T_A + S`)**: MISS Δ ≤ S−2 (≤ 14), **STALL at Δ = S−1 (15)** (re-captured inside the rung handler → no timer → delivered at the next press/release, then adapted, ≈ 60 ms late in T-23's event shape), HIT Δ ≥ S.
  - "Hack OFF, k2 > 0 → HIT for every Δ ≥ 0" becomes "… for pairs sharing no real combo".
  - "The hack rescues 12 pairs / breaks all 23 for Δ ≤ 10" must exclude shared pairs: for them the hack changes nothing.
- **Pairs affected (static scan in T-23, INF except the first)**
  | trigger → follower | follower binding | shared combo | expected native miss band |
  |---|---|---|---|
  | L (LB2) → LB3 | `&bk L` | magicCloseQuitCb 16 ms, 3-key | Δ ≤ 15 — **PROVEN** |
  | H (RM4) → RM2 | `ak_hE` | capsWord 18 ms, 4-key | Δ ≤ 17 — INF |
  | M (LT2) → LT3 | `&bk M` | typeZ 16 ms, **2-key** | follower completes the combo → `&bk Z` output — INF |
  | W (LT3) → LT2 | `WM_to_LM` | typeZ, 2-key | → Z — INF |
  | D (LB1) → LB0 | `DV_to_LV` | tab 16 ms, 2-key | → tab linger combo — INF |
  | V (LB0) → LB1 | `&bk L` | tab, 2-key | → tab — INF |
  - 2-key rows (INF from R7 PROVEN in T-09): Δ < 11 with hack → combo fires at its own deadline T_A + 16; 11 ≤ Δ < 16 → fires at B's press; hack off → fires at B's press. No AK output at all.
- **Evidence**
  - T-23-e5 (hack OFF, Δ = 13, MISS): `[00:00:00.026,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=2 timestamp=26` → `[00:00:00.030,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=29` → `[00:00:00.030,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 21, binding name: flo,behavior-adaptive-key` → `[00:00:00.041,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x0A implicit_mods 0x00 explicit_mods 0x00` ("LG").
  - T-23-d1 (hack ON, Δ = 13): L at t+17 not t+13: `[00:00:00.030,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x0F implicit_mods 0x00 explicit_mods 0x00`; G on base at `[00:00:00.041,000] … keycode 0x0A`.
  - T-23-d5 (hack ON, Δ = 15, MISS): `[00:00:00.032,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=31`.
  - T-23-d6 (hack ON, Δ = 16, HIT): `[00:00:00.049,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 12 position: 21, binding name: flo,behavior-buffered-key`.
  - T-23-e1 (hack OFF, Δ = 20, HIT; spec predicted MISS): `[00:00:00.057,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 12 position: 21, binding name: flo,behavior-buffered-key`.
  - Control (LT4 follower, no shared combo, k2 = 0) behaves exactly per MODEL (d): T-23-d3 `[00:00:00.038,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 12 position: 0, binding name: flo,behavior-buffered-key` (G at t+25).
- **Confidence**: high (native L→LB3); medium (board band, STALL at S−1); medium-low (other five pairs; the 2-key rows not run). Proving test: R2 runs RM4→RM2 at Δ = 17/18 and LT2→LT3 at Δ = 6/13 (expect HID 0x1D).

### B-02 · model-refinement (paired with B-01) · target: MODEL (d) "Δ ≤ 9 → MISS … both wait for the hack rung at T_A+11"; CLAIMS contradictions 2 and 3

- **Corrected statement**: for Δ below the flush point both keys wait for the **longest candidate they share** — the hack (11 ms) when no real combo is shared, otherwise S. The bypass test is then `T_B ≤ now_flush − 2` with `now_flush = T_A + S` (board, mostly) / `T_A + S + 1` (native). CLAIMS 2 ("Δ-flush only for 11 ≤ Δ < k1") and 3 ("Δ ≥ 11 → Δ + max(11,k2)") hold only for non-shared pairs.
- **Evidence**: T-23-d2 (Δ = 5): hack rung does not flush, `[00:00:00.017,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=1 timestamp=16`; both leave at `[00:00:00.022,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=21` (t+17, not t+12).
- **Confidence**: high.

### B-03 · model-correction · target: MODEL (e) Linger keys, TAP path "with `&bk` as tap the follower's HID down lands after `tap↑` at the next 10 ms tick"

- **Corrected statement**
  - TAP decision → `tap↓` (queued `&bk`, synchronous when the queue is idle) → captured keys re-raised in the same handler.
  - **Raw `&kp` (non-queued) captured key**: its HID↓ is emitted **in the decision instant, after `tap↓` and before `tap↑`** → report order `Y↓ D↓ Y↑ D↑` (overlap). Text unchanged ("yd").
  - **Queued captured key** (`&ak`, `&bk`, any macro): enqueued behind `tap↑` → HID↓ at decision + 10 (native +11).
  - HOLD path unchanged: hold binding, then captured keys in the same instant.
- **Native / board**: decision is event-driven (same on both). Queued follower: native +11, board +10+δ.
- **Evidence**
  - T-15-d (raw `&kp D`): `[00:00:00.123,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x1C implicit_mods 0x00 explicit_mods 0x00` → `[00:00:00.123,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x07 implicit_mods 0x00 explicit_mods 0x00` → `[00:00:00.134,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0x1C implicit_mods 0x00 explicit_mods 0x00`.
  - T-15-f (`&ak B`): `[00:00:00.134,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x05 implicit_mods 0x00 explicit_mods 0x00` (after Y↑).
  - T-15-fix-a-bk-follower (`&bk D`, raw log, no write-up): `[00:00:00.134,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0x1C …` then `[00:00:00.134,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x07 implicit_mods 0x00 explicit_mods 0x00`.
- **Confidence**: high.

### B-04 · model-correction · target: MODEL (e) Callum mods — `htls` "any other key DOWN while undecided → HOLD immediately" (outcome part) and `htm` "the modifier is DOWN from the key press … never absent between press and consumption"

- **Corrected statement**
  - `htls` interrupt: `decided hold-interrupt` in the interrupting key's own ms, `&mo l_mod` synchronous, `l_mod` ON in that ms (unchanged, PROVEN).
  - **Then the interrupting key is re-raised at the hold-tap listener (`ht:235`, `ZMK_EVENT_RAISE_AT`) and passes the combo engine again with `l_mod` as highest layer** (`combo.c:147`). With ≥ 1 candidate live on `l_mod` it is captured and delivered at `ts_key + longest such candidate`; with none, in the decision ms.
  - `htm` modifier is DOWN from the key's **delivery to the keymap** (hold-while-undecided at hold-tap creation), not its physical press. "Never absent between press and consumption" → "between delivery and consumption" (and see B-21 for the HOLD double release).
  - **Flo's `l_mod` (26)**: only **LM1 (`entr` <13 14>)** and **RM1 (`entr2` <15 16>)** carry an `l_all` 16 ms combo → Shift down at `ts_key + 16` (native +17). LM4/LM3/LM2/RM2/RM3/RM4 have none on 26 → mod in the decision ms.
- **Native / board**: LM1 after interrupt: native t+48 (= key t+31 + 17), board key + 16 + δ. LM4: t+31 both.
- **Evidence**
  - T-17-a4 (real LM1): `[00:00:00.062,000] <dbg> zmk: decide_hold_tap: 31 decided hold-interrupt (hold-preferred decision moment other-key-down)` → `[00:00:00.062,000] <dbg> zmk: position_state_down: combo: capturing position event 13` → `[00:00:00.079,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0xE1 implicit_mods 0x00 explicit_mods 0x00`.
  - T-17-a3 (real LM4): `[00:00:00.062,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0xE0 implicit_mods 0x00 explicit_mods 0x00`.
  - T-17-a (R1 pos 5, S16/Q18 on layer 4): `[00:00:00.081,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0xE0 implicit_mods 0x00 explicit_mods 0x00` (t+50, spec said t+31); T-17-fix-a-tiers-alpha-only: `[00:00:00.062,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0xE0 implicit_mods 0x00 explicit_mods 0x00`.
  - T-19-a (htm held from press): `[00:00:00.081,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0xE0 implicit_mods 0x00 explicit_mods 0x00` (t+19) vs T-19-fix-a-nocombo `[00:00:00.062,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0xE0 implicit_mods 0x00 explicit_mods 0x00` (t+0).
- **Confidence**: high (LM1, LM4 observed on R2); RM1 INF from the combo table (test: R2 LH1 hold + RM1 at +31 → expect 0xE1 at t+48).

### B-05 · model-correction · target: CLAIMS contradiction 14 ("no exact-ms tie exists in the 2-key model"), E-128

- **Corrected statement**: exact-ms ties exist outside the hack-ON Δ ≤ 10 band: hack-OFF `k2 = 0` at board Δ = k1+10 (native Δ = k1+11 when k1 = 0, k1+12 when k1 > 0) and at the AK window's upper edge. On native they resolve deterministically toward the timer (B-18); on the board they are sub-ms races. MODEL's own ⚖️ cells were right; CLAIMS 14's parenthetical is wrong; E-128 ("ties depend on Zephyr scheduling") is essentially right.
- **Evidence**: T-07-d11 `[00:00:00.022,000] <dbg> zmk: set_layer_state: layer_changed: layer 2 state 1` before `[00:00:00.022,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 3, position: 3, pressed: true`; T-23-e4 `[00:00:00.056,000] <dbg> zmk: set_layer_state: layer_changed: layer 12 state 1` before `[00:00:00.056,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 1, position: 0, pressed: true`; T-12-b-d112 `[00:00:00.179,000] <dbg> zmk: set_layer_state: layer_changed: layer 19 state 0` before `[00:00:00.179,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=178`.
- **Confidence**: high.

### B-06 · model-correction · target: CLAIMS contradiction 16 / E-60 ("AK window … pinned by any held modifier")

- **Corrected statement**: only a keycode (modifiers included) whose DOWN is **delivered after `aksl` arms** pins the layer. A modifier already held when the AK letter is typed does not pin: the layer times out at D+110 (native D+112) with Shift still down. MODEL (c)'s wording ("the first keycode DOWN after arming") is exact and stays.
- **Evidence**: T-20-d `[00:00:00.211,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 0` while Shift (down since `[00:00:00.058,000] … keycode 0xE1`) is held until `[00:00:00.346,000]`.
- **Confidence**: high.

---

## 🔧 Model refinements

### B-07 · model-refinement · target: MODEL R10 (late-deadline stall) — mechanism

- **Corrected statement (replaces R10 text)**
  - `k_work_schedule` is refused whenever the combo delayable is **DELAYED, QUEUED or CANCELING**; only RUNNING (inside its own handler) may re-arm (`work.c:967`). `combo.c:417-418` still records the wanted deadline → phantom `timeout_task_timeout_at`.
  - When a later key's position filter removes the candidate owning the armed deadline and a later-deadline candidate survives, the later deadline is never armed; the old timer fires, `combo.c:473-475` sees `uptime < timeout_task_timeout_at`, returns silently. The set is timer-less until the next position event.
  - QUEUED case (new): a re-captured key whose fresh MIN deadline is already past → `K_MSEC(<0)` clamps to `K_NO_WAIT` → immediate submit → QUEUED → any schedule in the same handler is refused (INF from source; outcome observed in the fix case).
  - Stall ends by the ordinary rules: (1) press completing the **only** surviving candidate → fires at that press; (2) press completing `candidates[0]` with ≥ 2 alive → marked, fires at first release; (3) press sharing no live candidate / after all deadlines → flush at that press; (4) any release → flush.
  - Band (hack ON): second key at ≥ t+11 and < shortest survivor's deadline. Hack OFF (nav/num layers): any key that drops the shortest candidate while a longer survives (INF, not run).
- **Evidence**
  - T-10-c: no line between `[00:00:00.024,000] <dbg> zmk: position_state_down: combo: capturing position event 6` and `[00:00:00.129,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 1, col: 0, position: 4, pressed: false` (E, G flushed only at E↑ t+117; unstalled would be t+19).
  - T-10-fix-lateF-d13: E delivered at t+25 by F's press, not at the t+19 rung: `[00:00:00.037,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=37` → `[00:00:00.037,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x08 implicit_mods 0x00 explicit_mods 0x00`; G, F then stranded to `[00:00:00.138,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 1, col: 0, position: 4, pressed: false`.
- **Confidence**: high (outcomes); QUEUED path = SRC + observed outcome.

### B-08 · model-refinement · target: MODEL (e) combo tiers "3-key combos typed out of order (RM1, RM3, RM2) stall until a release (R10)"; CLAIMS contradiction 7

- **Corrected statement**: a 3-key combo typed out of order stalls **only if a longer sibling is still a candidate when it completes** (Flo: capsWord RM1–RM4 beside delWord RM1–RM3 → delWord fires at the first release, as MODEL says for Flo's board). Without a live sibling, the completing press fires it immediately (R7), and the stall between the 2nd and 3rd key is invisible. With 2 keys held and no third (RM1 + RM3 at +12), both letters are held until the first release instead of leaving at t+18.
- **Evidence**: T-10-a (no sibling) `[00:00:00.028,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x1A implicit_mods 0x00 explicit_mods 0x00` (t+16, spec predicted t+117); T-10-e (4-key sibling) `[00:00:00.129,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x1A implicit_mods 0x00 explicit_mods 0x00` (t+117 = E↑).
- **Confidence**: high. (Spec error on T-10-a itself: see S-06.)

### B-09 · model-refinement · target: MODEL R6 (release while buffered; dupe release re-flushes a re-captured key 2)

- **Corrected statement**
  - With a queue-stamped key 1 (`&ak`, `&bk`), the release flush stamps key 1's keycode at the release instant; key 2 (`T_B ≤ T_rel − 2`) is **bypassed**, not re-captured → the dupe release finds an empty buffer, no `releasing position event` for key 2.
  - Re-capture + dupe cleanup happens only for a raw `&kp` key 1, or when `T_B ≥ T_rel − 1`.
  - Either path: key 2 resolved at the release instant on the base layer. With an `&ak` key 1 its HID↓ waits for the queue tick: release + 10 (native +11), after key 1's `kp↑` and AK layer ON → MISS; key 1's AK layer is then consumed by key 2's base keycode.
- **Evidence**
  - T-08-a: `[00:00:00.016,000] <dbg> zmk: release_pressed_keys: combo: reraising position event 1` → `[00:00:00.016,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 1, binding name: flo,behavior-adaptive-key` (no capture); `[00:00:00.027,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x05 implicit_mods 0x00 explicit_mods 0x00` (t+21).
  - T-08-c (raw `&kp` key 1): `[00:00:00.016,000] <dbg> zmk: release_pressed_keys: combo: releasing position event 1`.
  - T-08-fix-boundary-rel1 (T_B = T_rel; raw log, no write-up): `[00:00:00.012,000] <dbg> zmk: position_state_down: combo: capturing position event 1` → `[00:00:00.012,000] <dbg> zmk: release_pressed_keys: combo: releasing position event 1`; rel2 (T_B = T_rel − 2): `[00:00:00.014,000] <dbg> zmk: release_pressed_keys: combo: reraising position event 1` with no capture after it.
- **Board**: release flush has no timer offset; HID of key 2 at release + 10 + δ.
- **Confidence**: high. Note rel1 tested T_B = T_rel (mock ms 0 → 0 gap, H-02), not T_rel − 1; the −1 edge is SRC only.

### B-10 · model-refinement · target: MODEL (c) "R thumb … 0 ms tap, layer ON at the decision instant" (INF → PROVEN) + addendum

- **Corrected statement**: PROVEN as written (H↓, H↑, `l_akR` ON and the captured key's resolution all in the thumb-up handler; captured key adapted; D's T7b refuted). **Addendum**: the nested `process_next` scheduled the queue's 10 ms delay, so the behaviour queue is **parked until thumb-up + 10 (native +11)**; any queued output resolved in that window (captured follower's `&bk`, a follower pressed 5 ms after thumb-up) emits HID only at that tick. The tick first runs `ak_R_macro`'s no-op `&ak↑`.
- **Evidence**
  - T-13-b: `[00:00:00.093,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 3 position: 1, binding name: flo,behavior-buffered-key` → `[00:00:00.104,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x17 implicit_mods 0x00 explicit_mods 0x00`.
  - T-13-fix-e-park (hack off; my `--no-rt` run of the built exe): thumb up `[00:00:00.062,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 2, col: 2, position: 10, pressed: false`; follower at +5 resolved `[00:00:00.067,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 3 position: 1, binding name: flo,behavior-buffered-key`; HID only `[00:00:00.073,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x17 implicit_mods 0x00 explicit_mods 0x00`.
  - T-13-fix-f-nopark (follower at +15): `[00:00:00.077,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 1, position: 1, pressed: true` and `[00:00:00.077,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x17 implicit_mods 0x00 explicit_mods 0x00` (same ms).
  - Real keymap T-13-d: `[00:00:00.093,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 17 position: 0, binding name: flo,behavior-buffered-key` ("RR").
- **Board**: tick at thumb-up + 10 + δ.
- **Confidence**: high.

### B-11 · model-refinement · target: MODEL (e) "A linger key pressed ≤ 9 ms after an `&ak` alpha is force-decided TAP at delivery" (INF → PROVEN) + timeline

- **Corrected statement**
  - PROVEN: re-raised at the `&ak`'s delivery D with its original timestamp, bypasses the combo (R8), `decided tap (tap-preferred decision moment quick-tap)` at D, never lingers however long it is held.
  - Band: **native Δ ≤ 10** (Δ = 10 observed forced TAP, Δ = 11 normal HOLD); **board Δ ≤ 9** (INF); board Δ = 10 → stranded inside the rung handler → hold-tap created at the next position event with an expired term → HOLD at that event (INF, hardware only).
  - Tap output `&bk Y` is enqueued behind the running `&ak` macro → **Y↓ at D+10** (native D+11), in the same tick as `kp A↑` and AK layer ON; Y is the first keycode after arming, so Y↑ at D+20 turns the AK layer OFF → layer alive only (D+10, D+20].
  - Combo bypass and hold-tap quick-tap flip at the same Δ (both compare `last_tapped − 1 > T_linger`).
  - The term timer still fires at `T_L + 100` but is a no-op.
- **Evidence**: T-16-a `[00:00:00.018,000] <dbg> zmk: decide_hold_tap: 9 decided tap (tap-preferred decision moment quick-tap)`, `[00:00:00.029,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x1C implicit_mods 0x00 explicit_mods 0x00`, `[00:00:00.040,000] <dbg> zmk: set_layer_state: layer_changed: layer 2 state 0`; T-16-c-d10 `[00:00:00.022,000] <dbg> zmk: decide_hold_tap: 9 decided tap (tap-preferred decision moment quick-tap)`; T-16-d-d11 `[00:00:00.123,000] <dbg> zmk: decide_hold_tap: 9 decided hold-timer (tap-preferred decision moment timer)`; T-16-fix-a-kptap (tap = `&kp Y`) `[00:00:00.018,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x1C implicit_mods 0x00 explicit_mods 0x00` (Y↓ at the decision once the queue is bypassed).
- **Board**: Y↓ ≈ t+21 (D = t+11+δ, +10+δ'); control X↓ at T_L + 100 + δ.
- **Confidence**: high (native); medium (board Δ = 10 HOLD).

### B-12 · model-refinement · target: MODEL (e) Callum mods — `moAndBuffer` 130 ms buffer (closing edge)

- **Corrected statement**: a key pressed inside the buffer resolves on `l_mod` iff its **delivery** precedes layer OFF (release + 130 + δ₁). Delivery = min(own key-up, press + k), k = longest combo candidate live on `l_mod` for that position (0 if none). Effective closing edge: **release + 130 − k** for a key still held at its deadline; release + 130 for keys without an `l_mod` combo or released earlier. Flo: LM1/RM1 Shift (k = 16) lose the last ≈ 16 ms → resolve on base as their `&ak` letter, parked to release + 260 (LM1 → "t"); LM4/RM4 Ctrl keep the full 130. Layer is resolved at delivery, the release uses the press-time snapshot (B-27).
- **Evidence**: T-18-g (real LM1 at t+240) `[00:00:00.373,000] <dbg> zmk: set_layer_state: layer_changed: layer 26 state 0` → `[00:00:00.378,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 13, binding name: flo,behavior-adaptive-key` → `[00:00:00.504,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x17 implicit_mods 0x00 explicit_mods 0x00`; T-18-fix-b-htm232 `[00:00:00.372,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 4 position: 5, binding name: hold_tap_mod` one ms before `[00:00:00.373,000] <dbg> zmk: set_layer_state: layer_changed: layer 4 state 0`; T-18-b3 (key-up flush first) `[00:00:00.371,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 4 position: 5, binding name: hold_tap_mod`.
- **Confidence**: high (mechanism); board edge INF.

### B-13 · model-refinement · target: MODEL headline 8 ("any letter typed in that window is emitted at thumb-release + 260") and (e) park numbers

- **Corrected statement**: the park holds **only queue-routed output** (`&ak`, `&bk`, macros, morph macros). A raw `&kp` (non-queued) key is emitted at its normal delivery and overtakes parked output (overtaking = INF, no case mixes both). Park end: native **release + 262** (two chained `K_MSEC(130)` timers, +1 each), board release + 260 + δ₁ + δ₂; layer OFF native release + 131, board release + 130 + δ₁. Every parked `&ak` emits HID↓ at the park end regardless of when it reached the keymap; HID↑ + its AK layer ON 10 (+δ) later. Park is anchored to the central's stamp of the thumb-up (left-half thumb → +debounce +BLE after the physical release).
- **Evidence**: T-18-c `[00:00:00.402,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x09 implicit_mods 0x00 explicit_mods 0x00` (raw F at t+281, 102 ms before park end); T-18-a `[00:00:00.242,000] <dbg> zmk: behavior_queue_process_next: Processing next queued behavior in 130ms` → `[00:00:00.373,000] <dbg> zmk: set_layer_state: layer_changed: layer 4 state 0` → `[00:00:00.504,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x05 implicit_mods 0x00 explicit_mods 0x00`; T-18-a2 (delivered t+274) same HID time `[00:00:00.504,000] … keycode 0x05`.
- **Confidence**: high.

### B-14 · model-refinement · target: MODEL (c) Consumption ("a held/sticky Shift pins the AK layer until Shift up (≤ 1500 ms for skms)")

- **Corrected statement**
  - Pin requires the modifier's DOWN to be **delivered** after arming and before the sticky timer (D+110): delivery includes the modifier's own combo wait (11–18 ms) or the hold-tap decision (INF for the exact boundary).
  - While pinned, **every** key resolves on the AK layer until the modifier's UP, not just the first (two follower taps both adapted).
  - A follower's own UP does not release a Shift-pinned layer (the pin belongs to the Shift keycode).
  - `skms` (htls tap): pins until the sticky Shift releases = the **first letter's key-up** → at most one adapted letter; the ≤ 1500 is counted from the thumb **press** (B-19).
  - `ignore-modifiers` on `aksl` removes the pin (control).
  - INF: a held `htm` home-row mod pressed inside the window pins the same way until released.
- **Evidence**: T-20-a `[00:00:00.465,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0xE1 implicit_mods 0x00 explicit_mods 0x00` → `[00:00:00.465,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 0` (no OFF at t+129); T-20-e two adapted K at `[00:00:00.414,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 1 position: 1, binding name: flo,behavior-buffered-key` and `[00:00:00.446,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 1 position: 1, binding name: flo,behavior-buffered-key`, OFF only at `[00:00:00.477,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 0`; T-20-c `[00:00:00.377,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 0` (same ms as K↑); T-20-b `[00:00:00.180,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 0`.
- **Confidence**: high.

### B-15 · model-refinement · target: MODEL headline 8 "Every macro key … is serialised through ONE queue"; CLAIMS contradiction 13 / E-72

- **Corrected statement**: FIFO is **per queued item**. A macro nested in a macro (`&macro_tap &ak 3 B` inside REPLACE_CHAR_WITH_BIGRAM) enqueues its own steps only when its item executes (F+20 board, F+22 native). A `&bk` follower delivered in (F, F+20) lands **before** the nested output (text "LDB", "LLB"); only one delivered after F+20 lands after it. `&bk` does not guarantee "after the whole replace". Raw `&kp` overtakes queued output (PROVEN). Replace macro board timeline: ⌫↓ F · ⌫↑ + L↓ F+10 · L↑ + no-op Shift releases + `ak↓` F+20 · `ak↑` + B↓ F+30 · B↑ + new AK layer F+40 (native F+11k).
- **Evidence**: T-21-c `[00:00:00.111,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x07 implicit_mods 0x00 explicit_mods 0x00` before `[00:00:00.122,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x05 implicit_mods 0x00 explicit_mods 0x00`; T-21-f follower L `[00:00:00.107,000] … keycode 0x0F` before B `[00:00:00.118,000] … keycode 0x05`; T-21-e (delivered after `ak↓`) D `[00:00:00.125,000] … keycode 0x07` after B `[00:00:00.114,000] … keycode 0x05`; T-21-d raw D `[00:00:00.108,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x07 implicit_mods 0x00 explicit_mods 0x00` before B at `[00:00:00.114,000]`.
- **Confidence**: high.

### B-16 · model-refinement · target: MODEL (c) "Window seen from the next key-down … Δ ≤ D_A + 110 − max(11,k2)" and (d) "Upper window edge"

- **Corrected statement**: the bound value itself is a **tie**. Board (16/16 pair T→LB3): HIT Δ ≤ 109, **sub-ms race at Δ = 110**, MISS Δ ≥ 111 (INF: OFF path crosses three timers, follower one). Native: HIT Δ ≤ 111, Δ = 112 same-ms tie → **MISS** (sticky timer armed earlier fires first; equal-deadline timeouts fire in schedule order, `timeout.c:125-131`). Native window is 2 ms wider than the board's; page numbers must name the target. A consuming follower keeps the layer on past D+110 until its own `kp↑`.
- **Evidence**: T-12-b-d111 `[00:00:00.178,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 19 position: 21, binding name: flo,behavior-buffered-key`; T-12-b-d112 `[00:00:00.179,000] <dbg> zmk: set_layer_state: layer_changed: layer 19 state 0` → `[00:00:00.179,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=178` → `[00:00:00.179,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 21, binding name: flo,behavior-adaptive-key`.
- **Confidence**: high (native); medium (board race at 110).

### B-17 · model-refinement · target: MODEL (d) caveat "Nominal 1 ms margin at Δ = 11 … can be eaten by sub-ms phase (≈ 0.05 %)"

- **Corrected statement**: in the key-driven band 11 ≤ Δ < dA the layer's `K_MSEC(10)` (329 ticks) and the follower's `K_MSEC(11)` (362 ticks) are armed in the **same handler** → board margin ≈ 1.01 ms regardless of phase; the 0.05 % caveat applies only to Δ ≥ dA (key 1 delivered by its own timer). Native margin exactly 1 ms (observed Δ = 11, 13, 15, 16).
- **Evidence**: T-05 `[00:00:00.037,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 1` → `[00:00:00.038,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x0F implicit_mods 0x00 explicit_mods 0x00`.
- **Confidence**: medium (board part = SRC tick arithmetic, INF).

### B-18 · new-fact · target: MODEL (c) "Visibility to the next key … same-tick ordering question (native order / board coin flip)", (d) ⚖️ legend "deterministic on native", CLAIMS T-07 expectation

- **Statement**
  - Native order inside one ms (PROVEN): equal-deadline timeouts fire in schedule order (`timeout.c:125-131`); each expiring delayable appends its work item FIFO; **a kscan event reaches the keymap through a second work item** (`physical_layouts.c:147-160`: `k_msgq_put` + `k_work_submit(msg_processor)`), appended behind every already-queued item. ⇒ A timer (queue tick, combo rung, hold-tap term, sticky release) expiring in the same ms as a key event always runs **before** the key.
  - Consequences on native: hack-OFF k1 = 0, k2 = 0: MISS Δ ≤ 10, **HIT Δ ≥ 11** (tie resolves layer-first; CLAIMS predicted MISS); k1 = 16: tie at Δ = 28 → HIT; window edge Δ = 112 → MISS; linger release at +101 → HOLD by timer; combo gap = T+1 → timer path; hack ON Δ = 12 → rung first, key starts a fresh set.
  - Board: ties at k1+10 remain sub-ms races; the same msgq hop biases toward the timer (INF).
- **Evidence**: T-07-d11 `[00:00:00.022,000] <dbg> zmk: kscan_mock_work_handler_0: ev 2151416576 row 0 column 3 state 1` → `[00:00:00.022,000] <dbg> zmk: set_layer_state: layer_changed: layer 2 state 1` → `[00:00:00.022,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 3, position: 3, pressed: true` → `[00:00:00.022,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 2 position: 3, binding name: flo,behavior-buffered-key`; T-07-fix-d10 (my run) `[00:00:00.020,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 3, binding name: key_press` before `[00:00:00.021,000] <dbg> zmk: set_layer_state: layer_changed: layer 2 state 1` (Δ = 10 MISS); T-04-d12 `[00:00:00.024,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=23` before `[00:00:00.024,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 3, position: 3, pressed: true`; T-15-c `[00:00:00.202,000] <dbg> zmk: decide_hold_tap: 9 decided hold-timer (tap-preferred decision moment timer)` before the release's `Row:` line; T-22-fix-h `[00:00:00.034,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=33` before `[00:00:00.034,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 3, position: 3, pressed: true`.
- **Confidence**: high (native); board bias INF.

---

## 🆕 New facts

### B-19 · new-fact · target: MODEL (e) Callum `skms` / `htm` tap "sticky 1500 ms"; MODEL (c) "(≤ 1500 ms for skms)"

- **Statement**: sticky expiry is anchored at the **hold-tap's press timestamp** (`sk:182` `release_at = event.timestamp + 1500`; hold-tap passes its original timestamp, `ht:410-413`, `ht:433-436`). Effective window after key-up = 1500 − hold time. Native release + 1 (t+1501); board press + 1500 + δ.
- **Evidence**: T-17-b2 (thumb press `.051`, tap up `.102`) `[00:00:01.552,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0xE1 implicit_mods 0x00 explicit_mods 0x00`; T-19-d (htm press `.062`, up `.113`) `[00:00:01.563,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0xE0 implicit_mods 0x00 explicit_mods 0x00`.
- **Confidence**: high.

### B-20 · new-fact · target: MODEL (e) `htm` (hold path)

- **Statement**: `htm` (hold-while-undecided + linger) key-up after a **HOLD** calls `release_hold_binding` twice (`ht:642`, then `ht:644-645`) → modifier refcount −2. Alone: `<err> zmk: Tried to unregister modifier 0 too often`, harmless on the host. **With another holder of the same modifier** (proven: a still-armed `skm` sticky Ctrl from an earlier tap of the same key) the count hits 0 early → modifier released → the next letter is **unmodified** (Ctrl+C becomes "c"), and the sticky's later release errors.
- **Evidence**: T-19-b `[00:00:00.225,000] <err> zmk: Tried to unregister modifier 0 too often`; T-19-fix-c-hold-refcount2 (raw log, no write-up): `[00:00:00.255,000] <dbg> zmk: decide_hold_tap: 5 decided hold-timer (tap-preferred decision moment timer)` → `[00:00:00.325,000] <dbg> zmk: zmk_hid_unregister_mod: Modifier 0 released` → `[00:00:00.543,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x06 implicit_mods 0x00 explicit_mods 0x00` + `[00:00:00.543,000] <dbg> zmk: zmk_hid_implicit_modifiers_press: Modifiers set to 0x00` → `[00:00:00.577,000] <err> zmk: Tried to unregister modifier 0 too often`. (T-19-fix-b tested tap-then-tap by gap slip: Ctrl kept, no error.)
- **Board**: same code path; only visible with USB logging. Other two-holder cases (e.g. held `&kp LSHIFT` + HOLD `htm LSHIFT`) INF.
- **Confidence**: high (R1, same `htm` shape as Flo's).

### B-21 · new-fact · target: MODEL (e) page "late" scenario

- **Statement**: a sticky Shift armed before the thumb release survives the whole 262 ms (board 260) park; it is consumed by the parked key's queued `kp↓` (report mods 0x02) and released in the same ms as that key's queued `kp↑`, **before** the key's `aksl` layer turns ON. Real keymap: "A" shifted at release + 262 native (board ≈ 380 in the page scenario).
- **Evidence**: T-18-f `[00:00:00.483,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x04 implicit_mods 0x00 explicit_mods 0x00` + `[00:00:00.483,000] <dbg> zmk: zmk_hid_implicit_modifiers_press: Modifiers set to 0x02` → `[00:00:00.494,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0xE1 implicit_mods 0x00 explicit_mods 0x00` → `[00:00:00.494,000] <dbg> zmk: set_layer_state: layer_changed: layer 2 state 1`.
- **Confidence**: high.

### B-22 · new-fact · target: MODEL (c)/(e) (AK replacement macros), CLAIMS E-98

- **Statement**: after a replace macro fires at F, the old AK layer is consumed by ⌫ (first keycode after arming) and drops at ⌫↑ (board F+10, native F+11); the new AK layer (nested `&ak`) turns ON only at F+40 (native F+44). **Any key delivered in (F+10, F+40) resolves on base layer 0** (dead window). Queue items: 8 outer + 4 nested (E-98 confirmed).
- **Evidence**: T-21-a `[00:00:00.089,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 0` → `[00:00:00.090,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 3, binding name: key_press` → `[00:00:00.122,000] <dbg> zmk: set_layer_state: layer_changed: layer 3 state 1`; T-21-d `[00:00:00.108,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 3, binding name: key_press`.
- **Board**: follower delivery vs layer OFF is a ~1 ms margin (`K_MSEC(11)` vs `K_MSEC(10)` from the same handler) on both targets.
- **Confidence**: high.

### B-23 · new-fact · target: CLAIMS E-71 ("out of order or dropped"), MODEL headline 8

- **Statement**: a raw `&kp` of the **same letter** the running macro types is not dropped: `hid_listener` pre-releases it (`unregistering … since it was already pressed`) → host sees two key-downs; the macro's `L↑` also releases the physically held follower key early. Different letter (raw M) overtakes the macro's own L.
- **Evidence**: T-21-g `[00:00:00.085,000] <dbg> zmk: hid_listener_keycode_pressed: unregistering usage_page 0x07 keycode 0x0F since it was already pressed`; T-21-h raw M `[00:00:00.074,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x10 implicit_mods 0x00 explicit_mods 0x00` before macro L `[00:00:00.085,000] … keycode 0x0F`.
- **Confidence**: high (the `-95` send error beside it is native transport noise).

### B-24 · new-fact · target: MODEL (e) "captured keys delivered" (linger, htls, htm, blt_akR); MODEL (b) R1/R8

- **Statement**: after any hold-tap decision, each captured key is **re-raised at the hold-tap listener** (`ht:232-235`, `ZMK_EVENT_RAISE_AT`) with its **original timestamp** and passes the combo engine again: R1 on the **then-active layer**, deadline anchored at the original timestamp (often already past → `K_MSEC(<0)` → flushed in the same ms), and subject to the quick-tap bypass when a non-modifier keycode was just stamped (tap output, R-thumb H↓). A modifier-only or layer-only decision (`htm` hold, `htls` `&mo`) stamps no keycode → no bypass → re-capture.
- **Evidence**
  - Re-capture on the new layer: T-17-a `[00:00:00.062,000] <dbg> zmk: position_state_down: combo: capturing position event 5` (after `hold-interrupt`).
  - Deadline already past: T-19-b `[00:00:00.193,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=129` (C's R16 deadline t+67, executed at t+131).
  - Bypass (no capture): T-15-d, T-13-b (no `capturing` line after `Releasing key position event`).
  - **Bypass cause proven (my case `CB-T15-noquicktap`, T-15-d events + `&combo_hack { require-prior-idle-ms = <(-1000)>; }`, compiled `…require_prior_idle_ms 4294966296`)**: `[00:00:00.123,000] <dbg> zmk: position_state_down: combo: capturing position event 3` → `[00:00:00.123,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=93` → `[00:00:00.123,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x07 implicit_mods 0x00 explicit_mods 0x00` (same HID as T-15-d; only the capture lines differ) ⇒ T-15's "inferred by elimination" is now PROVEN.
- **Confidence**: high.

### B-25 · new-fact · target: MODEL (c) Consumption, (d) Δ ≤ 9 MISS row

- **Statement**: in a bypass MISS, key 2's base keycode (dequeued right after `aksl↓`) is the first keycode after arming → it **consumes key 1's AK layer**, which drops at key 2's `kp↑`; key 1's layer serves no key. Same for a hold-tap captured key resolved on base (T-13-c) and for ⌫ inside a replace macro (B-22).
- **Evidence**: T-06-b `[00:00:00.040,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 0` right after `[00:00:00.040,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0x0B implicit_mods 0x00 explicit_mods 0x00`; T-02-a `[00:00:00.040,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 0`.
- **Confidence**: high.

### B-26 · new-fact · target: MODEL (c) Consumption

- **Statement**: a key already DOWN when `aksl` arms does not consume the sticky layer, and its later UP does not release it → the layer times out at D+110 (native ON + 101).
- **Evidence**: T-07-d5 (D↓ at t+5, layer ON t+11): `[00:00:00.117,000] <dbg> zmk: set_layer_state: layer_changed: layer 2 state 0` while D is released only at `[00:00:00.112,000]` with no layer change.
- **Confidence**: high.

### B-27 · new-fact · target: MODEL (a) "layer resolved NOW (live bitmask)" / keymap

- **Statement**: the binding layer is chosen when the position event **reaches the keymap** (delivery, after any combo/hold-tap hold), not at the physical press; the key's release is dispatched on that stored press-time layer even if the layer is off by then (`keymap.c:651-654`, `:665-666`). Consequence: combo holds can move a key across a layer edge (B-12).
- **Evidence**: T-18-b `[00:00:00.373,000] <dbg> zmk: set_layer_state: layer_changed: layer 4 state 0` → `[00:00:00.380,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 5, binding name: key_press`; T-12-b-d110 release `[00:00:00.211,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 19 position: 21, binding name: flo,behavior-buffered-key` after layer 19 went off at `[00:00:00.188,000]`.
- **Confidence**: high.

### B-28 · new-fact · target: MODEL (e) combo tiers / R3

- **Statement**: when the 2nd key of a combo arrives at gap ≥ T (window missed), it starts a **fresh set anchored at its own timestamp** and waits its own full timeout before delivery (16 ms → own ts + 16, native +17); it is not delivered at key 1's flush. A non-member key at gap T bubbles at once.
- **Evidence**: T-22-b `[00:00:00.049,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=48` (C at t+33); T-22-f I at `[00:00:00.091,000]` (`timestamp=90`); T-22-fix-g (non-member D at gap 16): `[00:00:00.032,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x07 implicit_mods 0x00 explicit_mods 0x00`.
- **Confidence**: high.

### B-29 · new-fact · target: MODEL R4

- **Statement**: the timer ladder does not drift: each rung is re-armed relative to the absolute deadline (`combo.c:417` `K_MSEC(first_timeout − k_uptime_get())`), so every rung executes at `deadline + 1` native (board `deadline + δᵢ`, independent per rung).
- **Evidence**: T-11-a pos 4 rungs `[00:00:00.797,000] … remaining_candidates=2 timestamp=796`, `[00:00:00.802,000] … remaining_candidates=1 timestamp=801`, `[00:00:00.804,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=803`.
- **Confidence**: high.

### B-30 · new-fact (minor) · target: MODEL (c) R thumb / T-14 host-drop question

- **Statement**: the 0 ms R-thumb tap sends **two separate HID reports** (press, then release) in one ms; ZMK drops nothing. Host acceptance of a ~0 ms pair is hardware-only. USB spaces them ≥ one host poll (SRC `usb_hid.c:139`); BLE may put both in one connection event (INF).
- **Evidence**: T-14-a: two `zmk_endpoints_send_report: usage page 0x07` lines at `[00:00:00.102,000]`, around `[00:00:00.102,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x0B implicit_mods 0x00 explicit_mods 0x00` and `[00:00:00.102,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0x0B implicit_mods 0x00 explicit_mods 0x00`.
- **Confidence**: high (native), host part untested.

### B-31 · new-fact (minor) · target: log reading, REPLACE_CHAR_WITH_BIGRAM

- **Statement**: the replace macro's `&macro_release &kp LSHFT` / `RSHFT` log `<err> zmk: Tried to unregister modifier 1/5 too often` + `Unable to release keycode` when no Shift is held. No HID effect. Do not confuse with B-20.
- **Evidence**: T-21-a `[00:00:00.100,000] <err> zmk: Tried to unregister modifier 1 too often` and `[00:00:00.100,000] <err> zmk: Tried to unregister modifier 5 too often`; T-23-c `[00:00:00.051,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0xE1 implicit_mods 0x00 explicit_mods 0x00` / `… 0xE5`.
- **Confidence**: high.

---

## 🧪 Harness facts

### H-01 · harness · target: RIG.md reading rules (log-line origin)

- **Statement**: `filter_timed_out_candidates` from the **key path** prints the key's own timestamp at its own ms; from the **timer path** it prints the deadline at deadline + 1 (native). The printed count is **before** the position filter. At gap = T (native) the key (due at T) beats the +1-late rung, so the flush is logged from the key path; the "timestamp=t+16 at [t+17]" line exists only when the timer runs first (gap ≥ T+1, or the key alone). Board: sub-ms order, same outcome.
- **Evidence**: T-22-b `[00:00:00.032,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=32`; T-22-d `[00:00:00.118,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=117`; T-05-d16 `[00:00:00.032,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=32`; T-10-a count 2 printed at `[00:00:00.024,000] … remaining_candidates=2 timestamp=24` when only Q18 survives the position filter.
- **Confidence**: high.

### H-02 · harness · target: RIG.md headline "every gap is ms + 1"

- **Statement**: holds only for `ms ≥ 1`. `ZMK_MOCK_*(…, 0)` gives a **0 ms gap**: `kscan_mock.c:58` `k_work_schedule(&data->work, K_MSEC(0))` = `K_NO_WAIT` → no +1 tick. Consequences: `T-07-fix-d11-rev` actually tested Δ = 10 (not the intended reversed-order Δ = 11) → MISS; `T-08-fix-boundary-rel1` tested T_B = T_rel (not T_rel − 1).
- **Evidence**: my run of T-07-fix-d11-rev: `[00:00:00.042,000] <dbg> zmk: kscan_mock_work_handler_0: ev 2147483904 row 0 column 1 state 1` then `[00:00:00.042,000] <dbg> zmk: kscan_mock_work_handler_0: ev 590336 row 0 column 2 state 0` then `[00:00:00.052,000] <dbg> zmk: kscan_mock_work_handler_0: ev 2151416576 row 0 column 3 state 1`; T-08-fix-boundary-rel1 `[00:00:00.012,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 1, position: 1, pressed: true` and `[00:00:00.012,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 0, position: 0, pressed: false`.
- **Confidence**: high.

### H-03 · harness · target: RIG.md / CLAIMS reading rule (confirmed, restated for the writer)

- **Statement**: native expected time = board engine time + number of **relative timers crossed**: combo rung +1, each 10 ms queue tick +1, hold-tap term +1, sticky 100/1500 +1, each 130 ms `moAndBuffer` wait +1. Key-driven instants (a press/release emptying a set, a key with no candidate) carry no offset. An `&ak` delivered by a rung: `D = t + max(11,k) + 1`, `kp↑`/layer ON/next queued keycode at `D + 11`; delivered by a key: `D = Δ`, layer at `Δ + 11`.
- **Evidence**: T-02 Reconciliation `[00:00:00.018,000] <dbg> zmk: behavior_queue_process_next: Processing next queued behavior in 10ms` → `[00:00:00.029,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 1`; T-02-b `[00:00:00.012,000] … keycode 0x04` → `[00:00:00.023,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 1`.
- **Confidence**: high.

---

## 🧮 Spec-arithmetic / spec-derivation slips (MODEL unchanged)

| id | test | spec said | observed (verbatim) | cause |
|---|---|---|---|---|
| S-01 | T-02 (a) | B↓ + `layer 1 state 1` at t+22 | `[00:00:00.029,000] <dbg> zmk: set_layer_state: layer_changed: layer 1 state 1` + `[00:00:00.029,000] … keycode 0x05` = t+23 | spec put +1 on the rung, not on the queue tick |
| S-02 | T-06 (b) | H at t+22 | `[00:00:00.029,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x0B implicit_mods 0x00 explicit_mods 0x00` = t+23 | same |
| S-03 | T-23 (a)(b) | T / P at t+22 | `[00:00:00.028,000] … keycode 0x17` (t+23), `[00:00:00.029,000] … keycode 0x13` (t+23) | same |
| S-04 | T-06 (c) | A t+7, layer t+18, O t+38 | `[00:00:00.012,000] … keycode 0x04` (t+6), `[00:00:00.023,000] … layer 1 state 1` (t+17), `[00:00:00.043,000] … keycode 0x12` (t+37) | key-driven flush has no +1; key 2 is at t+6 |
| S-05 | T-23 (c), T-07 | C at t+1; D at t+6 for Δ = 5 | `[00:00:00.006,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x06 implicit_mods 0x00 explicit_mods 0x00` (t+0); T-07-d5 D at `[00:00:00.010,000]` (t+5) | no timer on a no-candidate key |
| S-06 | T-10 (a) | W only at E↑ t+117 | `[00:00:00.028,000] … keycode 0x1A` (t+16) | spec derivation error: lone complete candidate fires (R7); see B-08 |
| S-07 | T-15 | releases at +99/+100/+101 via n = 99/100/101; Y↓ t+81; Y↑ t+91 | n = 98/99/100 needed; `[00:00:00.123,000] … keycode 0x1C` (t+82), `[00:00:00.134,000] … released … 0x1C` (t+93) | mock gap = ms + 1 |
| S-08 | T-16 (b) | X at t+112 | `[00:00:00.125,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x1B implicit_mods 0x00 explicit_mods 0x00` (t+113) | term timer +1 native (board t+112+δ) |
| S-09 | T-16 (a) | Y↓ at t+12 with the decision | `[00:00:00.029,000] … keycode 0x1C` (t+23) | spec derivation: `&bk Y` queued behind the `&ak`; see B-11 |
| S-10 | T-18 (a) | B delivered t+274; B↓ at [t+382] | `[00:00:00.394,000] <dbg> zmk: release_pressed_keys: combo: releasing position event 1` (t+273, B's own key-up at gap 11); `[00:00:00.504,000] … keycode 0x05` (t+383 = release + 262) | key-up beats the rung; two chained 130 ms timers (+1 each). Fix run: `[00:00:00.395,000] … layer_id: 0 position: 1` = t+274 when held ≥ 12 |
| S-11 | T-20 (a) | K ~t+362 | `[00:00:00.414,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x0E implicit_mods 0x00 explicit_mods 0x00` (t+363) | mock gap 10 + 1; K delivered by its own key-up |
| S-12 | T-21 | E-key triggers replace at +31; follower resolves on layer 1 | E released at `[00:00:00.078,000] <dbg> zmk: release_pressed_keys: combo: releasing position event 4` (t+47); follower `[00:00:00.090,000] … layer_id: 0 position: 3` | spec derivation: E held by its 18 ms combos (headline 1); layer 1 consumed by ⌫ (B-22) |
| S-13 | T-23 (d)(e) | "G-follower `&bk L`, 0x0F at t+25" | two followers exist on `l_akL`: LT4 = `&bk G` (times t+13/t+25 match), LB3 = `&bk L` (shared combo, B-01) | spec mixed two keys |
| S-14 | T-17 (a), T-18 (b), T-19 (a) | mod at the decision / at press; htm at 240 → LCTRL | R1 pos 5 is in `l_all` S16/Q18 live on layer 4 (rig mirrors real `l_all`) | spec ignored R1 on `l_mod`; see B-04, B-12 |
| S-15 | T-08 (a) | dupe cleanup lines; B↓ and A↑ at t+10 | bypass; `[00:00:00.027,000] … keycode 0x05` (t+21) | spec described the raw-`&kp` path; see B-09 |
| S-16 | T-22 (b) | `timestamp=t+16` at `[t+17]` | key path `[00:00:00.032,000] … timestamp=32` | see H-01 |
| S-17 | T-20 rig | follower pos 11 on akA = `&bk M` | case copies set akA pos 11 = `&trans` | rig inconsistency, not a result |

---

## 🗣️ Wording (log strings; MODEL/CLAIMS text only)

| id | target | corrected wording | evidence |
|---|---|---|---|
| W-01 | CLAIMS T-16/T-17 lines | status strings are `decided hold-interrupt (hold-preferred decision moment other-key-down)`, `decided hold-timer (… timer)`, `decided tap (… key-up / quick-tap)` (`ht:369-378`) | T-17-a `[00:00:00.062,000] <dbg> zmk: decide_hold_tap: 10 decided hold-interrupt (hold-preferred decision moment other-key-down)` |
| W-02 | CLAIMS T-02/T-04 "no `capturing position event N`" | "no capture **after the re-raise**"; key 2's own-press capture is required by the mechanism | T-04-d9 `[00:00:00.018,000] <dbg> zmk: position_state_down: combo: capturing position event 3` |
| W-03 | CLAIMS T-13 "no `queue wait 10ms` between H↓ and H↑" | the nested call logs `Processing next queued behavior in 10ms` between them; H↑ still same ms | T-13-b `[00:00:00.093,000] <dbg> zmk: behavior_queue_process_next: Processing next queued behavior in 10ms`; T-14-a same line at `[00:00:00.102,000]` |
| W-04 | CLAIMS T-18/T-19/T-20 "`explicit_mods 0x02`" | a held/sticky modifier shows as the report byte `Modifiers set to 0x0N` in the same ms; `explicit_mods` on the letter stays `0x00` | T-18-d `[00:00:00.381,000] <dbg> zmk: zmk_hid_implicit_modifiers_press: Modifiers set to 0x02` |
| W-05 | CLAIMS T-19 "no `kp_released 0xE0` at tap end" | a `kp_released 0xE0` IS logged (refcount 2→1); report byte stays 0x01 | T-19-a `[00:00:00.113,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0xE0 implicit_mods 0x00 explicit_mods 0x00` + `Modifier 0 count: 1` |
| W-06 | CLAIMS T-10 "press stamped t" | combo press timestamp is SRC-only (`combo.c:349`); no log line carries it | T-10 |
| W-07 | MODEL (d) examples "L(16)→G(0)" | name the key: on `l_akL`, **LT4 (X key) = `&bk G`**, **LB3 (G key) = `&bk L`**; the k2 = 0 example is LT4 | T-23 d3 vs d1 |
| W-08 | log reading | queue-invoked keycodes (incl. combo `&bk` output) log `position 0` | T-09-a `[00:00:00.023,000] <dbg> zmk: on_keymap_binding_pressed: position 0 keycode 0x70006` |

---

## ✅ MODEL statements confirmed verbatim (mark PROVEN)

| MODEL location | statement (short) | test · key line |
|---|---|---|
| Headline 1 / (b) table | solo delivery = longest candidate: 11 / 16 / 18 (native +1) | T-11 sweep: pos 1 `[00:00:00.073,000] … keycode 0x05` (+12), pos 0 `[00:00:00.440,000]` (+17), pos 4 `[00:00:00.804,000]` (+19); R2 LM1 T-12-a `[00:00:00.118,000] … keycode 0x17` (+17); R2 RM1 18 ms T-18-f `[00:00:00.381,000] … remaining_candidates=0 timestamp=380` (+19); R2 LH0 hack-only T-14-c `[00:00:00.063,000] … timestamp=62` (+12) |
| Headline 2 / (c) table / native offsets | `&ak`: kp↓ at D, kp↑ + layer ON at D+10, OFF at D+110 (native D+11 / D+112) | T-12-a `[00:00:00.129,000] <dbg> zmk: set_layer_state: layer_changed: layer 19 state 1` (+28), `[00:00:00.230,000] … layer 19 state 0` (+129) |
| Headline 3 / R8 / (d) Δ ≤ 9 | quick-tap bypass, key 2 on base, same ms as key 1; native reach Δ ≤ 10 | T-02-a `[00:00:00.018,000] … layer_id: 0 position: 1`; T-02-c control `[00:00:00.018,000] <dbg> zmk: position_state_down: combo: capturing position event 1`; T-04-d10; T-23-a/b |
| (c) "a raw `&kp` … keeps the position timestamp" / R8 vs R9 | `&kp` key 1 → strand (R9); `&bk` key 1 → bypass (R8) | T-03 `[00:00:00.018,000] <dbg> zmk: position_state_down: combo: capturing position event 1` then nothing until `[00:00:00.073,000] … releasing position event 1`; T-03-bk no capture |
| R9 | re-capture inside the rung handler → no timer until next event | T-02-c, T-03, T-10-d `[00:00:00.024,000] … capturing position event 6` → `[00:00:00.122,000] … releasing position event 6` |
| R2 strict `>` / (e) acceptance `gap ≤ T−1` | 16 ms: 15 in, 16 out; 30 ms: 29 in, 30 out | T-22-a `[00:00:00.030,000] … remaining_candidates=1 timestamp=30`, T-22-b `[00:00:00.032,000] … remaining_candidates=0 timestamp=32`, T-22-e/f; T-04-d11 `[00:00:00.022,000] … remaining_candidates=0 timestamp=22` |
| R3 | re-raised key starts a fresh set anchored at its own ts | T-06-a `[00:00:00.073,000] … remaining_candidates=0 timestamp=72` (= t+21+30); T-06-c `timestamp=42` |
| R4 | ladder: key held alone leaves at longest deadline | T-11 (B-29) |
| R5 (RAISE part) | elements ≥ 1 re-raised through hold-tap listener | T-17-d `[00:00:00.018,000] … reraising position event 3` → `10 capturing 3 down event` |
| R6 / R7 release | combo behaviour released on the FIRST key up (either key); 2nd up swallowed | T-09-a2 `[00:00:00.113,000] <dbg> zmk: queue_macro: Iterating macro bindings - starting: 3, count: 0` at A↑ |
| R7 / headline 7 | completed 2-key combo under the hack fires at its own deadline; alone in 11 ≤ Δ < T fires at Δ; hack off fires at Δ | T-09-a `[00:00:00.023,000] … keycode 0x06` (t+17), T-09-b `[00:00:00.026,000]` (t+13), T-09-c `[00:00:00.012,000]` (t+6) |
| R10 (Flo example) | RM1, RM3 +12, RM2 → fires only at first release (with capsWord sibling) | T-10-e `[00:00:00.129,000] … keycode 0x1A` |
| R11 | no poison timer: next first key after a timer flush schedules normally | T-11-a pos 0 after pos 1's timer flush: `[00:00:00.435,000] … remaining_candidates=1 timestamp=434` |
| (c) Visibility | key flushed in key 1's burst resolves before D+10 → base | T-02-a, T-13-a |
| (c) Consumption | first keycode DOWN after arming pins until its UP (after HID) | T-12-b-d110 `[00:00:00.188,000] … released … 0x17` → `mo_keymap_binding_released: position 0 layer 19` → `layer 19 state 0` |
| (c) chaining | `&ak` follower's kp↑ releases old layer, its aksl↓ same tick → gapless | T-12-c `[00:00:00.118,000] … layer 13 state 0` and `[00:00:00.118,000] … layer 3 state 1` |
| (c) position-0 collision "moot" | new aksl finds nothing to release (`0 new sticky_key`) | T-12-c |
| (c) R thumb | 0 ms tap, layer ON at decision, captured key adapted (T7b refuted) | T-14-a `[00:00:00.102,000]` H↓ H↑ `layer 3 state 1`; T-13-b/d (+ B-10 addendum) |
| (d) 11 ≤ Δ < dA | A at Δ, layer Δ+10, B at Δ+max(11,k2); margin 1 ms | T-05 Δ = 11/13/15 (+16 native) `[00:00:00.026,000] … releasing position event 0` |
| (d) dA ≤ Δ | A at dA by ladder; B fresh at Δ | T-06-a `[00:00:00.038,000] … keycode 0x04` (t+17), O `[00:00:00.073,000]`; T-04-d12 |
| (d) hack OFF, k2 > 0 (non-shared) | HIT at Δ = 6 | T-06-c `[00:00:00.043,000] … layer_id: 1 position: 7`; T-23-c `[00:00:00.029,000] … layer_id: 4 position: 3, binding name: flo-macro-replace-char-with-bigram-TP` |
| (d) hack OFF, k2 = 0 | k1 = 16: MISS Δ = 6, 20; HIT Δ = 28 · k1 = 0: MISS ≤ 10 native | T-02-b `[00:00:00.012,000] … layer_id: 0 position: 1`; T-23-e3 `[00:00:00.040,000] … layer_id: 0 position: 0`; T-23-e4; T-07 |
| (d) example L(16)→G(0) Δ = 13 | L@13, layer@23, G@24 board (native 13/24/25) | T-23-d3 (LT4) |
| (d) hack cost | +11 only on hack-only positions; combo positions unchanged | T-11-c/d sweep |
| Contradiction 1 / E-38 / E-39 | M→T@5 and C→P@6 MISS with the hack; C→P@6 HIT without | T-23-a/b/c |
| Contradiction 5 | real margin = max(11,k2) − 10 | T-04-d11/d12, T-05 |
| Contradiction 8 | without the hack, a non-member key empties the set at Δ | T-02-b, T-06-c |
| (e) linger | hold-tap created after combo hold, term from original ts; ≤ T+100 TAP (native), ≥ T+101 HOLD; others captured never decide; HOLD: linger then captured same ms | T-15-b `[00:00:00.200,000] … decided tap (tap-preferred decision moment key-up)`; T-15-c `[00:00:00.202,000] … decided hold-timer`; T-15-e `[00:00:00.142,000]` X then D |
| (e) htls | held alone → `&mo` at T+90 (native +91), hack not added; tap alone → skms at key-up; buffered-with-thumb key forces HOLD | T-17-c `[00:00:00.212,000] <dbg> zmk: decide_hold_tap: 10 decided hold-timer (hold-preferred decision moment timer)`; T-17-b `[00:00:00.102,000] … keycode 0xE1`; T-17-d `[00:00:00.018,000] … decided hold-interrupt` |
| (e) moAndBuffer | layer OFF release + 130 (native +131); queue parked to + 260 (native + 262) | T-18-a `[00:00:00.373,000] … layer 4 state 0`, `[00:00:00.504,000] … keycode 0x05` |
| (e) page late scenario / contradiction 10 | RM1 after `l_mod` off → `&ak A`, shifted, ≈ 100 ms late | T-18-f `[00:00:00.483,000] … keycode 0x04` + `Modifiers set to 0x02` |
| (e) htm tap | skm count 2 → 1, mod stays until next non-mod key's UP or 1500 | T-19-a `[00:00:00.325,000] … Modifier 0 released` after C↑ |
| (e) htm hold / key-up after captured key | captured key delivered with mod down | T-19-b `[00:00:00.193,000] … keycode 0x06` + `Modifiers set to 0x01`; T-19-c |
| Headline 9 "timestamps never move" | terms, sticky windows, combo deadlines from original ts | T-15-c, T-17-c, T-19-b (`timestamp=129`), B-19 |
| (g) refuted D T7b | R thumb then held key → adapted | T-13-b/d |
| CLAIMS E-98 | replace macro = 8 outer + 4 nested items | T-21 |

---

## 🔭 Still INFERRED — and the test that would settle each

| item | current status | test |
|---|---|---|
| Board STALL at Δ = 10 (hack ON, `&ak` key 1) | SRC R9 + native can't show | T-24a hardware (USB logging) |
| Board STALL at Δ = S−1 for shared pairs (L→LB3 at 15) | INF (B-01) | hardware, same method |
| H→RM2 band Δ ≤ 17; 2-key shared pairs → combo output | INF (B-01) | R2: RM4→RM2 at Δ = 17/18; LT2→LT3 at Δ = 6/13 (expect 0x1D); LB1→LB0 |
| RM1 Callum Shift lag +16 | INF from combo table (B-04) | R2: LH1 hold, RM1 at +31 → 0xE1 at t+48 |
| R10 with the hack off (nav/num layers) | INF (B-07) | R1 hack-off: E, G at +5, no F → stall until E↑ |
| QUEUED-state refusal | SRC + outcome (B-07) | already implied by T-10-fix; a log of `k_work_schedule` return would prove it |
| Raw `&kp` overtaking parked `&ak` during the Callum park | INF (B-13) | R1: htls hold, release, `&ak B` then `&kp F` at +20/+30 → expect F before B |
| Held `htm` mod pins the AK layer | INF (B-14) | R1: `&ak A`, then `htm` hold on `l_mod` within 100 ms, follower → adapted until htm up |
| Two-holder double release other than the sticky case | INF (B-20) | R1: `&kp LCTRL` held + `htm LCTRL` HOLD release → Ctrl lost while `&kp` still held |
| Board ties (window edge 110, hack-off k1+10) and msgq-hop bias | INF (B-16, B-18) | hardware only |
| Key-driven band margin ≈ 1.01 ms on board | SRC tick arithmetic (B-17) | hardware only |
| Forced-TAP board Δ = 10 → HOLD at next event | INF (B-11) | hardware only |
| BLE/debounce transport, 7.5 ms quantisation | untouched by native | T-24b |
| E-20 (M→T@5 hack off, T re-raised with own timer) | not run | R2 T-23-a events with hack deleted |
| Upstream (f) | not tested | — |

---

## 📂 Files created by extractor B

- `results/CORR-B/T-07-fix-d10.raw.log`, `T-07-fix-d11-rev.raw.log`, `T-13-fix-e-park.raw.log`, `T-13-fix-f-nopark.raw.log` — `zmk.exe --no-rt` output of already-built cases (not rebuilt, case dirs untouched).
- `zmk/app/tests/ak-truth/CB-T15-noquicktap/` (copy of `_rig_R1` + `&combo_hack { require-prior-idle-ms = <(-1000)>; }` + T-15-d events; snapshot auto-accepted) → `results/CORR-B/CB-T15-noquicktap.raw.log`.
