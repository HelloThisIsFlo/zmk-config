# B — Behaviour pipeline (keymap → behaviours → HID)

Scope: everything after a `zmk_position_state_changed` event reaches the keymap listener. Combo internals are out of scope except where they hand off or interleave.

Legend: **PROVEN** = read directly from the code that ships on the board. **INFERRED** = follows from PROVEN facts by tracing, not yet executed. **OPEN** = genuinely ambiguous, test proposed.

Paths: `zmk/` = `/Users/flo/Work/Private/Dev/Keyboard/zmk/app`, `cfg/` = `/Users/flo/Work/Private/Dev/Keyboard/zmk-config/config`, `zephyr/` = Zephyr v3.5.0 read from the docker volume `zmk-zephyr` (`/z/VERSION` = 3.5.0.0).

## 0. Ground truth + what Flo actually uses

- Firmware = fork HEAD `4211ad74`. `git diff 6e03a0bb HEAD -- app/src app/include app/Kconfig app/Kconfig.behaviors app/dts app/CMakeLists.txt` is **empty** → source identical to upstream `6e03a0bb` (PROVEN).
- Zephyr = `v3.5.0+zmk-fixes` (`zmk/west.yml:9-11`).
- ⚠️ The scratchpad `zmk-upstream` checkout is at `5b51501f` (current upstream main), NOT the fork point. Its `behavior_queue.c` has a different API (event-based, split `source`). Do not cite it for the board.
- Behaviours in `cfg/` (`compatible = "zmk,behavior-…"` counts): hold-tap 36, macro 26 (+7 one-param, +1 two-param), mod-morph 23, sticky-key 6, tap-dance 1. Built-ins referenced: `&kp` 428, `&mo` 28, `&sk` 10, `&to` 7, `&mt` 5, `&sl` 3, `&tog` 3, `&caps_word` 2, `&trans` 3, `&none` 23, `&macro_tap` 65, `&macro_release` 55, `&macro_press` 7, `&macro_pause_for_release` 6, `&macro_wait_time` 1, `&macro_tap_time` 1.
- Relevant constants (`cfg/CONFIG.h`): `linger_term` 100 (:4), `my_tapping_term_main` 500 (:5), `my_tapping_term_thumb` 200 (:6), `my_ak_window` 100 (:8), `action_mod_tapping_term` 130 (:14), `action_lay_tapping_term` 90 (:15), `ak_tap_time` 10 (:28), `hold_key_event_delay` 11 (:29), `TEMP_macro_tap_time` 10 (:36); `&mt { tapping-term-ms = <500> }` (:37-39).
- Kconfig that matters (`cfg/corne.conf`): `CONFIG_ZMK_BEHAVIORS_QUEUE_SIZE=512` (default 64, `zmk/Kconfig:497-499`), `CONFIG_ZMK_HID_SEPARATE_MOD_RELEASE_REPORT=y` (`zmk/Kconfig:116-120`, compiled in — see §8). Macro defaults `CONFIG_ZMK_MACRO_DEFAULT_WAIT_MS=15`, `_TAP_MS=30` (`zmk/Kconfig:503-509`) — every Flo macro overrides both except `dotcom`/`dotcouk` (tap-ms left at 30, `cfg/features/hands_down/adaptive_keys/macros.dtsi:108-118`).
- No `zmk,conditional-layers` node in `cfg/` → `set_layer_state` has no side listeners beyond display widgets.

## 1. Threading model (everything below runs on ONE thread)

- **PROVEN** — all pipeline code runs on the Zephyr system workqueue thread:
  - kscan matrix scan: `k_work_reschedule(&data->work …)` → sysworkq (`zmk/module/drivers/kscan/kscan_gpio_matrix.c:190,200,214`).
  - kscan → position event: callback only `k_msgq_put` + `k_work_submit(&msg_processor.work)` (`zmk/src/physical_layouts.c:172-181`); the event is raised from that work with `.timestamp = k_uptime_get()` (:178-182).
  - Left-half keys (right = central): BLE notification callback does `k_msgq_put` + `k_work_submit(&peripheral_event_work)` with `.timestamp = k_uptime_get()` **at receipt on the central** (`zmk/src/split/bluetooth/central.c:259-266`, work :72-80). Queue depth `CONFIG_ZMK_SPLIT_BLE_CENTRAL_POSITION_QUEUE_SIZE` = 5.
  - combo timeout, hold-tap timer, sticky-key timer, tap-dance timer, behaviour queue: all `k_work_delayable` on the default (system) queue.
- **PROVEN** — sysworkq priority = `CONFIG_SYSTEM_WORKQUEUE_PRIORITY` default `-1` = "lowest cooperative priority … any work handler, once started, won't be preempted by any other thread until finished" (`zephyr/kernel/Kconfig:656-664`).
- Consequences (INFERRED from the above):
  - Strict serialisation: no two of {position event dispatch, timer handler, behaviour-queue tick} ever overlap. Any "race" in this system is an *ordering* question, never a concurrency one.
  - Timers fire late by however long the current handler runs. Known blockers: `k_msleep(10)` per captured event in `release_captured_events` when a second hold-tap becomes undecided (`zmk/src/behaviors/behavior_hold_tap.c:220-222`); USB `k_sem_take(&hid_sem, K_MSEC(30))` per report if the host stalls (`zmk/src/usb_hid.c:139`).
  - BLE HID is the only thing off-thread: `zmk_hog_send_keyboard_report` copies the report body into `zmk_hog_keyboard_msgq` (20 deep) and submits to `hog_work_q` (own thread, prio `CONFIG_ZMK_BLE_THREAD_PRIORITY`=5) (`zmk/src/hog.c:223-276`). Report *content and order* are frozen at `zmk_endpoints_send_report` time; radio timing is asynchronous.

## 2. Event manager (Q6)

- **PROVEN** — dispatch = linear scan of the `.event_subscription` link section from `start_index`, calling each matching listener synchronously (`zmk/src/event_manager.c:20-46`):
  ```c
  ret = ev_sub->listener->callback(event);
  switch (ret) {
  case ZMK_EV_EVENT_BUBBLE:   continue;      // 0
  case ZMK_EV_EVENT_HANDLED:  return 0;      // 1
  case ZMK_EV_EVENT_CAPTURED: return 0;      // 2
  default:                    return ret;    // negative = error, also stops
  }
  ```
  - `HANDLED` and `CAPTURED` are **identical to the manager**; the difference is convention: CAPTURED = "I copied it and will re-raise it later", HANDLED = "done, drop it".
  - Events live on the raiser's stack (`raise_##event_type` builds a local struct, `zmk/include/zmk/event_manager.h:54-58`). Capturers must copy (`copy_raised_*`, :50-53) — combo, hold-tap and sticky-key all do.
