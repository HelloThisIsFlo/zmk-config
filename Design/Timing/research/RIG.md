# RIG — shared native_posix test rigs for the AK-truth plan

> Status: **both rigs build and run**; 7 throwaway cases green (`run-test.sh` PASS after auto-accept), timestamped logs in `results/`.
> Everything below is observed in this session unless marked *predicted*.

## 🎯 Headline facts (read these first)

- **Mock timing = `[e0.ms+1] e0 [e0.ms+1] e1 [e1.ms+1] e2 … eN [eN.ms+1] exit`.** The first event's `ms` is applied **twice** (boot delay *and* gap after e0); every gap is `ms + 1`. CLAIMS T-01 forgot the doubling → its expected times from event 2 on are wrong (see §5).
- **Every relative timer fires at `intended + 1` ms**; combo `timestamp=` in the log prints the intended deadline, the line prefix shows execution (`timestamp=112` at `[.113]`).
- **Solo-key delivery = press + (longest candidate combo timeout) + 1**: hack-only key +12, 16-ms key +17, 18-ms key +19 (all observed).
- **`&ak` timeline on the real keymap (LM1 = T)**: HID↓ at +17, HID↑ + `layer 19 ON` at +28, `layer 19 OFF` at +129. Exactly as CLAIMS T-12(a) predicts.
- **Hack removal idioms both work**: R1 `/delete-node/ &combo_hack;` (log byte-identical to `_rig_R1_nohack`), R2 `/ { combos { /delete-node/ combo_ak_consistency_hack; }; };` (no label in the real config).
- **R2 coordinate mapping verified on all four mock rows** (LT2→M, LM1→T, LB2→L, RM1→A, LH1→sticky LSHIFT).

## 📂 Paths

| What | Path (host; container = `/workspaces/zmk/app/…`) |
|---|---|
| R1 template (hack ON) | `/Users/flo/Work/Private/Dev/Keyboard/zmk/app/tests/ak-truth/_rig_R1/` |
| R1 template (hack OFF) | `/Users/flo/Work/Private/Dev/Keyboard/zmk/app/tests/ak-truth/_rig_R1_nohack/` |
| R2 template (real keymap) | `/Users/flo/Work/Private/Dev/Keyboard/zmk/app/tests/ak-truth/_rig_R2/` |
| each template holds | `native_posix_64.keymap` (no `events` — **will not build as-is**), `native_posix_64.conf`, `events.patterns` |
| proof cases | `…/tests/ak-truth/T-01-r1`, `T-01-r1-full`, `T-01-r1-nohack`, `T-01-r1-delhack`, `T-01-r2`, `T-01-r2-map`, `T-01-r2-nohack` |
| build output | `/Users/flo/Work/Private/Dev/Keyboard/zmk/app/build/tests/ak-truth/<case>/` (`zephyr/zmk.exe`, `keycode_events_full.log` = prefix-stripped, `keycode_events.log` = filtered) |
| timestamped logs + snapshots | `/private/tmp/claude-501/-Users-flo-Work-Private-Dev-Keyboard-zmk-config/56bdead7-aa9e-4bbc-b13e-b1255ed79094/scratchpad/investigation/results/<case>.raw.log`, `<case>.snapshot` |
| timeline helper | `/private/tmp/claude-501/-Users-flo-Work-Private-Dev-Keyboard-zmk-config/56bdead7-aa9e-4bbc-b13e-b1255ed79094/scratchpad/investigation/tl.py` |

- Do not edit the three `_rig_*` directories. `cp -r` one into `tests/ak-truth/<case>/`, append your `&kscan { events = <…>; };` block (and any `/delete-node/`), run.
- A group run (`./run-test.sh tests/ak-truth`) will try to build the templates and report `FAILED … did not build` for them (no `events` property → `DT_INST_PROP_LEN` fails). Run cases individually.

## 🧭 Coordinate mapping

### R1 — `rows = <3>; columns = <4>;`, no transform → `position = row * 4 + col`

```
            col 0        col 1        col 2         col 3
row 0   pos 0 (0,0)   pos 1 (0,1)   pos 2 (0,2)   pos 3 (0,3)
row 1   pos 4 (1,0)   pos 5 (1,1)   pos 6 (1,2)   pos 7 (1,3)
row 2   pos 8 (2,0)   pos 9 (2,1)   pos 10 (2,2)  pos 11 (2,3)
```

