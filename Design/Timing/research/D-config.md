# D — Flo's config, expanded (NAQUADAH, as built)

Scope: `zmk-config/config` after preprocessing, cross-checked against the ZMK fork at `/Users/flo/Work/Private/Dev/Keyboard/zmk` (HEAD `4211ad74`, merge-base with upstream = `6e03a0bb`; `git diff --stat 6e03a0bb HEAD -- app` = only `app/run-test-debug.sh`, so runtime source == upstream 6e03a0bb).

Legend: **PROVED** = read directly from source / preprocessor output. **INFERRED** = derived by tracing runtime code paths; each carries a test. Paths below are relative to `zmk-config/config/` unless prefixed `zmk/`.

Preprocessor artefacts (read-only copy, real `clang -E -x assembler-with-cpp -D__DTS__ -P` with ZMK include paths):
- `scratchpad/investigation/tmp-cpp/expanded_symbolic.dts` (keycodes kept symbolic, 1157 lines)
- `scratchpad/investigation/tmp-cpp/expanded_full.dts` (real includes, 1471 lines; same 28 combos, identical structure)
- `scratchpad/investigation/tmp-cpp/{parse_combos,aktable,xref2}.py` (tables below)

---

## 0. Conclusions that matter most

- 🧱 **&ak is a 4-item behavior-queue program**: `kp X ↓` · wait 10 · `kp X ↑` · `aksl L ↓` · `aksl L ↑` (waits 0). The AK layer turns on **10 ms after the trigger's key-down reaches the keymap**, not at physical press. PROVED (`adaptive_keys/macros.dtsi:25-39`, `zmk/app/src/behaviors/behavior_macro.c:161-183`, `behavior_queue.c:27-63`).
- ⏱ **aksl** = `zmk,behavior-sticky-key`, `release-after-ms = <100>`, wraps `&mo`, **no** `quick-release`, **no** `ignore-modifiers`, **no** `lazy`. Window = 100 ms from the moment the queue executes `aksl ↑` (= layer-on instant) to the next **keycode** down (any keycode, modifiers included). PROVED (`adaptive_keys/behaviors.dtsi:1-9`, `behavior_sticky_key.c:167-190, 234-300`).
- 🪝 **Hack combo** = 36 positions, `timeout-ms = <11>`, `layers = <0..24>` (25 layers), `bindings = <&none>`. It sorts last in every key's lookup (36 keys > everything). Every key press on layers 0-24 is held ≥ 11 ms from its own timestamp. PROVED (`adaptive_keys/combos.dtsi:64-68`, `zmk/app/src/combo.c:93-126`).
- 🎚 **Only two combo tiers are live: 16 ms and 18 ms.** `my_combo_timeout_two_hnds = 30` has **zero consumers**: the only `COMBO_*_TWO_HAND` users (`pronouns/combos.dtsi`) and `h_digraphs/combos.dtsi` are `//`-commented in `corne.keymap:86-87`. PROVED (expanded combos block; 28 combos total, 21 active on layer 0).
- 📊 **Per-key max combo timeout on alpha/AK layers**: 18 ms for RM1-RM4 (16,17,18,19), 16 ms for 25 other keys, **none** for LT4, RT0, LM4, LB4, LH0-LH2, RH0 (0, 5, 10, 20, 30, 31, 32, 33). Those 8 keys are delayed by the hack alone (11 ms). PROVED (table §6).
- 🔁 **Trigger delivery latency** = min(press + max candidate timeout, physical release, next non-sharing key press), never below press + 11 on layers 0-24. INFERRED from `combo.c:422-454, 472-486, 456-470`.
- 🚫 **d < 10 ms follower → no adaptation** (both keys typed base-layer). Reason: the re-raised follower keeps its stale timestamp and `is_quick_tap()` (`combo.c:141-143`, `require-prior-idle-ms` default `-1`) becomes `last_tap - 1 > ts` → combos skipped → delivered before the layer flips. Flo's comment in `adaptive_keys/combos.dtsi:56-61` describes this window differently ("released at once"); the mechanism is the quick-tap bypass. INFERRED, test T3.
- 🧮 **Effective physical AK window** for a same-hand pair with no shared combo: roughly **[10-11 ms, 105-117 ms]** between key-downs (lower bound from the hack + 10 ms tap, upper bound = 100 ms sticky window shifted by the trigger's own delivery delay 11-18 ms and the follower's 11-18 ms). INFERRED, tests T2/T4.
- 🧷 **R is special**: `&blt_akR 25 0` (LH0) → tap = `&ak_R_macro` (tap-ms 0) → `&ak 17 R`. Nested macro invoked outside the queue's work handler → queue re-entrancy → **R's key-down and key-up are emitted back-to-back (0 ms tap)** and l_akR flips on immediately. INFERRED from `behavior_queue.c:57-63` + Zephyr `k_work_delayable_is_pending` (Zephyr tree not on disk; test T7 settles it).
- 🧵 **Action thumb release blocks the behavior queue for 260 ms** (`moAndBuffer` release phase: `&none` tap · wait 130 · `&mo 26 ↑` · wait 130). Any `&ak`/`&bk` keystroke typed in that window is emitted late, in order. INFERRED (`mods/macros.dtsi:1-25`, `behavior_macro.c:114-137, 205-213`), test T8.
- 🅸 **`I` is `&ak 999 I`** on the base layer (`l_akI = 999` "Disabled", `aliases_layers_NAQUADAH.dtsi:30`). `&mo 999` → `set_layer_state` returns `-EINVAL` (`zmk/app/src/keymap.c:142-145`), silently. I types normally; a dead aksl entry occupies one of 10 sticky slots ≤ 100 ms. PROVED.
- 🖐 **All 23 live AK pairs are same-hand** (trigger and every follower on the same half) → split-BLE timestamp skew (left = peripheral, stamped on receipt `central.c:259-266`) does not affect AK timing; it would have affected the (disabled) two-hand pronoun combos. PROVED from the follower table (§10).
- 🎛 `corne.conf` knobs that shape timing: `COMBO_MAX_KEYS_PER_COMBO=36` (hack), `COMBO_MAX_COMBOS_PER_KEY=30`, `COMBO_MAX_PRESSED_COMBOS=20`, `BEHAVIORS_QUEUE_SIZE=512`, `HID_SEPARATE_MOD_RELEASE_REPORT=y` (extra HID report on key release, before mods are dropped). Debounce is the corne default: 5 ms press / 5 ms release / 1 ms scan (`zmk/app/module/dts/bindings/kscan/zmk,kscan-gpio-matrix.yaml:22-31`, nothing overrides it).

---

## 1. Build facts

- Layout selection: `CONFIG.h:47-49` defines RHODIUM, PROMETHIUM, NAQUADAH; `corne.keymap:18-26` and `:101-117` test `#if defined NAQUADAH` **first** → NAQUADAH wins. PROVED (expanded layers 0-31 match `layers_A_NAQUADAH_alpha.dtsi` + `layers_B_NAQUADAH_adaptive_keys.dtsi` + `layers_C_extra*.dtsi`).
- Include order (`corne.keymap`): `CONFIG.h` → `preprocessor_macros.c` → key-position aliases → layer aliases → `hands_down/aliases.dtsi` → `adaptive_keys/aliases.dtsi` → `default_behaviors_config.dtsi` → `macros { … }` (`:44-56`) → `behaviors { … }` (`:60-72`) → `combos { … }` (`:76-91`) → `keymap { … }` (`:95-121`).
- `EXPERIMENT` undefined (`CONFIG.h:44`), so `__EXPERIMENT__/behaviors.dtsi` nodes exist but `EXPERIMENT_LAYER.dtsi` is not included; `__EXPERIMENT__/combos.dtsi` is all comments.
- Layer ids (`aliases_layers_NAQUADAH.dtsi:18-56`): 0 alpha, 1 alpha_linwin, 2 akA, 3 akB, 4 akC, 5 akD, 6 akE, 7 akF, 8 akG, 9 akH, 10 akhE, 11 akK, 12 akL, 13 akM, 14 akN, 15 akO, 16 akP, 17 akR, 18 akS, 19 akT, 20 akU, 21 akV, 22 akW, 23 akX, 24 akY, 25 nav, 26 mod, 27 fn, 28 num, 29 numsym, 30 cfg, 31 nav_linwin. `l_akI = l_akJ = l_akQ = l_akZ = 999`.
- `l_alpha_aks` = `0 1 2 … 24` (25 ids). `l_all` = `0 … 31` (32 ids). `l_any = -1` unused.
- Key positions (`aliases_key_positions.dtsi:21-59`): row-major 0-35, `LT4..LT0 = 0..4`, `RT0..RT4 = 5..9`, `LM4..LM0 = 10..14`, `RM0..RM4 = 15..19`, `LB4..LB0 = 20..24`, `RB0..RB4 = 25..29`, `LH2 LH1 LH0 = 30 31 32`, `RH0 RH1 RH2 = 33 34 35`.
- Listener order for **position** events (link order, `zmk/app/CMakeLists.txt`): hold-tap (`:50`) → combo (`:67`) → keymap (`:74`). For **keycode** events: hold-tap → sticky-key (`:51`) → combo (`:67`) → hid_listener (`:73`). PROVED (`.event_subscription` is an ordered iterable section, `zmk/app/include/linker/zmk-events.ld`).

