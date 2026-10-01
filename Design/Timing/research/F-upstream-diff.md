# F · Upstream diff vs fork (timing story only)

> Fork = upstream `6e03a0bb` (2024-09-12). Upstream = `5b51501f` = `v0.3-192-g5b51501f` (2026-09-26).
> Paths: `fork:` = `/Users/flo/Work/Private/Dev/Keyboard/zmk` (byte-identical to `6e03a0bb` for every file cited), `HEAD:` = scratchpad worktree `zmk-upstream`.
> Legend: **PROVEN** = read in both trees / in generated build output. **INFERRED** = reasoning, not executed.

## 🎯 Verdict first

- ✅ **The 19-key claim is TRUE for v0.3.0 and all later upstream.** Mechanism = `LISTIFY(20, …)` iteration bound in `combos[]` construction (HEAD `app/src/combo.c:100-101`), not a Kconfig range, not a hard-coded 19. Build succeeds, two `#warning`s, combo silently absent at runtime. Details §2.
- ✅ **Combo engine timing semantics are identical** fork → HEAD: buffering, capture/bubble, release-then-re-raise order, first-key timestamp on the combo behavior, timeout deadline, shortest-first winner, slow-release. What changed is storage (bitmasks), limits, layer filtering encoding, virtual-position numbering, and the invocation entry point. Details §1.
- ✅ **Behaviour queue timing identical** (dequeue-time `k_uptime_get()` stamps, `k_work_schedule(K_MSEC(wait))` only for `wait > 0`, synchronous drain otherwise). One macro fix (`1bac680c`) is a **no-op for Flo's macros** (audited). §3.
- ✅ **Hold-tap: zero logic change.** Sticky key: `find_sticky_key` now matches on (position, behavior, param) instead of position alone (`7186528f`); **no observable difference for Flo's `aksl`/`sk` usage** (quick-release makes the cross-type collision unreachable). §4.
- ✅ **Split transport: same wire format, same queues, same BLE link params (7.5 ms interval, latency 30).** One semantic change: a left-hand key's timestamp is taken in the BT RX callback on the fork, in the system workqueue on HEAD (sub-ms, INFERRED magnitude). §5.
- 🧨 **The only conclusion that flips on upstream:** the 36-key `combo_ak_consistency_hack` stops existing, so every "keys with no other combo candidate" press is no longer delayed by `hold_key_event_delay` (11 ms) and the "released AT ONCE" failure documented in `adaptive_keys/combos.dtsi:15-25` returns. Everything else on the page can be stated for "ZMK 2024-09 fork through upstream main 2026-09".

## 🏷️ Version naming (for the page's "true for ZMK …" line)

- Tags (PROVEN, `git tag` + `git log`):
  - `v0.1` = `v0.1.0` → `a9ff3a78` 2024-12-04
  - `v0.2.0` → `fadafc77` 2025-03-01; `v0.2` = `v0.2.1` → `241ff395` 2025-03-02
  - `v0.3` = `v0.3.0` → `edf5c081` 2025-08-01
  - HEAD `5b51501f` = `git describe` → `v0.3-192-g5b51501f`; `.release-please-manifest.json` still `0.3.0` → "unreleased main after v0.3.0" (next tag will be ≥ 0.4.0: `c06fa48c feat!: Move to zephyr v4.1`).
- Fork point `6e03a0bb` is **pre-v0.1.0** (145 commits before the first tag; `git describe` fails). Call it "ZMK main @ 2024-09-12 (pre-v0.1)". 455 commits fork→HEAD.
- Where each relevant change lands (PROVEN via `git tag --contains`):
  - Locality plumbing (`9e36ebd5`, `4fdfb01b`, `fb18a4d8`, all committed 2024-09-23, 11 days after fork): **v0.1.0+**
  - Combo `const` (`18d0d2f4`), sticky-key same-position fix (`7186528f`): **v0.2.0+**
  - Combo rewrite (`c4ee8ab8`), cleanup fix (`e3030bfc`), deprecated-Kconfig prompt restore (`00ff4869`), macro release fix (`1bac680c`), split transport abstraction (`6b44d33d`), wired split (`147c340c`): **v0.3.0+**
  - Zephyr 4.1 + `native_sim` (`c06fa48c` 2025-12-09), layer locking (`5138c6fb` 2025-11-14), hold-tap include cleanup (`9ebbeff0`): **main only, unreleased**
- Zephyr: fork `v3.5.0+zmk-fixes` (PROVEN: `/z/VERSION` in the `zmk-zephyr` Docker volume), HEAD `v4.1.0+zmk-fixes` (`app/west.yml`).

## 1 · Combo engine · semantic changelog

### 🟰 Unchanged (PROVEN, both files read in full)

