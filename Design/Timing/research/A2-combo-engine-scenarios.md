# A2 — Combo engine: scenario-first traces

Source of truth: `/Users/flo/Work/Private/Dev/Keyboard/zmk/app/src/combo.c` (fork, upstream 6e03a0bb). Zephyr 3.5.0 (`dacab4875d`, inside `zmk-devcontainer` at `/workspaces/zmk/zephyr`). Board config: `app/build/right/zephyr/.config` (central = right half, the one that runs the keymap).

Notation used in every trace:

- `PSD(k)` = `position_state_down` (combo.c:422) · `PSU(k)` = `position_state_up` (456) · `TH` = `combo_timeout_handler` (472)
- `SETUP(k)` = `setup_candidates_for_first_keypress` (145) · `FTO(ts)` = `filter_timed_out_candidates` (221) · `FC(k)` = `filter_candidates` (163)
- `UTT` = `update_timeout_task` (407) · `CAP` = `capture_pressed_key` (262) · `CLEAN` = `cleanup` (397) · `RPK` = `release_pressed_keys` (273) · `ACT(R)` = `activate_combo` (341)
- Delivery paths ("how did the key reach the keymap"):
  - `[TIMER]` = `TH → CLEAN → RPK → ZMK_EVENT_RELEASE`
  - `[NEWKEY]` = `PSD(other key) → CLEAN → RPK` (head key via `ZMK_EVENT_RELEASE`, rest via `ZMK_EVENT_RAISE`)
  - `[KEYUP]` = `PSU(any key) → CLEAN → RPK`
  - `[IMMEDIATE]` = `PSD` returned `ZMK_EV_EVENT_BUBBLE` (no candidate at all)
  - `[RERAISE-BUBBLE]` = re-raised by `RPK`, then `SETUP` found 0 candidates → bubbles straight through
- `t0` = timestamp (ms) of X's position event. "wall" = when `keymap_listener` actually runs. `δ` = timer lateness on the board (see 🕰️).

---

## 🎯 Headline conclusions