---

## 2. Timing constants → consumers (10)

| Constant (`CONFIG.h`) | Value | Consumed by (expanded) | Live in NAQUADAH? |
|---|---|---|---|
| `linger_term` (`:4`) | 100 | `tapping-term-ms` of every `lk*` hold-tap: `lk`, `lk_bk`, `lk_wispr`, all `LK()` nodes, `lk_DOT_SPACE`, `lk_E_*`, `lk_par`… | yes (lk, lk_bk, lk_wispr, lk_magic*) |
| `my_tapping_term_main` (`:5`) | 500 | `&mt` override (`CONFIG.h:37-39`), `hrmSk`, `hml`, `hmr`, `hml_S/C/N/T`, `hmr_A/E/M` | only `hml`/`hmr` on l_fn (27); `&mt` unused |
| `my_tapping_term_thumb` (`:6`) | 200 | `blt`, `blt_akR`, `bksl`, `bsklt` | `blt` (RH0 space), `blt_akR` (LH0 R) |
| `require_prior_idle_ms` (`:7`) | 100 | **nothing** (grep of expanded output: 0 hits for `require-prior-idle`) | no |
| `my_ak_window` (`:8`) | 100 | `aksl.release-after-ms` | yes |
| `my_combo_timeout_adjacent` (`:9`) | 16 | `COMBO_*_ONE_HAND` → 18 combos | yes |
| `my_combo_timeout_non_adjc` (`:10`) | 18 | `COMBO_*_NON_ADJC` → delWord, delWordTrans, capsWord, delWord(Trans)_linwin | yes |
| `my_combo_timeout_two_hnds` (`:11`) | 30 | `COMBO_*_TWO_HAND` → only in commented-out `pronouns/combos.dtsi`, `__EXPERIMENT__/combos.dtsi` | **no** |
| `sticky_key_release_timeout` (`:12`) | 1000 | `&sk` override (`default_behaviors_config.dtsi:8-11`, + `quick-release`) | `&sk` unreachable (only via unused `bsk`, `hrmSk`, `S_AppSwitch`) |
| `sticky_key_release_timeout_long` (`:13`) | 3000 | `skL` | unreachable (`bskL`, `type_dot_space` unused) |
| `action_mod_tapping_term` (`:14`) | 130 | `htm.tapping-term-ms`, `slm.release-after-ms`, `moAndBuffer` `&macro_wait_time 130` | `htm`, `moAndBuffer` yes; `slm` no |
| `action_lay_tapping_term` (`:15`) | 90 | `htls.tapping-term-ms` | yes (LH1) |
| `ak_tap_time` (`:27`) | 10 | `ak.tap-ms` | yes |
| `hold_key_event_delay` (`:28`) | 11 | hack combo `timeout-ms` | yes |
| `TEMP_macro_tap_time` (`:36`) | 10 | `tap-ms` of `bk`, `bskL`, `REPLACE_CHAR_WITH_BIGRAM`, `TYPING_MACRO`, h-digraph/pronoun macros, `shiftAndDisableModsLayer`, `AppSwitch` | `bk`, replace, typing macros yes |
| literals | 1500 `skm`/`skms`; 900 `skapp`; 200 `togMacPc`; 50 `dotcom`/`pair*`; 100 `logseqPageRef.wait-ms`; 10 `TYPING_MACRO.wait-ms` | | `skm`,`skms`,`togMacPc`,`logseqPageRef`, typing macros yes |

- ZMK defaults that apply because nothing sets them: `CONFIG_ZMK_MACRO_DEFAULT_WAIT_MS=15`, `…TAP_MS=30` (`zmk/app/Kconfig:503-509`) — only matter for `dotcom`/`dotcouk`/`pair*` (no `tap-ms`), all unreachable. `CONFIG_ZMK_BEHAVIOR_STICKY_KEY_MAX_HELD=10`, `HOLD_TAP_MAX_HELD=10`, `HOLD_TAP_MAX_CAPTURED_EVENTS=40` (`Kconfig.behaviors:52-87`). Combo `require-prior-idle-ms` default `-1`, `slow-release` false, `timeout-ms` default 50 (never used: every combo sets it) (`zmk/app/dts/bindings/zmk,combos.yaml`). Hold-tap `quick-tap-ms = -1`, `require-prior-idle-ms = -1`.

---

## 3. `corne.conf` / per-side conf, timing-relevant (11)

| Setting | Value (default) | Effect on timing |
|---|---|---|
| `CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO` (`corne.conf:44`) | 36 (4) | Required by the hack; sizes `combo_cfg.key_positions[]`, `pressed_keys[]`, `active_combo.key_positions_pressed[]` (`combo.c:29-56`). |
| `CONFIG_ZMK_COMBO_MAX_COMBOS_PER_KEY` (`:39`) | 30 (5) | Sizes `combo_lookup[36][30]` and `candidates[30]`. Real need: max 6 combos on one key (RM1/RM2 incl. hack). Quirk: `capture_pressed_key` guards with this value (30) although the array is 36 long (`combo.c:262-269`) — harmless. |
| `CONFIG_ZMK_COMBO_MAX_PRESSED_COMBOS` (`:42`) | 20 (4) | `active_combos[]` depth only. |
| `CONFIG_ZMK_BEHAVIORS_QUEUE_SIZE` (`:40`) | 512 (64) | Depth of the single global `k_msgq` behind every macro (`behavior_queue.c:23`). `k_msgq_put` failure = silently dropped macro step. `&ak` = 4 items, `replace_char_with_bigram` = 10 + 4 nested. |
| `CONFIG_ZMK_HID_SEPARATE_MOD_RELEASE_REPORT` (`:49`) | y (n) | `hid_listener.c:69-78`: on a keycode release, send the HID report **immediately after removing the key**, then unregister explicit/implicit mods (possibly a second report). Host sees key-up before mod-up. No effect on ZMK-internal timing. |
| `CONFIG_ZMK_IDLE_TIMEOUT` / `IDLE_SLEEP_TIMEOUT` (`:23,25`) | 1 200 000 ms (right, central); left overrides 7 200 000 (`corne_left.conf`) | Sleep only; first key after deep sleep wakes, is not typed. |
| `CONFIG_ZMK_SLEEP=y`, `CONFIG_BT_CTLR_TX_PWR_PLUS_8=y`, `CONFIG_ZMK_USB_LOGGING=n` | | No keystroke-timing effect. |
| `CONFIG_ZMK_SPLIT_ROLE_CENTRAL` | right `=y`, left `=n` | Right-hand keys: timestamp = `k_uptime_get()` after debounce in `physical_layouts.c:178-182`. Left-hand keys: timestamp = `k_uptime_get()` **at BLE receipt on the right** (`split/bluetooth/central.c:259-266`); adds one BLE interval (peripheral prefers 7.5-15 ms, `Kconfig:235-242`). |
| Debounce (not set) | 5 ms press, 5 ms release, 1 ms scan (matrix yaml defaults; `corne.dtsi:59` uses `zmk,kscan-gpio-matrix`, no override; `CONFIG_ZMK_KSCAN_DEBOUNCE_*_MS` default -1) | Every timestamp is ~5 ms after contact. Same on both halves. |