- **Event model** · subscribes `zmk_position_state_changed` + `zmk_keycode_state_changed`; keydown → `position_state_down`, keyup → `position_state_up`. Runs synchronously inside the event listener (system workqueue context).
- **Buffering / capture** · first key with ≥1 candidate returns `ZMK_EV_EVENT_CAPTURED` and is copied into `pressed_keys[]`; a key with zero candidates bubbles untouched (`fork:426` / `HEAD:426`).
- **Release / re-raise order** · `release_pressed_keys` (`fork:273-289` / `HEAD:263-279`, byte-identical): index 0 → `ZMK_EVENT_RELEASE` (resume original propagation), index ≥1 → `ZMK_EVENT_RAISE` (re-enter from the top). Key-up path `position_state_up` (`fork:456-470` / `HEAD:459-473`): `cleanup()` first, then `release_combo_key`, then re-raise a dupe key-up if >1 keys were flushed. Identical.
- **Timestamps** · combo behavior press carries `key_positions_pressed[0].data.timestamp` = first key's event timestamp (`fork:349` / `HEAD:347-348`); release carries the releasing key's timestamp. Identical.
- **Timeout scheduling** · `update_timeout_task` identical (`fork:407-420` / `HEAD:406-419`): `k_work_schedule(&timeout_task, K_MSEC(first_timeout - k_uptime_get()))`, deduped via `timeout_task_timeout_at`. Deadline value identical = `first_key.timestamp + min(timeout_ms over live candidates)`:
  - fork stores it per candidate at setup: `candidates[i].timeout_at = timestamp + combo->timeout_ms` (`fork:155`), reads min in `first_candidate_timeout` (`fork:197-208`)
  - HEAD recomputes from `pressed_keys[0].data.timestamp + combos[i].timeout_ms` (`HEAD:216`, `HEAD:237`)
- **Winner ordering** · shortest `key-positions` first, then declaration order:
  - fork: `initialize_combo` insertion-sorts `combo_lookup[pos]` by `(key_position_len, virtual_key_position)` where `virtual_key_position = __COUNTER__` in DT order (`fork:110-117`, `fork:524`)
  - HEAD: `combos[]` is emitted length-bucket by length-bucket (`LISTIFY(20, …)`, `HEAD:100-101`), so lowest set bit in `candidates` = shortest, then DT order (`HEAD:438-449`)
- **Fully-pressed decision** · `candidate_is_completely_pressed` = `key_position_len == pressed_keys_count` (`fork:216` / `HEAD:225`). 1 candidate & complete → immediate `cleanup()` → `activate_combo`; ≥2 candidates & shortest complete → park in `fully_pressed_combo`, wait for timeout or next key. Same branches (`fork:438-453` / `HEAD:437-454`).
- **`require-prior-idle`** (`is_quick_tap`, `store_last_tapped`, `last_combo_timestamp`), **slow-release** (`release_combo_key`), **`CONFIG_ZMK_COMBO_MAX_PRESSED_COMBOS`** (Flo: 20) · identical.

### 🔁 Changed

