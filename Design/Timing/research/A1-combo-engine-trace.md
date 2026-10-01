# 🧩 A1 — Combo engine trace (`app/src/combo.c`, fork = upstream 6e03a0bb)

> Scope: the ZMK combo engine as it runs on Flo's right (central) half. Every claim is tagged **PROVEN** (read in the source that built the board, or in the compiled build artefacts) or **INFERRED** (reasoning that a test should settle).
> Paths: `zmk/` = `/Users/flo/Work/Private/Dev/Keyboard/zmk`, `cfg/` = `/Users/flo/Work/Private/Dev/Keyboard/zmk-config/config`, `zephyr/` = `/workspaces/zmk/zephyr` inside the `zmk-devcontainer` (Zephyr 3.5.0, the tree that built the firmware).

---

## 🎯 TL;DR — what the page must say (and what it must not)

- 🔒 **Provenance PROVEN:** `zmk/app/src/combo.c` is byte-identical to upstream at fork point 6e03a0bb (`git diff --stat 6e03a0bb HEAD -- app/src app/include app/Kconfig app/dts` is empty). Its last upstream change is 7d1f84e3 (2024-05-14).
  - ⚠️ The scratchpad `zmk-upstream/` checkout is at 5b51501 (2026-09-26): its `combo.c` is a bitmask rewrite. **It is NOT the engine on the board.** Every line number below is the fork file.
- 🧠 **Core model:** a position PRESS is *captured* (withheld from the keymap) iff, after filtering, ≥1 candidate combo remains. Captured presses sit in `pressed_keys[]` until `cleanup()` flushes them. `cleanup()` runs on: every RELEASE of any position (`position_state_up`), a press that leaves 0 candidates, a press that completes the *only* candidate, and the timer handler when *all* candidates have expired.
- ⏱️ **A key held alone is delayed by the LONGEST timeout among its candidates, not the shortest.** On alpha: `LT4/RT0/LM4/LB4/LH*/RH0` → 11 ms (hack only); most letters → 16 ms; `RM1..RM4` → 18 ms. The 11 ms "hack" timeout only sets the *first* rung of the timer ladder.
- 🔁 **Flush order is deterministic:** first buffered key is *released* into the listeners after combo (skips hold-tap!), every later buffered key is *re-raised from listener 0* (goes through hold-tap and combo again, synchronously, keeps its ORIGINAL timestamp, gets a fresh candidate set anchored to that original timestamp).
- 🐛 **Three timer defects, all real on the board, one invisible on `native_posix_64`:**
  1. **32-bit `LONG_MAX` poison (PROVEN, board-only):** `first_candidate_timeout()` returns `LONG_MAX` (= 2147483647 on `arm-zephyr-eabi-gcc`, `__LONG_MAX__ 0x7fffffffL`), `update_timeout_task()` compares against `LLONG_MAX` → the "cancel" branch never runs → after every timer-driven flush the delayable is (re)scheduled ~24.8 days out. Because `k_work_schedule()` is a no-op on an already-scheduled item, **the next key pressed before any release gets NO live timer and is delivered only by the next press/release.** `native_posix_64` has `long` = 64 bit → branch works → tests there model an engine the board does not run.
  2. **Deadline can never move later (PROVEN, reproducible on `native_posix_64`):** when a 2nd key filters out the shortest candidate, `k_work_schedule()` silently keeps the old deadline; the handler fires early, sees `now < timeout_task_timeout_at`, returns *without rescheduling* → stuck until next event.
  3. **`require-prior-idle-ms = -1` + stale timestamps (PROVEN mechanism, INFERRED reach):** a *re-raised* key whose original timestamp is ≥2 ms older than the last synchronous `&kp` press (macro-driven keys like `&ak` press `&kp` with `timestamp = k_uptime_get()`) is classed `is_quick_tap` for **every** combo → 0 candidates → bypasses the engine → delivered back-to-back with the key before it. This defeats the AK-consistency hack exactly in its "minor caveat" window (2nd key ≤ 9 ms after the 1st).
- 🧪 Ordering to the keymap is always **press order preserved, releases interleaved at flush points**; timestamps carried to behaviors are always the ORIGINAL physical timestamps (`copy_raised_*` copies the struct). Combo behaviors are pressed with the FIRST combo key's timestamp (`combo.c:349`).

---

## 📦 Data structures & limits (`combo.c:29-83`, `Kconfig:478-492`, `zmk,combos.yaml`)

