# G — Proving AK timelines with ZMK's native_posix harness

> Scope: what the `native_posix_64` test harness can observe, how precisely, and how to point it at Flo's real keymap.
> Legend: **PROVED** = read in source and/or observed in a run this session. **INFERRED** = reasoned from source, not executed.
> All zmk paths relative to `/Users/flo/Work/Private/Dev/Keyboard/zmk/app` (= `/workspaces/zmk/app` in the container). Zephyr paths relative to `/workspaces/zmk/zephyr` (v3.5.0 zmk-fixes, commit `dacab4875df7`, only visible inside the container — host `zmk/zephyr` is an empty dir; it is a docker volume).

## 🎯 Headline conclusions

- **Flo's real `corne.keymap` builds and runs on native_posix_64 unmodified.** PROVED by a scratch build in the container's `/tmp` (deleted afterwards): 32 layers, 28 combos, no init errors, `T` then `N` typed, AK layers 19 (`l_akT`) and 14 (`l_akN`) toggled. Recipe in §5.
- **Timing resolution is exactly 1 ms and fully deterministic.** Tick = 1 ms (`CONFIG_SYS_CLOCK_TICKS_PER_SEC=1000`), log timestamps are µs but every event lands on a whole ms. Two runs are byte-identical; `--no-rt` output is byte-identical to real-time output. PROVED.
- **Every relative timer fires 1 tick (= 1 ms) late on native_posix.** Zephyr `kernel/timeout.c:122` → `to->dticks = timeout.ticks + 1 + elapsed();`. Applies to mock key delays, combo timeouts, macro `tap-ms`/`wait-ms`, sticky `release-after-ms`, hold-tap `tapping-term-ms`. On the nice!nano (32768 Hz tick) the same +1 tick is 30.5 µs. PROVED on native_posix by observation (100 → 101, 10 → 11, 1500 → 1501).
- **`run-test.sh` throws the timestamps away.** Line 35: `sed -e "s/.*> //"` runs *before* `tee keycode_events_full.log`, so even the "full" log has no `[hh:mm:ss.mmm,uuu]` prefix. For ms analysis run the built exe directly (§4).
- **The container's `/workspaces/zmk-config` is the live host directory, not a copy.** Docker volume `zmk-config` is created with `-o type=none -o o=bind -o device=/Users/flo/.../zmk-config` (`create_docker_volume_for_zmk_devcontainer.sh`); md5 of `corne.conf`/`corne.keymap`/`CONFIG.h` identical host vs container. PROVED.
- **`-DZMK_CONFIG` does not add an include path.** It selects `${ZMK_CONFIG}/native_posix_64.keymap` as the DT overlay and merges `${ZMK_CONFIG}/native_posix_64.conf` *in addition to* `app/boards/native_posix_64.conf`. Flo's files are pulled in with an absolute `#include "/workspaces/zmk-config/config/corne.keymap"` (works because DTS goes through cpp). PROVED.
- **Build + run is fast:** cold `west build` ≈ 5.7 s (135 ninja steps, no BLE stack), `run-test.sh` on an already-built case ≈ 4.5 s (cmake no-op overhead), the exe itself 0.07 s for 2 s of simulated time with `--no-rt` (default is real-time: 0.30 s for 235 ms). PROVED.
- **Side finding (same on hardware, not an artefact):** `behavior_queue.c:53` never sets `q_item.position`, so every behavior invoked from a macro (`&ak` → `&kp`, `&aksl`) runs with `position 0`. Consequence: all `aksl` sticky layers share position 0 → a new `&ak` finds the previous sticky layer via `find_sticky_key(0)` and releases it (`behavior_sticky_key.c:148-152`). Cross-check with the AK-mechanics agent; the log lines prove it (`on_keymap_binding_pressed: position 0 keycode 0x70017`).

## 1 · ⏱️ `ZMK_MOCK_PRESS/RELEASE` semantics

### Encoding — `module/include/dt-bindings/zmk/kscan_mock.h:9-14` (PROVED)