- **Storage** (`c4ee8ab8`, v0.3.0) · pointers → indices; `candidates` and `combo_lookup[pos]` are `uint32_t` bitmasks (`HEAD:114`, `HEAD:118`); `combos[]` is `const` in flash (`18d0d2f4` + `c4ee8ab8`). Pure representation change.
- **Limits**
  - `CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO` → auto: `#define MAX_COMBO_KEYS sizeof(union {DT_INST_FOREACH_CHILD(0, COMBOS_KEYS_BYTE_ARRAY)})` (`HEAD:43-46`) = longest `key-positions` across **all** combo nodes (including ones later dropped, see §2).
  - `CONFIG_ZMK_COMBO_MAX_COMBOS_PER_KEY` → unlimited (bitmask). The fork's silent `-ENOMEM` "Too many combos for key position" drop (`fork:119-123`, return value ignored by `INITIALIZE_COMBO` `fork:530,536`) no longer exists. Flo's build peaks at 6 combos/position (positions 12, 16, 17, 23; PROVEN from `build/right/zephyr/zephyr.dts`) vs cap 30 → never hit on the fork either.
  - **New hard cap**: `key-positions` length ≥ 20 → node not compiled into `combos[]` (§2).
  - Fork buffer-cap bug fixed: `capture_pressed_key` guards with `CONFIG_ZMK_COMBO_MAX_COMBOS_PER_KEY` (`fork:263`, = 30 in Flo's conf) although `pressed_keys` has `MAX_KEYS_PER_COMBO` (36) slots; HEAD guards with `MAX_COMBO_KEYS` (`HEAD:253`). Consequence on the fork: at most 30 keys ever buffered; the 31st bubbles. Irrelevant in practice.
  - Fork's runtime `position >= ZMK_KEYMAP_LEN` check (`fork:96-99`) is gone; HEAD indexes `combo_lookup[position]` unchecked (`HEAD:144`).
- **Layer filtering encoding** · fork: `int8_t layers[]` + `-1` sentinel in slot 0 (`fork:128-139`, yaml default `[-1]`); HEAD: `uint32_t layer_mask = OR(BIT(layer))` via `NODE_PROP_BITMASK` (`HEAD:69-73`, `:87`), empty/omitted → mask 0 → global (`HEAD:150-156`); yaml default removed (`app/dts/bindings/zmk,combos.yaml`). Same decision for explicit layer lists. **INFERRED risk**: an explicit `layers = <-1>` on HEAD expands to `BIT(4294967295)` (DT arrays are u32 cells) = UB / shift-count warning. Flo's config never uses it: `l_all` / `l_alpha_aks` are explicit lists (`__BASE__/aliases_layers_NAQUADAH.dtsi:59-60`); `l_any (-1)` is defined (`:16`) but unused (grep).
- **Virtual key position numbering** · fork `ZMK_VIRTUAL_KEY_POSITION_COMBO(__COUNTER__)` in DT order (`fork:524`); HEAD `ZMK_VIRTUAL_KEY_POSITION_COMBO(combo_idx)` with `combo_idx` = index in the length-sorted `combos[]` (`HEAD:284`, `:300`). Different numbers, still unique per combo → hold-tap `position_of_first_other_key_pressed` and sticky-key position identity behave the same.
- **Invocation entry point** (`4fdfb01b`, v0.1.0) · `behavior_keymap_binding_pressed/released` (`fork:299/308`) → `zmk_behavior_invoke_binding(&combo->behavior, event, pressed)` with `.source = ZMK_POSITION_STATE_CHANGE_SOURCE_LOCAL` (`HEAD:281-307`). `zmk_behavior_invoke_binding` (HEAD `app/src/behavior.c:67-115`) adds `behavior_keymap_binding_convert_central_state_dependent_params` (implemented only by backlight / ext_power / rgb_underglow) and a locality switch (`:87-112`). Every behavior Flo binds to combos (`&bk`, `&none`, `&lk_*` hold-taps, bigram macros) has default `BEHAVIOR_LOCALITY_CENTRAL` (only reset/backlight/ext_power/rgb_underglow/soft_off declare `.locality`, PROVEN by grep in both trees) → `invoke_locally` → same function as before plus one `zmk_behavior_get_binding` name lookup. Not a timing change.
- **First-key test** · `candidates[0].combo == NULL` (`fork:424`) → `!pressed_keys_count` (`HEAD:423`). Both are reset together in `cleanup()`; INFERRED equivalent in every reachable state.
- **`update_timeout_task()` moved after `capture_pressed_key`** (`fork:433,437` → `HEAD:434-435`) because `first_candidate_timeout` now reads `pressed_keys[0]`. Same deadline.
- **`filter_candidates` return saturates** at "0 / 1 / ≥2" (`zero_one_or_more_bits`, `HEAD:181-202`); only ever compared to 0 and 1. Same.
- **`combo_init`** · seeds `active_combos[i].combo_idx = UINT16_MAX`, logs `LOG_WRN("Have %d combos!", ARRAY_SIZE(combos))` (`HEAD:523-534`).
- **`e3030bfc`** · fixed `memset(candidates, 0, BYTES_FOR_COMBOS_MASK)` → `* sizeof(uint32_t)` (`HEAD:398`). Between `c4ee8ab8` and `e3030bfc` (one day, never released) only 8 candidate bits were cleared on cleanup. No released version carries the bug.

## 2 · The 19-key claim · VERIFIED

**Claim**: "On ZMK v0.3 the combo is silently dropped: the engine only builds combos with up to 19 key positions."
**Verdict: TRUE** for `v0.3.0` and every later upstream commit (introduced by `c4ee8ab8` 2025-04-20, not in `v0.2.1`; `combo.c` untouched since `e3030bfc` 2025-04-22).

- **Mechanism** (PROVEN, HEAD `app/src/combo.c:77-101`):

  ```c
  #define COMBO_INST(n, positions)                                                                   \
      COND_CODE_1(IS_EQ(DT_PROP_LEN(n, key_positions), positions),                                   \
                  ( { .timeout_ms = DT_PROP(n, timeout_ms), ... .layer_mask = NODE_PROP_BITMASK(n, layers), }, ), \
                  ())
  #define COMBO_CONFIGS_WITH_MATCHING_POSITIONS_LEN(positions, _ignore)                              \
      DT_INST_FOREACH_CHILD_VARGS(0, COMBO_INST, positions)
  // `20` is chosen as a reasonable limit, since the theoretical maximum number of keys you might
  // reasonably press simultaneously with 10 fingers is 20 keys, two keys per finger.
  static const struct combo_cfg combos[] = {
      LISTIFY(20, COMBO_CONFIGS_WITH_MATCHING_POSITIONS_LEN, (), 0)};
  ```

  - Zephyr `LISTIFY(LEN, F, sep, ...)` = `UTIL_CAT(Z_UTIL_LISTIFY_, LEN)(F, sep, ...)` → `F(0) … F(LEN-1)` (PROVEN in Zephyr 3.5: `include/zephyr/sys/util_macro.h:418`, `util_listify.h:92`). So lengths **0..19** are emitted; a 20-key combo is dropped too (the claim's "up to 19" is exact).
  - `IS_EQ(a, b)` = `Z_HAS_COMMA(Z_CAT4(Z_IS_, a, _EQ_, b)())` backed by a table `Z_IS_0_EQ_0 … Z_IS_4095_EQ_4095` (`util_internal.h:55`, `util_internal_is_eq.h:16,52,4111`). `IS_EQ(36, k)` for k ∈ 0..19 is a well-defined `0` → `COND_CODE_1` emits nothing. No error, no diagnostic.
  - PROVEN for Zephyr `v4.1.0+zmk-fixes` too (what upstream actually builds with; headers fetched from `zmkfirmware/zephyr` at that tag, saved as `scratchpad/z41_util_*.h`): `LISTIFY` one-liner identical (`util_macro.h:478` vs 3.5 `:418`), `IS_EQ(a,b) → Z_IS_EQ` identical (`util_macro.h:322` / `util_internal.h:55`, both versions), `COND_CODE_1` identical (`:203` vs `:179`), `Z_UTIL_LISTIFY_0..4096` = 4097 entries in both `util_listify.h`, `Z_IS_0_EQ_0 … Z_IS_4095_EQ_4095` in both `util_internal_is_eq.h` (4.1 adds `U`-suffix twins only). Same drop on Zephyr 3.5 and 4.1.
- **Not** a hard-coded 19, **not** a Kconfig range, **not** a DT build assert: nothing in `app/dts/bindings/zmk,combos.yaml` or `combo.c` checks `key-positions` length.
- **Build vs runtime, error vs silent** (Flo's `corne.conf` on upstream):
  - Kconfig: `CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO=36` and `…_MAX_COMBOS_PER_KEY=30` are **accepted**. Symbols still exist with a prompt and `default 0` (`app/Kconfig:454-464`). `00ff4869` "Restore prompts for two deprecated Kconfigs … to avoid errors for existing builds that set them explicitly" — Zephyr's `kconfig.py` aborts on assignments to promptless/undefined symbols (`scripts/kconfig/kconfig.py:41-44,118` in the 3.5 volume), so for one day (`c4ee8ab8`→`00ff4869`, never released) this was a hard Kconfig error; in v0.3.0 it is not.
  - Compile: `#warning "CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO is deprecated, and is auto-calculated from the devicetree now."` and the `MAX_COMBOS_PER_KEY` twin (`HEAD:30-41`). No `-Werror` / `COMPILER_WARNINGS_AS_ERRORS` in ZMK's app Kconfig/CMake (grep empty) → warning only.
  - Runtime: `combo_init` logs `Have 27 combos!` (Flo has 28 combo nodes: 19×2-key, 7×3-key, 1×4-key, 1×36-key — PROVEN from `zmk/app/build/right/zephyr/zephyr.dts`, built 2025-09-27 12:07). No error for the missing one.
  - Side effect: the 36-key node still inflates `MAX_COMBO_KEYS` to 36 (`sizeof(union …)` includes every child) → `combo_cfg.key_positions[36]` in each of the 27 flash entries, `pressed_keys[36]` and `active_combos[20].key_positions_pressed[36]` in RAM. Wasteful, harmless.
- **What the hack loses on upstream** (PROVEN mechanism, from `adaptive_keys/combos.dtsi` + `zephyr.dts`):
  - `combo_ak_consistency_hack`: `key-positions` = all 36, `timeout-ms = 0xb` (11 = `hold_key_event_delay`), `layers` = 0..24 (alpha, alpha_linwin, 23 AK layers), `bindings = <&none>`.
  - Its job: be a candidate for **every** key on those 25 layers so `setup_candidates_for_first_keypress` never returns 0 and every press is buffered ≥11 ms, guaranteeing `&ak`'s `kp` tap (10 ms) completes before a flushed follow-up key.
  - On upstream the node is absent from `combos[]` → for a key that is in no other combo, `position_state_down` returns `ZMK_EV_EVENT_BUBBLE` at `HEAD:425-426` → immediate delivery, no 11 ms delay → the timed-out-combo "released AT ONCE" ordering bug the hack fixes (combos.dtsi:15-25) comes back. Silent: firmware runs, AKs misfire on fast rolls.
- **On the fork (what actually runs)**: the 36-key combo is compiled (`key_positions[CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO=36]`, `fork:30`) and registered on all 36 positions. It can never complete: `capture_pressed_key` caps the buffer at 30 (`fork:263` bug above) < 36. By design it never needs to.

## 3 · Behaviour queue / macro timing

- **`app/src/behavior_queue.c`** (HEAD read in full, fork diff is plumbing only):
  - `zmk_behavior_queue_add` (`HEAD:60-82`): `k_msgq_put(K_NO_WAIT)` then, `if (!k_work_delayable_is_pending(&queue_work))`, drains **synchronously in the caller's context** (`:77-79`).
  - `behavior_queue_process_next` (`:31-58`): loop; each item invoked with `.timestamp = k_uptime_get()` **at dequeue** (`:39`); `if (item.wait > 0) { k_work_schedule(&queue_work, K_MSEC(item.wait)); break; }` (`:53-56`). Zero-wait items chain back-to-back with no yield.
  - Identical on the fork (same file minus `.source`/`position` plumbing and `zmk_behavior_invoke_binding` at `:46/:48`). Signature changed: `zmk_behavior_queue_add(uint32_t position, …)` → `(const struct zmk_behavior_binding_event *event, …)`.
  - `CONFIG_ZMK_BEHAVIORS_QUEUE_SIZE` unchanged (Flo: 512). `CONFIG_ZMK_MACRO_DEFAULT_WAIT_MS=15` / `TAP_MS=30` unchanged (Flo overrides per macro).
  - Consequence for `&ak` (`adaptive_keys/macros.dtsi:25-39`): `kp X` press (wait = tap_ms = 10 ms via `k_work_schedule`), `kp X` release (wait 0), `&macro_tap_time 0`, `&aksl L` press+release (wait 0) → same sequence and same 10 ms scheduled hop on both trees.
- **`app/src/behaviors/behavior_macro.c` · `1bac680c` (v0.3.0+)**:
  - `behavior_macro_init` precomputes `release_state` by scanning bindings. Fork ignores regular (non-control) bindings during the scan (`fork:132` "Ignore regular invokable bindings"); HEAD resets `release_state.param1/2_source = PARAM_SOURCE_BINDING` on each regular binding (`HEAD:131-135`). Bug on fork: a `&macro_param_*` consumed by a press-phase binding leaks into `release_state` and re-applies to the first regular binding after `&macro_pause_for_release`. Upstream test `app/tests/macros/param-then-no-param` (`&macro_param_1to1`, `&macro_tap &kp PH`, `&macro_press &mo 1`, pause, `&macro_release &mo 1` → fork releases `&mo <keycode>` instead of `&mo 1`).
  - Flo's macros audited (PROVEN no difference):
    - `ak`, `bk`, `bskL`, `ak_R_macro`, `REPLACE_CHAR_WITH_BIGRAM`, `dotcom`/`dotcouk`: no `&macro_pause_for_release` → `release_state.count = 0`, nothing runs on release.
    - `bm`, `bsk` (`macros.dtsi:60-75`, `89-104`): pause present, but the release phase re-declares `<&macro_param_1to1>` before `<&macro_release &kp/&sk MACRO_PLACEHOLDER>` (`:72-73`, `:101-102`) → `handle_control_binding` overwrites any leaked source → same output.
    - ⚠️ `hands_down/mods/macros.dtsi:14,24` has commented-out `&macro_param_1to1` / `&macro_release &mo MACRO_PLACEHOLDER`. If re-enabled **without** a param control in the release phase, fork and upstream diverge.
- **`zmk_behavior_invoke_binding`** (HEAD `app/src/behavior.c:67-115`) is now the single entry point for keymap (`keymap.c:718`), combos, hold-tap inner bindings, sticky inner binding, and queued macro items. For Flo's behaviors it resolves to `invoke_locally` (`:58-65`) = the exact fork calls, plus a name lookup and a no-op `convert_central_state_dependent_params`.

## 4 · Sticky key / hold-tap

- **Hold-tap (`behavior_hold_tap.c`)** · **zero logic change** (39-line diff = `.source` in `active_hold_tap`, `store_hold_tap(event*, …)`, four press/release helpers via `zmk_behavior_invoke_binding`, two includes removed by `9ebbeff0`). `decide_hold_tap` (`HEAD:527`), `tapping_term_ms_left` (`:636`), the `event.timestamp > hold_tap->timestamp + tapping_term_ms` late-decision test (`:653`), `position_state_changed_listener` (`:726`), quick-tap, hold-trigger-key-positions: untouched. Linger keys (`LK` → hold-tap, tap-preferred, `linger_term` 100 ms) and `blt`/`bksl`/`blt_akR` (200 ms) behave identically.
- **Sticky key (`behavior_sticky_key.c`) · `7186528f` (v0.2.0+)**
  - `find_sticky_key(uint32_t position)` (`fork:85`) → `find_sticky_key(position, struct zmk_behavior_binding behavior, uint32_t binding_param)` (`HEAD:91-92`), matching `config->behavior.behavior_dev` and `param1` too.
  - Press (`fork:147` / `HEAD:161`): fork releases **any** active sticky at the same `event.position` before storing the new one; HEAD only the same behavior+param ("found same sticky key pressed at position %d, release it first", `HEAD:163`).
  - Release (`fork:169` / `HEAD:187`): fork releases whichever sticky sits at that position; HEAD the matching one.
  - Unused `param2` dropped; `ZMK_BHV_STICKY_KEY_MAX_HELD`, timer, `release-after-ms`, `quick-release`, `lazy`, `ignore-modifiers` logic untouched.
  - Flo impact: `aksl` = sticky `&mo`, `release-after-ms = my_ak_window` (100), no quick-release (`adaptive_keys/behaviors.dtsi:1-9`), pressed from the `ak` macro at the invoking key's position (physical key, combo virtual position, or the `blt_akR` key).
    - Same key twice → same position, same behavior, same param → both trees release-then-restore. Identical.
    - Different keys → different positions. Identical.
    - Cross-type at one position (`&sk` via `bsk` on a mod layer, `aksl` on alpha at the same physical key): fork would release the pending `sk` when `aksl` is stored; HEAD would not. **INFERRED unreachable**: Flo's `&sk` has `quick-release` (`__BASE__/default_behaviors_config.dtsi:9-10`) → released on the `&kp X` press that precedes `&aksl` inside `ak`. Test T5.
- **Layer behaviors · `5138c6fb` (main only)** · `&mo`/`&to`/`&tog` gain a `locking` DT property (default false); `set_layer_state(layer, state, locking)` returns early for a non-locking deactivate of a locked layer (`keymap.c:145-148`). No `locking` anywhere in Flo's DT → identical. `zmk_keymap_highest_layer_active` now returns a layer *index* (`keymap.c:196`) = ID when `CONFIG_ZMK_KEYMAP_LAYER_REORDERING` is off → combo layer filter identical.
- **Keymap dispatch** · `zmk_keymap_apply_position_state` (`fork:588-646` inline locality switch → `HEAD:702-719` via `zmk_keymap_get_layer_binding_at_idx` + `zmk_behavior_invoke_binding`). `get_layer_binding_at_idx` now maps through `selected_to_stock_map` (`physical_layouts.c:329-332`, a static array, identity with one layout). No timing effect.

## 5 · Split transport · left-hand latency

- **Peripheral path (left half) — same** (PROVEN):
  - kscan → `physical_layouts.c` msgq (`CONFIG_ZMK_KSCAN_EVENT_QUEUE_SIZE`=4) → system workqueue → `raise_zmk_position_state_changed(... .timestamp = k_uptime_get())` (`fork:178-182` / `HEAD:297-301`, identical).
  - listener: fork `split_listener` (`split/bluetooth/split_listener.c:21-30`, deleted) / HEAD `split_peripheral_listener` (`split/peripheral.c:148-160`) → `zmk_split_peripheral_report_event` → `zmk_split_transport_peripheral_bt_report_event` (`bluetooth/service.c:386-395`) → `zmk_split_bt_position_pressed/released` → `send_position_state()` (`fork service.c:185-204` / `HEAD:230-249`, identical): flips a bit in the 16-byte `position_state` bitmap, `k_msgq_put(…, K_MSEC(100))` (queue 10, drops oldest when full), `k_work_submit_to_queue(&service_work_q, …)` (dedicated thread, `CONFIG_ZMK_SPLIT_BLE_PERIPHERAL_PRIORITY`=5, stack 756) → `bt_gatt_notify` of the **whole bitmap**.
  - Wire format unchanged → same coalescing property: several changes between two notifications arrive as one snapshot and are replayed by the central in **position order, not chronological order** (`fork central.c:254-268` / `HEAD:373-389`).
- **Central path (right half) — same queues, one timestamp move**:
  - `split_central_notify_func` XORs against the last snapshot, per changed bit `k_msgq_put(&peripheral_event_msgq, K_NO_WAIT)` (`CONFIG_ZMK_SPLIT_BLE_CENTRAL_POSITION_QUEUE_SIZE`=5 both; overflow silently drops) + `k_work_submit(&peripheral_event_work)` (system workqueue).
  - fork: event fully formed in the BT RX callback with `.timestamp = k_uptime_get()` (`fork central.c:259-263`), raised verbatim by `peripheral_event_work_callback` (`:72-78`).
  - HEAD: callback queues a `peripheral_event_wrapper {source, event}` (`HEAD central.c:141-147`, `:378-386`); `peripheral_event_work_callback` (`:1284-1290`) → `zmk_split_transport_central_peripheral_event_handler` (`split/central.c:32-48`) builds `zmk_position_state_changed` with `.timestamp = k_uptime_get()` **there** (`:46`).
  - Net semantic change: on the fork a left-hand key is stamped at BT-RX time (before the workqueue hop); on HEAD at raise time, exactly like local keys. PROVEN ordering, INFERRED magnitude: the RX-thread → workqueue hop is sub-millisecond on nRF52 (BT RX prio 8 vs workqueue prio −1, `.config`). Only cross-hand arithmetic (combo deadline, hold-tap `tapping_term_ms_left`) sees it.
- **BLE link parameters identical** (PROVEN): central connects with `BT_LE_CONN_PARAM(CONFIG_ZMK_SPLIT_BLE_PREF_INT, PREF_INT, PREF_LATENCY, PREF_TIMEOUT)` (`fork central.c:591` / `HEAD:818`), defaults 6 / 30 / 400 in both Kconfigs → 7.5 ms interval, slave latency 30, 4 s supervision. `BT_PERIPHERAL_PREF_MIN/MAX_INT` 6/12 unchanged. `BT_CTLR_PHY_2M=y` in Flo's build; `ZMK_BLE_EXPERIMENTAL_CONN` still forces it off if enabled (unchanged).
- **Changes with no steady-state latency effect**: runtime transport selection (`6b44d33d`, `select_first_available_transport`), wired split (`147c340c`, needs `zmk,wired-split` DT, absent on Corne), peripheral advertising `BT_LE_ADV_CONN` → `BT_LE_ADV_CONN_FAST_2` (`HEAD peripheral.c:71`, reconnection only), `BT_L2CAP_TX_BUF_COUNT 5` → `BT_ATT_TX_COUNT 10` (Zephyr 4.1 API, GATT discovery), release-on-disconnect already present at fork (`release_peripheral_slot`, `fork central.c:101-140`; `24487bd9` only adds it for pointing), `5b51501f` (input reports only), `ZMK_INPUT_SPLIT_MSG_QUEUE_SIZE` (pointing).
- **kscan drivers**: `kscan_gpio_matrix.c` / `kscan_gpio_direct.c` diffs are `static const` only; debounce algorithm and DT defaults unchanged; `ZMK_KSCAN_DEBOUNCE_PRESS/RELEASE_MS` default −1 both; `SYSTEM_WORKQUEUE_STACK_SIZE` 2048 moved to `app/Kconfig.defaults` (3072 with display).

## 6 · Verdict table

| Conclusion drawn from the fork | On upstream main (2026-09) |
|---|---|
| Every alpha/AK-layer press is buffered ≥ 11 ms by the 36-key hack | ❌ **Different** — hack not compiled (§2); no delay, ordering bug returns |
| Combo capture / bubble / release-then-re-raise / first-key timestamp | ✅ Identical |
| Combo deadline = first key ts + min timeout; shortest-first winner | ✅ Identical |
| Combo per-key limit 30, per-combo 36 (Kconfig) | ❌ Different — auto-sized, ≥20 keys dropped, Kconfigs deprecated (warning) |
| Macro tap/wait via behaviour queue, dequeue-time stamps, 10 ms `ak_tap_time` hop | ✅ Identical |
| Parametrized macro release semantics for Flo's `bm`/`bsk`/`ak` | ✅ Identical (bug fixed upstream is unreachable in Flo's DT) |
| Hold-tap / linger decision logic | ✅ Identical |
| `aksl` sticky-layer lifecycle | ✅ Identical for Flo's usage (cross-type collision semantics changed, unreachable) |
| Left-hand key path: bitmap notify, 7.5 ms interval, position-order replay | ✅ Identical |
| Left-hand key timestamp taken before the workqueue hop | ❌ Different (sub-ms) — now taken at raise time |
| Local key timestamp taken in the workqueue | ✅ Identical |
| Test board `native_posix_64`, Zephyr 3.5 | ❌ Different — `native_sim//zmk_test_mock`, Zephyr 4.1 (`c06fa48c`) |

Page wording that holds across the whole range: "ZMK main from 2024-09 (pre-v0.1) through v0.3.x and current main, **except** the 36-key consistency hack, which requires ZMK < v0.3.0 (or `CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO` era) and is silently dropped from v0.3.0 on."

## 🧪 Test-infra notes for later phases

- Fork: `app/run-test.sh` builds `-b native_posix_64` (`fork run-test.sh:29`), discovers `native_posix_64.keymap`, runs `zmk.exe | sed -n -f events.patterns`, diffs against `keycode_events.snapshot`. No `.conf` files in `app/tests/combo/*` at the fork; a test needing `CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO=36` needs a board `.conf` in the test dir (INFERRED: ZMK reads `${ZMK_CONFIG}/<board>.conf`; verify).
- HEAD: `native_sim//zmk_test_mock`, `native_sim.keymap` (rename in `c06fa48c`). `kscan_mock` (`app/module/drivers/kscan/kscan_mock.c`, same path in both trees) gained a bounds guard in the work handler (`HEAD:68-73`); fork's `kscan_mock_schedule_next_event` already stops rescheduling at the end (`fork:55-62`), so existing fork tests terminate.
- Upstream `app/tests/combo/` has 25 cases, none with a `.conf`; the test mock matrix size comes from the test's DT overlay, so a ≥20-position combo test needs its own `native_sim.overlay` enlarging the `zmk,kscan-mock` `rows`/`cols`.
- Upstream added no combo test with >4 keys (`press-release-long-combo-*` use 4 positions).

## 🧪 Testable claims (for the native_posix / native_sim phase)

- **T1 · 36-key hack is dropped on upstream, kept on fork** (the one flipped conclusion)
  - Setup: keymap with `&ak`-shaped macro on pos 0 (`&kp X` tap_ms 10 → `&aksl 1`), layer 1 maps pos 1 to `Y`, base maps pos 1 to `B`; combos node = one 36-position combo (`timeout-ms = <11>`, `bindings = <&none>`) over a mock matrix ≥ 36 positions; fork `.conf` sets `CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO=36`.
  - Events: `ZMK_MOCK_PRESS(0)` @0 ms, `ZMK_MOCK_PRESS(1)` @3 ms, releases @50 ms. Keep the Zephyr log timestamp prefix in `events.patterns` (the stock patterns strip it); the differential is timing, not order.
  - Upstream expected (PROVEN path): pos 0 bubbles at `HEAD:425-426` → `X↓ @0`, `B↓ @3` (layer 1 only active from @10), `X↑ @10`; `combo_init` logs `Have 0 combos!`; two `#warning`s in the build log; build succeeds.
  - Fork expected (INFERRED trace, A2's domain to confirm): pos 0 captured by the hack, delivered at the 11 ms timeout → `X↓ @11`, `X↑ @21`; pos 1 re-raised at @11 and **re-captured with its original timestamp** (`fork:155` `timeout_at = timestamp + timeout_ms` = 3 + 11) → `B↓ @14`. Same order as upstream, every delivery shifted by +11 ms.
  - Any timestamped keycode event on the fork before @11 falsifies "the hack delays every press"; any delay of pos 0 on upstream falsifies "the 36-key node is dropped".
- **T2 · LISTIFY threshold = 19 keys** · same rig, two combo nodes: 19 positions → `&kp A`, 20 positions → `&kp B`. Press all 19 within 50 ms → `A↓` on both trees; press all 20 → `B↓` on fork, nothing on upstream (`Have 1 combos!`).
- **T3 · Combo timing identity** · run upstream's 25 `app/tests/combo/*` on both trees (rename `native_sim.keymap` ↔ `native_posix_64.keymap`); plus a Flo-shaped case: 2-key combo `timeout-ms=16`, `ZMK_MOCK_PRESS(0)` @0, `ZMK_MOCK_PRESS(1)` @15 → combo fires with press timestamp 0; @17 → no combo, `A↓ B↓` in order. Identical snapshots expected.
- **T4 · Macro release-param fix (`1bac680c`) is a no-op for Flo's shapes** · (a) upstream's `app/tests/macros/param-then-no-param` on the fork → diverges (fork releases `&mo <keycode>`); (b) Flo's `bm` shape (`&macro_param_1to1` re-declared after `&macro_pause_for_release`, `adaptive_keys/macros.dtsi:60-75`) → identical on both.
- **T5 · Sticky cross-type collision (`7186528f`) is unreachable for Flo** · pos 0 on layer 0 = `&sk LSHIFT` (no quick-release), pos 0 on layer 1 = `&aksl 2`; press `&sk`, switch layer, press `&aksl` at the same position → fork releases the shift sticky, upstream keeps it. Then add `quick-release` + a `&kp` between → identical. Neither reaches Flo's DT.
- **T6 · Hold-tap identity** · run `app/tests/hold-tap/**` (all flavors, `hold-trigger-key-positions`, `quick-tap-ms`, `require-prior-idle-ms`) on both trees; identical snapshots expected (diff is plumbing only).
- **T7 · Left-hand timestamp move (§5)** · NOT native-testable (no BLE on native_sim). On-device only: RTT-log `k_uptime_get()` in `split_central_notify_func` vs in `peripheral_event_work_callback` / `zmk_split_transport_central_peripheral_event_handler`; expected delta < 1 ms.

## ❓ Open questions

- ~~Zephyr 4.1 `IS_EQ`/`LISTIFY` identical to 3.5~~ → PROVEN by header fetch (§2). T1 remains the end-to-end confirmation.
- Exact BT-RX → system-workqueue hop latency on nRF52840 (INFERRED sub-ms; needs on-device RTT timestamps, not native_posix).
- Upstream behaviour of an explicit `layers = <-1>` (UB via `BIT(4294967295)`); Flo doesn't use it.
- Whether `hands_down/mods/macros.dtsi` commented-out `&macro_release &mo MACRO_PLACEHOLDER` is ever revived (would expose the `1bac680c` divergence).