`ZMK_MOCK_PRESS(p / 4, p % 4, ms)`. Verified: `(0,3)` → `position: 3`, `(0,2)` → `position: 2`.

### R2 — Flo's `five_column_transform` (`columns = <10>`, `zmk,physical-layout = &foostan_corne_5col_layout`)

```
 p <  30 :  ZMK_MOCK_PRESS(p / 10, p % 10 + 1, ms)       (col 1..10; col 0 unused)
 p 30..35:  ZMK_MOCK_PRESS(3, p - 27, ms)                 (LH2 LH1 LH0 = (3,3) (3,4) (3,5); RH0 RH1 RH2 = (3,6) (3,7) (3,8))
```

| key | pos | mock | key | pos | mock |
|---|---|---|---|---|---|
| LT4 | 0 | (0,1) | RT0 | 5 | (0,6) |
| LT3 | 1 | (0,2) | RT1 | 6 | (0,7) |
| LT2 | 2 | (0,3) | RT2 | 7 | (0,8) |
| LT1 | 3 | (0,4) | RT3 | 8 | (0,9) |
| LT0 | 4 | (0,5) | RT4 | 9 | (0,10) |
| LM4 | 10 | (1,1) | RM0 | 15 | (1,6) |
| LM3 | 11 | (1,2) | RM1 | 16 | (1,7) |
| LM2 | 12 | (1,3) | RM2 | 17 | (1,8) |
| LM1 | 13 | (1,4) | RM3 | 18 | (1,9) |
| LM0 | 14 | (1,5) | RM4 | 19 | (1,10) |
| LB4 | 20 | (2,1) | RB0 | 25 | (2,6) |
| LB3 | 21 | (2,2) | RB1 | 26 | (2,7) |
| LB2 | 22 | (2,3) | RB2 | 27 | (2,8) |
| LB1 | 23 | (2,4) | RB3 | 28 | (2,9) |
| LB0 | 24 | (2,5) | RB4 | 29 | (2,10) |
| LH2 | 30 | (3,3) | RH0 | 33 | (3,6) |
| LH1 | 31 | (3,4) | RH1 | 34 | (3,7) |
| LH0 | 32 | (3,5) | RH2 | 35 | (3,8) |

Verified by `T-01-r2-map` (one key per row): `(0,3)` → `position: 2` → M · `(1,4)` → `position: 13` → T · `(2,3)` → `position: 22` → L · `(1,7)` → `position: 16` → A · `(3,4)` → `position: 31` → hold-tap 31 → sticky LSHIFT (0xE1).

## 🔤 Keycode tables

HID usage (page 0x07): A 0x04 … Z 0x1D (`0x04 + letter index`), BSPC 0x2A, SPACE 0x2C, RET 0x28, LCTRL 0xE0, LSHIFT 0xE1.

### R1 — every binding

| pos | base (0) | akA (1) | akB (2) | akH (3) | mod (4) | nav (5) | combos containing pos → longest k |
|---|---|---|---|---|---|---|---|
| 0 | `&ak 1 A` 0x04 | – | `&bk P` 0x13 | `&bk U` 0x18 | – | – | R16 `<0 2>`, hack → 16 |
| 1 | `&ak 2 B` 0x05 | `&bk K` 0x0E | – | `&bk T` 0x17 | – | – | hack only → 11 |
| 2 | `&kp C` 0x06 | – | – | – | – | – | R16, hack → 16 |
| 3 | `&kp D` 0x07 | `&bk L` 0x0F | `&bk Q` 0x14 | – | – | – | hack only → 11 |
| 4 | `&kp E` 0x08 | `&bk N` 0x11 | `&bk R` 0x15 | – | – | – | S16 `<4 5>`, Q18 `<4 5 6>`, hack → 18 |
| 5 | `&kp F` 0x09 | – | – | – | `&htm LCTRL LCTRL` 0xE0 | – | S16, Q18, hack → 18 |
| 6 | `&kp G` 0x0A | – | – | – | – | – | Q18, V16 `<6 11>`, hack → 18 |
| 7 | `&ak 3 H` 0x0B | `&bk O` 0x12 | `&bk S` 0x16 | – | – | – | W30 `<7 8>`, hack → 30 |
| 8 | `&kp I` 0x0C | – | – | – | – | – | W30, hack → 30 |
| 9 | `&lk X Y` tap Y 0x1C / linger X 0x1B | – | – | – | – | – | hack only → 11 |
| 10 | `&blt_akR 5 0` tap → `&ak 3 H` 0x0B / hold `&mo 5` | – | – | – | – | – | hack only → 11 |
| 11 | `&kp J` 0x0D | `&bk M` 0x10 | – | – | – | – | V16, hack → 16 |