```
combo_cfg            {key_positions[MAX_KEYS_PER_COMBO], key_position_len, behavior, timeout_ms,
                      require_prior_idle_ms, slow_release, virtual_key_position, layers_len, layers[]}   :29-43
active_combo         {combo*, key_positions_pressed_count, key_positions_pressed[MAX_KEYS_PER_COMBO]}    :45-53
combo_candidate      {combo*, timeout_at}                                                                :55-61
pressed_keys[MAX_KEYS_PER_COMBO] + pressed_keys_count        (the capture buffer, FIFO by press order)   :63-65
candidates[MAX_COMBOS_PER_KEY]                               (NULL-terminated, sorted len↑ then vkp↑)   :67
fully_pressed_combo                                          (single pointer, latest completed cand.)    :69
combo_lookup[ZMK_KEYMAP_LEN][MAX_COMBOS_PER_KEY]             (per position, same sort order)             :71
active_combos[MAX_PRESSED_COMBOS] + active_combo_count       (fired combos with ≥1 key still down)       :74-75
timeout_task (ONE k_work_delayable) + timeout_task_timeout_at (int64 deadline, 0 = none)                :77-78
last_tapped_timestamp / last_combo_timestamp                 (require-prior-idle bookkeeping)            :81-83
```

- **Sort order (PROVEN, `initialize_combo` :93-126):** per position, combos are inserted shortest `key_position_len` first, ties by `virtual_key_position` = `ZMK_KEYMAP_LEN + ZMK_KEYMAP_SENSORS_LEN + __COUNTER__` (:524) = **devicetree definition order**. `candidates[0]` is therefore "shortest, then earliest-defined".
- **Limits on Flo's board (PROVEN, `build/right/zephyr/.config:177-179`, `cfg/corne.conf:39-44`):** `MAX_PRESSED_COMBOS=20`, `MAX_COMBOS_PER_KEY=30`, `MAX_KEYS_PER_COMBO=36`, `ZMK_KEYMAP_LEN=36` (`devicetree_generated.h:23531`, 5-col transform), 32 layers. Actual usage: max 6 combos on one position (`RM1`,`RM2`,`LM2`,`LB1`), max 36 keys (the hack).
- **What happens when exceeded:**
  - `MAX_COMBOS_PER_KEY` at init → `LOG_ERR("Too many combos for key position …")`, `-ENOMEM` (:119-123) **but `INITIALIZE_COMBO` discards the return** (:530,:536) → silent partial registration: the combo is in the lookup of the positions processed before the full one, absent from the rest. Runtime effect: never a candidate when the full position is pressed first; filtered out when it is pressed later.
  - Position ≥ `ZMK_KEYMAP_LEN` → `LOG_ERR`, `-EINVAL`, same silent discard (:96-98).
  - `MAX_KEYS_PER_COMBO` → build-time: `.key_positions = DT_PROP(...)` initialiser overflow (GCC "excess elements" diagnostic; INFERRED whether it is fatal under Zephyr's flags). Flo's 36 = exact fit.
  - `MAX_PRESSED_COMBOS` at runtime → `store_active_combo` `LOG_ERR` + NULL (:335-338) → `activate_combo` **does not fire the combo, flushes the keys as individual presses instead** (:343-346).
  - Capture buffer full → `capture_pressed_key` returns `BUBBLE` and does NOT store (:263-264). **Guard uses `MAX_COMBOS_PER_KEY` (30), not `MAX_KEYS_PER_COMBO` (36)** — an upstream typo; harmless here because 30 < 36 (no overflow), but it caps the buffer at 30 keys, so the 36-key hack can never be "completely pressed" (:216) — irrelevant, it is designed never to fire.
- **Binding defaults (PROVEN, `zmk/app/dts/bindings/zmk,combos.yaml`):** `timeout-ms` 50, `require-prior-idle-ms` **-1**, `layers` `[-1]` (= all), `slow-release` false. Flo sets timeout and layers on every combo (`preprocessor_macros.c:32`), never prior-idle or slow-release → compiled values: prior-idle `-1` everywhere (`devicetree_generated.h:15160`, `:20318`), slow-release absent everywhere.

---

## 🔀 Event-manager semantics the engine relies on (`event_manager.c`, `event_manager.h`)

- Listener table = link order of `.event_subscription` (`event_manager.c:20-45`). **PROVEN from the right-half map (`build/right/zephyr/zmk.map:15991-16039`)** for `zmk_position_state_changed`:
  `activity → behavior_hold_tap → combo → behavior_tap_dance → keymap`
- Return codes (`event_manager.h:22-24`): `BUBBLE` continue to next listener; `HANDLED`/`CAPTURED` stop (`:30-38`).
- `ZMK_EVENT_RAISE(ev)` → `handle_from(ev, 0)`: **restarts at listener 0** (`:47`). Synchronous, nested inside the caller.
- `ZMK_EVENT_RELEASE(ev)` → `handle_from(ev, ev->last_listener_index + 1)` (`:79-81`): resumes **after the listener that captured it** — for combo that means `tap_dance → keymap`, **hold-tap is skipped**.
- `copy_raised_*` (`event_manager.h:49-52`) copies the whole event struct incl. `header.last_listener_index` (set at `:27` before the callback runs) and `data.timestamp`. **Buffered keys keep their original timestamps forever.**
- Thread model (PROVEN): local kscan events are raised from the system-workqueue work `zmk_physical_layouts_kscan_process_msgq` with `timestamp = k_uptime_get()` **at processing time** (`physical_layouts.c:161-183`, `:181`). Peripheral (left-half) events: timestamped `k_uptime_get()` **on the central at BLE notification** (`split/bluetooth/central.c:255-266`), queued, raised from `peripheral_event_work` (`:72-78`). The combo timer is also a system-workqueue item → **all combo code is single-threaded; no preemption between a key event and the timer handler.** Two events drained from the same msgq loop can share a timestamp.

---

## ⬇️ PRESS path — `position_state_down` (`combo.c:422-454`)

```c
if (candidates[0].combo == NULL) {                      // :424  "buffer empty" test
    num_candidates = setup_candidates_for_first_keypress(pos, ts);   // :425
    if (num_candidates == 0) return ZMK_EV_EVENT_BUBBLE;             // :426-427  never captured
} else {
    filter_timed_out_candidates(ts);                    // :430  uses THIS key's timestamp
    num_candidates = filter_candidates(pos);            // :431
}
update_timeout_task();                                  // :433  BEFORE capture, BEFORE switch
candidate_combo = candidates[0].combo;                  // :435
ret = capture_pressed_key(data);                        // :437  → CAPTURED (or BUBBLE if buffer full)
switch (num_candidates) {
case 0:  cleanup(); return ret;                                                  // :439-441
case 1:  if (complete(candidate_combo)) { fully_pressed_combo = it; cleanup(); } return ret;   // :442-447
default: if (complete(candidate_combo))   fully_pressed_combo = it;             return ret;   // :448-452
}
```

- **Buffer empty (first key):** `setup_candidates_for_first_keypress` (:145-161) walks `combo_lookup[pos]` in sorted order and keeps a combo iff `combo_active_on_layer(combo, zmk_keymap_highest_layer_active())` (:153, layer read ONCE, at this key) and `!is_quick_tap`. Each candidate gets `timeout_at = ts + timeout_ms` (:155) — **all deadlines are anchored to the FIRST key's timestamp**.
  - A key in **zero** active combos → `BUBBLE` at :427: never captured, never buffered, reaches keymap immediately. On layers 0-24 impossible (the hack covers all 36 positions); on `l_nav`(25) etc. true for e.g. `LT4`, `RT0-RT4`, `LM4`, `RM4`, `LB4`, `RB*`, `LH*`, `RH0`.
- **Buffer non-empty:** `filter_timed_out_candidates(ts)` (:221-250) drops candidates with `timeout_at <= ts` (:228, strict `>` keeps) — **the window is half-open: a 2nd key at exactly `T1 + timeout` is OUT**. Then `filter_candidates(pos)` (:163-195) keeps only candidates that also contain `pos` (merge-walk of two sorted lists; :171 stops at first NULL).
  - A key that shares **no** combo with the buffered keys → 0 → still **captured** (:437) then `cleanup()` (:440): the earlier keys are flushed, this key is re-raised at index ≥1 and starts a **fresh candidate set** (nested, synchronous, inside the same call). It is *not* delivered raw.
  - Layer is **never re-checked** for 2nd+ keys; `require-prior-idle` is never re-checked either.
- **`fully_pressed_combo`** (:443-451) only ever tests `candidates[0]` — safe because all candidates have `len >= pressed_keys_count` and the list is length-sorted; ties (identical key sets) → earliest-defined wins. With >1 candidate it is **set but not fired**; a later key that completes a longer candidate **overwrites** it (:450).
- **`capture_pressed_key`** copies the event (:267) — `pressed_keys[i].header.last_listener_index` = combo's index.

---

## ⏲️ Timer path — one delayable, ladder of deadlines (`combo.c:197-208`, `:407-420`, `:472-481`)

```c
static int64_t first_candidate_timeout() {                 // :197
    int64_t first_timeout = LONG_MAX;                      // :198  ← 2147483647 on ARM (32-bit long)
    for (...) { if (candidates[i].combo == NULL) break; first_timeout = MIN(…timeout_at); }
    return first_timeout;
}
static void update_timeout_task() {                        // :407
    int64_t first_timeout = first_candidate_timeout();
    if (timeout_task_timeout_at == first_timeout) return;  // :409  early-out, even if work is idle
    if (first_timeout == LLONG_MAX) {                      // :412  ← never true on ARM
        timeout_task_timeout_at = 0; k_work_cancel_delayable(&timeout_task); return; }
    if (k_work_schedule(&timeout_task, K_MSEC(first_timeout - k_uptime_get())) >= 0)   // :417
        timeout_task_timeout_at = first_timeout;           // :418  set even when schedule was a no-op (ret 0)
}
static void combo_timeout_handler(struct k_work *item) {   // :472
    if (timeout_task_timeout_at == 0 || k_uptime_get() < timeout_task_timeout_at) return;   // :473-476 no reschedule!
    if (filter_timed_out_candidates(timeout_task_timeout_at) == 0) cleanup();               // :477-479 uses deadline, not now
    update_timeout_task();                                 // :480
}
```

- **Ladder (PROVEN):** the timer is scheduled for the MIN `timeout_at`. When it fires, only candidates with `timeout_at <= deadline` are dropped; if any remain, the timer is re-armed for the next MIN (works here: `k_work_schedule` accepts an item in RUNNING state, `zephyr/kernel/work.c:966-968`). `cleanup()` only when the ladder is empty. Example RM1 alone on alpha: fires at T+11 (hack), T+16 (entr2,bspc), T+18 (delWord,capsWord) → flush at **T+18**.
- **`k_work_schedule` semantics (PROVEN, `zephyr/kernel/work.c:954-976`, doc `zephyr/include/zephyr/kernel.h:3616-3617`):** *"a no-op if the work item is already scheduled or submitted"* — returns 0, deadline untouched. Combo never uses `k_work_reschedule`. `K_MSEC(negative)` clamps to 0 (`zephyr/include/zephyr/sys_clock.h:121`, `MAX(t,0)`) → fires on the next workqueue turn.
- **Defect 1 — 32-bit poison (PROVEN by source + toolchain):** `arm-zephyr-eabi-gcc` (`/opt/zephyr-sdk-0.16.3`, the compiler in `build/right/CMakeCache.txt`) defines `__LONG_MAX__ 0x7fffffffL`. With an empty candidate list `first_timeout = 2147483647 ≠ LLONG_MAX` → :417 schedules the delayable for uptime 2147483647 ms (~24.85 d; `CONFIG_TIMEOUT_64BIT=y`, `.config:1420`, so no tick wrap) and sets `timeout_task_timeout_at = 2147483647`.
  - Trigger: any `combo_timeout_handler` run that ends with an empty buffer (i.e. **every solo key held past its longest candidate timeout — the normal case**), via :480. (In `position_state_down` case 0 the same schedule happens at :433 but `cleanup()` at :440 cancels it immediately.)
  - Consequence: while poisoned, the next first-key press hits :417 with the item DELAYED → no-op → :418 records a **lie**. The key is captured with **no live timer**. Cured only by the next `cleanup()` (any release; a press that filters to 0; a single-candidate completion), which calls `k_work_cancel_delayable` (:398).
  - Net effect on rolls: `A↓(T) … A flushed at T+d_A … B↓(T+40 while A held)` → **B is delivered at A↑ (or at the next press), not at T+40+d_B.** Non-overlapping typing (A↑ before B↓) is unaffected.
  - Not reproducible on `native_posix_64` (`long` = 64 bit, host gcc `__LONG_MAX__ 0x7fffffffffffffffL`; `-m32` unavailable in the container).
- **Defect 2 — deadline cannot move later (PROVEN, testable on `native_posix_64`):** after a 2nd key, the surviving MIN can only be ≥ the old MIN. If it is strictly later and the timer is pending: no-op + lie (:417-418) → handler fires at the old deadline → :473 early-return → **nobody re-arms**. Stuck until next event. Example on alpha past the hack rung: `RM1↓(T)`, timer at T+16 pending; `RM3↓(T+12)` → candidates `[delWord(T+18), capsWord(T+18)]` → lie T+18 → nothing fires at T+18. A 3rd `RM2↓` completes delWord but leaves 2 candidates (default case, no cleanup; :409 equality → no schedule) → delWord fires only on first release.
- **Defect 3 — equality early-out on an idle item (INFERRED, marginal):** `cleanup()` cancels the timer but leaves `timeout_task_timeout_at` stale; a later first key with identical deadline (same-ms timestamp) returns at :409 without scheduling. Needs two presses in the same millisecond on the same rung; in practice masked by the quick-tap bypass (below).

---

## 🚿 FLUSH path — `cleanup` → `release_pressed_keys` (`combo.c:397-405`, `:273-289`)

```c
static int cleanup() {                          // :397
    k_work_cancel_delayable(&timeout_task);     // :398  (does not reset timeout_task_timeout_at)
    clear_candidates();                         // :399
    if (fully_pressed_combo != NULL) { activate_combo(fully_pressed_combo); fully_pressed_combo = NULL; }  // :400-403
    return release_pressed_keys();              // :404  returns count BEFORE flush
}
static int release_pressed_keys() {             // :273
    count = pressed_keys_count; pressed_keys_count = 0;                    // :274-275  buffer emptied first
    for i in 0..count: i==0 ? ZMK_EVENT_RELEASE(pressed_keys[i])           // :280  → tap_dance → keymap
                            : ZMK_EVENT_RAISE(pressed_keys[i]);            // :284  → listener 0 (hold-tap, combo…)
}
```

- **Order of delivery:** strictly buffer (press) order. Element 0 goes straight to the keymap (skipping hold-tap). Elements ≥1 re-enter the pipeline from listener 0 **synchronously, one at a time, each fully processed (including any nested flush it causes) before the next is raised**.
- **Fresh candidate set on re-raise (PROVEN):** the nested `position_state_down` sees `candidates[0]==NULL` (cleared at :399) → `setup_candidates_for_first_keypress(pos, ORIGINAL ts)` → deadlines `ORIGINAL ts + timeout`, layer = *current* highest layer (which may have changed because element 0 just ran a behavior), `is_quick_tap` evaluated against `last_tapped_timestamp` **as updated by element 0's synchronous behaviors**.
- **Combo activation (`activate_combo` :341-350):** stores the active combo, moves the first `key_position_len` buffered keys into it (:311-325; later buffered keys shift down and are then re-raised by :284), presses the behavior with `timestamp = first combo key's original timestamp` (:349; note `press_combo_behavior(…, int32_t timestamp)` truncates to 32 bit — harmless below 24.8 d uptime) and records `last_combo_timestamp` (:297).
- If `store_active_combo` fails → keys are flushed individually, combo lost (:343-346).

---

## ⬆️ RELEASE path — `position_state_up` (`combo.c:456-470`) and `release_combo_key` (`:363-395`)

```c
int released_keys = cleanup();                          // :457  ALWAYS flush everything first
if (release_combo_key(pos, ts)) return HANDLED;         // :458-460  release belonged to a fired combo → swallowed
if (released_keys > 1) { dupe = copy(data); ZMK_EVENT_RAISE(dupe); return CAPTURED; }   // :461-468
return BUBBLE;                                          // :469
```

- **Any release flushes the whole buffer**, even a release of a key that is not buffered (e.g. a long-held earlier key). This is what un-sticks the timer defects.
- **`released_keys > 1` dupe rule:** because keys ≥1 were re-raised (and may have been re-captured), the release is re-raised from listener 0 so the keymap sees press/release in physical order. Recursion depth ≤ buffer length; only the innermost dupe reaches the keymap (BUBBLE), outer copies return CAPTURED.
  - Worked: buffer `[A,B,C]`, `A↑` → keymap sees `A↓ B↓ C↓ A↑` at the moment of `A↑`, each with its original timestamp. **The re-raised B and C are immediately re-flushed by the dupe's `cleanup()`, so their own timeouts never apply.**
- **`release_combo_key` (:363-395):** for each active combo, removes the position from `key_positions_pressed` (:371-380). `all_keys_pressed` is computed **before** the decrement (:368). Behavior released iff `(slow_release && all_keys_released) || (!slow_release && all_keys_pressed)` (:384-386): non-slow (Flo's case) = **on the FIRST key release**; later releases of the remaining combo keys are swallowed (return true at :391 → `HANDLED`), and the combo is deactivated when the last one goes (:388-390). Release timestamp = the release event's timestamp (:386).
  - Release **before** activation (2-key combo fully pressed but still waiting behind longer candidates): `cleanup()` activates it first (:400-402), then `release_combo_key` releases it → behavior press and release back-to-back at release time, press stamped with the first key's timestamp.
- Release of a key whose press is still in the buffer (fast tap inside the window): press delivered by `cleanup()` (RELEASE path, element 0), then the release bubbles (count == 1) → keymap sees `X↓ X↑` back-to-back at release time.

---

## 🧘 require-prior-idle (`combo.c:141-143`, `:85-89`, `:496-502`)

```c
static bool is_quick_tap(combo, timestamp) { return (last_tapped_timestamp + combo->require_prior_idle_ms) > timestamp; }  // :141-143
store_last_tapped(ts): if (ts > last_combo_timestamp) last_tapped_timestamp = ts;                                        // :85-89
keycode listener: if (ev->state && !is_mod(...)) store_last_tapped(ev->timestamp);                                        // :496-502
```

- Checked **only** in `setup_candidates_for_first_keypress` (:153): per combo, at first-key time, never for later keys.
- With the compiled default `-1`: `last_tapped - 1 > ts`. For a **fresh** press (`ts == now`) this is false (keycode timestamps ≤ now) → feature is off, as intended.
- **For a re-raised press (`ts` in the past) it can be TRUE.** Keycode events from `&kp` invoked directly by the keymap carry the position's original timestamp (`behavior_key_press.c:40-44`), but keycodes produced through the behavior queue (macros, incl. `&ak`) carry `k_uptime_get()` at execution (`behavior_queue.c:34-35`), and the first queued step executes **synchronously** inside `zmk_behavior_queue_add` when the queue is idle (`behavior_queue.c:60-62`, `behavior_macro.c:161-185`). The keycode event reaches combo's listener (order on the map: `wpm → hold_tap → sticky_key → caps_word → combo → hid_listener`; hold-tap bubbles with no undecided HT `behavior_hold_tap.c:778-780`; sticky key bubbles or re-raises after itself `behavior_sticky_key.c:339`).
  - Consequence (PROVEN mechanism): flush of `[A,B]` where A is an `&ak` key: element 0 delivers `A↓` → `&kp A` pressed now → `last_tapped = now`; element 1 (`B↓`, ts `T_B`) → `is_quick_tap` = `now - 1 > T_B` → true whenever `T_B <= now - 2` → **B has zero candidates → BUBBLE → delivered immediately, back-to-back with A.**
  - When it bites on Flo's layout: 2nd key pressed 0-9 ms after the 1st (both inside the 11 ms hack rung); at the hack expiry `now = T_A+11`, so any `T_B <= T_A+9` bypasses. Also at any flush where the queue was idle. When it does NOT bite: the previous `&ak` tap still pending in the queue (< 10 ms since the previous delivery) → keycode deferred → `last_tapped` stale → B captured normally (INFERRED timing dependence; needs a test).

---

## 🗂️ Layer filtering

- `combo_active_on_layer` (:128-139): `layers[0] == -1` → global; else linear search. Evaluated **once**, at the first key of a candidate set, against `zmk_keymap_highest_layer_active()` (`keymap.c:187-194`: highest set bit, else default). Re-raised keys re-evaluate (they are "first keys" again), so a layer change caused by element 0's behavior (e.g. `&aksl` activating `l_akX`) IS seen by element 1 — but AK layers 2-24 have the same combo set as `l_alpha` for everything Flo defines on `l_alpha_aks` (compiled `layers = <0x0 … 0x18>`, `zephyr.dts:2545`).
- Compiled reality (PROVEN, `zephyr.dts:2379-2548`): 28 combos → 22×16 ms, 5×18 ms, 1×11 ms; none at 30 ms; the hack `combo_ak_consistency_hack` = 36 keys, layers 0-24, timeout 11.

---

## 🎲 Multiple combos at once

- Only one `fully_pressed_combo` slot; only `candidates[0]` is tested; it fires when the candidate list empties (timeout ladder, filter to 0 by a foreign key, or any release). With several candidates alive the shorter, earlier-defined complete one holds the slot until a longer one completes and overwrites it.
- Flo example, both keys held: `RM1↓(T)`, `RM2↓(T+5)` → candidates `[bspc(T+16), delWord(T+18), capsWord(T+18), hack(T+11)]` → bspc complete, waits; ladder T+11, T+16 (bspc itself drops but the slot keeps the pointer), **fires at T+18** (or first release). `RM3↓` before T+18 → delWord overwrites → fires at T+18 with `[capsWord]` remaining… but see Defect 2 (the T+18 rung is not actually armed after the T+16 rung was skipped) → in practice fires on first release.
- `MAX_PRESSED_COMBOS` limits how many *fired* combos can hold keys simultaneously (20 here); sequential combos never conflict.

---

## 🗺️ Flo's candidate landscape (compiled, alpha layer) — for timelines

| Position(s) | Alpha candidates (lookup order) | Solo delay (ladder end) |
|---|---|---|
| LT4, RT0, LM4, LB4, LH0-2, RH0 | hack(11) | **11 ms** |
| LT3, LT0, RT1, RT4, LM0, RM0, LB3, LB0, RB0-2, RH1, RH2, LM1, LM3, LM2 | one or two 16 ms combos + hack | **16 ms** |
| LT2, LT1, RT2, RT3, LB2, LB1, RB3, RB4 | two-three 16 ms + hack | **16 ms** |
| RM1, RM2, RM3 | 16 ms ×1-2, delWord(18), capsWord(18), hack | **18 ms** |
| RM4 | capsWord(18), hack | **18 ms** |

- On `l_nav`(25)/`l_num`(28)/`l_numsym`(29)/`l_nav_linwin`(31): hack absent; `LM1-LM3` get the `*Trans` combos (max 18), `RM1-RM3` keep bspc/del/delWord (max 18), many positions have **zero** combos → uncaptured (bubble at :427).
- Definition order (= tie-break): `#0 delWord_linwin … #27 ak_consistency_hack` (full list in `analyze_combos.py` output; script at `scratchpad/investigation/analyze_combos.py`).

---

## 🎬 Worked timelines (board semantics unless noted)

- **T1 — solo hack-only key (LT4) held 80 ms.** `↓T` capture, ladder T+11 → flush → `LT4↓` to keymap at **T+11** (stamped T) → poison armed. `↑T+80` → cleanup cancels poison → `↑` bubbles. Keymap: `↓@T+11, ↑@T+80`. (Same on native_posix_64.)
- **T2 — roll A(LT4) then B(RT0), overlap.** `A↓T`, `B↓T+40`, `A↑T+70`, `B↑T+110`. Board: A flushed T+11 (poison); B captured T+40 with dead timer; `A↑` → cleanup → `B↓` delivered **T+70**, then `A↑`; `B↑` bubbles T+110. native_posix_64: `B↓` at **T+51**. ← **the divergence to encode in tests.**
- **T3 — same as T2 but B pressed at T+5.** Both buffered; T+11 flush: `A↓` (→ `&ak` presses `&kp A` now → `last_tapped = T+11`), then `B↓` re-raised, `is_quick_tap(T+5)` true → **bypass** → `B↓` delivered at T+11 too. Keymap: `A↓ B↓` both at T+11 (stamps T, T+5). Same on both targets (mechanism is timestamp arithmetic, not `LONG_MAX`). *Requires a macro-driven A; with plain `&kp` A, B is captured and delivered at T+16.*
- **T4 — 2nd key at T+10 exactly (hack-only keys).** `is_quick_tap` = `T+10 > T+10` false → B captured, fresh ladder anchored T+10 → `B↓` at **T+21**. Gap to `A↓` = 10 ms = `ak_tap_time` (borderline for the AK layer being up).
- **T5 — 2nd key at T+12 (A's hack rung already fired, A's other candidates alive).** For A=RM1: `B↓` filters to 0 → case 0 → `A↓` delivered **at T+12** (B's press), `B↓` re-raised fresh (quick-tap false: `now-1 > now` no) → captured → `B↓` at T+12+d_B (11-18). For A=LT4 (hack only) A was already flushed at T+11 and B is a normal first key **but** poisoned → B delivered at next event (board) / T+23 (native).
- **T6 — 2-key combo `bspc` (RM1+RM2) pressed 5 ms apart, released after 100 ms.** Fires (press `&bk BSPC`, stamp T) at **T+18** on native_posix_64 (ladder end); on the board the T+16→T+18 step is arm-able (handler is RUNNING) so also T+18 — *unless* RM1 was pressed in a poisoned state (then only at first release). Release of `bspc` at the first of `RM1↑/RM2↑`; the second release is swallowed.
- **T7 — fast tap inside the window (X↓T, X↑T+8).** `X↑` → cleanup → `X↓` (stamp T) then `X↑` (stamp T+8) both at T+8.

---

## 🧭 State machine (engine-level; timer defects shown as the dashed "Dead timer" state)

```mermaid
stateDiagram-v2
    direction LR
    [*] --> Idle
    state "🟢 Idle — buffer empty, no candidates" as Idle
    state "🟡 Collecting — buffer[1..n], candidates≥1, ladder armed" as Coll
    state "🟠 Complete-pending — fully_pressed_combo set, candidates≥2" as Pend
    state "🔴 Dead timer — buffer≥1, candidates≥1, no live work item (board: poison / both: late-deadline)" as Dead

    Idle --> Idle : PRESS key with 0 active combos (layer, prior-idle) → bubble
    Idle --> Coll : PRESS key with ≥1 candidate → capture, arm MIN deadline
    Idle --> Dead : PRESS while poisoned (board only) → capture, schedule no-op
    Coll --> Coll : PRESS shares combos, MIN unchanged → capture
    Coll --> Dead : PRESS shares combos, MIN moved later → capture, no re-arm
    Coll --> Pend : PRESS completes candidates[0], ≥2 remain → capture
    Coll --> Idle : PRESS completes the only candidate → activate combo, flush rest (re-raise)
    Coll --> Idle : PRESS shares no combo → flush all (elem0 RELEASE, others RAISE→re-enter), poison (board)
    Coll --> Coll : TIMER rung, candidates remain → re-arm next MIN
    Coll --> Idle : TIMER last rung → flush all, re-raised keys may re-enter Coll; poison (board)
    Pend --> Pend : PRESS completes a longer candidate → overwrite slot
    Pend --> Idle : TIMER last rung → activate slot combo, flush rest
    Dead --> Idle : any RELEASE / PRESS filtering to 0 → cleanup cancels, flush
    Coll --> Idle : RELEASE (any position) → cleanup → flush; if >1 flushed, dupe RELEASE re-raised
    Pend --> Idle : RELEASE → activate slot combo, release it if its key, flush rest
    Idle --> Idle : RELEASE of fired-combo key → swallow (HANDLED), release behavior on first
```

- Transition legend for the page: **capture** = event stops at combo (CAPTURED); **flush** = element 0 released to `tap_dance → keymap`, elements ≥1 re-raised from listener 0; **poison** = far-future delayable left pending (board only).

---

## ✅ PROVEN vs 🤔 INFERRED

- PROVEN (source/build artefacts): listener order; capture rules; flush order and re-raise mechanics; original timestamps preserved; ladder timer; half-open window; release rules incl. first-release semantics; layer check only at first key; prior-idle only at first key; `LONG_MAX`=32-bit on the board toolchain; `k_work_schedule` no-op semantics in Zephyr 3.5; compiled combo set, timeouts, layers, limits.
- INFERRED (needs a test or hardware log): (a) exact ms at which quick-tap bypass flips (depends on whether the previous `&ak` tap left the behavior queue idle); (b) how often real rolls land in the "dead timer" state (depends on hold durations); (c) GCC diagnostic severity for `MAX_KEYS_PER_COMBO` overflow; (d) same-ms timestamp frequency on hardware (matrix scan/debounce, `CONFIG_ZMK_KSCAN_DEBOUNCE_*_MS=-1` = defaults).

---

## ❓ Open questions + how to settle them

- **Q1 Is the board really poisoned?** Hardware: hold an `&ak` letter, 40 ms later press+hold a second letter, keep both down 1 s. Prediction: second letter appears only on a release. Alternatively enable `CONFIG_ZMK_USB_LOGGING` (currently off, `.config:218`; `CONFIG_ZMK_LOG_LEVEL=4` already) and look for a missing `after filtering out timed out combo candidates` line for the 2nd key. Unit test: needs a 32-bit `long` → `native_posix` (32-bit) requires multilib not present in the container; or a test-only compile flag forcing `LONG_MAX` for `combo.c`.
- **Q2 Quick-tap bypass reach:** native_posix_64 test with a macro-based first key (see C3).
- **Q3 Late-deadline stall on native:** C4 below reproduces without any board-specific bit.

---

## 🧪 Test sketches (native_posix_64, kscan mock: `ZMK_MOCK_PRESS(row,col,ms)` = fire event then wait `ms`; first event fires at T+`ms` of entry 0 — `kscan_mock.c:52-60`; ticks 1 kHz in test builds)

- **C1 Solo delay = longest candidate.** Combos `<0 1>`@11, `<0 2>`@16, `<0 2 3>`@18; keymap `&kp A …`. `PRESS(0,0,100) RELEASE(0,0,10)`. Expect `filter_timed_out_candidates` lines at ts+11 (remaining 2), +16 (1), +18 (0) then `pressed A`; no keycode before +18.
- **C2 Flush order + original timestamps.** Combos `<0 1 2 3>`@11 only (36-key-hack analogue). `PRESS(0,0,5) PRESS(0,1,3) RELEASE(0,0,50) RELEASE(0,1,10)`. Expect log order `releasing position event 0`, `reraising position event 1`, then keycodes `A↓ B↓ A↑ B↑`, all before the 11 ms rung, and `B↓` in the same ms as `A↑`.
- **C3 Quick-tap bypass (prior-idle -1).** Same combo; position 0 bound to a macro `<&macro_tap &kp A>` (tap-ms 10), position 1 to `&kp B`. `PRESS(0,0,5) PRESS(0,1,50) …`. Expect `B↓` in the same ms as `A↓` (ts+11) and **no** `capturing position event 1` after the reraise. Control: bind position 0 to plain `&kp A` → `B↓` at ts+5+11.
- **C4 Late-deadline stall.** Combos `<0 1>`@16, `<0 2>`@18 (no shorter all-key combo). `PRESS(0,0,12) PRESS(1,0,100) RELEASE(0,0,10) RELEASE(1,0,10)`. Expect: no keycodes until the release at +112 (stall), then `A↓ C↓ A↑`. A fixed engine would emit `A↓ C↓` at +18.
- **C5 First-release semantics.** Combo `<0 1>`@30 → `&kp X`, non-slow. `PRESS(0,0,5) PRESS(0,1,50) RELEASE(0,0,20) RELEASE(0,1,10)`. Expect `X↓` at +30 (ladder end), `X↑` at +55 (first release), nothing at +75.
- **C6 Poison (board-only).** Same as C2 but `PRESS(0,0,40) PRESS(0,1,100) RELEASE(0,0,…)`. On native: `B↓` at +51. On a 32-bit build: `B↓` only at `A↑`. Use to pin the divergence.