```c
#define ZMK_MOCK_PRESS(row, col, msec)   (row + (col << 8) + (msec << 16) + (0x01 << 31))
#define ZMK_MOCK_RELEASE(row, col, msec) (row + (col << 8) + (msec << 16))
#define ZMK_MOCK_MSEC(v) ((v & ~(0x01 << 31)) >> 16)
```

- row: 8 bits, col: 8 bits, msec: **15 bits → max 32767 ms** (a larger value spills into the press bit).

### Delay placement — `module/drivers/kscan/kscan_mock.c` (PROVED)

- `kscan_mock_enable_callback_N()` (:81) → `schedule_next_event()` (:52) reads `events[event_index]` (index 0) and `k_work_schedule(&data->work, K_MSEC(msec))` (:58).
  - So `events[0].msec` is the delay **before** the first event.
- `kscan_mock_work_handler_N()` (:64) fires `events[i]` via the kscan callback (:71), **then** calls `schedule_next_event()` with `event_index` still `i` (:72), then increments (:73).
  - So `events[i].msec` is also the delay **after** event `i`.
- Net timeline: `[e0.msec+1] e0 [e0.msec+1] e1 [e1.msec+1] e2 … eN [eN.msec+1] exit`.
  - Observed (combo/multiple-timeouts, delays 100,10,10,10): events at **101, 202, 213, 224**, exit at 235.
  - The test author of `combo/overlapping-combos-4-different-timeouts` noticed the first-event quirk ("starts at T+50 because …").
- Exit: `exit-after` (board overlay) → `exit(0)` at `:61` when `event_index == len`.
  - Before that, the handler reads **one past the array** (`cfg->events[len]`, :68 — that is the adjacent `exit_after` bool → the odd final line `ev 1 row 1 column 0 state 0`). The spurious callback is queued but `exit(0)` runs synchronously first, so it never reaches ZMK. Harmless, but explains the garbage line.
  - **Consequence:** anything that must happen after the last key event (sticky timeout, AK window end, hold-tap timer) only shows if the *last event's* msec is long enough. Upstream tests use e.g. `ZMK_MOCK_RELEASE(0,0,1200)`.

### Why +1 ms — Zephyr `kernel/timeout.c:122` (PROVED)

- `z_add_timeout()`: relative timeouts get `to->dticks = timeout.ticks + 1 + elapsed();` (absolute `K_TIMEOUT_ABS_*` timeouts do not, `:117-120`).
- `k_work_schedule()` → `schedule_for_queue_locked()` → `z_add_timeout()` (`kernel/work.c:902`).
- All ZMK timers use relative `K_MSEC(...)` → every one is +1 tick.
- Real board: `CONFIG_SYS_CLOCK_TICKS_PER_SEC=32768` (`build/right/zephyr/.config:279`), so `K_MSEC(x)` = ceil(x·32.768) ticks + 1 → worst case +61 µs, typically +30.5 µs.

### Matrix size & position mapping (PROVED)

- Default mock: `boards/native_posix_64.overlay` → `rows = <2>; columns = <2>; exit-after;` chosen `zmk,kscan = &kscan`.
  - The driver ignores `rows`/`columns`; it only calls `callback(dev, row, col, pressed)`.
- Position = `zmk_matrix_transform_row_column_to_position()` (`src/matrix_transform.c:76-96`):
  - no transform → `row * columns + column` (:82) with `columns` from the kscan node (`include/zmk/matrix.h`, `ZMK_MATRIX_COLS`).
  - with a `zmk,matrix-transform` → lookup index `row * transform.columns + col` (:85) into the inverted `map`.
- Event timestamp = `k_uptime_get()` **at msgq processing** (`src/physical_layouts.c:182`), same ms as the mock fired (kscan callback → `k_msgq_put` + `k_work_submit` :158-159, zero latency).
- With Flo's `five_column_transform` (columns=10) the mock coordinates are Corne matrix coordinates: **position p → `ZMK_MOCK_PRESS(p/10, p%10+1, …)` for p<30; thumbs 30..35 → `(3, 3+(p-30))`**. Verified: `(1,4)` → position 13 = `LM1`, `(1,3)` → 12 = `LM2`.