`–` = `&trans`. Combo outputs: R16 `&bk C` 0x06 · S16 `&bk V` 0x19 · Q18 `&bk W` 0x1A · W30 `&bk Z` 0x1D · V16 `&bk Y` 0x1C · hack `&none`. Tier combos are on layers 0–5 (= `l_all`); hack on 0–3 only (= `l_alpha_aks`, not mod/nav).

Behavior names as they appear in logs: `key_press` (`&kp`), `flo,behavior-adaptive-key` (`&ak`), `flo,behavior-buffered-key` (`&bk`), `flo,behavior-adaptive-key-sticky-layer` (`&aksl`), `lk`, `blt_akR`, `ak_R_macro`, `hold_tap_mod` (`&htm`), `hold_tap_layer_sticky_shift` (`&htls`), `sticky_key_mod` (`&skm`), `sticky_key_mod_shift` (`&skms`), `moAndBuffer`, `momentary_layer` (`&mo`).

### R2 — keys the plan uses (Naquadah alpha, layer 0)

| key | pos | mock | base binding | HID | follower bindings that matter | candidates on layer 0 → k → solo delivery |
|---|---|---|---|---|---|---|
| LT2 | 2 | (0,3) | `&ak 13 M` | 0x10 | l_akM: LT3 `&bk M`, LT0 `ak_B` (=`&ak 3 B`), LM1 `&bk N` | typeQ(16) typeZ(16) hack → **+17 observed** |
| LM1 | 13 | (1,4) | `&ak 19 T` | 0x17 | l_akT: LB3 `&bk T`, LB0 `TV_to_NV` | entr(16) hack → **+17 observed** |
| LM4 | 10 | (1,1) | `&ak 4 C` | 0x06 | l_akC: LT1 `CP_to_TP`, LB3 `&bk C` | hack only → +12 *predicted* |
| LT1 | 3 | (0,4) | `&ak 16 P` | 0x13 | l_akP: LT3 `&bk P`, LM4 `&bk T`, LM2 `&bk D`, LM0 `PB_to_NB`, LB3 `&bk L` | space(16) typeQ(16) hack → +17 *predicted* |
| LB2 | 22 | (2,3) | `&ak 12 L` | 0x0F | l_akL: LT4 `&bk G`, LB3 `&bk L` | esc2(16) magicCloseQuitCb(16) hack → **+17 observed** |
| LT4 | 0 | (0,1) | `&ak 23 X` | 0x1B | on l_akL → `&bk G` 0x0A | hack only → +12 *predicted* |
| LT0 | 4 | (0,5) | `&ak 11 K` | 0x0E | on l_akM → `ak_B` (B 0x05, then layer 3) | space(16) hack → +17 *predicted* |
| LB3 | 21 | (2,2) | `&ak 8 G` | 0x0A | on l_akT → `&bk T`; on l_akB → `&bk L` | magicCloseQuitCb(16) hack → +17 *predicted* |
| LM2 | 12 | (1,3) | `&ak 14 N` | 0x11 | – | wispr(16) hack → +17 (G §3 probe) |
| LM0 | 14 | (1,5) | `&ak 3 B` | 0x05 | – | entr(16) hack → +17 *predicted* |
| RM1 | 16 | (1,7) | `&ak 2 A` | 0x04 | – | entr2(16) bspc(16) delWord(18) capsWord(18) hack → **+19 observed** |
| LH1 | 31 | (3,4) | `&htls 26 LSHIFT` | tap → sticky 0xE1; hold → `moAndBuffer` (layer 26) | – | hack only → **+12 observed** (hold-tap created at +12) |