- **PROVEN** — depth-first, no queue: a listener that raises another event (keymap → `&kp` → `raise_zmk_keycode_state_changed`) runs that whole nested dispatch to completion before returning. A re-raised event is therefore fully processed **before** the current dispatch finishes (it is nested inside the current listener's callback).
- Re-raise primitives (`event_manager.h:75-82`, impl `event_manager.c:48-82`):
  - `ZMK_EVENT_RAISE(ev)` — from listener 0.
  - `ZMK_EVENT_RAISE_AT(ev, mod)` — from `mod`'s own subscription (inclusive). Used by hold-tap release (:229,:235) so a released event can be re-captured by a new undecided hold-tap.
  - `ZMK_EVENT_RAISE_AFTER(ev, mod)` — from the subscription after `mod`. Used by sticky-key (:333).
  - `ZMK_EVENT_RELEASE(ev)` — from `last_listener_index + 1` stored in the copied header. Used by combo for the first released key (`zmk/src/combo.c:278-281`).
- Listener order = link order = `zmk/CMakeLists.txt` `target_sources` order (INFERRED: Zephyr links `app` whole-archive; ZMK relies on it — `behavior_hold_tap.c:731` "hold-tap listener should be called before before most other listeners!"; all upstream tests depend on it):
  - `zmk_position_state_changed`: activity (CMake :25) → **behavior_hold_tap** (:50) → **combo** (:67) → behavior_tap_dance (:68) → **keymap** (:74).
  - `zmk_keycode_state_changed`: **behavior_hold_tap** (:50) → **behavior_sticky_key** (:51) → behavior_caps_word (:52) → behavior_key_repeat (:53) → combo (:67, only records `last_tapped`) → **hid_listener** (:73) → zmk_ble (:83, passkey entry only). (`wpm` at :31 is `ifdef CONFIG_ZMK_WPM`, not set in Flo's conf.)
  - So: hold-tap sees a position event before the combo engine; a sticky key sees a keycode before HID; a mod keycode raised while a hold-tap is undecided is captured by hold-tap **before** the sticky key can see it.
- **PROVEN** — the only queues in the whole pipeline: kscan msgq (`physical_layouts.c`), split peripheral msgq (5), behaviour queue msgq (512), hold-tap `captured_events[40]`, combo `pressed_keys[36]`, HOG report msgq (20). Nothing else buffers.

## 3. Keymap: when the layer is resolved (Q1)

- **PROVEN** — listener `keymap_listener` (`zmk/src/keymap.c:747-752`) → `zmk_keymap_position_state_changed` (:651-682):
  ```c
  if (pressed) { zmk_keymap_active_behavior_layer[position] = _zmk_keymap_layer_state; }   // :653-655
  for (layer_idx = ZMK_KEYMAP_LAYERS_LEN - 1; …; layer_idx--) {                              // top → default
      if (zmk_keymap_layer_active_with_state(layer_id, zmk_keymap_active_behavior_layer[position])) {
          int ret = zmk_keymap_apply_position_state(...);                                     // :667-668
          if (ret > 0) continue;   /* ZMK_BEHAVIOR_TRANSPARENT (&trans) */                    // :669-671
          return ret;              /* 0 = OPAQUE (incl. &none), <0 = error */
  ```
  - Resolution instant = the moment the keymap listener runs = **delivery** time (after any combo capture, hold-tap capture, split hop), synchronous, using the live `_zmk_keymap_layer_state`. It is **not** the physical press time.
  - Binding read at :595 (`zmk_keymap[layer_id][position]`), event built at :597-601 with `.timestamp = timestamp` = the **original** position timestamp, `.layer = layer_id`.
  - Release routing: the layer bitmask snapshotted at press is reused for the release (:71-74 comment, :653-655), so a key pressed on `l_akX` releases into `l_akX`'s binding even after `l_akX` is off. Keys pressed on an AK layer therefore never "orphan" a press.
- **PROVEN** — layer changes are synchronous bit writes: `set_layer_state` (:141-164) `WRITE_BIT(_zmk_keymap_layer_state, …)` then `raise_layer_state_changed` (:157). `&mo` press/release = `zmk_keymap_layer_activate/deactivate` (`behavior_momentary_layer.c:44-54`). `&to` deactivates every layer then activates the target (`keymap.c:210-218`); default layer can never be deactivated (:148-150). `&tog` (:202-208).
- Answer to "same dispatch": a layer activated by a behaviour is visible to **every position event processed after that call returns**, including later iterations of a synchronous burst (combo `release_pressed_keys` :273-288, hold-tap `release_captured_events`). A key earlier in the same burst does not see it. For `&ak` the activation is deferred 10 ms into the behaviour queue (§4.3), so **no** key in the same burst sees it — that is exactly the inconsistency the 36-key hack pads against (`cfg/features/hands_down/adaptive_keys/combos.dtsi:64-68`).
- Locality (`keymap.c:619-646`): every behaviour Flo uses has no `.locality` → `BEHAVIOR_LOCALITY_CENTRAL` (0) → runs on the right half for both hands. Only `&bootloader`/`&sys_reset` are `EVENT_SOURCE` (`behavior_reset.c:40`).

## 4. Behaviour queue + macros (Q2)

### 4.1 Queue mechanics

- **PROVEN** — one global FIFO for all macros (`zmk/src/behavior_queue.c`):
  ```c
  struct q_item { uint32_t position; struct zmk_behavior_binding binding; bool press : 1; uint32_t wait : 31; };   // :15-20
  K_MSGQ_DEFINE(zmk_behavior_queue_msgq, sizeof(struct q_item), CONFIG_ZMK_BEHAVIORS_QUEUE_SIZE, 4);            // :22  (512 on the board)
  static K_WORK_DELAYABLE_DEFINE(queue_work, behavior_queue_process_next);                                        // :25
  ```
  - `zmk_behavior_queue_add` (:52-66): `k_msgq_put(K_NO_WAIT)`; on a full queue returns the error and **`queue_macro` discards the return value** (`behavior_macro.c:172-179`) → items silently dropped. Then:
    ```c
    if (!k_work_delayable_is_pending(&queue_work)) { behavior_queue_process_next(&queue_work.work); }   // :61-63
    ```
  - `behavior_queue_process_next` (:27-50): pop → `event = {.position, .timestamp = k_uptime_get()}` (:34-35, **not** the original timestamp, `.layer` = 0) → invoke pressed/released synchronously (:37-41) → `if (item.wait > 0) { k_work_schedule(&queue_work, K_MSEC(item.wait)); break; }` (:45-48).
  - So an item's `wait` is the gap between the **end of that item's invocation** and the start of the next item. It is `k_work_schedule`, not `k_work_reschedule` (the task brief's wording is inaccurate for this tree).
- **PROVEN** (Zephyr v3.5) — semantics the queue hinges on:
  - `k_work_delayable_is_pending()` = `busy_get != 0` where busy = `flags & K_WORK_MASK` and `K_WORK_MASK = DELAYED | QUEUED | RUNNING | CANCELING` (`zephyr/include/zephyr/kernel.h:3805-3811, 4046-4050`). → **true while the queue handler is executing** (RUNNING is set around `handler(work)`, `zephyr/kernel/work.c:622,672,681`).
  - `k_work_schedule_for_queue`: "Schedule the work item if it's idle or running" — `if ((work_busy_get_locked(work) & ~K_WORK_RUNNING) == 0U) schedule…` else no-op returning 0 (`zephyr/kernel/work.c`). An already DELAYED work keeps its **earlier** deadline. `k_work_reschedule` would cancel first; ZMK does not use it here.
- Derived rules (INFERRED, each a direct consequence):
  1. **Sync vs deferred.** If the queue is idle when a macro is pressed, its first item, and every following item up to and including the first with `wait > 0`, runs synchronously inside the caller (inside the keymap listener, inside the position-event dispatch, inside the combo/hold-tap re-raise). If the queue is busy (a delay pending or the handler running), **every** item is only enqueued and runs from the work later.
  2. **Second macro while items pending.** Appended FIFO behind everything already queued (including the pending wait). No concurrency, no blocking, no per-macro lanes. Macro B's first item cannot run before macro A's last item.
  3. **Nested macro (a macro binding as a queue item)** — two different outcomes:
     - Outer item executed by the **work handler** (RUNNING): inner `zmk_behavior_queue_add` calls only enqueue → inner items land **after** the outer macro's already-queued items → FIFO respected, inner tap/wait respected.
     - Outer macro's first item executed **synchronously** (queue idle): `behavior_queue_process_next` was a plain call (RUNNING not set), so the inner add sees "not pending" and **re-enters** `behavior_queue_process_next`. The inner loop pops the inner press, schedules its `wait`, breaks; control returns to the **outer** loop, which keeps popping — i.e. it drains the inner macro's remaining zero-wait items immediately. Net effect: the inner macro's `tap-ms` is not honoured (press and release in one burst). Worked out in §4.4.
  4. A stall anywhere stalls everything: e.g. `moAndBuffer`'s 130 ms wait (§4.4) parks the queue; every `&ak`/`&bk`/morph pressed meanwhile is deferred until it expires, then flushed in order.
  5. Timestamps of queued behaviours are the processing instant (:35). This feeds sticky `release_at`, hold-tap `timestamp` (if a hold-tap were queued — none of Flo's are), and keycode event timestamps → `last_tapped` in hold-tap and combo (§6.5).

### 4.2 Macro behaviour (`zmk/src/behaviors/behavior_macro.c`)

- Defaults per instance: `.default_wait_ms = DT wait-ms else CONFIG (15)`, `.default_tap_ms = DT tap-ms else CONFIG (30)` (:315-324).
- Control bindings (`handle_control_binding` :78-112): `&macro_tap/press/release` set mode; `&macro_tap_time N` / `&macro_wait_time N` overwrite the running `tap_ms`/`wait_ms` from that point; `&macro_param_1to1/2to1/1to2/2to2` mark which macro param replaces which param of the **next** real binding only (`replace_params` resets sources after use, :151-159).
- `queue_macro` (:161-187): per real binding — TAP: `add(press, wait=tap_ms); add(release, wait=wait_ms)`; PRESS: `add(press, wait=wait_ms)`; RELEASE: `add(release, wait=wait_ms)`.
- `&macro_pause_for_release` (init, :114-137): splits the list; press runs `[0, pause)`, release runs `(pause, end]`; controls seen before the pause are pre-applied to the release state (mode/tap/wait carry over). Without a pause the release part is empty (`release_state.count = 0`, :119) → releasing a macro key does nothing.
- Press handler (:189-203) and release handler (:205-214) both return `ZMK_BEHAVIOR_OPAQUE`. No per-instance "pressed" state → the same macro can be pressed again before release; items just interleave FIFO.

### 4.3 `&ak` expansion — the canonical timeline (PROVEN)

`&ak` (`cfg/features/hands_down/adaptive_keys/macros.dtsi:25-39`): `wait-ms = <0>; tap-ms = <ak_tap_time>` (10), bindings `param_2to1, tap &kp X, tap_time 0, param_1to1, tap &aksl l_akX`.

Queue idle, macro pressed at instant D (= delivery of the position event to the keymap; physical press was D − 11 ms via the hack combo):
- D: `add(kp X↓, wait 10)` → runs synchronously → keycode event → HID report `X down` → `k_work_schedule(10)` → break.
- D: `add(kp X↑, 0)`, `add(aksl↓, 0)`, `add(aksl↑, 0)` → enqueued (queue is DELAYED).
- D + 10 (work): `kp X↑` → HID `X up`; `aksl↓` → `&mo l_akX` → **layer on**; `aksl↑` → sticky timer, `release_at = (D+10) + 100 = D + 110`.
- Physical release of X → `on_macro_binding_released` → nothing (no pause).
- So relative to the physical press P: HID down at P+11, HID up and AK layer on at P+21, AK window nominal end at P+121 — and the window is extended/pinned by the next keycode (§5.4).
- If the queue was **not** idle at D (previous AK key's 10 ms tick still pending, i.e. two AK keys delivered < 10 ms apart), all four items queue behind it: X's HID down is delayed to the earlier tick.

### 4.4 Flo's other macros (PROVEN wiring, INFERRED timelines)

- `&bk KEY` (`adaptive_keys/macros.dtsi:72-80`, tap 10 / wait 0): press → `kp↓` sync (if idle), `kp↑` 10 ms later; release → nothing.
- `&bm MOD` (:57-70): press → `kp MOD↓`; pause; release → `kp MOD↑`. Real held modifier.
- `&bsk MOD` (:82-95): press → `&sk MOD↓`; release → `&sk MOD↑` (sticky timer starts at the physical release).
- `&moAndBuffer` (`cfg/features/hands_down/mods/macros.dtsi:1-25`): press → `&mo l_mod↓` (sync). Release → `wait_ms := 130`, `tap &none` → `add(none↓, wait=tap_ms=0)`, `add(none↑, wait=130)`, then `add(mo l_mod↑, 0)`. Timeline: release R → none↓, none↑, `k_work_schedule(130)`; R+130 → `&mo l_mod↑`. **The global queue is parked for those 130 ms** (rule 4): any `&ak`/`&bk`/mod-morph key pressed in (R, R+130) has its HID output deferred to R+130 (order preserved). Meanwhile `l_mod` is still active, so a key pressed on an `l_mod` position that is *not* transparent (e.g. `&htm …` on the home row, `layers_C_extra.dtsi:41-43`) resolves on `l_mod` — that is the intended "buffer"; transparent positions fall through to alpha `&ak` and get delayed.
- `REPLACE_CHAR_WITH_BIGRAM(B0,B1)` (`cfg/features/__BASE__/preprocessor_macros.c:12-27`, wait 0 / tap 10): items `[bspc↓ w10][bspc↑][B0↓ w10][B0↑][LSHFT↑][RSHFT↑][ak↓ w10][ak↑]`. From trigger delivery T: T bspc↓; T+10 bspc↑, B0↓; T+20 B0↑, LSHFT↑, RSHFT↑ (each a no-op error if Shift isn't held: `hid.c:61-64` → `hid_listener.c:63-67` returns early, **no report**; if a sticky/held Shift *is* registered it is force-released), `ak↓` (executed by the work → inner items enqueue **after** the already-queued `ak↑`): queue = `[ak↑][kpB1↓ w10][kpB1↑][aksl↓][aksl↑]`; T+30 ak↑ (nop), kpB1↓; T+40 kpB1↑, aksl↓ → `l_akB1` on, aksl↑ → window to T+140. The triggering AK layer `l_akX` is released by the backspace: bspc↓ sets it as the modified key, bspc↑ (T+10) releases `&mo l_akX`.
- `ak_S_macro` etc. (`cfg/features/hands_down/mods/behaviors.dtsi`, `wait-ms 0; tap-ms 0; bindings <&ak l_akS S>`) and `ak_R_macro` (`adaptive_keys/behaviors.dtsi:19`) used as hold-tap **tap** bindings — the nested-sync case (rule 3b) when the queue is idle at decision time:
  - `add(ak↓, 0)` → sync L1 pops ak↓ → `&ak` press → `add(kpS↓, 10)` → not pending → **re-entrant L2** pops kpS↓ → HID `S down` → schedule(10) → break → `add(kpS↑,0)`, `add(aksl↓,0)`, `add(aksl↑,0)` enqueue → back in L1: `ak↓.wait == 0` → L1 pops **kpS↑ → HID `S up` immediately** (0 ms tap), aksl↓ → `l_akS` **on immediately**, aksl↑ → timer. Then `add(ak↑,0)` enqueues; runs at +10 (nop).
  - So an HRM/thumb tap through `ak_X_macro` emits press+release back-to-back and activates the AK layer **synchronously at the decision instant** — which is precisely why the captured next key (re-raised right after, §6.4) lands on `l_akS`. If the queue had been busy, the layer would come 10 ms later and the re-raised key would miss it. Flo's own note (`combos.dtsi:20`) says a 0 ms tap drops keys on the M1 — this path produces exactly that.
- `dotcom`/`dotcouk`: wait 50, tap 30 (CONFIG default).

## 5. Sticky key (Q3) — `zmk/src/behaviors/behavior_sticky_key.c`

### 5.1 Instances on the board
| name | binding | release-after-ms | quick-release | ignore-modifiers | where |
|---|---|---|---|---|---|
| `aksl` | `&mo` | 100 | no | no | `adaptive_keys/behaviors.dtsi:1-9` |
| `slm` | `&mo` | 130 | no | yes | `mods/behaviors.dtsi:24-32` |
| `skm` | `&kp` | 1500 | no | yes | `mods/behaviors.dtsi:2-11` |
| `skms` | `&kp` | 1500 | no | no | `mods/behaviors.dtsi:13-22` |
| `skL` | `&kp` | 3000 | yes | no | `hands_down/behaviors.dtsi:1-8` |
| stock `sk` | `&kp` | 1000 | no | yes | `zmk/dts/behaviors/sticky_key.dtsi` |
| stock `sl` | `&mo` | 1000 | yes | no | same |

`lazy` exists in this tree (:36, :160-163, :290-293) but nothing enables it.

### 5.2 Press / release of the sticky key itself (PROVEN)
- Press (:142-165): if this position already has an active sticky key → stop its timer and release its behaviour first (:147-151). Store (max 10, `Kconfig.behaviors:84-88`). Not lazy → **press the bound behaviour now** (:160-163): `&mo` → layer on synchronously; `&kp MOD` → keycode event → HID report with the modifier.
- Release (:167-189):
  ```c
  if (modified_key set) { return release_sticky_key_behavior(...); }          // :175-178  "act like a normal key"
  timer_started = true; release_at = event.timestamp + release_after_ms;      // :181-182
  ms_left = release_at - k_uptime_get(); if (ms_left > 0) k_work_schedule(release_timer, ms_left);   // :184-187
  ```
  - `event.timestamp` is the position timestamp for a keymap-invoked sticky, the queue processing instant for `aksl` (§4.3).
- Timeout (:124-131, handler :342-354) → release behaviour (`&mo↑` layer off / `&kp MOD↑`).

### 5.3 What "the next key" means (PROVEN)
- The listener subscribes to `zmk_keycode_state_changed` **only** (:229-232). A sticky key therefore reacts to keys that produce a keycode and is blind to: `&mo`/`&to` layer keys, `&none`, an undecided hold-tap, `&trans`, a combo whose binding is not a key. It runs before `hid_listener` (§2).
- Per active sticky key, per keycode event (:251-310):
  - `&kp`-bound sticky keys skip their own keycode (:260-266). `&mo`-bound ones have no such check (irrelevant: they emit no keycode).
  - **key down**: `ignore_modifiers && is_mod` → skip (:269-274). Already has a modified key → skip (:275-278). Else **`stop_timer`** (:281); if `release_at != 0 && ev.timestamp > release_at` → timeout now (release), continue (:285-288); `quick_release && timer_started` → mark for release-after-reraise (:294-299); record `modified_key` (:300-301).
  - **key up**: `timer_started && matches modified_key` → `stop_timer`, mark for release-after-reraise (:303-308).
  - Release-after-reraise (:323-337): `dupe = copy; ZMK_EVENT_RAISE_AFTER(dupe, behavior_sticky_key)` → caps_word, key_repeat, combo, **hid_listener** process the key first; **then** `release_sticky_key_behavior` (`&mo↑` or `&kp MOD↑` → its own keycode event → HID). Returns `CAPTURED` so the original event stops (:339).
- Answers:
  - **Activated**: at the sticky key's press, synchronously.
  - **Deactivated, no quick-release** (`aksl`, `slm`, `skm`, `skms`, `sk`): on the **release** of the first keycode-producing key pressed after the sticky was released — after HID has sent that key's up report. Or at `release-after-ms` if no such key.
  - **Deactivated, quick-release** (`sl`, `skL`): right after HID processes that key's **press** (mod released before the key's up).
  - **Before or after keymap processing?** After. The keymap resolves the next key's binding *before* any keycode exists; the sticky listener runs only once that binding raises a keycode. The consuming key is always resolved on the sticky layer.
  - **Next key while the sticky key is still physically held** (timer not started): `modified_key` is recorded (:300-301) but nothing is scheduled; the key's up does nothing (:303 requires `timer_started`); on the sticky key's physical release it releases immediately (:175-178). Net: behaves like a normally held modifier/layer.
  - **release-after-ms** is a one-shot deadline from the sticky release; it is **cancelled by the next key down** (:281). After that the sticky is pinned until that key's up (or forever if that key never sends an up — not possible for `&kp`).
  - **ignore-modifiers**: modifier keycodes are not "the next key" (stacking). Without it (`aksl`, `skms`, `sl`, `skL`) a modifier down **is** the next key.
- Two sticky keys active at once are each evaluated; the dupe is raised once (`event_reraised` guard :330-335).
- Interaction with an undecided hold-tap: mod keycodes are captured by hold-tap first (`behavior_hold_tap.c:783-801`) → the sticky key sees them only when re-raised via `RAISE_AT(behavior_hold_tap)`, which passes through the sticky listener again.

### 5.4 `aksl` specifics (INFERRED from 5.3 + §4.3)
- The "100 ms AK window" is measured from the queue tick that releases `aksl` (P+21 after the physical press P), not from P: nominal end P+121.
- The window is **not a hard 100 ms**: the first keycode down inside it stops the timer (:281); `l_akX` then stays on until that key's up. Because `aksl` lacks `ignore-modifiers`, a **modifier** keycode counts: e.g. `skms LSHIFT` tap (→ `&kp LSHIFT↓` immediately, §6.6) pins `l_akX` until Shift's up — up to 1500 ms — and a later alpha still resolves on `l_akX`. Same for `&bm`/`htm` hold decisions. See test T-05.
- The `release_at` late check (:285-288) only bites when the timer is late (sysworkq blocked); the key that triggers it has already been resolved on the AK layer.
- Design doc `Design/ak-deepdive.md:86-87` states the window as "100 ms if no key is pressed" and "stays until next `&kp` releases" — consistent, but the modifier-pinning case is not documented.

## 6. Hold-tap (Q4) — `zmk/src/behaviors/behavior_hold_tap.c`

### 6.1 Instances on the board
| name | flavor | term | hold | tap | extras |
|---|---|---|---|---|---|
| `lk` / `LK(…)` | tap-preferred | 100 | `&bk`/linger macro | `&bk`/tap macro | `linger_keys/behaviors.dtsi:2-9`, `preprocessor_macros.c:66-74` (bindings order `<LINGER>,<TAP>`) |
| `lk_wispr` | tap-preferred | 100 | `&kp` | `&bk` | :11-18 |
| `htls` | hold-preferred | 90 | `&moAndBuffer` | `&skms` | `mods/behaviors.dtsi:45-54` |
| `htm` | tap-preferred | 130 | `&kp` | `&skm` | hold-while-undecided + linger, :35-43 |
| `hml`/`hmr`/`hml_X`/`hmr_X` | balanced | 500 | `&bm` | `&bk` / `ak_X_macro` | hold-trigger-key-positions (other hand + thumbs), hold-trigger-on-release, :92-149 |
| `hrmSk` | balanced | 500 | `&sk` | `&bk` | :84-90 |
| `blt`, `blt_akR`, `bksl` | tap-preferred | 200 | `&mo` / `&sl` | `&bk` / `ak_R_macro` | `adaptive_keys/behaviors.dtsi:11-38` |
| `bsklt` | balanced | 200 | `&mo` | `&bsk` | `mods/behaviors.dtsi:62-68` |
| stock `&mt` | hold-preferred | 500 (override) | `&kp` | `&kp` | `CONFIG.h:37-39` |

Not set anywhere → `quick-tap-ms = -1`, `require-prior-idle-ms = -1` (binding defaults, `zmk/dts/bindings/behaviors/zmk,behavior-hold-tap.yaml`), no retro-tap.

### 6.2 State + capture (PROVEN)
- One global `undecided_hold_tap` (:97); `active_hold_taps[10]`; `captured_events[40]` (`Kconfig.behaviors:52-62`).
- Press (:589-623): if another hold-tap is undecided → log + `OPAQUE`, **the press is dropped** (:594-598; reachable only for a hold-tap invoked outside the position pipeline, e.g. from a combo, since position events are captured). Store; `undecided_hold_tap = this`; `is_quick_tap` → decide `HT_QUICK_TAP` (:611-613); `HT_KEY_DOWN` (:615, matters only for hold-while-undecided); timer `k_work_schedule(work, (timestamp + tapping_term) − k_uptime_get())` (:619-620) → **term counts from the event timestamp** (physical press), delivery delay is subtracted.
- Position listener (:709-768), while undecided:
  - Records `position_of_first_other_key_pressed` on the first other-key **press**, or **release** when `hold-trigger-on-release` (:720-727) — before any decision.
  - Own key-up bubbles (:733-736). Late-timer check `ev.timestamp > timestamp + term` → `HT_TIMER_EVENT` first (:742-745).
  - Other key **up** with no captured down bubbles through (:751-757) — a key already held before the hold-tap started is released normally, does not decide.
  - Otherwise copy into `captured_events`, `decide(HT_OTHER_KEY_DOWN/UP)`, return `CAPTURED` (:759-767). The captured key is invisible to combo/keymap until release.
- Keycode listener (:770-802): `store_last_tapped(ts)` for every non-mod key **down** (:774-776, unconditional); while undecided, **modifier** keycode events are captured (:783-801) unless hold-while-undecided (:789-792).
- Release of captured events (:181-242): after `undecided_hold_tap = NULL`, each event is re-raised with `ZMK_EVENT_RAISE_AT(…, behavior_hold_tap)` in capture order. If a re-raised press creates a **new** undecided hold-tap, every remaining event is preceded by `k_msleep(10)` (:220-222) and is captured by the new one (comment :186-210).

### 6.3 Decision (PROVEN)
- `decide_hold_tap` (:511-558): flavor table → if decided: `decide_positional_hold` (:489-509) may flip HOLD→TAP when a first other key was recorded and it is **not** in `hold-trigger-key-positions` → `undecided_hold_tap = NULL; press_binding; release_captured_events` (:555-557).
- Flavors (:278-350):
  - **balanced**: KEY_UP→TAP, **OTHER_KEY_UP**→HOLD_INTERRUPT, TIMER→HOLD_TIMER, QUICK_TAP→TAP. Other-key *down* never decides.
  - **tap-preferred**: KEY_UP→TAP, TIMER→HOLD_TIMER, QUICK_TAP→TAP. Other keys never decide; they are captured until the term or the key-up.
  - **hold-preferred**: OTHER_KEY_DOWN→HOLD_INTERRUPT, KEY_UP→TAP, TIMER→HOLD, QUICK_TAP→TAP.
- `press_binding` (:444-464): HOLD → `press_hold_binding` unless hold-while-undecided already did (:449-455); TAP → if hold-while-undecided && !linger release the hold first (:457-461), then `press_tap_binding` (also `store_last_hold_tapped`, :418).
- Own release (:625-659): cancel timer; late-timer decision (:635-638); `HT_KEY_UP`; retro; `release_binding` (:642); **if hold-while-undecided-linger → `release_hold_binding` again** (:644-646) — on a HOLD decision this releases the hold binding twice (second is a harmless `-EINVAL` for `&kp`, `hid.c:61-64`).

### 6.4 Ordering on a tap decided by key-up (linger keys, HRM tap) — PROVEN
- Sequence inside `on_hold_tap_binding_released`: `decide(HT_KEY_UP)` → `press_binding(tap)` → `release_captured_events()` (captured other keys are delivered to combo/keymap **now**) → return → `release_binding(tap)` (:640-642).
- So output order is **TAP↓, OTHER↓(/↑)…, TAP↑**. With `&bk` as tap: `kp↓` sync + `kp↑` queued (+10 ms); the other key's `&ak` items queue behind → its HID down is emitted at the +10 ms tick, after `kp↑`.
- Linger key example (`lk` 100 ms): press L at t; press N at t+40 (captured, invisible); release L at t+80 → TAP → `bk`: `kp L↓` at t+80; N delivered → `&ak N` enqueued; t+90: `kp L↑`, `kp N↓`; t+100: `kp N↑`, `aksl N↓/↑`. If instead L is still held at t+100 → `HT_TIMER_EVENT` → HOLD → linger macro pressed at t+100, then N delivered (captured until then).

### 6.5 `is_quick_tap` with `-1` defaults is not fully disabled (INFERRED, testable T-06)
```c
static bool is_quick_tap(struct active_hold_tap *hold_tap) {
    if ((last_tapped.timestamp + hold_tap->config->require_prior_idle_ms) > hold_tap->timestamp) return true;   // :143
    return (last_tapped.position == hold_tap->position) && (last_tapped.timestamp + quick_tap_ms) > hold_tap->timestamp;
}
```
- With `require_prior_idle_ms = -1` the test is `last_tapped.ts − 1 > ht.ts`: true whenever a non-mod keycode down was recorded with a timestamp **later** than this hold-tap's physical press. Queued keycodes carry the processing instant (§4.1 rule 5) while the hold-tap carries the physical press.
- Scenario: AK alpha X at t0, hold-tap H at t0+5 (both inside the 11 ms hack window → combo releases X then H at t0+11). X's `kp↓` keycode ts = t0+11 → `last_tapped = t0+11`. H delivered (re-captured once by the hack, ~t0+16) with `timestamp = t0+5` → `t0+10 > t0+5` → **forced TAP immediately**, regardless of how long H is then held. Applies to HRMs, linger keys, thumb `blt`/`htls`/`bsklt` following an `&ak` alpha within ~11 ms. Effectively a hidden `require-prior-idle ≈ 11 ms` for AK-preceded hold-taps only (plain `&kp` predecessors keep their physical timestamp → no skew). `combo.c:141-146` has the same shape for combos' `require-prior-idle-ms`.

### 6.6 `htm` (hold-while-undecided + linger, tap = `&skm`) — PROVEN trace
- Press → `HT_KEY_DOWN` → `press_hold_binding` → `&kp MOD↓` (explicit count 1, HID report) (:522-526). Mod keycode bubbles (not captured, :789-792).
- Tap (<130 ms): `press_binding` → linger → no hold release → `&skm MOD↓` → sticky presses `&kp MOD↓` again (count 2). `release_binding` → `&skm↑` → timer 1500 ms. Then :645 `&kp MOD↑` (count 1). Net: modifier stays registered through the sticky until the next non-mod key's up (`ignore-modifiers` → other mods stack). No gap in the modifier.
- Hold (≥130 ms or other key): HOLD_TIMER/… → `press_binding` returns 0 (:449-451). Release → `&kp MOD↑` (count 0) then :645 again → `-EINVAL`, no report.

### 6.7 HRM (`hml*`/`hmr*`: balanced, 500 ms, positional on-release) — INFERRED timelines
- Cross-hand: S↓ (undecided), E↓ captured, E↑ captured → `HT_OTHER_KEY_UP` → HOLD_INTERRUPT → positional: first other key = E recorded at its **release** (:720-727) ∈ trigger list → HOLD → `&bm LSHIFT↓`, then E↓/E↑ re-raised → shifted E. **Nothing is emitted until E is released** (or 500 ms).
- Same-hand: S↓, T↓ captured, T↑ captured → HOLD_INTERRUPT → positional: T ∉ trigger list → TAP → `ak_S_macro` (§4.4 nested-sync burst: S↓ S↑ `l_akS` on) → T↓/T↑ re-raised → T resolved on `l_akS`. Output S then T, both only at T's release.
- Two HRMs: S↓, N↓ captured, K↓ captured, K↑ captured → decision at K↑ (HOLD for S if K is cross-hand) → re-raise N↓ → new undecided HT → `k_msleep(10)` before K↓, again before K↑ (each re-raise re-captured by N) → 20 ms of sysworkq sleep (timers, kscan all wait).

## 7. Mod-morph (Q5) — `zmk/src/behaviors/behavior_mod_morph.c` (PROVEN)

- Press (:37-55): `if (zmk_hid_get_explicit_mods() & cfg->mods) { zmk_hid_masked_modifiers_set(cfg->masked_mods); pressed = morph; } else pressed = normal;` then press it with the same event.
  - **Explicit** mods only (`hid.c:50` = mods registered via `&kp MOD` presses: sticky, `&bm`, `htm`, held `&kp LSHIFT`). Implicit mods of `LS(X)`-style keycodes do not count.
  - `masked_mods = mods & ~keep-mods` (:94-101); none of Flo's 23 morphs set `keep-mods` → the whole trigger set is masked.
  - Pressing the same instance again before release → `-ENOTSUP` (:43-46): a morph is per-instance single-shot.
- Release (:57-73): release the remembered binding, then `zmk_hid_masked_modifiers_clear()` (:71).
- Masking (`hid.c:42-46`): `report.modifiers = (explicit & ~masked) | implicit`. Set/clear only rewrite the report struct; the next keycode event's report carries it. The mask is global while the morph is held.
- With `&bk` bindings (all of Flo's): morph↓ → `kp↓` sync if idle (report without the masked mod), `kp↑` +10 ms; physical release → mask cleared. If the queue is busy at morph press (e.g. inside `moAndBuffer`'s 130 ms park, §4.4) the `kp↓` is deferred; if the physical release (mask clear) lands before the deferred `kp↓`, the modifier leaks into the report (INFERRED, T-08).
- `MagicSlash` (`mod_morph/behaviors.dtsi:120-126`) morphs between two **linger keys**: the hold-tap is only created when the morph is pressed, so the linger term starts at morph press.

## 8. HID emission — when a report actually goes out (PROVEN)

- `&kp` → `raise_zmk_keycode_state_changed_from_encoded(param1, state, event.timestamp)` (`behavior_key_press.c:42-52`); page defaults to keyboard; mods in the encoding become `explicit_modifiers` for a mod keycode, else `implicit_modifiers` (`keycode_state_changed.h:32-40`).
- `hid_listener` (`zmk/src/hid_listener.c`), last in the keycode chain:
  - Down (:19-56): if the same usage is already pressed → release + **extra report** first (:22-35). `zmk_hid_press`, `zmk_hid_register_mods(explicit)`, `zmk_hid_implicit_modifiers_press(implicit)`, then `zmk_endpoints_send_report(page)` (:55) → **one report per keycode down** (plus a keyboard-page report for consumer keys whose mods changed, :46-53).
  - Up (:58-97): `zmk_hid_release`; on error (e.g. releasing a mod whose count is 0, `hid.c:60-64`) **return early, no report** (:63-67). `CONFIG_ZMK_HID_SEPARATE_MOD_RELEASE_REPORT=y` → report with the key up and mods unchanged (:69-78), then `unregister_mods(explicit)` + `implicit_modifiers_release()` → second report (:96). So `&kp LS(A)` release = 2 reports (A up with Shift, then Shift up). Flo's `corne.conf` FIXME "doesn't seem to work" — the code path is compiled and active; what he observed is OPEN (T-09).
- Modifier bookkeeping (`hid.c`): explicit mods are **ref-counted** per modifier (:37, :52-75) → two holders (e.g. `htm`'s `&kp` + `skm`) keep the bit until both release. Implicit mods are one global byte overwritten by every non-mod press and cleared by every release (:265-276; upstream comment :81-85 documents the `LC(A)`+`LS(B)` premature-release quirk).
- Transport: `zmk_endpoints_send_report` (`endpoints.c:191-204`) → BLE: copy into the HOG msgq + submit to the HOG thread (`hog.c:258-276`, blocks up to 100 ms only if 20 reports are already queued); USB: `hid_int_ep_write` after `k_sem_take(30 ms)` (`usb_hid.c:129-147`), synchronous.
- Report type: `ZMK_HID_REPORT_TYPE` choice, not overridden → HKRO, 6 keys (`Kconfig:53-70, 82-85`).

## 9. Composite timelines for the page (each derivable from the above)

- **T-A plain AK alpha X** (physical P): P kscan → position event (ts P) → hold-tap bubble → combo captures (36-key hack) → P+11 combo timeout → keymap resolves on highest active layer → `&ak` → HID `X↓` at P+11 → P+21 HID `X↑`, `l_akX` on, window armed to P+121.
- **T-B chain X then Y (Y within window, Y is `&ak`/`&trans` on `l_akX`)**: Y physical Q → Q+11 keymap resolves on `l_akX` → falls through to `&ak Y` → `Y↓` (sync) → aksl X: `stop_timer`, modified = Y → Q+21 `Y↑` → aksl X released **after** HID (`l_akX` off) → `aksl Y↓` (`l_akY` on) → `aksl Y↑`. Old layer off and new layer on in the same tick; matches `adaptive_keys/behaviors.dtsi:7-8`.
- **T-C replacement**: as §4.4, 40 ms from trigger delivery to `l_akB1` on.
- **T-D linger**: §6.4.
- **T-E Callum thumb (`htls`)**: tap <90 ms → `skms LSHIFT↓` immediately at release; hold → at 90 ms (or first other key down, hold-preferred) `moAndBuffer↓` → `l_mod` on; release → 130 ms park + `l_mod` off at +130.
- **T-F HRM**: §6.7.

## 10. Open questions (each with the test that settles it)

- **OQ-1** Listener order really equals `CMakeLists.txt` order in Flo's build (INFERRED). Settle: `objdump -s -j .event_subscription zmk.elf` (or `nm --numeric-sort | grep zmk_event_sub_`) on the built firmware; expect `activity < behavior_hold_tap < combo < behavior_tap_dance < keymap` for position subs.
- **OQ-2** Nested-sync 0 ms tap for `ak_X_macro` (§4.4) — is this what Flo perceives as "missed keys"? Settle with T-03; if confirmed, `ak_X_macro` should set `tap-ms` on the outer macro or the inner `&ak` should be invoked from the work.
- **OQ-3** Late tapping term: `k_work_schedule(K_MSEC(negative))` when the term has already elapsed at delivery (`behavior_hold_tap.c:619-620`). Not reachable with 11 ms combo delay vs ≥90 ms terms unless the sysworkq blocks >90 ms; the release/position late checks (:636, :742) cover correctness. Worth one native_posix case with a 30 ms combo hack + 20 ms term.
- **OQ-4** `SEPARATE_MOD_RELEASE_REPORT`: code is active; what did Flo expect? Settle with T-09 (count reports on `LS(A)` release).
- **OQ-5** `hold-while-undecided` "presses twice" (Flo's comment `mods/behaviors.dtsi:50`): code shows a double **release** (:642 + :645) on HOLD, not a double press; with `moAndBuffer` as hold the second release re-queues the 130 ms park (macro release part) — plausible root of the observation. Settle with T-10.

## 11. Testable claims (id → claim → native_posix sketch)

- **T-01** Queue tick timing: `&ak`-style macro (wait 0 / tap 10) emits `kp↓` synchronously and `kp↑`, `aksl↓`, `aksl↑` exactly one tick later. Keymap: `&ak_like 1 A` on pos 0 where `ak_like` = macro `wait-ms 0; tap-ms 10; <&macro_tap &kp A>, <&macro_tap_time 0>, <&macro_tap &aksl 1>`; layer 1 pos 1 = `&kp B`, layer 0 pos 1 = `&kp C`. Events `PRESS(0,0,5) RELEASE(0,0,5) PRESS(0,1,50) RELEASE(0,1,50)`. Patterns: `hid_listener_keycode`, `mo_keymap_binding`, `behavior_queue_process_next`. Expect: `kp_pressed A`, `Processing next queued behavior in 10ms`, then `kp_released A`, `mo_pressed`, then `kp_pressed B` (layer 1 active at 10 ms < 60 ms).
- **T-02** Second macro appends FIFO and cannot overtake: two macro keys `M1` (`&kp A` tap 10, wait 10, then `&kp B`) and `M2` (`&kp C`). Events `PRESS(0,0,2) PRESS(0,1,100) …`. Expect `A↓ A↑ B↓ B↑ C↓ C↑` with `C↓` after `B↑` even though M2 was pressed 2 ms after M1.
- **T-03** Nested-sync 0 ms tap + immediate AK layer: hold-tap `ht` tap-preferred 100, tap = `outer` (macro `wait 0; tap 0; <&ak_like 1 A>`), hold = `&kp X`; layer 1 pos 1 = `&kp B`. Events `PRESS(0,0,10) PRESS(0,1,10) RELEASE(0,1,10) RELEASE(0,0,10)`… simpler: `PRESS(0,0,20) RELEASE(0,0,10) PRESS(0,1,5) RELEASE(0,1,10)`. Expect `kp_pressed A` and `kp_released A` with **no** "Processing next queued behavior in 10ms" between them, `mo_pressed` in the same burst, and `kp_pressed B` (layer 1 seen 5 ms later). Control: same keymap but `ak_like` bound directly on pos 0 → `A↑` after the 10 ms tick.
- **T-04** Sticky `&mo` without quick-release is released on the consuming key's **up**, after HID: `&aksl_like 1` on pos 0 (release-after 100, `&mo`), layer 1 pos 1 `&kp B`. Events `PRESS(0,0,10) RELEASE(0,0,10) PRESS(0,1,50) RELEASE(0,1,10)`. Expect `mo_pressed`, `kp_pressed B`, `kp_released B`, then `mo_released` (order in log). Variant with `quick-release` → `mo_released` right after `kp_pressed B`.
- **T-05** Modifier pins an `aksl` layer beyond 100 ms: pos 0 `&aksl_like 1`, pos 1 `&sk LSHIFT`-style sticky mod without ignore-modifiers…, actually use `&kp LSHIFT` held: events `PRESS(0,0,10) RELEASE(0,0,10) PRESS(0,1,300) …` where pos 1 = `&kp LSHIFT`; then `PRESS(0,2,10)` where layer 1 pos 2 = `&kp B`, layer 0 pos 2 = `&kp C`. Expect `kp_pressed B` (layer 1 still active at 320 ms) and `mo_released` only after `kp_released LSHIFT`. Control with `ignore-modifiers` on the sticky → `mo_released` at 110 ms and `kp_pressed C`.
- **T-06** Skewed `is_quick_tap` forces TAP: pos 0 = `ak_like 1 A` (queued keycode), pos 1 = `&ht LSHIFT J` balanced 300 with defaults, plus a 2-key combo on {0,1} with 11 ms timeout bound to `&none` (to emulate the hack). Events `PRESS(0,0,5) PRESS(0,1,50) RELEASE(0,1,300) RELEASE(0,0,10)`. Expect `ht_decide: 1 decided tap (balanced decision moment quick-tap)` at delivery, `kp_pressed J`. Control: pos 0 = plain `&kp A` → `decided hold-timer`.
- **T-07** `moAndBuffer` release parks the queue 130 ms: pos 0 = `moAndBuffer_like` (as Flo's), pos 1 = `&bk_like C` (tap 10). Events `PRESS(0,0,200) RELEASE(0,0,20) PRESS(0,1,10) RELEASE(0,1,200)`. Expect `kp_pressed C` only after `Processing next queued behavior in 130ms` elapses (i.e. ~130 ms after pos 0 release), and `mo_released` before `kp_pressed C`.
- **T-08** Mod-morph mask leak when queue busy: same as T-07 plus pos 2 = mod-morph(`&bk_like A`, `&bk_like B`, mods LSFT), pos 3 = `&kp LSHIFT` held first. Events: hold Shift, hold+release pos 0 (parks queue), tap pos 2 for 20 ms inside the park. Expect `kp_pressed B` with the report's modifier byte including Shift (log `Modifiers set to 0x02` before `kp_pressed`), i.e. morph chosen but mask cleared before emission. Control without the park → `Modifiers set to 0x00`.
- **T-09** SEPARATE_MOD_RELEASE: `&kp LS(A)` tap with `CONFIG_ZMK_HID_SEPARATE_MOD_RELEASE_REPORT=y` in the test `.conf`. Expect two `zmk_endpoints_send_report`/`usage page` log lines on release (pattern on `endpoints`), first with A cleared and modifiers 0x02, second modifiers 0x00.
- **T-10** `hold-while-undecided-linger` double release: `ht` tap-preferred 130, hwu+linger, hold = macro with `pause_for_release` and a 130 ms wait in its release part, tap = `&kp B`. Hold 200 ms then release. Expect the macro's release part queued **twice** (two `Processing next queued behavior in 130ms` lines).
- **T-11** Tap-preferred captured-key ordering (§6.4): `lk_like` tap-preferred 100, tap `&bk_like L`, hold `&kp X`; pos 1 = `ak_like 1 N`. Events `PRESS(0,0,40) PRESS(0,1,40) RELEASE(0,0,10) RELEASE(0,1,50)`. Expect log order: `kp_pressed L`, (queue tick 10 ms) `kp_released L`, `kp_pressed N`, i.e. N's down after L's up although N was physically pressed before L was released.
- **T-12** `k_msleep(10)` on nested hold-taps: two balanced HTs on pos 0/1 (hold `&kp LSHIFT`/`&kp LCTRL`), pos 2 `&kp K`. Events `PRESS(0,0,10) PRESS(0,1,10) PRESS(0,2,10) RELEASE(0,2,10) RELEASE(0,1,10) RELEASE(0,0,10)`. Expect uptime stamps in the log (enable `CONFIG_LOG_TIMESTAMP`… native_posix prints `[hh:mm:ss.mmm]`) to show ≥10 ms between "Releasing key position event for position 2 pressed" and "… released".