## 2 · 📜 Log format and which lines exist

### Format (PROVED from raw exe output and `.config`)

```
[00:00:00.113,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=1 timestamp=112
```

- `[hh:mm:ss.mmm,uuu]` — `subsys/logging/log_output.c:291`. Source = `k_cycle_get_32()` at 1 MHz (`log_core.c:211-242`: hw cycles/sec = 1 000 000 on native_posix → µs). µs are always `000` because simulated time only advances at 1 ms ticks.
- `<dbg>` level, `zmk:` module, `func:` prefix only on DBG (`CONFIG_LOG_FUNC_NAME_PREFIX_DBG=y`, INF lines like `Welcome to ZMK!` have none).
- `CONFIG_LOG_MODE_IMMEDIATE=y` (forced by `boards/posix/native_posix/Kconfig.defconfig:37-38`) → synchronous: **line order == execution order**, timestamp taken at the call. (Real board defaults to deferred mode — not relevant to tests.)
- `kscan_mock.c:69` format string ends in `\n` → one blank line after every mock event line.
- Kconfig needed (already in `boards/native_posix_64.conf`): `CONFIG_LOG=y`, `CONFIG_ZMK_LOG_LEVEL_DBG=y` (→ `CONFIG_ZMK_LOG_LEVEL=4`, `app/Kconfig:578,738-740`), `CONFIG_LOG_BACKEND_SHOW_COLOR=n` (else ANSI escapes), `CONFIG_DEBUG=y`, `CONFIG_SYS_CLOCK_TICKS_PER_SEC=1000`.
  - `run-test.sh:29` adds `-DCONFIG_ASSERT=y` (one CMake warning "__ASSERT() statements are globally ENABLED" is normal).
  - **One log module for all of ZMK**: `LOG_MODULE_REGISTER(zmk, …)` `src/main.c:13`, 76× `LOG_MODULE_DECLARE(zmk)`. No per-file level. Filtering = `events.patterns` (sed), not Kconfig. `CONFIG_ZMK_LOGGING_MINIMAL=y` would silence everything.

### Observable lines (function → string, all `LOG_DBG` unless noted; PROVED by source + probe run)