AK layer ids: A 2 · B 3 · C 4 · D 5 · E 6 · F 7 · G 8 · H 9 · hE 10 · K 11 · L 12 · M 13 · N 14 · O 15 · P 16 · R 17 · S 18 · T 19 · U 20 · V 21 · W 22 · X 23 · Y 24 · nav 25 · mod 26 · fn 27 · num 28 · numsym 29 · cfg 30 · nav_linwin 31 · (I/J/Q/Z = 999, no layer).

## ⏱️ T-01 observations (harness baseline)

### T-01-r1 — R1 with the whole `combos` node deleted; events `PRESS(0,3,100) RELEASE(0,3,10) PRESS(0,2,50) RELEASE(0,2,10)`

```
[00:00:00.000,000] <dbg> zmk: kscan_mock_schedule_next_event_0: delaying next keypress: 100
[00:00:00.101,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 0, col: 3, position: 3, pressed: true
[00:00:00.101,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x07 implicit_mods 0x00 explicit_mods 0x00
[00:00:00.101,000] <dbg> zmk: kscan_mock_schedule_next_event_0: delaying next keypress: 100
[00:00:00.202,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0x07 implicit_mods 0x00 explicit_mods 0x00
[00:00:00.202,000] <dbg> zmk: kscan_mock_schedule_next_event_0: delaying next keypress: 10
[00:00:00.213,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x06 implicit_mods 0x00 explicit_mods 0x00
[00:00:00.213,000] <dbg> zmk: kscan_mock_schedule_next_event_0: delaying next keypress: 50
[00:00:00.264,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0x06 implicit_mods 0x00 explicit_mods 0x00
[00:00:00.264,000] <dbg> zmk: kscan_mock_schedule_next_event_0: delaying next keypress: 10
[00:00:00.275,000] <dbg> zmk: kscan_mock_work_handler_0: ev 1 row 1 column 0 state 0
[00:00:00.275,000] <dbg> zmk: kscan_mock_schedule_next_event_0: Exiting
```

| event | CLAIMS T-01 expected | **observed** | why |
|---|---|---|---|
| D ↓ | `.101` | `[00:00:00.101,000]` | boot delay 100 + 1 ✓ |
| D ↑ | `.112` | `[00:00:00.202,000]` | **e0.ms (100) applied again** after e0, +1 |
| C ↓ | `.163` | `[00:00:00.213,000]` | 202 + 10 + 1 |
| C ↑ | `.174` | `[00:00:00.264,000]` | 213 + 50 + 1 |
| Exiting | `.185` | `[00:00:00.275,000]` | 264 + 10 + 1 |

- **Verdict:** "+1 per timer" ✓ and "mock gap = ms + 1" ✓, but CLAIMS' arithmetic omits that `events[0].msec` is *also* the gap after event 0 (`kscan_mock.c`: the handler calls `schedule_next_event` before incrementing `event_index`). Correct rule: `t(e0) = e0.ms + 1`, `t(e1) = t(e0) + e0.ms + 1`, `t(eN) = t(eN-1) + eN-1.ms + 1`, exit = `t(eN) + eN.ms + 1`.
- Practical consequence for every test: either give event 0 a small `ms` and accept the double gap, or put a throw-away dummy first… simplest: write event 0 with the gap you want between e0 and e1 and remember boot-to-e0 equals that same gap. `t` (first position event) = `e0.ms + 1` in absolute ms.
- The trailing `ev 1 row 1 column 0 state 0` line is the known one-past-the-array read (G §1); harmless.
- With `--no-rt`, output is byte-identical to the harness run (snapshot diff PASS after auto-accept).

### T-01-r1-full — same events, full R1 (hack + tiers)

```
[00:00:00.101,000] <dbg> zmk: position_state_down: combo: capturing position event 3
[00:00:00.113,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=112
[00:00:00.113,000] <dbg> zmk: release_pressed_keys: combo: releasing position event 3
[00:00:00.113,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x07 implicit_mods 0x00 explicit_mods 0x00
[00:00:00.202,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0x07 implicit_mods 0x00 explicit_mods 0x00
[00:00:00.213,000] <dbg> zmk: position_state_down: combo: capturing position event 2
[00:00:00.225,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=1 timestamp=224
[00:00:00.230,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=229
[00:00:00.230,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x06 implicit_mods 0x00 explicit_mods 0x00
[00:00:00.264,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0x06 implicit_mods 0x00 explicit_mods 0x00
```