- 🧨 **The hack's "minor caveat" is wrong.** Two keys pressed within 11 ms of each other (S1, S9, S10, S4b): the first key is delivered at t0+11 by the timer, the **second key is stranded** in `pressed_keys` with no timer and is delivered only by the *next position event* (usually the first key's release). It is NOT "released at the same time".
  - Root cause: `CLEAN` (combo.c:398) self-cancels `timeout_task` from inside `TH` → Zephyr marks the work item `CANCELING` → the `k_work_schedule` issued for the re-raised key (combo.c:417) is refused (returns 0) → combo.c treats `0 >= 0` as success and records a phantom `timeout_task_timeout_at`.
  - PROVEN by source (Zephyr `kernel/work.c` + combo.c) **and** reproduced in native_posix (S1: X→18 ms, Y→73 ms = X's release).
- ✅ **The hack's intended 7-step mechanism is real, but only for gaps ≥ 11 ms** (S2, S5): second key arrives after H expired → first key delivered `[NEWKEY]` at the second key's arrival, second key delivered `[TIMER]` exactly 11 ms (+δ) later.
- ⏳ **Every key is held for the LAST of its candidate timeouts, not the first.** `TH` only calls `CLEAN` when `FTO` leaves 0 candidates (combo.c:477). A lone key that is in combos with timeouts 16 and 30 (plus H=11) is delivered at 30+δ (S4: Y→30 ms). With H, no key on an `l_alpha_aks` layer is ever delivered earlier than 11+δ.
- 🐢 **With H, a completed real combo does not fire when completed.** It fires at its own `timeout-ms` (S7: R completed at 6 ms fires at 16+δ), or earlier at the next key press/release (any `CLEAN`). Without H it fires immediately at completion. The "position" it fires with is the combo's virtual key position; its timestamp is the FIRST key's timestamp (combo.c:349).
- 🔀 **Delivered events always carry their ORIGINAL timestamp** (`CAP` copies the raised event, combo.c:267; `RELEASE`/`RAISE` replay the copy). A key delivered 60 ms late still says "pressed at t0". Downstream timers (hold-tap tapping-term, sticky layer windows) computed from that timestamp are already partly elapsed at delivery.
- 🎲 **The S5 tie (Y at exactly t0+11) is outcome-invariant for the scenario as specified**, in both orderings (key-first, timer-first). It becomes a stranding bug when X and Y share a still-live longer candidate (3-key combos: Flo has 12 of them on alpha layers). Also: any change of `first_timeout` while the timer is pending is silently dropped (`k_work_schedule` refuses a `DELAYED` item), which can strand keys without H too (two combos on one key with different timeouts).
- 🧵 Everything runs on ONE thread (`k_sys_work_q`, prio -1 cooperative): local key events, peripheral key events, the combo timer, macro steps. Ordering is FIFO by submission; there is no preemption between them.

---

## 🧱 Ground truth (PROVEN, with locations)

### Firmware identity

- Fork `combo.c` logic == upstream through Sep 2026 for everything traced here; upstream diff is only the bitmask refactor (#2837/#2849) and its fix (#2928, `memset` size), which do not exist in the fork's array representation. `update_timeout_task` and `combo_timeout_handler` are byte-identical in intent (upstream combo.c:406-419, 475-487).
- Build on the board: `app/build/right/zephyr/zmk.uf2` (Sep 27 12:11) predates commit `83aa2ab` (12:31) by 20 min; consistent with build-then-commit. Map file used for listener order: `app/build/right/zephyr/zephyr_final.map`.
- Board config (`app/build/right/zephyr/.config`):
  - `CONFIG_ZMK_COMBO_MAX_COMBOS_PER_KEY=30`, `CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO=36`, `CONFIG_ZMK_COMBO_MAX_PRESSED_COMBOS=20`
  - `CONFIG_SYS_CLOCK_TICKS_PER_SEC=32768`, `CONFIG_TICKLESS_KERNEL=y`, `CONFIG_TIMEOUT_64BIT=y`, `CONFIG_NRF_RTC_TIMER=y`
  - `CONFIG_SYSTEM_WORKQUEUE_PRIORITY=-1` (cooperative), `CONFIG_BT_RX_PRIO=8` (preemptible), `CONFIG_ZMK_KSCAN_DEBOUNCE_PRESS_MS=-1` → DT default 5 ms press / 5 ms release, scan period 1 ms (`zmk,kscan-gpio-matrix.yaml:22-33`)
- Flo's values (`config/CONFIG.h`): `my_combo_timeout_adjacent 16`, `non_adjc 18`, `two_hnds 30`, `hold_key_event_delay 11` (= H timeout), `ak_tap_time 10`.
- H = `combo_ak_consistency_hack` (`features/hands_down/adaptive_keys/combos.dtsi:64-68`): `COMBO_LAY_BASE(l_alpha_aks, …, &none, ALL_KEYS, hold_key_event_delay)` → 36 keys (`aliases_key_positions.dtsi:61-65`), layers = alpha + linwin + all 23 AK layers, `require-prior-idle-ms` default -1 (`app/dts/bindings/zmk,combos.yaml:21-23`), `slow-release` false.

### Listener order for `zmk_position_state_changed` (map file `zephyr_final.map:15991-16039`)

| idx | listener | file |
|---|---|---|
| 1 | activity | activity.c |
| 4 | behavior_hold_tap | behavior_hold_tap.c |
| **8** | **combo** | combo.c |
| 9 | behavior_tap_dance | behavior_tap_dance.c |
| 13 | keymap | keymap.c:766 |

- `zmk_event_manager_handle_from` (event_manager.c:20-44): synchronous loop; `CAPTURED`/`HANDLED` stop the loop; `BUBBLE` continues.
- `ZMK_EVENT_RELEASE(ev)` resumes at `last_listener_index + 1` = 9 (tap_dance) → keymap. Never revisits combo.
- `ZMK_EVENT_RAISE(ev)` restarts at 0 → activity → hold_tap → **combo again** → this is why a re-raised key re-enters `PSD` as a fresh first key with its ORIGINAL timestamp.
- hold_tap bubbles when `undecided_hold_tap == NULL` (behavior_hold_tap.c, `position_state_changed_listener`); tap_dance bubbles when no tap-dance is active. For plain alphas both are transparent (scope of this report; hold-tap interactions are another topic).

### Where events come from, and their timestamps

- Local (right half) key: kscan matrix driver (debounced, 5 ms) → `zmk_physical_layout_kscan_callback` → msgq + `k_work_submit(&msg_processor.work)` → **sysworkq** → `zmk_physical_layouts_kscan_process_msgq` raises with `.timestamp = k_uptime_get()` **at raise time** (physical_layouts.c:178-182).
- Peripheral (left half) key: BT notify on BT RX thread → `split_central_notify_func` stamps `.timestamp = k_uptime_get()` at receipt (central.c:263) → msgq + `k_work_submit(&peripheral_event_work)` → **sysworkq** → `peripheral_event_work_callback` raises (central.c:71-77). Timestamp is slightly OLDER than raise time.
- Combo timer: `k_work_schedule(&timeout_task, …)` → `k_sys_work_q` (Zephyr `k_work_schedule` work.c:978 → `k_work_schedule_for_queue(&k_sys_work_q…)`); expiry callback `work_timeout` (work.c:810) runs in the RTC ISR and only *submits* the handler to the sysworkq.
- `k_work_submit` → `k_sys_work_q` (work.c:405-409). Therefore key events (both halves) and `TH` are serialized FIFO on the same thread.

### 🕰️ Timer arithmetic

- `k_uptime_get()` = `k_ticks_to_ms_floor64(ticks)` (kernel.h:1757). Event timestamps and `timeout_at` are integer ms (floored).
- `K_MSEC(n)` = `k_ms_to_ticks_ceil64(MAX(n,0))` ticks (sys_clock.h:121). `K_MSEC(≤0)` = `K_NO_WAIT` → immediate submit (work.c:894).
- `z_add_timeout` relative: `dticks = ticks + 1 + elapsed()` (timeout.c) → fires at least `n` full ms plus one tick after the current tick boundary.
- Board (32768 Hz, tick = 30.5 µs): `K_MSEC(11)` = 361 ticks → fires 362 ticks = 11.047 ms after the tick boundary in which it was scheduled. Because the scheduling instant has an unknown sub-ms fraction f ∈ [0,1) ms, **timer-path deliveries happen at `timeout_at + δ`, δ ∈ [0.05, 1.05] ms** (plus sysworkq queueing latency). The guard `k_uptime_get() < timeout_task_timeout_at` (combo.c:473) can therefore never trip for a normally scheduled timer; it only trips on the phantom-timer path (see ⚠️ H2).
- native_posix (1000 Hz): every `K_MSEC(n)` fires exactly n+1 ms later. Mock kscan (`kscan_mock.c`): an event's `msec` is the gap *after* it, and event 0's `msec` is also the boot delay; observed gaps are `msec+1`. The mock also emits one garbage trailing event (reads `events[len]`), harmless (release of an unpressed key).

### The three Zephyr rules the engine silently depends on (work.c, 3.5.0)

1. `k_work_schedule_for_queue` (work.c:954-977) schedules **only if `(busy & ~K_WORK_RUNNING) == 0`**, i.e. item is idle or currently running. If it is `DELAYED`, `QUEUED` or `CANCELING`, it does nothing and returns **0** (doc: kernel.h:3630 "@retval 0 if work was already scheduled or submitted").
2. `k_work_cancel_delayable` (work.c:1026) → `cancel_delayable_async_locked` → `unschedule_locked` (aborts a pending timeout) then `cancel_async_locked` (work.c:495-510): if the item is still busy (i.e. RUNNING because we are inside its own handler) it sets `K_WORK_CANCELING_BIT`.
3. `work_queue_main` (work.c:672-684) clears `RUNNING` and finalises `CANCELING` **only after the handler returns**.

combo.c:417 `if (k_work_schedule(...) >= 0) timeout_task_timeout_at = first_timeout;` accepts return value 0 as success → **phantom timer** whenever rule 1 refuses.

---

## ⚙️ Engine mechanics needed to read the traces

- `combo_lookup[pos][]` sorted shortest `key_position_len` first, then `virtual_key_position` (combo.c:93-126). H (36 keys) is always LAST in every key's list; R/Q (2 keys) precede it.
- `candidates[]` is created ONLY in `SETUP` at the first key press of a burst (combo.c:424-428) with `timeout_at = first_key.timestamp + timeout_ms` for each combo on that key that is active on `zmk_keymap_highest_layer_active()` and not a quick-tap. **Later keys never add candidates; they only intersect** (`FC`) and expire (`FTO`, strict `timeout_at > ts` keeps → a candidate with `timeout_at == ts` is already expired).
- `PSD` decision (combo.c:435-453), after `UTT` and `CAP`:
  - `num == 0` → `CLEAN` now (everything buffered is flushed, this key included).
  - `num == 1` and that combo fully pressed → `fully_pressed_combo = it; CLEAN` (fires now).
  - `num ≥ 2` and `candidates[0]` fully pressed → only mark `fully_pressed_combo`; **no fire** until `CLEAN` happens for another reason (timer chain reaching 0 candidates, or any key event).
  - otherwise → keep buffering, return `CAPTURED`.
- `CLEAN` (397-405): cancel timer → `clear_candidates` → if `fully_pressed_combo` then `ACT` (moves that combo's keys out of `pressed_keys`, presses behavior with ts of its first key) → `RPK`.
- `RPK` (273-289): `pressed_keys[0]` via `ZMK_EVENT_RELEASE` (continues to tap_dance → keymap), `pressed_keys[1..]` via `ZMK_EVENT_RAISE` (re-enter combo as new first keys, original timestamps). Nested `PSD` calls happen INSIDE `RPK`.
- `PSU` (456-470): always `CLEAN` first (flush everything), then `release_combo_key`; if `CLEAN` re-raised ≥ 1 key (`released_keys > 1`) the key-up is re-raised too (`CAPTURED`), else it bubbles.
- `TH` (472-481): guard; `FTO(timeout_task_timeout_at)`; `CLEAN` only if 0 remain; `UTT` (reschedules to the next candidate's `timeout_at` — allowed here because the item is RUNNING but not CANCELING… unless `CLEAN` ran in this same invocation).
- `UTT` (407-420): no-op if `first_timeout == timeout_task_timeout_at` (note: `CLEAN` never resets `timeout_task_timeout_at`, so a stale value can suppress scheduling if a later `first_timeout` happens to equal it — theoretical, see H4).

---

## 🧪 Method

- Hand-executed every scenario against the code above.
- Then confirmed empirically: 4 native_posix builds (`native_posix_64`, Zephyr 3.5.0, same combo.c) built and run **inside the container's `/tmp/a2`** (no file touched under `zmk/`, `zmk-config/` or `zmk-upstream/`; `git status` of `zmk` clean afterwards). Keymaps + full logs saved at `/private/tmp/claude-501/-Users-flo-Work-Private-Dev-Keyboard-zmk-config/56bdead7-aa9e-4bbc-b13e-b1255ed79094/scratchpad/a2-exp/` (`run-main-H.log`, `run-main-noH.log`, `run-s4-H.log`, `run-s4-noH.log`).
  - 4-key mock matrix: X = pos 0 (`&kp A`), Y = pos 1 (`&kp B`), Z = pos 2 (`&kp C`), W = pos 3 (`&kp D`). R = `<0 2>` 16 ms `&kp E`; Q (S4 builds only) = `<1 3>` 30 ms `&kp F`; H = `<0 1 2 3>` 11 ms `&none`.
  - Observed times below are native_posix (timer path = timeout + 1 ms). Board equivalent = timeout + δ.
- In every trace: "Result" lines give wall time of delivery, the path, and the timestamp the event carries.

---

## 📜 Scenario traces

### S1 — X at 0, Y at 5

**Without H**

- t=0 `PSD(X)`: candidates empty → `SETUP(X)` → `[R: timeout_at 16]` → `UTT` schedules timer for 16 → `CAP(X)` → num=1, not fully pressed → `CAPTURED`.
- t=5 `PSD(Y)`: `FTO(5)` keeps R → `FC(Y)`: Y's lookup is empty → 0 matches → `UTT`: no candidates → `timeout_task_timeout_at=0`, `k_work_cancel_delayable` (DELAYED → aborted) → `CAP(Y)` (`pressed_keys=[X,Y]`) → case 0 → `CLEAN` → `RPK`: `RELEASE X` → tap_dance → keymap; `RAISE Y` → activity → hold_tap → `PSD(Y)` → `SETUP(Y)` = 0 → `BUBBLE` → tap_dance → keymap. Return `CAPTURED` for the original Y event.
- **Result**: X → keymap at wall 5 `[NEWKEY]`, ts 0. Y → keymap at wall 5 `[RERAISE-BUBBLE]`, ts 5. Both "at once", in order.
- Observed: X@6, Y@12 → both delivered @12.

**With H**

- t=0 `PSD(X)`: `SETUP(X)` → `[R:16, H:11]` (sorted shortest-first) → `UTT` timer for 11 → `CAP(X)` → num=2, not fully pressed → `CAPTURED`.
- t=5 `PSD(Y)`: `FTO(5)` keeps both → `FC(Y)`: Y's lookup `[H]` → R skipped (shorter), H matches → `candidates=[H:11]` → `UTT`: first_timeout 11 == 11 → no-op → `CAP(Y)` → num=1, H not fully pressed (36 ≠ 2) → `CAPTURED`.
- t=11+δ `TH`: guard ok → `FTO(11)`: H (11 > 11 false) dropped → 0 → `CLEAN`: `k_work_cancel_delayable` on itself while RUNNING → **CANCELING set**; `clear_candidates`; `RPK` (count 2): `RELEASE X` → keymap (X pressed, ts 0). `RAISE Y` → `PSD(Y)`: `SETUP(Y)` → `[H: timeout_at 5+11=16]` → `UTT`: 16 ≠ 11 → `k_work_schedule(K_MSEC(16-11))` → **refused (CANCELING), returns 0** → `timeout_task_timeout_at=16` recorded anyway → `CAP(Y)` → `CAPTURED`. Back in `TH`: `UTT`: 16 == 16 → no-op. Handler exits, CANCELING cleared. **No timer is pending.**
- Next position event flushes Y. If X is released at 60: `PSU(X)` → `CLEAN` → `RPK`: `RELEASE Y` → keymap (Y pressed, ts 5) → `release_combo_key` false → `released_keys == 1` → X-up bubbles → keymap (X released, ts 60).
- **Result**: X → keymap at wall 11+δ `[TIMER]`, ts 0. **Y → keymap at the next position event** `[KEYUP]`/`[NEWKEY]`, ts 5. Order preserved, latency unbounded by the engine.
- Observed: X@6, Y@12; X delivered @18; Y delivered @73 (= X release), X-up @73.

### S2 — X at 0, Y at 13

**Without H**: identical to S1 (13 < 16): X and Y both delivered at wall 13 (`[NEWKEY]`, `[RERAISE-BUBBLE]`), ts 0 and 13. Observed: X@415, Y@429 → both @429.

**With H**

- t=0: as S1 → `[R:16, H:11]`, timer 11.
- t=11+δ `TH`: `FTO(11)` drops H, keeps R → 1 remains → no `CLEAN` → `UTT`: 16 ≠ 11 → `k_work_schedule` (item RUNNING, not CANCELING → allowed) → timer for 16.
- t=13 `PSD(Y)`: `FTO(13)` keeps R → `FC(Y)`: `[H]` vs `[R]` → 0 → `UTT`: cancel (DELAYED → aborted), `timeout_task_timeout_at=0` → `CAP(Y)` → case 0 → `CLEAN` → `RPK`: `RELEASE X` → keymap (ts 0). `RAISE Y` → `PSD(Y)` → `SETUP(Y)` → `[H: 24]` → `UTT` → `k_work_schedule` (item idle → **accepted**) → timer 24 → `CAP(Y)` → `CAPTURED`.
- t=24+δ `TH`: `FTO(24)` → 0 → `CLEAN` → `RPK`: `RELEASE Y` → keymap (ts 13). (`CLEAN`'s self-cancel sets CANCELING again, harmless: nothing else is scheduled in this invocation; `UTT` → LLONG_MAX → `timeout_task_timeout_at=0`.)
- **Result**: X → wall 13 `[NEWKEY]`, ts 0. Y → wall 24+δ `[TIMER]`, ts 13. This is the hack's documented 7-step behaviour.
- Observed: X@415, TH@427 (remaining 1), Y@429 → X @429, Y @441.

### S3 — X at 0, Y at 20

**Without H**

- t=16+δ `TH`: `FTO(16)` drops R → 0 → `CLEAN` → `RELEASE X` → keymap (ts 0). No re-raise.
- t=20 `PSD(Y)`: `SETUP(Y)` = 0 → `BUBBLE`.
- **Result**: X → wall 16+δ `[TIMER]`, ts 0. Y → wall 20 `[IMMEDIATE]`, ts 20. Observed: X@832 → @849; Y@853 → @853.

**With H**

- t=11+δ `TH`: drops H, keeps R, reschedules 16. t=16+δ `TH`: drops R → `CLEAN` → `RELEASE X` (ts 0).
- t=20 `PSD(Y)`: `SETUP(Y)` → `[H: 31]` → timer 31 → `CAPTURED`. t=31+δ `TH` → `CLEAN` → `RELEASE Y` (ts 20).
- **Result**: X → wall 16+δ `[TIMER]`, ts 0. Y → wall 31+δ `[TIMER]`, ts 20. Observed: X@832 → @849 (TH@844 then @849); Y@853 → @865.

### S4 — X at 0, Y at 30, Y ∈ Q = (Y, W) timeout 30

**Without H**

- X: as S3 → wall 16+δ `[TIMER]`, ts 0.
- t=30 `PSD(Y)`: `SETUP(Y)` → `[Q: 60]` → timer 60 → `CAPTURED`. t=60+δ `TH` → `CLEAN` → `RELEASE Y`.
- **Result**: Y → wall 60+δ `[TIMER]`, ts 30. Observed (s4-noH): X@31 → @48; Y@62 → @93.

**With H**

- X: as S3-with-H → wall 16+δ `[TIMER]`.
- t=30 `PSD(Y)`: `SETUP(Y)` → `[Q: 60, H: 41]` → timer 41. t=41+δ `TH`: drops H, keeps Q → reschedule 60 (allowed). t=60+δ `TH`: drops Q → `CLEAN` → `RELEASE Y`.
- **Result**: Y → wall 60+δ `[TIMER]`, ts 30. H does not shorten anything; **the key waits for its LAST candidate**. Observed (s4-H): X@31 → TH@43 (1 left) → @48; Y@62 → TH@74 (1 left) → @93.

**S4b (extra, observed): X at 0, Y at 5, Y ∈ Q**

- Without H: at Y: `FC(Y)`: `[Q]` vs `[R]` → 0 → `CLEAN` → X `[NEWKEY]` at 5; `RAISE Y` → `SETUP(Y)` → `[Q: 35]` → timer accepted (inside `PSD`, item idle) → Y `[TIMER]` at 35+δ. Observed: X@485,Y@491 → X @491, Y @522.
- With H: at Y: `FC(Y)` → `[H]` → `CAPTURED`. t=11+δ `TH` → `CLEAN` (CANCELING) → `RELEASE X`; `RAISE Y` → `SETUP(Y)` → `[Q: 35, H: 16]` → `k_work_schedule` refused → **Y stranded** despite having a live real candidate. Observed: X @497; Y @572 (= X release).

### S5 — X at 0, Y at exactly 11 (tie with H's timeout)

**Without H**: 11 < 16 → identical to S1: both at wall 11. Observed: X@1256, Y@1267 → both @1267.

**With H** — two possible orderings on the board (both run on the sysworkq; which is enqueued first depends on sub-ms phase, see 🤔 G1). Both give the SAME result for this scenario:

- **Ordering A — key work runs before the timer work** (this is what native_posix did: Y@1267 = X.ts+11, timer due at 1268):
  - `PSD(Y)`: `FTO(11)`: H (11 > 11 false) dropped, R kept → `FC(Y)`: `[H]` vs `[R]` → 0 → `UTT`: LLONG_MAX → cancel (item DELAYED → aborted; or QUEUED → dequeued, `queue_remove_locked`) → `CAP(Y)` → case 0 → `CLEAN` → `RELEASE X` (ts 0) → keymap; `RAISE Y` → `SETUP(Y)` → `[H: 22]` → schedule accepted (item idle) → `CAPTURED`.
  - t=22+δ `TH` → `CLEAN` → `RELEASE Y` (ts 11).
- **Ordering B — timer work runs first** (observed in S5b where Y arrived 12 ms after X and `TH` ran in the same ms): `TH`: drops H, keeps R, reschedules 16 → then `PSD(Y)`: R kept, `FC(Y)` → 0 → cancel (DELAYED → aborted) → `CLEAN` → `RELEASE X`; `RAISE Y` → `[H: 22]` → accepted.
- **Result (both)**: X → wall 11 `[NEWKEY]`, ts 0. Y → wall 22+δ `[TIMER]`, ts 11. Observed S5a: X @1267, Y @1279. Observed S5b (gap 12): X @1682, Y @1694.
- ⚠️ The tie is NOT benign when X and Y share a still-live longer candidate (e.g. a 3-key combo `X Y Z` timeout 18): Ordering A → `FTO(11)` drops H, keeps `XYZ:18` → `FC(Y)` keeps it → `UTT`: 18 ≠ 11 → `k_work_schedule` while the item is DELAYED/QUEUED → **refused**, phantom 18 → timer fires at 11+δ → `TH` guard `k_uptime_get() < 18` → returns **without rescheduling** → X and Y stranded until the next position event. Ordering B is fine (reschedule from inside `TH` is allowed). Flo has 12 combos with ≥3 keys on alpha layers (`hands_down/combos.dtsi`, `h_digraphs/combos.dtsi`, e.g. `RB2 RB3 RB4`, `LB3 LB2 LB1`, `LM3 LM2 LM1`) — see H2.

### S6 — X at 0, X released at 8, Y at 20

**Without H and with H (same shape)**

- t=8 `PSU(X)`: `CLEAN` → cancel timer (DELAYED → aborted) → `RPK`: `RELEASE X` → keymap (X pressed, ts 0) → `release_combo_key(X)` false (no active combos) → `released_keys == 1` → `BUBBLE` → the X-up event continues → keymap (X released, ts 8).
- t=20 `PSD(Y)`: without H → `[IMMEDIATE]`; with H → `[H: 31]` → `[TIMER]` at 31+δ.
- **Result**: X down → wall 8 `[KEYUP]`, ts 0; X up → wall 8 (bubbled, ts 8), back-to-back in the same call stack. Y → wall 20 `[IMMEDIATE]` (no H) or wall 31+δ `[TIMER]` (with H), ts 20.
- Observed: X@2085, X-up@2094 → X down+up both @2094; Y@2107 → @2107 (noH) / @2119 (H).
- Note: `timeout_task_timeout_at` stays at its stale value (11 or 16) after `CLEAN`; harmless here because Y's `first_timeout` differs (see H4).

### S7 — X at 0, Z at 6 (completes R)

**Without H**

- t=6 `PSD(Z)`: `FTO(6)` keeps R → `FC(Z)`: `[R]` vs `[R]` → 1 → `UTT`: 16 == 16 no-op → `CAP(Z)` → num=1 and `candidate_is_completely_pressed(R)` (2 == 2) → `fully_pressed_combo=R` → `CLEAN`: cancel timer; `ACT(R)`: `store_active_combo`, `move_pressed_keys_to_active_combo` (X,Z leave `pressed_keys`), `press_combo_behavior(R, ts of X = 0)` → `behavior_keymap_binding_pressed` with `position = R.virtual_key_position` (= `ZMK_KEYMAP_LEN + n`), `timestamp = 0`; `RPK` → nothing left. Return `CAPTURED`.
- Release: first of X/Z up (say X at 50) → `PSU`: `CLEAN` (nothing) → `release_combo_key(X)`: found in active R; `all_keys_pressed` true and `slow_release` false → `release_combo_behavior(R, ts 50)` → `HANDLED` (X-up never reaches keymap). Z up later → matches, `all_keys_released` → `deactivate_combo` → `HANDLED`.
- **Result**: R fires at wall 6 (immediately on completion), ts 0. X and Z never reach the keymap. H: n/a.
- Observed: X@2469, Z@2476 → `position 4 keycode E` pressed @2476, released @2537 (X up).

**With H**

- t=6 `PSD(Z)`: `FTO(6)` keeps both → `FC(Z)`: Z's lookup `[R, H]` → both match → num=2 → `UTT` no-op → `CAP(Z)` → default branch: `candidates[0]` = R is fully pressed → `fully_pressed_combo=R`, **but no `CLEAN`** → `CAPTURED`. R is armed but not fired.
- t=11+δ `TH`: `FTO(11)` drops H, keeps R → 1 remains → no `CLEAN` → `UTT` → reschedule 16 (allowed: RUNNING, not CANCELING). H is now gone; nothing re-checks "fully pressed with one candidate".
- t=16+δ `TH`: `FTO(16)` drops R → 0 → `CLEAN` → `ACT(R)` → R pressed with ts 0 at wall 16+δ.
- Any key event between 6 and 16 (e.g. X up at 12) triggers `CLEAN` earlier → R fires then; then `release_combo_key` releases it in the same call (press + release back-to-back).
- **Result**: R fires at wall 16+δ `[TIMER]` (10 ms later than without H), ts 0. **H's effect on real combos: they fire at their `timeout-ms`, never at completion.** H itself is silently dropped as an expired candidate at 11 (it can only "fire" with 36 keys down).
- Observed: Z@2476 (remaining 2, captured) → TH@2481 (1 left) → TH@2486 → E pressed @2486; released @2537.

### S8 — Y (in no real combo) at 0, then X at 20

**Without H**

- t=0 `PSD(Y)`: `SETUP(Y)` = 0 → `BUBBLE` → keymap immediately.
- t=20 `PSD(X)`: `SETUP(X)` → `[R: 36]` → timer 36 → `CAPTURED`. t=36+δ `TH` → `CLEAN` → `RELEASE X`.
- **Result**: Y → wall 0 `[IMMEDIATE]`, ts 0. X → wall 36+δ `[TIMER]`, ts 20. Observed: Y@2879 → @2879; X@2900 → @2917.

**With H**

- t=0 `PSD(Y)`: `SETUP(Y)` → `[H: 11]` → timer 11 → `CAPTURED`. t=11+δ `TH` → drops H → 0 → `CLEAN` → `RELEASE Y` (ts 0). No re-raise, so the CANCELING flag set by `CLEAN` has no victim.
- t=20 `PSD(X)`: `SETUP(X)` → `[R: 36, H: 31]` → timer 31. t=31+δ: drops H, keeps R → reschedule 36. t=36+δ: drops R → `CLEAN` → `RELEASE X` (ts 20).
- **Result**: Y → wall 11+δ `[TIMER]`, ts 0. X → wall 36+δ `[TIMER]`, ts 20. Observed: Y@2879 → @2891; X@2900 → TH@2912 → @2917.

### S9 (extra) — X at 0, Y at 5, W at 9 (three keys inside the hack window; W only in H)

- With H, observed (X@3303, Y@3309, W@3314 — W landed exactly on the tie): `PSD(W)`: `FTO(3314)` drops H → 0 → `CLEAN` → `RELEASE X` @3314 `[NEWKEY]`; `RAISE Y` → `[H: 3320]` → **accepted** (inside `PSD`, item idle) → captured; `RAISE W` → `FTO` keeps → `FC(W)` → H → captured `[Y, W]`. TH@3321 → `CLEAN` (CANCELING) → `RELEASE Y` @3321 `[TIMER]`; `RAISE W` → `[H: 3325]` → **refused** → W stranded → delivered @3375 (X release).
- Shows both mechanisms in one burst: a re-raise inside a key event gets a real timer; a re-raise inside `TH` does not.
- Without H: X,Y @3309; W @3314 `[IMMEDIATE]`.

### S10 (extra) — X at 0, Y at 5, W at 40 (stranded key flushed by a later press)

- With H, observed (X@3728, Y@3734, W@3770): X @3740 `[TIMER]`; Y stranded (phantom 3745); `PSD(W)`: `FTO(3770)` drops Y's H → 0 → `CLEAN` → `RELEASE Y` @3770 `[NEWKEY]`, ts 3734; `RAISE W` → `[H: 3781]` → accepted → W @3782 `[TIMER]`.
- Without H: X,Y @3734; W @3770 `[IMMEDIATE]`.

---

## ⚠️ Hazards found (all PROVEN by source; H1 also observed)

- **H1 — Stranded re-raised key (the CANCELING trap).** `CLEAN` (combo.c:398) inside `TH` → CANCELING → every `k_work_schedule` from nested `PSD` calls in that invocation is refused (work.c:965 test) → phantom `timeout_task_timeout_at` (combo.c:417-418). Trigger condition: `TH` reaches 0 candidates with `pressed_keys_count ≥ 2` and the re-raised key has ≥1 candidate on the current layer. **With H this is every 2-key burst tighter than 11 ms on an alpha/AK layer.** Recovery: next position event of any kind (`PSD` → `FTO`/`FC` → `CLEAN`, or `PSU` → `CLEAN`). Observed S1, S4b, S9, S10.
- **H2 — Lost timer when `first_timeout` changes while a timer is pending.** `UTT` from `PSD` while the item is DELAYED/QUEUED → refused → phantom value → when the old timer fires, `TH` guard (combo.c:473) returns without `UTT` → nothing pending. Triggers: (a) S5-style tie where a longer shared candidate survives `FTO` (3-key combos, Ordering A only); (b) even without H: key in two combos with different timeouts, second key matches only the longer one (e.g. X ∈ {R:16, S:30}, key in S arrives at 5 → phantom 30, timer at 16 returns early). Not observed (not in the scenario set) → test T11/T12 below.
- **H3 — Real combos never fire early while a longer candidate is alive.** `PSD` default branch only marks `fully_pressed_combo` (combo.c:448-452). With H, every real combo fires at its own `timeout-ms` (+δ) or at the next key event. Observed S7 (16 vs 6).
- **H4 — Stale `timeout_task_timeout_at`.** `CLEAN` cancels the timer but never zeroes `timeout_task_timeout_at`; `UTT` skips scheduling when the new `first_timeout` equals the stale value (combo.c:409). Needs an exact ms coincidence between an old and a new `timeout_at`; only conceivable for re-raised keys with old timestamps. Theoretical; not traced.
- **H5 — `CAP` capacity guard uses the wrong constant.** combo.c:263 compares `pressed_keys_count` to `CONFIG_ZMK_COMBO_MAX_COMBOS_PER_KEY` (30) although `pressed_keys[]` is sized `MAX_KEYS_PER_COMBO` (36). Safe on this board (30 < 36); a 31st simultaneously buffered key would bubble unbuffered. Irrelevant to the page.

---

## 🤔 Guesses and ambiguities (flagged)

- **G1 — Same-ms ordering of timer vs key on the board.** Both are sysworkq items. The timer item is submitted from the RTC ISR at `timeout_at` + δ; a local key item is submitted from the matrix-scan work (5 ms debounce, 1 ms scan) and stamped when it *runs*; a peripheral key item is stamped in the BT RX thread and raised when the sysworkq runs it. For S5 as specified the outcome is ordering-invariant (proved above). For 3-key combos it is not (H2a). native_posix is deterministic (key-first at a true tie: S5a; timer-first when the key is 1 ms late: S5b), so a test can only pin one ordering per timing.
- **G2 — Sysworkq latency.** All "wall" times assume the queue is drained promptly. Macro steps (`behavior_queue.c`, delayed work on the same queue) and BLE work can delay both key processing and `TH` by the length of one work item; they cannot reorder them relative to each other except through submission order.
- **G3 — Cross-half skew.** A left-half key's timestamp is taken at BT receipt (central.c:263), i.e. after BLE connection-interval latency (typically 7.5–15 ms after the physical press), whereas a right-half key is stamped after 5 ms debounce. Two physically simultaneous presses on different halves can be seen 5–10 ms apart by the engine. Not modelled in the scenarios.
- **G4 — "t = 0" is the event timestamp, not the physical press.** Debounce (5 ms) precedes it. Every number on the page is relative to the debounced event.
- **G5 — Layer at first press.** H is a candidate only if `zmk_keymap_highest_layer_active()` at `SETUP` time is in `l_alpha_aks`. On nav/num/mod layers H does not exist and every trace collapses to the "without H" column. Re-raised keys re-evaluate the layer at re-raise time.
- **G6 — `require-prior-idle-ms = -1`.** `is_quick_tap` (combo.c:141) reduces to `last_tapped_timestamp - 1 > event.ts`. Never true for in-order events; could be true for a re-raised (old-timestamp) key if a macro-emitted keycode (stamped at execution, `behavior_queue.c:35`) landed in between. Not traced.

---

## 🧪 Test recipes (native_posix)

Common harness (`app/run-test.sh` style): test dir with `native_posix_64.keymap` (+ optional `native_posix_64.conf`, picked up as a Kconfig fragment; 13 upstream tests do this). Mock timing: `ZMK_MOCK_PRESS(row,col,msec)` = gap AFTER the event, observed gap = msec+1; event 0's msec is also the boot delay. Timer deliveries = timeout+1 ms. Use `events.patterns` that keeps the log timestamp, e.g. `s/^\[00:00:0\([0-9.]*\),[0-9]*\] <dbg> zmk: \(on_keymap_binding_pressed\|on_keymap_binding_released\|release_pressed_keys\|filter_timed_out_candidates\): /\1 \2 /p`, so the snapshot pins times, not just order. Positions in the 2×2 mock: pos = row*2+col. Combo virtual position for the n-th combo = 4+n. A 36-key H is not needed to reproduce H's mechanics; a 4-key H = `<0 1 2 3>` with `timeout-ms = <11>` behaves identically (only `key_position_len` matters, never the count). To mirror the board exactly, add `CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO=36` in `native_posix_64.conf` and a bigger mock matrix; not required for any claim here.

The ready-made keymaps in `scratchpad/a2-exp/{main-H,main-noH,s4-H,s4-noH}/native_posix_64.keymap` already encode S1–S10 with 300 ms separators and produced the observed times quoted above.