| Event | Function / file:line | Exact string |
|---|---|---|
| mock event fired | `kscan_mock_work_handler_0` `kscan_mock.c:69` | `ev %u row %d column %d state %d` |
| next mock delay | `kscan_mock_schedule_next_event_0` `:57` | `delaying next keypress: %d` |
| position event | `zmk_physical_layouts_kscan_process_msgq` `physical_layouts.c:176` | `Row: %d, col: %d, position: %d, pressed: true/false` |
| combo captured key | `position_state_down` `combo.c:436` | `combo: capturing position event %d` |
| combo timeout / filter | `filter_timed_out_candidates` `combo.c:245` | `after filtering out timed out combo candidates: remaining_candidates=%d timestamp=%lld` |
| combo gave key back | `release_pressed_keys` `combo.c:279/283` | `combo: releasing position event %d` / `combo: reraising position event %d` |
| combo fired | *(no log)* — `press_combo_behavior` `combo.c:289` | observe the bound behavior's own line (e.g. `on_keymap_binding_pressed: position <virtual pos> keycode …`) |
| keymap lookup | `zmk_keymap_apply_position_state` `keymap.c:603` | `layer_id: %d position: %d, binding name: %s` |
| **layer on/off** | `set_layer_state` `keymap.c:156` | `layer_changed: layer %d state %d` |
| `&mo` press/release | `mo_keymap_binding_pressed/released` `behavior_momentary_layer.c:46/52` | `position %d layer %d` |
| `&kp` press/release | `on_keymap_binding_pressed/released` `behavior_key_press.c:44/50` | `position %d keycode 0x%02X` |
| **HID press / release** | `hid_listener_keycode_pressed/released` `hid_listener.c:37/61` | `usage_page 0x%02X keycode 0x%02X implicit_mods 0x%02X explicit_mods 0x%02X` |
| modifiers byte | `zmk_hid_implicit_modifiers_press/release` `hid.c:45` | `Modifiers set to 0x%02X` |
| report sent | `zmk_endpoints_send_report` `endpoints.c:193` | `usage page 0x%02X` (+ `<err> USB endpoint is not supported` `:133` — noise, no transport in tests) |
| macro start | `queue_macro` `behavior_macro.c:164` | `Iterating macro bindings - starting: %d, count: %d` |
| macro control | `handle_control_binding` `:82-106` | `macro mode set: tap/press/release`, `macro tap time set: %d`, `macro wait time set: %d`, `macro param: 2to1`… |
| **queue step** | `behavior_queue_process_next` `behavior_queue.c:31/43` | `Invoking %s: 0x%02x 0x%02x` / `Processing next queued behavior in %dms` |
| sticky key stored | `on_sticky_key_binding_pressed` `behavior_sticky_key.c:159` | `%d new sticky_key` (position is 0 when reached via a macro) |
| sticky used as normal key | `on_sticky_key_binding_released` `:176` | `Another key was pressed while the sticky key was pressed. Act like a normal key.` |
| sticky timeout | *(no log)* — `on_sticky_key_timeout` `:133` | observe the bound behavior release (`mo_keymap_binding_released` → `layer_changed … state 0`, or `hid_listener_keycode_released`) |
| hold-tap new | `on_hold_tap_binding_pressed` `behavior_hold_tap.c:608` | `%d new undecided hold_tap` |
| hold-tap decided | `decide_hold_tap` `:552` | `%d decided %s (%s decision moment %s)` e.g. `13 decided tap (tap-preferred decision moment key-up)` |
| hold-while-undecided | `decide_hold_tap` `:523` | `%d hold behavior pressed while undecided` |
| hold-tap captures | `position_state_changed_listener` `:759/754/715/734` | `%d capturing %d down/up event`, `%d bubbling %d … event`, `%d bubble (no undecided hold_tap active)`, `%d bubble undecided hold-tap keyrelease event` |
| hold-tap mod capture | `keycode_state_changed_listener` `:796` | `%d capturing 0x%02X down/up event` |
| hold-tap cleanup | `on_hold_tap_binding_released` `:654/651` | `%d cleaning up hold-tap` / `%d hold-tap timer work in event queue` |
| event manager | `zmk_event_manager_handle_from` `event_manager.c:34/37` | `Listener handled the event` / `Listener captured the event` |
| tap-dance noise | `tap_dance_position_state_changed_listener` | `Ignore upstroke at position %d.` (appears because `togMacPc` exists) |

- Timestamp semantics inside strings: `filter_timed_out_candidates … timestamp=` prints the **intended** time (`timeout_task_timeout_at`, `combo.c:472`) when called from the timer, and the event timestamp when called from a key press. Line prefix shows the **execution** time (intended + 1).
- `-95` error `Failed to send key report for the released keycode` (`hid_listener.c:75`) appears only because Flo's `CONFIG_ZMK_HID_SEPARATE_MOD_RELEASE_REPORT=y` sends an extra report; ignore.

## 3 · 📂 Using Flo's real config from a test

### Mount facts (PROVED)

- `docker inspect zmk-devcontainer`: `/workspaces/zmk` = bind of host `zmk`; `/workspaces/zmk-config` = volume `zmk-config` whose driver options are `type=none, o=bind, device=/Users/flo/Work/Private/Dev/Keyboard/zmk-config` → **same inode tree as the host** (edits appear instantly both ways). `zephyr/`, `modules/`, `tools/` are real docker volumes (not on host).
- `west` config: manifest `app/west.yml`, `zephyr.base = zephyr`.

### What `-DZMK_CONFIG=<dir>` does — `keymap-module/modules/modules.cmake` (PROVED)