- D (hack-only): delivered at **t+12** (`timestamp=112` printed, executed `[.113]`) ✓ CLAIMS R2 note "hack flush handler runs at t+12 with timestamp=t+11".
- C (R16 + hack): hack rung at `[.225]` (`remaining_candidates=1`), R16 rung at `[.230]` → HID at **t+17** ✓ "longest candidate + 1".
- Releases pass straight through (`.202`, `.264`): the combo layer does not hold key-ups once the press was released.

### T-01-r1-nohack / T-01-r1-delhack — tiers only

- D at `[.101]` (no candidate at all → immediate), C captured `[.213]`, `remaining_candidates=0 timestamp=229` at `[.230]`, HID C `[.230]`.
- `T-01-r1-delhack` (= `_rig_R1` + `/delete-node/ &combo_hack;`) produced a raw log with the **same md5 as `T-01-r1-nohack`** (`848cbcfd351b6ec4dc0b6b4ad00ddb83`). Either idiom is fine.

### T-01-r2 — real keymap, LM1 alone: `PRESS(1,4,100) RELEASE(1,4,300)`

```
[00:00:00.101,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 1, col: 4, position: 13, pressed: true
[00:00:00.101,000] <dbg> zmk: position_state_down: combo: capturing position event 13
[00:00:00.113,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=1 timestamp=112
[00:00:00.118,000] <dbg> zmk: filter_timed_out_candidates: after filtering out timed out combo candidates: remaining_candidates=0 timestamp=117
[00:00:00.118,000] <dbg> zmk: release_pressed_keys: combo: releasing position event 13
[00:00:00.118,000] <dbg> zmk: zmk_keymap_apply_position_state: layer_id: 0 position: 13, binding name: flo,behavior-adaptive-key
[00:00:00.118,000] <dbg> zmk: behavior_queue_process_next: Invoking key_press: 0x70017 0x00
[00:00:00.118,000] <dbg> zmk: hid_listener_keycode_pressed: usage_page 0x07 keycode 0x17 implicit_mods 0x00 explicit_mods 0x00
[00:00:00.118,000] <dbg> zmk: behavior_queue_process_next: Processing next queued behavior in 10ms
[00:00:00.129,000] <dbg> zmk: hid_listener_keycode_released: usage_page 0x07 keycode 0x17 implicit_mods 0x00 explicit_mods 0x00
[00:00:00.129,000] <dbg> zmk: behavior_queue_process_next: Invoking flo,behavior-adaptive-key-sticky-layer: 0x13 0x00
[00:00:00.129,000] <dbg> zmk: on_sticky_key_binding_pressed: 0 new sticky_key
[00:00:00.129,000] <dbg> zmk: set_layer_state: layer_changed: layer 19 state 1
[00:00:00.202,000] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: Row: 1, col: 4, position: 13, pressed: false
[00:00:00.230,000] <dbg> zmk: set_layer_state: layer_changed: layer 19 state 0
[00:00:00.503,000] <dbg> zmk: kscan_mock_schedule_next_event_0: Exiting
```

| prediction (task / CLAIMS T-12a) | observed | |
|---|---|---|
| `kp T` at t+17 | `[00:00:00.118,000]` = 101 + 17 | ✓ |
| `layer 19 state 1` at t+28 | `[00:00:00.129,000]` = 101 + 28 | ✓ |
| `layer 19 state 0` at t+129 | `[00:00:00.230,000]` = 101 + 129 | ✓ |

- Also visible: `kp_released 0x17` at `[.129]` (same ms as layer ON, `queue wait 10ms` between ↓ and ↑), the sticky key lives at `position 0` (behavior-queue artefact, G headline), the physical release at `[.202]` runs the `&ak` release branch with `count: 0` → no HID.
- Noise unique to R2 (from `CONFIG_ZMK_HID_SEPARATE_MOD_RELEASE_REPORT=y`): `<err> zmk: Failed to send key report for the released keycode (-95)` after every key-up, plus `<err> zmk: USB endpoint is not supported` on every report in both rigs. Ignore.

### T-01-r2-nohack — same events, `combo_ak_consistency_hack` deleted by name

- `[00:00:00.118,000] … remaining_candidates=0 timestamp=117` is the **only** filter line (the `timestamp=112` rung is gone); T still at `[.118]`, layer 19 ON `[.129]`, OFF `[.230]`. Removing the hack changes nothing for a key that has a real 16-ms combo — as MODEL predicts.