---

## 4. The AK keystroke path, fully expanded (1)(2)(3)

### 4.1 `&ak` — PROVED (`expanded_symbolic.dts:73-85`)

```dts
ak: ak {
        label = "flo,behavior-adaptive-key";
        compatible = "zmk,behavior-macro-two-param";
        #binding-cells = <2>;
        wait-ms = <0>;
        tap-ms = <10>;
        bindings =
                <&macro_param_2to1>,
                <&macro_tap &kp 0>,
                <&macro_tap_time 0>,
                <&macro_param_1to1>,
                <&macro_tap &aksl 0>;
};
```

- Concrete instance, L key: base layer LB2 (pos 22) = `&ak 12 L` (`expanded_symbolic.dts:872`, from `layers_A_NAQUADAH_alpha.dtsi:18` `ak_L` → `adaptive_keys/aliases.dtsi:17`).
- Runtime program on press (`behavior_macro.c:161-183`, mode starts TAP, `tap_ms=10`, `wait_ms=0`):
  1. `macro_param_2to1` → param1 source = binding param2 (`L`).
  2. `macro_tap &kp 0` → `queue_add(kp L, press, wait=tap_ms=10)`, `queue_add(kp L, release, wait=wait_ms=0)`.
  3. `macro_tap_time 0` → tap_ms = 0.
  4. `macro_param_1to1` → param1 source = binding param1 (`12`).
  5. `macro_tap &aksl 0` → `queue_add(aksl 12, press, wait=0)`, `queue_add(aksl 12, release, wait=0)`.
- Physical release of the key: `release_state.count = 0` (no `macro_pause_for_release`) → nothing (`behavior_macro.c:114-137`). Holding an AK key never repeats.
- Queue semantics (`behavior_queue.c:27-63`): items execute in a `while` loop; after an item with `wait > 0` the loop schedules itself `K_MSEC(wait)` later and stops; `zmk_behavior_queue_add` runs the loop synchronously only when no work is pending. Each executed binding gets `timestamp = k_uptime_get()` (`:35`).
- Resulting timeline, queue idle, trigger delivered to keymap at **D**: `D`: `kp L ↓` (HID report). `D+10`: `kp L ↑`, `mo 12 ↓` (layer 12 on), `aksl ↑` → sticky timer armed, `release_at = D+10+100`.

### 4.2 `aksl` — PROVED (`expanded_symbolic.dts:357-363`)

```dts
aksl: aksl {
    compatible = "zmk,behavior-sticky-key";
    label = "flo,behavior-adaptive-key-sticky-layer";
    #binding-cells = <1>;
    release-after-ms = <100>;
    bindings = <&mo>;
};
```

- Absent booleans → false: `quick-release`, `lazy`, `ignore-modifiers` (`zmk,behavior-sticky-key.yaml`).
- Press: `press_sticky_key_behavior` → `&mo L` ↓ → `zmk_keymap_layer_activate(L)` (`behavior_sticky_key.c:142-165`, `behavior_momentary_layer.c`).
- Release (from the queue, ~0 ms after press): no keycode seen yet → `timer_started`, `release_at = timestamp + 100`, `k_work_schedule(release_timer, 100)` (`:167-190`).
- Any **keycode** ↓ event afterwards (`:234-300`): if `ev.timestamp > release_at` → timeout path (layer off, key not adapted); else `stop_timer`, remember the keycode; **no quick-release** → the layer stays on until that keycode's ↑ (`:303-310`), i.e. 10 ms longer for a `&bk` follower. Modifiers count (no `ignore-modifiers`) — see quirk Q5.
- Timer expiry (`:124-131`, `:340-352`): `release_sticky_key_behavior` → `&mo L ↑` → layer off exactly at `release_at`.
- Layer 999 (`&ak 999 I`, RM3): `&mo 999` ↓/↑ → `set_layer_state` → `-EINVAL` (`keymap.c:142-145`); return value ignored. Sticky slot consumed until next keycode ↑ or 100 ms.

### 4.3 `&bk` — PROVED (`expanded_symbolic.dts:100-110`)

```dts
bk: bk {
        label = "flo,behavior-buffered-key";
        compatible = "zmk,behavior-macro-one-param";
        #binding-cells = <1>;
        wait-ms = <0>;
        tap-ms = <10>;
        bindings = <&macro_param_1to1>, <&macro_tap &kp 0>;
};
```

- `&bk X` = `kp X ↓`, wait 10, `kp X ↑`. Release does nothing → no key repeat, fixed 10 ms tap regardless of hold. Used 86× in keymap+combos; it is every AK follower and every combo output.

### 4.4 Other macros in the AK path — PROVED

- `bm` (`expanded_symbolic.dts:86-99`): `macro_press &kp MOD` · `macro_pause_for_release` · `macro_release &kp MOD` — a real hold. Only via `hml`/`hmr` (l_fn). Not in the AK path on alpha.
- `ak_R_macro` (`:372`): `compatible = "zmk,behavior-macro"; wait-ms = <0>; tap-ms = <0>; bindings = <&ak 17 R>;` → wraps `&ak` for the thumb (see Q3).
- `ak_S/C/N/T/A/E/M_macro` + `hml_*`/`hmr_*`: defined, **unreachable** in NAQUADAH.
- `replace_char_with_bigram_XY`, 9 reachable of 22 (`BM LB LK LM LP LV NB NV TP`).

### 4.5 `REPLACE_CHAR_WITH_BIGRAM(L, B)` expansion (3) — PROVED (`expanded_symbolic.dts:55`; template `preprocessor_macros.c:12-28`)

```dts
replace_char_with_bigram_LB: replace_char_with_bigramLB {
        label = "flo-macro-replace-char-with-bigram-LB";
        compatible = "zmk,behavior-macro";
        #binding-cells = <0>;
        wait-ms = <0>;
        tap-ms = <10>;
        bindings = <&macro_tap &kp BACKSPACE>,
                   <&macro_tap &kp L>,
                   <&macro_release &kp LSHFT>,
                   <&macro_release &kp RSHFT>,
                   <&macro_tap &ak 3 B>;
};
```

- Bound as `DB_to_LB` on l_akD at LM0 (`layers_B_NAQUADAH_adaptive_keys.dtsi:39`; expanded layer 5 line `916`): after D, pressing the B key yields "L B" in place of "D B" → host sees `D`, `⌫`, `L`, `B`.
- Timeline (queue idle at F = follower delivery): `F` ⌫↓ · `F+10` ⌫↑ L↓ · `F+20` L↑ LSHFT↑ RSHFT↑ `ak(3,B)`↓ [its 4 items enqueue behind; no re-entrancy because the queue work is RUNNING] · `F+30` `ak`↑(no-op) B↓ · `F+40` B↑ `mo 3`↓ (l_akB on) `aksl`↑ (off at `F+140`). INFERRED (queue order), test T9.
- The two `macro_release &kp *SHFT` drop any held/sticky shift before B (so "Db" typed with sticky shift → "LB"? no: shift is released before `B`, giving "Lb"). Note the replaced char `L` is typed while shift may still be held → "DB" with caps → "LB"… exact casing is host-visible, test T9.

---

## 5. Hack combo, fully expanded (4) — PROVED (`expanded_symbolic.dts:863`)

```dts
combo_ak_consistency_hack {
    bindings = <&none>;
    key-positions = <4 3 2 1 0 14 13 12 11 10 24 23 22 21 20 5 6 7 8 9 15 16 17 18 19 25 26 27 28 29 32 31 30 33 34 35>;
    layers = <0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24>;
    timeout-ms = <11>;
};
```

- 36 key positions (`ALL_KEYS = KEYS_L KEYS_R THUMBS_L THUMBS_R`, `aliases_key_positions.dtsi:61-65`; order is alias order, not numeric — irrelevant to matching).
- 25 layers = `l_alpha_aks`. **Not** active on nav/mod/fn/num/numsym/cfg/nav_linwin (25-31): keys on those layers are only delayed by real combos.
- Implicit: `require-prior-idle-ms = -1`, `slow-release` false, virtual key position = `ZMK_KEYMAP_LEN + sensors + 27` (28th and last `COMBO_INST`, `combo.c:517-533`).
- `initialize_combo` (`combo.c:93-126`) sorts each key's list by `key_position_len` then virtual position → the hack is always the **last** candidate; `candidates[0]` is always a real combo when any exists.
- Never fires: `candidate_is_completely_pressed` needs 36 pressed keys (`combo.c:209-216`).