- `:155` `list(PREPEND KEYMAP_DIRS ${ZMK_CONFIG})` → `:200-208` first `${dir}/${BOARD}.keymap` found becomes `KEYMAP_FILE` **and** `DTC_OVERLAY_FILE`. Overlays compiled: `app/boards/native_posix_64.overlay` (board root scan `:90`) then the keymap.
- `:179-193` `${dir}/native_posix_64.conf` and `${dir}/default.conf` → appended to `shield_conf_files` → Zephyr `cmake/modules/kconfig.cmake:265` merges them. Observed merge order: `prj.conf` → `app/boards/native_posix_64.conf` → `${ZMK_CONFIG}/native_posix_64.conf` → `extra_kconfig_options.conf` (the `-DCONFIG_…` CLI). So the test conf is **additive**; upstream tests that repeat the board lines (`tests/wpm/*`) are redundant.
- `:51-58` adds `${dir}/boards` and `${dir}/dts` as roots only if those subdirs exist. **No `-I` for `#include`.** DTS include paths are Zephyr's `dts/`, `dts/common`, `include/` under each DTS root (`app/dts` → `<behaviors.dtsi>`, `<layouts/foostan/corne.dtsi>`, `<physical_layouts.dtsi>`).
- Absolute `#include "/workspaces/zmk-config/config/corne.keymap"` works; nested `#include "./CONFIG.h"` etc. resolve relative to the including file. PROVED.
- `CACHED_ZMK_CONFIG` is sticky per build dir (`:26-35`): changing the config path needs `--pristine` / new build dir.

### Why the physical layout must be wired by the test (PROVED by build)

- Flo's keymap sets `chosen { zmk,physical-layout = &foostan_corne_5col_layout; }` — that node lives in `app/dts/layouts/foostan/corne.dtsi` and **requires** a `transform` phandle (`dts/bindings/zmk,physical-layout.yaml`), normally supplied by the shield's `corne.dtsi`. No shield on native_posix → the test must include the layouts file and define both transforms (copied verbatim from `boards/shields/corne/corne.dtsi`).
- `kscan` on the layout falls back to chosen `zmk,kscan` = the mock (`physical_layouts.c:48-49`), selection at boot via `DT_CHOSEN(zmk_physical_layout)` (`:265-268`).
- `ZMK_KEYMAP_LEN` = `sizeof(union{…})` over all okay physical layouts' map lengths (`include/zmk/matrix.h:14-22`) → **42** with both Corne layouts present; Flo's 36-binding layers are zero-padded. INFERRED (build passed; no runtime warning). Combos use positions <36 so fine. Disabling the 6-col node instead is untested (edtlib required-property rules for disabled nodes — open question).
- Conf lines Flo's firmware relies on and the test must replicate (from `config/corne.conf`): `CONFIG_ZMK_COMBO_MAX_COMBOS_PER_KEY=30`, `CONFIG_ZMK_COMBO_MAX_PRESSED_COMBOS=20`, `CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO=36` (the 36-key hack combo; `combo.c:60` array sizes; without it: `LOG_ERR("Too many combos for key position …")` `:120` or `Unable to initialize combo` `:97` at boot), `CONFIG_ZMK_BEHAVIORS_QUEUE_SIZE=512`, `CONFIG_ZMK_HID_SEPARATE_MOD_RELEASE_REPORT=y`. Verified merged into `.config`.
- Bindings to `&bt`, `&to`, `&togMacPc` etc. compile fine (behavior nodes exist in `behaviors.dtsi`; drivers absent just mean "No behavior assigned" at press time).

### Probe timeline with Flo's keymap (PROVED — press `LM1`=T at mock 100, release +200, press `LM2`=N, release +1500)