### T-01-r2-map — mapping probe (one key per row, 300 ms apart)

```
[00:00:00.051,000] … Row: 0, col: 3, position: 2, pressed: true
[00:00:00.068,000] … hid_listener_keycode_pressed: usage_page 0x07 keycode 0x10 …      M   (+17; remaining 2 → 0)
[00:00:00.079,000] … set_layer_state: layer_changed: layer 13 state 1                    l_akM (+28), off [.180] (+129)
[00:00:00.403,000] … Row: 1, col: 4, position: 13, pressed: true
[00:00:00.420,000] … hid_listener_keycode_pressed: usage_page 0x07 keycode 0x17 …      T   (+17)
[00:00:00.431,000] … layer_changed: layer 19 state 1                                     off [.532]
[00:00:00.755,000] … Row: 2, col: 3, position: 22, pressed: true
[00:00:00.772,000] … hid_listener_keycode_pressed: usage_page 0x07 keycode 0x0F …      L   (+17; remaining 2 → 0)
[00:00:00.783,000] … layer_changed: layer 12 state 1                                     off [.884]
[00:00:01.107,000] … Row: 1, col: 7, position: 16, pressed: true
[00:00:01.126,000] … hid_listener_keycode_pressed: usage_page 0x07 keycode 0x04 …      A   (+19; remaining 4 → 2 → 0, 18-ms tier)
[00:00:01.137,000] … layer_changed: layer 2 state 1                                      off [1.238]
[00:00:01.459,000] … Row: 3, col: 4, position: 31, pressed: true
[00:00:01.471,000] … on_hold_tap_binding_pressed: 31 new undecided hold_tap              (+12, hack-only key)
[00:00:01.510,000] … decide_hold_tap: 31 decided tap (hold-preferred decision moment key-up)
[00:00:01.510,000] … on_sticky_key_binding_pressed: 31 new sticky_key
[00:00:01.510,000] … hid_listener_keycode_pressed: usage_page 0x07 keycode 0xE1 …      LSHIFT (sticky)
```

- Note `31 new sticky_key` carries the real position: the hold-tap invokes `&skms` directly, not via the behavior queue. Only queue-driven behaviors (`&ak` → `&aksl`) show `position 0`.

## 🛠️ Exact command lines

```sh
# 1. make a case from a template (never edit _rig_* in place)
cp -r /Users/flo/Work/Private/Dev/Keyboard/zmk/app/tests/ak-truth/_rig_R1 /Users/flo/Work/Private/Dev/Keyboard/zmk/app/tests/ak-truth/T-XX-something
cat >> /Users/flo/Work/Private/Dev/Keyboard/zmk/app/tests/ak-truth/T-XX-something/native_posix_64.keymap <<'EOF'

&kscan {
    events = <
        ZMK_MOCK_PRESS(0,0,30)
        ZMK_MOCK_PRESS(0,1,50)
        ZMK_MOCK_RELEASE(0,0,10)
        ZMK_MOCK_RELEASE(0,1,300)
    >;
};
EOF

# optional variants, appended before the &kscan block:
#   R1 hack off ............ /delete-node/ &combo_hack;
#   R1 no combos at all .... /delete-node/ &combos;
#   R2 hack off ............ / { combos { /delete-node/ combo_ak_consistency_hack; }; };
#   R2 own transform etc. .. any further overlay text is fine after the #include

# 2. build + run + create snapshot (first run of a case)
docker exec -e ZMK_TESTS_AUTO_ACCEPT=1 -w /workspaces/zmk/app zmk-devcontainer ./run-test.sh tests/ak-truth/T-XX-something
#    later runs (assert against the snapshot):
docker exec -w /workspaces/zmk/app zmk-devcontainer ./run-test.sh tests/ak-truth/T-XX-something

# 3. timestamped log (the evidence) — after any build
docker exec -w /workspaces/zmk/app zmk-devcontainer ./build/tests/ak-truth/T-XX-something/zephyr/zmk.exe --no-rt \
  > /private/tmp/claude-501/-Users-flo-Work-Private-Dev-Keyboard-zmk-config/56bdead7-aa9e-4bbc-b13e-b1255ed79094/scratchpad/investigation/results/T-XX-something.raw.log 2>&1

# 4. compact timeline
python3 /private/tmp/claude-501/-Users-flo-Work-Private-Dev-Keyboard-zmk-config/56bdead7-aa9e-4bbc-b13e-b1255ed79094/scratchpad/investigation/tl.py \
  /private/tmp/claude-501/-Users-flo-Work-Private-Dev-Keyboard-zmk-config/56bdead7-aa9e-4bbc-b13e-b1255ed79094/scratchpad/investigation/results/T-XX-something.raw.log
```