---

## 6. Combo macros, all combos, per-key summary (5)

### 6.1 Macro expansions — PROVED (`preprocessor_macros.c:32-56`)

```
COMBO_LAY_BASE(LAYERS, NAME, BINDINGS, KEYPOS, TIMEOUT) →
  combo_NAME { bindings = <BINDINGS>; key-positions = <KEYPOS>; layers = <LAYERS>; timeout-ms = <TIMEOUT>; };

COMBO_ANY_ONE_HAND(N,B,K) → COMBO_LAY_BASE(l_all,  N,B,K, 16)     COMBO_LAY_ONE_HAND(L,N,B,K) → COMBO_LAY_BASE(L, N,B,K, 16)
COMBO_ANY_NON_ADJC(N,B,K) → COMBO_LAY_BASE(l_all,  N,B,K, 18)     COMBO_LAY_NON_ADJC(L,N,B,K) → COMBO_LAY_BASE(L, N,B,K, 18)
COMBO_ANY_TWO_HAND(N,B,K) → COMBO_LAY_BASE(l_all,  N,B,K, 30)     COMBO_LAY_TWO_HAND(L,N,B,K) → COMBO_LAY_BASE(L, N,B,K, 30)
```
- `l_all` → `0 1 2 … 31`; `l_alpha_aks` → `0 1 2 … 24`; `l_alpha_aks l_nav l_num l_nav_linwin l_numsym` → `0…24 25 28 31 29`.

### 6.2 All 28 combos in definition order (= virtual-key-position order) — PROVED

| # | name | positions | ms | layers | binding |
|---|---|---|---|---|---|
| 0 | delWord_linwin | RM1 RM2 RM3 `<16 17 18>` | 18 | 1 31 | `&bk LC(BSPC)` |
| 1 | delWordTrans_linwin | LM3 LM2 LM1 `<11 12 13>` | 18 | 31 | `&bk LC(BSPC)` |
| 2 | tab_linwin | LB1 LB0 `<23 24>` | 16 | 1 | `&lk LA(TAB) TAB` |
| 3 | magicCloseQuitCb_linwin | LB3 LB2 LB1 `<21 22 23>` | 16 | 1 | `&lk_magicCloseQuitLinWin 0 0` |
| 4 | typeQ | LT2 LT1 `<2 3>` | 16 | 0-24 | `&bk Q` |
| 5 | typeZ | LT3 LT2 `<1 2>` | 16 | 0-24 | `&bk Z` |
| 6 | space | LT1 LT0 `<3 4>` | 16 | 0-31 | `&bk SPACE` |
| 7 | entr | LM1 LM0 `<13 14>` | 16 | 0-31 | `&bk RETURN` |
| 8 | entr2 | RM0 RM1 `<15 16>` | 16 | 0-31 | `&bk RETURN` |
| 9 | tab | LB1 LB0 `<23 24>` | 16 | 0-31 | `&lk LG(TAB) TAB` |
| 10 | esc2 | LB2 LB1 `<22 23>` | 16 | 0-31 | `&bk ESC` |
| 11 | bspc | RM1 RM2 `<16 17>` | 16 | 0-24,25,28,31,29 | `&bk BSPC` |
| 12 | del | RM2 RM3 `<17 18>` | 16 | 0-24,25,28,31,29 | `&bk DEL` |
| 13 | delWord | RM1 RM2 RM3 `<16 17 18>` | 18 | 0-24,25,28,31,29 | `&bk LA(BSPC)` |
| 14 | bspcTrans | LM3 LM2 `<11 12>` | 16 | 25 28 31 29 | `&bk BSPC` |
| 15 | delTrans | LM2 LM1 `<12 13>` | 16 | 25 28 31 29 | `&bk DEL` |
| 16 | delWordTrans | LM3 LM2 LM1 `<11 12 13>` | 18 | 25 28 31 29 | `&bk LA(BSPC)` |
| 17 | magicCloseQuitCb | LB3 LB2 LB1 `<21 22 23>` | 16 | 0-31 | `&lk_magicCloseQuit 0 0` |
| 18 | wispr | LM3 LM2 `<11 12>` | 16 | 0-24 | `&lk_wispr GLOBE LA(R)` |
| 19 | typeExcl | RT1 RT2 `<6 7>` | 16 | 0-24 | `&bk EXCL` |
| 20 | typeQues | RT2 RT3 `<7 8>` | 16 | 0-24 | `&bk QMARK` |
| 21 | typeGrav | RT3 RT4 `<8 9>` | 16 | 0-24 | `&MagicGrave` |
| 22 | magicBracketsL | RB0 RB1 `<25 26>` | 16 | 0-24 | `&MagicBracketsL` |
| 23 | magicBracketsR | RB3 RB4 `<28 29>` | 16 | 0-24 | `&MagicBracketsR` |
| 24 | logseqPageRef | RB2 RB3 RB4 `<27 28 29>` | 16 | 0-24 | `&logseqPageRef` |
| 25 | capsWord | RM1 RM2 RM3 RM4 `<16 17 18 19>` | 18 | 0-24 | `&caps_word` |
| 26 | settings | RH1 RH2 `<34 35>` | 16 | 0-31 | `&mo 30` |
| 27 | ak_consistency_hack | all 36 | 11 | 0-24 | `&none` |