```
101  Row: 1, col: 4, position: 13, pressed: true → hold-tap "13 bubble" → "combo: capturing position event 13"
113  filter_timed_out… remaining_candidates=1 timestamp=112      ← 36-key hack combo (11 ms) expired
118  filter_timed_out… remaining_candidates=0 timestamp=117      ← a 16 ms (adjacent) combo containing LM1 expired
118  combo: releasing position event 13 → layer_id: 0 position: 13, binding name: flo,behavior-adaptive-key
118  queue_macro … count: 7 → Invoking key_press: 0x70017 → hid_listener_keycode_pressed keycode 0x17 (T)
118  Processing next queued behavior in 10ms
129  Invoking key_press: 0x70017 → hid_listener_keycode_released 0x17
129  Invoking flo,behavior-adaptive-key-sticky-layer: 0x13 → "0 new sticky_key" → mo … layer 19 → layer_changed: layer 19 state 1
129  Invoking flo,behavior-adaptive-key-sticky-layer (release) → sticky timer: release_at = 129+100
202  position 13 released → &ak release (queue_macro count 0) — nothing sent
230  mo_keymap_binding_released: position 0 layer 19 → layer_changed: layer 19 state 0
403…532  same pattern for N (position 12, keycode 0x11, layer 14: on 431, off 532)
2005 Exiting
```

- Lone-key latency = **longest** candidate combo timeout on that key (+1), not the hack's 11 ms: `combo_timeout_handler` (`combo.c:468-476`) only calls `cleanup()` when `filter_timed_out_candidates()` returns 0; earlier expiries just reschedule (`update_timeout_task` `:404-416`). For LM1 that was 16 ms → key out at press+17. Hand to the combo/AK agents for the page wording.
- AK window as seen from the physical press = combo hold (17) + `ak_tap_time` (10+1) + `release-after-ms` (100+1) = **+129 ms** on native_posix; ≈ +126 ms on hardware (each +1 → +30 µs).

## 4 · 🧪 Recipe for a new test case

### Files (PROVED from `run-test.sh` and upstream cases)

- `tests/<group>/<case>/native_posix_64.keymap` — discovery key (`run-test.sh:16` `find … -name native_posix_64.keymap`). Contains: includes, DT nodes, and `&kscan { events = < … >; };`.
- `tests/<group>/<case>/events.patterns` — a `sed -n` script; only `s/…/…/p` lines survive. Input lines have already lost the prefix up to and including the last `> ` (`run-test.sh:35`), i.e. they look like `zmk: func: msg`.
  - Typical: `s/.*hid_listener_keycode_//p` → `pressed: usage_page 0x07 keycode 0x17 …`.
  - For timing-ish assertions without timestamps: `s/.*\(hid_listener_keycode_pressed\|filter_timed_out_candidates\): //p` (used by `combo/overlapping-combos-4-different-timeouts`, whose snapshot pins `timestamp=71/81/91` — proof that the harness already asserts ms values via the combo log).
  - For layers: `s/.*set_layer_state: //p` → `layer_changed: layer 19 state 1`.
- `tests/<group>/<case>/keycode_events.snapshot` — expected filtered output; `diff -auZ` (`:36`, `-Z` ignores trailing whitespace).
- Optional `native_posix_64.conf` (additive, see §3), optional empty `pending` file → mismatch reports `PENDING` instead of failing (`:38`).
- Shared fragments: a sibling `behavior_keymap.dtsi` included with `#include "../behavior_keymap.dtsi"` (macros/, sticky-keys/, hold-tap/<flavor>/).
- `ZMK_TESTS_AUTO_ACCEPT=1` overwrites the snapshot from the run (`:44-46`).

### Skeleton for a Flo-keymap test (PROVED to build & run)

```dts
#include <dt-bindings/zmk/kscan_mock.h>
#include <dt-bindings/zmk/matrix_transform.h>
#include <layouts/foostan/corne.dtsi>
/ {
    default_transform: keymap_transform_0 { compatible = "zmk,matrix-transform"; columns = <12>; rows = <4>; map = < /* 42 RC() as in boards/shields/corne/corne.dtsi */ >; };
    five_column_transform: keymap_transform_1 { compatible = "zmk,matrix-transform"; columns = <10>; rows = <4>; map = < /* 36 RC() */ >; };
};
&foostan_corne_6col_layout { transform = <&default_transform>; };
&foostan_corne_5col_layout { transform = <&five_column_transform>; };
#include "/workspaces/zmk-config/config/corne.keymap"
&kscan { events = < ZMK_MOCK_PRESS(1,4,100) ZMK_MOCK_RELEASE(1,4,200) /* … */ >; };
```