- Path after `run-test.sh` must be relative to `app/` (`tests/ak-truth/<case>`); the build dir is `build/tests/ak-truth/<case>`.
- Cold build ≈ 6–10 s, rebuild ≈ 4–5 s; concurrent cases in separate directories are fine.
- `run-test.sh` output on a new case: `diff: … keycode_events.snapshot: No such file or directory` → `Auto-accepting failure` → `PASS`. That PASS only means "built and ran"; read the raw log.
- Snapshot missing / build failed → `FAILED: tests/ak-truth/<case> did not build`; the CMake/DTC error is swallowed (`> /dev/null 2>&1`). To see it: `docker exec -w /workspaces/zmk/app zmk-devcontainer west build -d build/tests/ak-truth/<case> -b native_posix_64 -- -DCONFIG_ASSERT=y -DZMK_CONFIG=/workspaces/zmk/app/tests/ak-truth/<case>`.
- Last event's `ms` bounds the observation window: 100-ms AK window needs ≥ 130 after the last key-up (use 300); a 1500-ms sticky mod needs ≥ 1600.

## 📜 Reading the `--no-rt` log

- Prefix: `[hh:mm:ss.mmm,uuu] <lvl> zmk: <function>: <message>`. `uuu` is always `000` (1 ms tick). `<lvl>` is `dbg` for everything that matters; `<err>` lines are transport noise; `<inf> zmk: Welcome to ZMK!` marks boot.
- Time zero: boot. First position event at `e0.ms + 1`. Take `t` = first `Row: … pressed: true` line (that is what `tl.py` does).
- Line order == execution order (`CONFIG_LOG_MODE_IMMEDIATE`). Same-ms lines are an ordering assertion.

| you want | grep for | line |
|---|---|---|
| physical press/release (`t`) | `Row:` | `zmk_physical_layouts_kscan_process_msgq: Row: 1, col: 4, position: 13, pressed: true` |
| combo captured the key | `capturing position event` | `position_state_down: combo: capturing position event 13` |
| combo rung expired (timer) or re-evaluated (key) | `remaining_candidates` | `filter_timed_out_candidates: … remaining_candidates=1 timestamp=112` (timestamp = intended deadline; prefix = execution, +1 when timer-driven) |
| key handed to the keymap | `releasing position event` / `reraising position event` | `release_pressed_keys: combo: releasing position event 13` |
| **delivery** to a binding (which layer resolved it) | `layer_id:` | `zmk_keymap_apply_position_state: layer_id: 0 position: 13, binding name: flo,behavior-adaptive-key` |
| **HID ↓ / ↑ (ground truth)** | `hid_listener_keycode_` | `hid_listener_keycode_pressed: usage_page 0x07 keycode 0x17 implicit_mods 0x00 explicit_mods 0x00` |
| **layer on/off** | `layer_changed` | `set_layer_state: layer_changed: layer 19 state 1` |
| behavior-queue step | `Invoking` / `Processing next queued behavior` | `behavior_queue_process_next: Invoking key_press: 0x70017 0x00`, `… in 10ms` |
| macro start (`&ak`, `&bk`, …) | `Iterating macro bindings` | `queue_macro: Iterating macro bindings - starting: 0, count: 7` (release branch: `starting: 7, count: 0`) |
| sticky armed / consumed | `new sticky_key` / `Act like a normal key` | `on_sticky_key_binding_pressed: 0 new sticky_key` |
| hold-tap life | `new undecided hold_tap`, `decided`, `capturing`, `Releasing key position event` | `decide_hold_tap: 31 decided tap (hold-preferred decision moment key-up)` |
| mock event / end | `kscan_mock_work_handler_0: ev` / `Exiting` | `kscan_mock_schedule_next_event_0: Exiting` |