- No 30 ms combo exists. `combos_linwin.dtsi` "overrides" are separate nodes, not DT overrides: on layer 1 both `delWord` (18) and `delWord_linwin` (18) are candidates for RM1-3; both complete together; `candidates[0]` = lower virtual position = `delWord_linwin` (#0) wins. On AK layers 2-24 the `_linwin` combos are **inactive** (`combo_active_on_layer` checks the *highest* active layer, `combo.c:128-139`, `keymap.c:187-193`): inside an AK window on the Windows layer, RM1-3 gives `LA(BSPC)` (mac delWord) instead of `LC(BSPC)`. PROVED from tables, behavioural consequence INFERRED (test T10).

### 6.3 Per-key summary on layers 0-24 (hack excluded) — PROVED

| pos | key | real combos (ms) | n | min | max |
|---|---|---|---|---|---|
| 0 | LT4 (X) | — | 0 | – | – |
| 1 | LT3 (W) | typeZ(16) | 1 | 16 | 16 |
| 2 | LT2 (M) | typeQ(16) typeZ(16) | 2 | 16 | 16 |
| 3 | LT1 (P) | typeQ(16) space(16) | 2 | 16 | 16 |
| 4 | LT0 (K) | space(16) | 1 | 16 | 16 |
| 5 | RT0 (MagicSlash) | — | 0 | – | – |
| 6 | RT1 (dotcol) | typeExcl(16) | 1 | 16 | 16 |
| 7 | RT2 (equalDash) | typeExcl(16) typeQues(16) | 2 | 16 | 16 |
| 8 | RT3 (minus) | typeQues(16) typeGrav(16) | 2 | 16 | 16 |
| 9 | RT4 (sqtDqt) | typeGrav(16) | 1 | 16 | 16 |
| 10 | LM4 (C) | — | 0 | – | – |
| 11 | LM3 (S) | wispr(16) | 1 | 16 | 16 |
| 12 | LM2 (N) | wispr(16) | 1 | 16 | 16 |
| 13 | LM1 (T) | entr(16) | 1 | 16 | 16 |
| 14 | LM0 (B) | entr(16) | 1 | 16 | 16 |
| 15 | RM0 (comsemi) | entr2(16) | 1 | 16 | 16 |
| 16 | RM1 (A) | entr2(16) bspc(16) delWord(18) capsWord(18) | 4 | 16 | 18 |
| 17 | RM2 (E) | bspc(16) del(16) delWord(18) capsWord(18) | 4 | 16 | 18 |
| 18 | RM3 (I) | del(16) delWord(18) capsWord(18) | 3 | 16 | 18 |
| 19 | RM4 (H) | capsWord(18) | 1 | 18 | 18 |
| 20 | LB4 (F) | — | 0 | – | – |
| 21 | LB3 (G) | magicCloseQuitCb(16) | 1 | 16 | 16 |
| 22 | LB2 (L) | esc2(16) magicCloseQuitCb(16) | 2 | 16 | 16 |
| 23 | LB1 (D) | tab(16) esc2(16) magicCloseQuitCb(16) | 3 | 16 | 16 |
| 24 | LB0 (V) | tab(16) | 1 | 16 | 16 |
| 25 | RB0 (MagicUnder) | magicBracketsL(16) | 1 | 16 | 16 |
| 26 | RB1 (U) | magicBracketsL(16) | 1 | 16 | 16 |
| 27 | RB2 (O) | logseqPageRef(16) | 1 | 16 | 16 |
| 28 | RB3 (Y) | magicBracketsR(16) logseqPageRef(16) | 2 | 16 | 16 |
| 29 | RB4 (J) | magicBracketsR(16) logseqPageRef(16) | 2 | 16 | 16 |
| 30 | LH2 (mo num) | — | 0 | – | – |
| 31 | LH1 (htls) | — | 0 | – | – |
| 32 | LH0 (blt_akR) | — | 0 | – | – |
| 33 | RH0 (blt space) | — | 0 | – | – |
| 34 | RH1 (mo numsym) | settings(16) | 1 | 16 | 16 |
| 35 | RH2 (togMacPc) | settings(16) | 1 | 16 | 16 |

- On layer 1 add: delWord_linwin(18) to RM1-3, tab_linwin(16) to LB1/LB0, magicCloseQuitCb_linwin(16) to LB3-LB1 → same min/max everywhere.
- Meaning of "max" (INFERRED, `combo.c:472-486` + `:197-207`): after a key is captured (first press or re-raise), the combo timer walks the candidate deadlines and only releases the key when **all** candidates have expired → an isolated key press reaches the keymap at `ts + max(11, max real timeout)` unless a release or a non-sharing key press happens first (`:456-470`, `:436-441` case 0).

---

## 7. Linger keys (6) — PROVED

Template (`preprocessor_macros.c:69-77`) and instance (`expanded_symbolic.dts:566`):
```dts
lk_magicCloseQuit: lk_magicCloseQuit {
    compatible = "zmk,behavior-hold-tap"; label = "lk_magicCloseQuit"; #binding-cells = <2>;
    tapping-term-ms = <100>; flavor = "tap-preferred";
    bindings = <&quitApp>, <&closeTab>;      /* <LINGER>, <TAP> — hold slot first */
};
```
Generic (`linger_keys/behaviors.dtsi:2-9`): `lk { … tapping-term-ms = <100>; flavor = "tap-preferred"; bindings = <&bk>, <&bk>; }` used as `&lk HOLD_KEY TAP_KEY`; `lk_bk` identical (`:39`).

- Implicit properties: `quick-tap-ms = -1`, `require-prior-idle-ms = -1`, no `hold-while-undecided`, no `retro-tap`, no positional trigger.
- Decision (`behavior_hold_tap.c:297-311`): key ↑ before 100 ms → **TAP**; 100 ms timer → **HOLD**; other keys ↓/↑ during the undecided period do **not** decide, they are captured (`:709-768`) and re-raised after the decision (`:181-243`) with their **original timestamps**.
- Tap output: TAP binding pressed at decision then released immediately (`:625-660`) → for `&bk X`: `X ↓`, 10 ms, `X ↑`. Hold output: LINGER binding pressed at exactly `press_ts + 100` (`:589-622` schedules `tapping_term_ms_left`), released on key ↑.
- Live linger keys on layer 0: RT1 `&lk COLON DOT` (tap `.`, linger `:`), RT2 `&lk_bk MINUS EQUAL` (tap `=`, linger `-`), RT4 `&lk_bk DQT SQT` (tap `'`, linger `"`), RM0 `&lk SEMI CMMA` (tap `,`, linger `;`); via mod-morph RT0 `MagicSlash`, RB0 `MagicUnder`; via combos `tab`, `wispr`, `magicCloseQuitCb`, `typeGrav`, `magicBrackets*`.
- `lk_wispr` (`:11-18`): hold = `&kp GLOBE` (real hold), tap = `&bk LA(R)`.
- Because the trigger is a hold-tap, a linger key's own AK-style delay is: combo capture (max timeout) → hold-tap undecided (≤ 100 ms) → macro tap (10 ms).

---

## 8. Callum mods (7)

### 8.1 Nodes — PROVED (`mods/behaviors.dtsi`, `mods/macros.dtsi`; expanded `:389-424`, `:148-168`)

```dts
htls: hold_tap_layer_sticky_shift { compatible = "zmk,behavior-hold-tap"; #binding-cells = <2>;
    tapping-term-ms = <90>; flavor = "hold-preferred"; bindings = <&moAndBuffer>, <&skms>; };
htm: hold_tap_mod { compatible = "zmk,behavior-hold-tap"; #binding-cells = <2>;
    tapping-term-ms = <130>; flavor = "tap-preferred"; bindings = <&kp>, <&skm>;
    hold-while-undecided; hold-while-undecided-linger; };
skm:  sticky_key_mod       { compatible = "zmk,behavior-sticky-key"; #binding-cells = <1>; bindings = <&kp>; release-after-ms = <1500>; ignore-modifiers; };
skms: sticky_key_mod_shift { compatible = "zmk,behavior-sticky-key"; #binding-cells = <1>; bindings = <&kp>; release-after-ms = <1500>; };
moAndBuffer: moAndBuffer { compatible = "zmk,behavior-macro-one-param"; #binding-cells = <1>; wait-ms = <0>; tap-ms = <0>;
    bindings = <&macro_press &mo 26>, <&macro_pause_for_release>, <&macro_wait_time 130>, <&macro_tap &none>, <&macro_release &mo 26>; };
```
- Bindings: LH1 = `&htls 26 LSHIFT`; l_mod (26) home row = `&htm LCTRL LCTRL`, `&htm LALT LALT`, `&htm LGUI LGUI`, `&htm LSHIFT LSHIFT` (LM4..LM1) and mirrored RM1..RM4 (`expanded:1105`). `moAndBuffer`'s param is ignored (no `macro_param_1to1`; layer 26 is hard-coded).
- Unreachable siblings: `slm`, `shiftAndDisableModsLayer`, `bsklt`, `bsk`, `hrmSk`, `bm` on alpha (only via `hml`/`hmr` on l_fn).

### 8.2 Mechanics — PROVED unless marked

- **Thumb (`htls`, hold-preferred, 90 ms)**: any other key ↓ while undecided → HOLD immediately (`decide_hold_preferred`, `:333-347`); 90 ms → HOLD; ↑ before → TAP = `skms LSHIFT` (sticky shift 1500 ms, consumed by the next keycode, released on that keycode's ↑; no `ignore-modifiers` → a second sticky mod would consume it).
- **Hold = `moAndBuffer`**: press phase = `mo 26 ↓` (layer on at once). Release phase (state precomputed in `behavior_macro_init` `:114-137`: start index 3, mode PRESS, wait 0) = `wait_time 130` → `tap &none` (↓ wait 0, ↑ wait **130**) → `release &mo 26` (wait **130**). ⇒ layer 26 stays on **130 ms after thumb release** (Flo's "buffer" for an `htm` still undecided), and the behavior queue is busy for **260 ms** total (Q4, INFERRED).
- **`htm` (tap-preferred 130 ms, hold-while-undecided + linger)**: on ↓ the hold binding `kp MOD` is pressed at once (`decide_hold_tap` `:511-558`, HID mod refcount 1, `hid.c:52-59`). Other keys are captured (not decisive). ↑ < 130 ms → TAP: linger set → hold **not** released before `skm MOD ↓` (`press_binding` `:444-464`) → sticky presses `kp MOD` again (count 2) → `skm ↑` starts its 1500 ms timer → then `release_hold_binding` (`:640-642`) → count 1 → MOD still down, now owned by the sticky. ≥ 130 ms → HOLD (already pressed; captured keys re-raised with the mod down).
- **`skm` with `ignore-modifiers`**: another mod keycode ↓ does not consume it → Ctrl+Alt+… stacks. Consumption on a non-mod keycode ↓ (`behavior_sticky_key.c:267-300`), release on that keycode's ↑ (`:303-310`) → with `CONFIG_ZMK_HID_SEPARATE_MOD_RELEASE_REPORT` the host sees `key ↑` then `mod ↑` in separate reports.
- Hold-tap's keycode listener deliberately does not capture the mod produced by hold-while-undecided (`:786-789`).
- **"Callum mod buffer"** most plausibly means `moAndBuffer` (the 130 ms `action_mod_tapping_term` linger of `l_mod` after the thumb is lifted, `mods/macros.dtsi:2-7` comment). Secondary readings: `bm` = "buffered mod" macro; Flo's general "buffered" = routed through the behavior queue.

---

## 9. Mod-morph usage (8) — PROVED (`mod_morph/behaviors.dtsi`)

- Reachable: `MagicSlash` (RT0, `:120-126`) = `<&lk_magicSlashHome 0 0>` / shifted `<&lk_magicHashDotHome 0 0>`; `MagicUnder` (RB0, `:139-145`) = `<&lk_magicUnderPipe 0 0>` / `<&lk BSLH STAR>`; `MagicGrave` (combo RT3 RT4, `:193-199`) = `<&lk_magicGraveCodeblock 0 0>` / `<&bk GRAVE>`; `MagicBracketsL/R` (combos, `:166-180`) = `<&lk LEFT_BRACKET LEFT_PARENTHESIS>` / `<&lk LEFT_BRACE LESS_THAN>` (and R mirror); `MinusPlus` (l_num LT4/RT4, `:39-45`) = `<&bk MINUS>` / `<&bk PLUS>`. All `mods = <(MOD_LSFT|MOD_RSFT)>`, no `keep-mods`.
- 14 other mod-morphs (`CmmaSemi`, `ExclQues`, `DashEqual`, `SlshStar`, `HashDllr`, `UnderDash`, `SpaceUnder`, `Dqt*`, `Sqt*`, `BspcDel`, `SqtDqt`, `EqualSlash`, `EqualAt`, `aB`, `aB_cD`) unreachable.
- Semantics (`behavior_mod_morph.c`): branch chosen at ↓ from `zmk_hid_get_explicit_mods()` (sticky/held mods only); while the shifted branch is pressed, `masked_mods = mods` hides Shift from the HID report → `&lk BSLH STAR` linger gives `\` not `|`, matching the comment table (`:128-137`). Morph + linger + `&bk` = up to 100 ms (hold-tap) + 10 ms (macro) after combo capture.

---

## 10. AK triggers, layers, base vs AK binding (9) — PROVED (`aktable.py` over expanded layers)

Base layer 0 (`expanded:870-873`):
```
LT4 &ak 23 X   LT3 &ak 22 W   LT2 &ak 13 M   LT1 &ak 16 P   LT0 &ak 11 K   | RT0 &MagicSlash  RT1 &lk COLON DOT  RT2 &lk_bk MINUS EQUAL  RT3 &bk MINUS  RT4 &lk_bk DQT SQT
LM4 &ak 4 C    LM3 &ak 18 S   LM2 &ak 14 N   LM1 &ak 19 T   LM0 &ak 3 B    | RM0 &lk SEMI CMMA RM1 &ak 2 A       RM2 &ak 6 E             RM3 &ak 999 I  RM4 &ak 9 H
LB4 &ak 7 F    LB3 &ak 8 G    LB2 &ak 12 L   LB1 &ak 5 D    LB0 &ak 21 V   | RB0 &MagicUnder  RB1 &ak 20 U       RB2 &ak 15 O            RB3 &ak 24 Y   RB4 &bk J
                LH2 &mo 28   LH1 &htls 26 LSHIFT   LH0 &blt_akR 25 0        | RH0 &blt 29 SPACE   RH1 &mo 29   RH2 &togMacPc
```
- 22 direct triggers + R via thumb + `hE` (layer 10, reachable only from l_akH's RM2 `&ak 10 E`). `I` arms nothing (999). `J`, `Q`, `Z` are plain `&bk`.

Follower table (non-`&trans` cells; trigger hand → follower hands, all same-hand):

| layer | trigger | followers |
|---|---|---|
| 2 akA | RM1 A | RT2 `&bk U`; RM1 `&ak 2 A` |
| 3 akB | LM0 B | LM4 `&bk B`; LB3 `&bk L`; LB1 `&bk L`; LM0 `&ak 3 B` |
| 4 akC | LM4 C | LT1 `&replace…TP`; LB3 `&bk C`; LM4 `&ak 4 C` |
| 5 akD | LB1 D | LT4 `&bk V`; LT0 `&replace…LK`; LM4 `&bk D`; LM0 `&replace…LB`; LB0 `&replace…LV`; LB1 `&ak 5 D` |
| 6 akE | RM2 E | RT1 `&bk E`; RT3 `&bk O`; RM2 `&ak 6 E` |
| 7 akF | LB4 F | LB3 `&bk F`; LB4 `&ak 7 F` |
| 8 akG | LB3 G | LT1 `&replace…LP`; LT0 `&replace…LK`; LM4 `&bk G`; LB4 `&bk S`; LB3 `&ak 8 G` |
| 9 akH | RM4 H | RM2 `&ak 10 E` (→ akhE); RM4 `&ak 9 H` |
| 10 akhE | (via akH) | RT1 `&bk E`; RT3 `&bk O`; RB1 `&bk Y`; RM2 `&ak 10 E` |
| 11 akK | LT0 K | LT2 `&replace…BM`; LB3 `&bk L`; LB1 `&bk L`; LT0 `&ak 11 K` |
| 12 akL | LB2 L | LT4 `&bk G`; LB3 `&bk L`; LB2 `&ak 12 L` |
| 13 akM | LT2 M | LT3 `&bk M`; LT0 `&ak 3 B` (→ akB chain); LM1 `&bk N`; LT2 `&ak 13 M` |
| 14 akN | LM2 N | LT4 `&bk M`; LT3 `&bk N`; LM2 `&ak 14 N` |
| 15 akO | RB2 O | RT1 `&bk O`; RT3 `&bk E`; RB2 `&ak 15 O` |
| 16 akP | LT1 P | LT3 `&bk P`; LM4 `&bk T`; LM2 `&bk D`; LM0 `&replace…NB`; LB3 `&bk L`; LT1 `&ak 16 P` |
| 17 akR | LH0 R (thumb tap) | LT4 `&bk R`; LH0 `&ak 17 R` |
| 18 akS | LM3 S | LT4 `&bk F`; LB1 `&bk S`; LH0 `&bk W`; LM3 `&ak 18 S` |
| 19 akT | LM1 T | LB3 `&bk T`; LB0 `&replace…NV`; LM1 `&ak 19 T` |
| 20 akU | RB1 U | RT2 `&bk A`; RB1 `&ak 20 U` |
| 21 akV | LB0 V | LM1 `&bk N`; LB1 `&bk L`; LB0 `&ak 21 V` |
| 22 akW | LT3 W | LT4 `&bk S`; LT2 `&replace…LM`; LT3 `&ak 22 W` |
| 23 akX | LT4 X | LM3 `&bk C`; LT4 `&ak 23 X` |
| 24 akY | RB3 Y | RM4 `&bk I`; RB3 `&ak 24 Y` |

- Trigger key on its **own** AK layer = the same `&ak L X` (the `___X____` alias): types X again and re-arms the same layer (repeat). On any **other** AK layer it is `&trans` → falls through to layer 0's `&ak` (`keymap.c:651-680` walks layers high→low, `&trans` returns >0 → continue). A follower `&bk` types and **does not** arm a layer (chain ends); a follower `&ak` (akM→LT0 `&ak 3 B`, akH→RM2 `&ak 10 E`) chains; a follower `replace…` backspaces, retypes, and arms the second letter's layer.
- Layer resolution uses the layer state **at delivery of the position event** (`keymap.c:653-654` snapshot into `zmk_keymap_active_behavior_layer[position]`), not at physical press — this is why delivery order vs `mo` timing is everything.

---

## 11. Timelines and quirks (PROVED mechanics, INFERRED outcomes; tests in §13)

Notation: `ts` = position timestamp (post-debounce; native_posix: exact mock time). Queue idle unless stated.

- **Q1 — Isolated trigger (L, LB2, 16 ms combos)**: `ts`: captured (candidates esc2, magicCloseQuitCb, hack). `ts+11` hack expires (2 remain, no cleanup). `ts+16` all expire → `cleanup` → keymap → `kp L ↓`. `ts+26`: `kp L ↑`, layer 12 on, timer → layer off at `ts+126`. A combo-less trigger (X/C/F) is delivered at `ts+11`, layer on at `ts+21`. Release before delivery (`position_state_up` → `cleanup`) delivers early. **Test T1.**
- **Q2 — Follower timing (same hand, no shared combo), trigger L at 0, follower X-key at d**:
  - `d < 10`: X captured with only the hack (filter keeps hack, `combo.c:163-195`), no cleanup; at 11 hack expires → `cleanup` → L delivered (`kp L ↓` at 11 sets `last_tapped_timestamp = 11`, `combo.c:85-90, 496-502`), X re-raised (`ZMK_EVENT_RAISE`, `:273-289`) with `ts = d`; `is_quick_tap`: `11 + (-1) > d` → true → 0 candidates → **bubble straight to keymap at 11**, layer 12 still off (on at 21) → base `&ak 23 X` → output "lx" (no adaptation). **Test T3.**
  - `d = 10`: not quick-tap; X captured, hack deadline 21 = layer-on instant 21. Both are `k_work_delayable` timeouts on the same tick; queue work was scheduled first (at 11) → expected to run first, but **ambiguous**. **Test T3b.**
  - `11 ≤ d < 16`: X's press finds L's real candidates (esc2, mCQ) without X → `case 0: cleanup()` → L delivered at d, X re-raised (`is_quick_tap`: `d-1 > d` false) → hack → delivered at `d+11` ≥ 22 > layer-on `d+10` → "lg". `d ≥ 16`: L delivered at 16, layer on 26, X at `d+11` ≥ 27 → "lg" while `d+11 ≤ 126` → **d ≤ 115**. For followers with 16/18 ms combos the upper bound drops to 110/108, for combo-less triggers everything shifts 5 ms earlier. **Tests T2, T4.**
- **Q3 — R thumb (`&blt_akR 25 0`, tap-preferred 200 ms)**: tap decided on thumb ↑ (at r) → `press_tap_binding(ak_R_macro)` runs **outside** the queue's work handler → `queue_add(ak ↓, wait 0)` → synchronous loop A executes `ak ↓` → `ak` calls `queue_add(kp R ↓, 10)` → work not pending → **nested** loop B executes `kp R ↓`, schedules +10, returns → loop A continues draining: `kp R ↑`, `aksl 17 ↓`, `aksl 17 ↑` all at r. Result: R tap 0 ms, layer 17 on at r (not r+10). Depends on Zephyr's `k_work_delayable_is_pending()` returning false while the loop runs outside the work item (true by API contract: busy flags are DELAYED/QUEUED/RUNNING/CANCELING, none set here). Also: a follower pressed while the thumb is still down is captured by the hold-tap, re-raised with a stale ts → quick-tap bypass → base layer → no adaptation ("r" + X-key held-overlapping → "rx" not "rr"). **Tests T7, T7b.**
- **Q4 — Action thumb release blocks the queue 260 ms** (§8.2). Any `&ak`/`&bk` delivered in `(T_rel, T_rel+260)` is emitted at `T_rel+260` (order preserved). **Test T8.**
- **Q5 — aksl is consumed by modifier keycodes**: `skms LSHIFT ↓` (thumb tap) or an `htm` mod within the 100 ms window stops the timer and keeps the AK layer on until that modifier keycode's ↑ (up to 1500 ms for a sticky shift that is never consumed). E.g. `T`, tap shift-thumb ≤ ~100 ms later, then G-key 500 ms later → G-key resolves on l_akT (`&bk T`). **Test T5.**
- **Q6 — Shared 2-key combo never fires "instantly"**: with the hack always a co-candidate, a fully pressed 2-key combo waits for `cleanup` = its own deadline (`ts1 + 16/18`) or the first release (`position_state_up`), because `combo_timeout_handler` only cleans up when **zero** candidates remain (`combo.c:472-486`); the `case 1` fast path (`:445-450`) only triggers if the second key arrives after the hack expired (11 ≤ d < timeout). **Test T6.**
- **Q7 — Two-hand skew**: irrelevant to AK pairs (all same-hand) but left-hand `ts` lags physical contact by BLE interval (7.5-15 ms) + 5 ms debounce; right-hand by 5 ms only. Affects cross-hand roll order and would have affected the disabled 30 ms combos.
- **Q8 — Layer-999 `I`**: `&ak 999 I` → `kp I` 10 ms tap, then two failing `&mo 999` calls; the sticky entry still consumes the next keycode ↓/↑ pair. No output difference. **Test T11** (log shows `-EINVAL` via `LOG_DBG` only if debug on; simplest assertion: no `layer_changed` line after `I`).
- **Q9 — `_linwin` combos vanish inside AK windows** (§6.2). **Test T10.**
- **Q10 — Hold-tap vs hack ordering**: the position event of a hold-tap key (thumbs, linger keys) is itself captured by the hack first (11 ms) — the hold-tap's `timestamp` is the original `ts`, so its tapping term is **not** extended (`behavior_hold_tap.c:589-622` computes `tapping_term_ms_left` from `hold_tap->timestamp`), but its decision cannot happen before delivery.

---

## 12. Minimal reproduction recipe (native_posix, 3×4 mock matrix)

Files go in a test dir `app/tests/<name>/` (run with `./run-test.sh tests/<name>` from `zmk/app` inside the dev container; `run-test-debug.sh` keeps timestamps in `build/<test>/keycode_events_full.log`).

`native_posix_64.conf`
```
CONFIG_GPIO=n
CONFIG_ZMK_BLE=n
CONFIG_LOG=y
CONFIG_LOG_BACKEND_SHOW_COLOR=n
CONFIG_ZMK_LOG_LEVEL_DBG=y
CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO=12
CONFIG_ZMK_COMBO_MAX_COMBOS_PER_KEY=30
CONFIG_ZMK_COMBO_MAX_PRESSED_COMBOS=20
CONFIG_ZMK_BEHAVIORS_QUEUE_SIZE=512
```

`native_posix_64.keymap` — real node text from the config, no aliases. Positions: row0 = 0 1 2 3, row1 = 4 5 6 7, row2 = 8 9 10 11. Layer 1 plays l_akL, layer 2 plays l_akX.
```dts
#include <dt-bindings/zmk/keys.h>
#include <behaviors.dtsi>
#include <dt-bindings/zmk/kscan_mock.h>

/ {
    macros {
        ak: ak {
            compatible = "zmk,behavior-macro-two-param";
            #binding-cells = <2>;
            wait-ms = <0>;
            tap-ms = <10>;
            bindings = <&macro_param_2to1>, <&macro_tap &kp 0>,
                       <&macro_tap_time 0>,
                       <&macro_param_1to1>, <&macro_tap &aksl 0>;
        };
        bk: bk {
            compatible = "zmk,behavior-macro-one-param";
            #binding-cells = <1>;
            wait-ms = <0>;
            tap-ms = <10>;
            bindings = <&macro_param_1to1>, <&macro_tap &kp 0>;
        };
        ak_R_macro: ak_R_macro {                     /* only for T7 */
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            wait-ms = <0>;
            tap-ms = <0>;
            bindings = <&ak 1 R>;
        };
    };

    behaviors {
        aksl: aksl {
            compatible = "zmk,behavior-sticky-key";
            #binding-cells = <1>;
            release-after-ms = <100>;
            bindings = <&mo>;
        };
        lk: lk {                                     /* linger key, generic */
            compatible = "zmk,behavior-hold-tap";
            #binding-cells = <2>;
            tapping-term-ms = <100>;
            flavor = "tap-preferred";
            bindings = <&bk>, <&bk>;
        };
        blt_akR: blt_akR {                           /* only for T7 */
            compatible = "zmk,behavior-hold-tap";
            #binding-cells = <2>;
            flavor = "tap-preferred";
            tapping-term-ms = <200>;
            bindings = <&mo>, <&ak_R_macro>;
        };
    };

    combos {
        compatible = "zmk,combos";
        combo_space {                                /* real 16 ms tier (LT1 LT0 → SPACE) */
            bindings = <&bk SPACE>;
            key-positions = <2 3>;
            layers = <0 1 2>;
            timeout-ms = <16>;
        };
        combo_bspc {                                 /* real 16 ms, overlaps the 18 ms one (RM1 RM2) */
            bindings = <&bk BSPC>;
            key-positions = <4 5>;
            layers = <0 1 2>;
            timeout-ms = <16>;
        };
        combo_delWord {                              /* real 18 ms tier (RM1 RM2 RM3 → LA(BSPC)) */
            bindings = <&bk LA(BSPC)>;
            key-positions = <4 5 6>;
            layers = <0 1 2>;
            timeout-ms = <18>;
        };
        /* NOT in the shipped firmware: the only 30 ms combos (pronouns) are #include'd out.
           If a 30 ms tier is needed for the page, this is exactly what COMBO_LAY_TWO_HAND would emit: */
        /* combo_pnIm { bindings = <&typePnIm>; key-positions = <2 6>; layers = <0 1 2>; timeout-ms = <30>; }; */
        combo_ak_consistency_hack {                  /* 12-key version of the 36-key hack */
            bindings = <&none>;
            key-positions = <0 1 2 3 4 5 6 7 8 9 10 11>;
            layers = <0 1 2>;
            timeout-ms = <11>;
        };
    };

    keymap {
        compatible = "zmk,keymap";
        base {           /* 0 */
            bindings = <
                &ak 1 L   &ak 2 X   &ak 2 P   &ak 2 K
                &ak 2 A   &ak 2 E   &ak 2 I   &lk COLON DOT
                &kp F     &kp G     &blt_akR 3 0   &kp SPACE
            >;
        };
        akL {            /* 1: after L, pos 1 (X key) → G ; pos 0 repeats L */
            bindings = <
                &ak 1 L   &bk G     &trans    &trans
                &trans    &trans    &trans    &trans
                &trans    &trans    &trans    &trans
            >;
        };
        akX {            /* 2: dummy AK layer for the other letters */
            bindings = <
                &trans    &ak 2 X   &trans    &trans
                &trans    &trans    &trans    &trans
                &trans    &trans    &trans    &trans
            >;
        };
        nav {            /* 3: hold target of blt_akR */
            bindings = <
                &trans    &trans    &trans    &trans
                &trans    &trans    &trans    &trans
                &trans    &trans    &trans    &trans
            >;
        };
    };
};

&kscan {
    rows = <3>;
    columns = <4>;
    events = <
        /* T2: trigger L (r0,c0), follower X-key (r0,c1) 30 ms later → expect L then G */
        ZMK_MOCK_PRESS(0,0,30)
        ZMK_MOCK_PRESS(0,1,50)
        ZMK_MOCK_RELEASE(0,0,10)
        ZMK_MOCK_RELEASE(0,1,300)
    >;
};
```

`events.patterns`
```
s/.*hid_listener_keycode/kp/p
s/.*layer_changed/layer_changed/p
s/.*queue_process_next: Processing next queued behavior in/queue wait/p
```
(`layer_changed` is `keymap.c:156` `LOG_DBG("layer_changed: layer %d state %d")`; keep the `[hh:mm:ss.mmm,uuu]` prefix from the full log for timing assertions. `CONFIG_SYS_CLOCK_TICKS_PER_SEC=1000` on native_posix_64 → 1 ms resolution, so a 10 ms tie is genuinely a tie there; the nRF52840 build ticks at 32768 Hz.)

Mock semantics (`zmk/app/module/drivers/kscan/kscan_mock.c`): the third argument is the delay **after** this event before the next one; event 0 fires after its own delay from boot.

---

## 13. Open questions and ambiguities

- Zephyr sources are not on disk (`zmk/zephyr` is an empty mount point; the tree lives in the dev-container volume). Q3 (nested-macro re-entrancy) relies on `k_work_delayable_is_pending()` being false while `behavior_queue_process_next` runs from a non-work context; T7 settles it empirically.
- Q2 `d = 10` tie: same-tick expiry of the queue timer (layer on) and the combo timer (follower delivery). Zephyr inserts equal-deadline timeouts after existing ones, so the earlier-scheduled queue timer should fire first → adapted. T3b settles it; on hardware the tick is 30 µs so an exact tie is rare.
- Whether Flo's "99.9 %" reliability is explained by inter-key intervals almost never being < 10 ms (Q2) rather than by the mechanism described in `adaptive_keys/combos.dtsi:38-46` (which assumes the follower is delayed from the moment of re-raise; the code delays from the follower's original timestamp).
- `CONFIG_ZMK_HID_SEPARATE_MOD_RELEASE_REPORT` "doesn't seem to work" (`corne.conf:48`): the code path exists (`hid_listener.c:69-78`); host-side behaviour is outside firmware tests.
- The R thumb 0 ms tap (Q3) contradicts the config's own note that 0 ms taps are unreliable on the M1 host (`adaptive_keys/combos.dtsi:20`); whether the host drops R occasionally is unobservable in native_posix.

## 14. Test sketches (T-numbers referenced above)

- **T1 isolated trigger**: press pos 0 (L), release 200 ms later. Expect `kp_pressed L` at `ts+16` (recipe: L has no 16 ms combo, so at `ts+11`), `kp_released L` +10, `layer_changed: layer 1 state 1` same ms as release, `state 0` exactly 100 ms later.
- **T2 adapted follower**: recipe events (d = 30). Expect `kp L` ↓ at 11, ↑ 21, layer 1 on 21, `kp G` ↓ at 41 (= 30+11), ↑ 51, layer 1 off at 51 (consumed, released on G ↑). Output L G.
- **T3 too-fast follower**: `PRESS(0,0,5) PRESS(0,1,50) RELEASE…`. Expect `kp L` ↓ 11, `kp X` ↓ 21 (queued behind L's tap), layer 1 on 21 → output L X (no G). **T3b**: d = 10 → either L G (queue timer first) or L X; record which.
- **T4 window end**: d = 110 and d = 120 with a combo-less follower. Expect G at 121 (adapted) for 110; X for 120 (layer off at 121 before delivery at 131).
- **T5 mod keycode keeps the layer**: add `&sk LSHIFT` at pos 8; `PRESS(0,0,30) PRESS(2,0,20) RELEASE(2,0,400) PRESS(0,1,50)…`. Expect no `layer 1 state 0` at 121; G (shifted) at ~511 instead of X.
- **T6 combo waits for its deadline**: `PRESS(0,2,5) PRESS(0,3,100) RELEASE…`. Expect `kp SPACE` ↓ at 16 (not 5). Then `PRESS(0,2,13) PRESS(0,3,…)` → SPACE at 13.
- **T7 R thumb 0 ms tap**: `PRESS(2,2,50) RELEASE(2,2,300)`. Expect `kp_pressed R` and `kp_released R` in the same ms (50), `layer 1` on at 50, no `queue wait 10ms` between them. **T7b**: `PRESS(2,2,20) PRESS(0,1,30) RELEASE(2,2,10) …` → expect R then X (not G).
- **T8 queue block**: add `moAndBuffer` + `htls` nodes verbatim, `&htls 3 LSHIFT` at pos 9; `PRESS(2,1,150) RELEASE(2,1,20) PRESS(0,0,50) RELEASE(0,0,300)`. Expect `kp L` ↓ at `T_rel + 260` (not `press+11`).
- **T9 replace macro**: add `replace_char_with_bigram_LB` verbatim on layer 1 pos 2 and `&ak 4 B` dummy target; press 0 then 2 at d = 30. Expect ⌫ ↓ at 41, L ↓ 51, B ↓ 71, B ↑ 81, layer B on 81.
- **T10 linwin combo shadowed**: hardware-config-only claim; test by adding `combo_x { layers = <0>; }` and `combo_y { layers = <0 1>; }` on the same keys, pressing them inside the AK window → y fires.
- **T11 layer 999**: `&ak 999 I` at a position; press/release. Expect `kp I` ↓/↑ 10 ms apart and **no** `layer_changed` line.