- `native_posix_64.conf`: the five `CONFIG_ZMK_COMBO_*`/queue/HID lines from §3 (board lines optional).
- Position → mock coords: `(p/10, p%10+1)` for p<30, `(3, p-27)` for thumbs (see §1). A test-only `rows=<1>; columns=<36>` transform with `RC(0,0)…RC(0,35)` would let `ZMK_MOCK_PRESS(0, <alias>, …)` use Flo's `LT4`-style aliases directly — INFERRED, untested.

### Running

- One case: `docker exec -w /workspaces/zmk/app zmk-devcontainer ./run-test.sh tests/<group>/<case>` — **path must be relative to `app/`** (`:29` builds `-DZMK_CONFIG="$(pwd)/$testcase"`; an absolute path produced `CACHED_ZMK_CONFIG=/workspaces/zmk/app//tmp/aktest` → "did not build". PROVED).
- Group / all: same script with a directory (`all` = `tests`); parallel `xargs -P ${J:-4}` (`:20`), summary in `build/tests/pass-fail.log`.
- `run-test-debug.sh` is stale: it looks for `native_posix.keymap` (`:20`), which only a handful of cases still have; it also forces `--pristine`.
- Build artefacts: `build/<testcase>/` (gitignored `/build` in `zmk/.gitignore`), incl. `zephyr/zmk.exe`, `keycode_events_full.log` (prefix-stripped), `keycode_events.log` (filtered).
- **Timing analysis:** after any build, run the exe directly and keep stdout: `docker exec -w /workspaces/zmk/app zmk-devcontainer ./build/tests/<case>/zephyr/zmk.exe --no-rt > raw.log`. Same information as the harness plus timestamps; `--no-rt` skips real-time pacing (`CONFIG_NATIVE_POSIX_SLOWDOWN_TO_REAL_TIME=y` is the default; `-stop_at=<s>` also exists but `exit-after` already ends the run).
- Out-of-tree tests (e.g. in zmk-config): `run-test.sh` cannot take them, but the underlying command can: `west build -s /workspaces/zmk/app -d <builddir> -b native_posix_64 -- -DCONFIG_ASSERT=y -DZMK_CONFIG=/workspaces/zmk-config/tests/<case>` then the sed pipeline from `run-test.sh:35`. A 10-line wrapper in zmk-config reproduces the harness. PROVED for the build/run half.
- Durations measured: cold build 5.7–5.8 s; incremental `run-test.sh` 4.3–4.5 s; exe ≈ simulated time in rt mode, ≈50 ms in `--no-rt`.

## 5 · ⚠️ native_posix artefacts that can mislead