- Ignore: `USB endpoint is not supported`, `Failed to send key report for the released keycode (-95)` (R2 only), `Modifiers set to 0x00`, `zmk_endpoints_send_report`, `Listener captured/handled the event`, `tap_dance_position_state_changed_listener: Ignore upstroke` (R2, from `togMacPc`), `bubble (no undecided hold_tap active)` (one per position event).
- `events.patterns` (shared by all three rigs) keeps: `pos …`, `keymap …`, `kp_pressed/kp_released …`, `layer_changed …`, `after filtering …`, `capturing/releasing/reraising position event N`, `ht …` (hold-tap, minus the no-op bubble line), `sk …`, `macro …`, `queue invoke …`, `queue wait Nms`, `Exiting`. The snapshot has no timestamps; ordering only.

## 🐍 `tl.py`

```
python3 tl.py <raw.log> [--all] [--abs] [--t0 MS] [--grep REGEX]
```

- Prints `+rel  abs  event`; `rel` from the first `Row: … pressed: true` (override with `--t0`), `--abs` drops the relative column, `--all` shows every log line, `--grep` filters the event text.
- Event vocabulary: `POS ↓/↑ <pos> (mock r,c)`, `combo capturing/releasing/reraising …`, `combo filter: remaining=N (timestamp=T)`, `deliver pos P on layer L → <behavior>`, `HID ↓/↑ 0xNN <name>[ mods …]`, `LAYER N ON/OFF`, `mo ↓/↑ …`, `queue invoke …`, `queue wait Nms`, `macro …`, `sk …`, `ht …`, `mock press/release (r,c)`, `EXIT`.
- Tested on `results/T-01-r1.raw.log` (18 events, D↓ +0, D↑ +101, C↓ +112, C↑ +163, EXIT +174) and on the R2 logs (T↓ +17, T↑/layer ON +28, layer OFF +129).
- Needs the raw exe output; `keycode_events_full.log` has no prefixes and is rejected with a message.

## ⚠️ Deviations from CLAIMS / choices made (real config wins)

- **T-01 expected timestamps corrected** (above): only D↓ `.101` was right; the doubled first delay shifts everything else by +90 ms. The offsets themselves (`+1` per timer, gap `= ms + 1`) hold.
- **Hack combo defined last** in R1 (CLAIMS lists it first): the real `combos.dtsi` include order puts it after every other combo; `combo.c` sorts candidates by key count anyway, so it is always the last candidate either way.
- **Tier-combo `layers`**: CLAIMS does not say; real `COMBO_ANY_*` use `l_all` → R1 uses `<0 1 2 3 4 5>`. Hack stays on `<0 1 2 3>` (= `l_alpha_aks`, not mod/nav) as CLAIMS says.
- **`label` strings kept** on `ak`, `bk`, `aksl`, `lk` exactly as in the real config, so R1 logs name behaviors the same way R2 does (`flo,behavior-adaptive-key`, …).
- **`ak_R_macro`**: real = `<&ak l_akR R>`, D-config §12 = `<&ak 1 R>`, CLAIMS R1 = `<&ak 3 H>` → rig uses CLAIMS (`3 H`, the thumb shares layer akH) since letter/layer are synthetic anyway.
- **`moAndBuffer`** hard-codes `&mo 4` (real hard-codes `&mo l_mod`; the one-param is unused, as in the real macro).
- **`CONFIG_ZMK_HID_SEPARATE_MOD_RELEASE_REPORT=y`** is in the real firmware and in R2's conf; CLAIMS' R1 conf list omits it → left commented in `_rig_R1/native_posix_64.conf`. Effect on logs: the `-95` error line after key-ups (R2 only). Enable in a case copy if a test compares HID report order around modifier releases.
- **R2 transforms** copied verbatim from `app/boards/shields/corne/corne.dtsi`; both Corne layouts stay present (`ZMK_KEYMAP_LEN` = 42, 36-binding layers zero-padded, no runtime warning — same as G §3).
- **`nav` layer in R1 is all `&trans`**, `mod` has only `&htm LCTRL LCTRL` at pos 5 (CLAIMS). Tests that need `&mo 4` on a key (T-19) or `&htls 4 LSHIFT` on pos 10 (T-17/18) or `&kp LSHIFT` on pos 11 (T-20) edit their own copy.