- **+1 ms on every relative timer** (§1). A "30 ms combo" candidate expires at `timeout_at = press+30` but the handler runs at press+31; a mock gap of D ms is really D+1. Design tests with ≥2 ms margins from any boundary.
- **Strict comparison in combos**: `candidate->timeout_at > timestamp` (`combo.c:231`) — a second key arriving at exactly press+timeout is *too late*. Combined with the mock's +1: `ZMK_MOCK_PRESS(a,b,29)` before the second key of a 30 ms combo → gap 30 → **miss**; delay 28 → gap 29 → hit. INFERRED from source (test proposed below).
- **Zero scan latency, no debounce.** Real `zmk,kscan-gpio-matrix` defaults: `debounce-press-ms 5`, `debounce-release-ms 5`, `debounce-scan-period-ms 1` (`dts/bindings/kscan/zmk,kscan-gpio-matrix.yaml`; Flo's `CONFIG_ZMK_KSCAN_DEBOUNCE_*_MS=-1` → DT defaults). Hardware adds ≈5 ms to every press and release; relative gaps between keys survive, but "time from finger to HID" does not.
- **No split.** `CONFIG_ZMK_SPLIT` is unset; every position is local. On hardware the left half (peripheral) arrives over BLE and is stamped `k_uptime_get()` at the central on receipt (`src/split/bluetooth/central.c:125-131, 259-266`); connection interval / latency (`CONFIG_ZMK_SPLIT_BLE_PREF_INT=6`, `…LATENCY=30`) shifts left-hand keys relative to right-hand ones — the two-hand 30 ms combo tier is exposed to this, the harness cannot show it.
- **One thread of execution**: mock events, kscan msgq, combo timeout, behavior queue, sticky/hold-tap timers are all `k_work` on the system workqueue. Two things due on the same tick run in submission order; no preemption, no jitter. Deterministic — which also means a same-tick coincidence in a test is an ordering assertion, not a timing one.
- **Timestamps in messages ≠ execution time** for timer-driven combo lines (intended `timeout_at` printed, executed +1). Position-event lines print the true `k_uptime_get()`.
- **`position 0` for anything reached via `behavior_queue`** (`behavior_queue.c:53` omits `.position`). Same on hardware; only misleading if one expects the physical position in `on_keymap_binding_pressed`/`new sticky_key` lines.
- **No transport**: every report logs `<err> USB endpoint is not supported` (+ the `-95` release-report error under `SEPARATE_MOD_RELEASE_REPORT`). `hid_listener_keycode_*` lines are the ground truth, not endpoint lines.
- **Last-event delay bounds the observation window** (§1). Sticky/AK timers longer than the final `msec` never fire before `exit(0)`.
- **15-bit msec** cap 32 767 ms per gap; `k_uptime_get()` is ms-granular (`CONFIG_TIMEOUT_64BIT` irrelevant here).
- **No `native_posix.keymap` variant**: only `native_posix_64` is wired into `run-test.sh`; `boards/native_posix.conf/overlay` exist but are legacy.

## 6 · 🔬 Proposed tests to settle the open points

- **T1 +1 tick baseline** — `events = <PRESS(0,0,100) RELEASE(0,0,10)>`, plain `&kp A`; expect `hid_listener_keycode_pressed` at `[00:00:00.101]`, released at `.112`.
- **T2 combo boundary** — 30 ms combo on positions 0,1: run A with `PRESS(0,0,28) PRESS(0,1,10) …` → expect combo keycode; run B with `PRESS(0,0,29)` → expect two separate keycodes. Settles strict-inequality + mock offset.
- **T3 lone AK key latency on Flo's keymap** — press LM1 alone: expect `remaining_candidates=1 timestamp=<press+11>` then `remaining_candidates=0 timestamp=<press+16>` and HID press at press+17. Repeat on a key that belongs to a 30 ms two-hand combo → expect press+31.
- **T4 AK window end** — `PRESS(1,4,100) RELEASE(1,4,10)` then a long tail: expect `layer_changed: layer 19 state 1` at press+28 and `state 0` at press+129.
- **T5 sticky-layer handover via position 0** — press LM1, then LM2 50 ms later: expect `layer_changed: layer 19 state 0` in the same ms as `layer 14 state 1` (≈ LM2 press + 28), not at LM1 press + 129.
- **T6 same-tick ordering** — arrange a mock key exactly on a combo timeout tick (e.g. 30 ms combo, second key delay 30 → arrives at +31 with the handler) and record which runs first; then add ±1 ms and confirm the expected outcome on both sides.
- **T7 macro step timing** — `tap-ms=10 wait-ms=0` macro: HID press at t, release at t+11 (`Processing next queued behavior in 10ms` logged at t).

## 7 · ❓ Open questions

- Whether the 6-col physical layout can be disabled (`status = "disabled"`) without providing its transform — edtlib's required-property check on disabled nodes not verified; the recipe keeps both layouts.
- Behaviour of a 1×36 test transform (direct alias→col mapping) is INFERRED only.
- Real-hardware jitter beyond tick rounding (debounce scan quantisation, BLE) is out of reach of this harness; the page should state native_posix numbers as "firmware logic" timelines, not end-to-end latency.
- The "lone key held until the longest candidate combo expires" observation needs confirmation against the combo-mechanics report before the page claims 11 ms anywhere.
