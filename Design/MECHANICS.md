# Keyboard Mechanics

> Technical reference for how the keyboard systems work under the hood.
> Organized by topic. This is a living document -- refined as patterns evolve.
> For implementation recipes ("I want to add X"), see [COOKBOOK.md](COOKBOOK.md).
>
> Last refined: 2026-11-04
>
> Millisecond timing is proven in [`Timing/`](Timing/README.md) (mechanism: [`Timing/MODEL.md`](Timing/MODEL.md), numbers: [`Timing/FACTS.md`](Timing/FACTS.md)); where this file and those differ, they win. Evidence tags: 🧪 proven by test · 📜 proven by source · 🔮 predicted on hardware · 🧮 inferred · ⚖️ tie, undetermined on the board.

## Lineage

The technical foundation draws from Alan Reiser's [Hands Down](https://sites.google.com/alanreiser.com/handsdown) project, which pioneered Adaptive Keys and linger keys for ZMK. The concepts were imported in Sep 2023 from Moutis' Hands Down ZMK derivative. Everything documented below -- the layer-per-AK architecture, the buffered key system, the timing web, the preprocessor metaprogramming, the orchestrator pattern -- was built from scratch on top of those concepts.

## Adaptive Keys -- The Core Innovation

_Lineage: The concept of detecting key sequences and replacing output originated in Hands Down. The implementation below -- layer-per-AK architecture, `&aksl`, the consistency hack, the timing constants -- is entirely custom._

The layout is designed around AKs. Without them, it's unusable. Each AK gets its own dedicated layer.

_**Deep dives:** [ak-deepdive.md](ak-deepdive.md) covers the full AK mechanism. [ak-combo-hack.md](ak-combo-hack.md) covers the consistency hack. [`Timing/`](Timing/README.md) holds the proven timing model._

**How it works (brief):** Each adaptive key on the alpha layer uses `ak_X` (= `&ak l_akX X`), which types the character and, 10ms later, activates the key's AK layer via `&aksl` for 100ms (counted from layer ON, not from the press). The next key that reaches the keymap while the layer is on hits a replacement binding on the AK layer. For the full mechanism -- chaining, two replacement types, the `___X____` convention, and the `&bk` consistency role -- see [ak-deepdive.md](ak-deepdive.md).

**`REPLACE_CHAR_WITH_BIGRAM(A, B)`** -- the replacement mechanism. Steps:

1. Backspace (delete the first key already output)
2. Type BIGRAM_0 (first char of replacement)
3. Release both LSHFT and RSHFT (prevents unintended case changes)
4. Tap `ak_##BIGRAM_1` (second char, through the AK behavior so it can chain)

In the behaviour queue that is 8 outer + 4 nested items, and it leaves a short dead window with no AK layer on (see *Buffered Behaviors*).

**The AK Consistency Hack.** A combo on all 36 keys with timeout `hold_key_event_delay` (11ms) and a `&none` binding: it never fires. Its only effect is that every press on layers 0–24 has a combo candidate, so the combo engine holds it for its longest live combo (11ms on the 8 hack-only keys X, C, F, RT0 and the thumbs LH2 LH1 LH0 RH0; 16ms on most; 18ms on A E I H), unless a key-up or a press that shares none of its combos releases it earlier. The gap it targets: `&ak` types its letter when the key is delivered and turns the AK layer on 10ms later (`ak_tap_time`), so a follower delivered inside those 10ms lands on the base layer. What it buys is a trade (🧪 T-02, T-04, T-23; board bands 🔮):

- **Follower ≥ 11ms after its trigger, sharing no real combo with it (45 pairs):** it reaches the keymap after its own hold (≥ 11ms from its own press), which ends after the trigger's layer is on → adapted, up to the window edge (~105–115ms). This rescues the 11 pairs whose follower is a hack-only key; without the hack they miss up to 25ms.
- **Follower ≤ 9ms after:** both keys share the hack and leave the combo engine together at the trigger's 11ms mark; ZMK's quick-tap check sends the follower straight to the keymap, on base. M then T 5ms apart types "mt", not "mn". At exactly 10ms the board is predicted to stall the follower until your next key-up or a later press (a press within 10ms of the follower joins the stall instead), then usually adapt late. This costs the 34 pairs that adapt at every gap without the hack.
- **Trigger and follower share a real combo (6 pairs):** fragile to 14–16ms whatever the hack does (L→G, H→E); M↔W and D↔V are themselves 2-key combos and type Z / Tab on any roll under 16ms (D↔V 🧮, not run).

There is no "1ms margin that makes the whole system reliable": the 11 > 10 margin only exists for followers pressed ≥ 11ms behind their trigger. Full account: [ak-combo-hack.md](ak-combo-hack.md); proof: [`Timing/`](Timing/README.md).

**Layer scoping.** The AK consistency hack combo uses `l_alpha_aks` (alpha + all AK layers, layers 0–24). AKs can chain but don't trigger from utility layers, with one exception: a `&trans` cell falls through to the alpha `ak_X` below it and still runs it (types X, arms `l_akX`), on a utility layer just as on an AK layer (📜 `keymap.c:658-679`; 🧪 on an AK layer, RVB-pin-akfollower). The armed `l_akX` sits below every utility layer, so the next key adapts only where the utility layer's own cell is `&trans` too 📜.

**Disabled AKs.** Some AK layers are disabled by setting them to `999` (e.g., l_akI, l_akJ, l_akQ, l_akZ). Frees up layer IDs while keeping combo definitions intact.

## Buffered Behaviors -- `&bk`, `&bsk`, `&bm`

_Lineage: Invented in Sep 2023 to solve timing race conditions in the Hands Down AK system. Not present in the original Hands Down implementation._

**`&bk` (Buffered Key):** A `behavior-macro-one-param` that wraps `&kp` with `tap-ms = 10` (`TEMP_macro_tap_time`) and `wait-ms = 0`. Being a macro, its press and release go through ZMK's behaviour queue instead of straight to HID.

**Why the queue matters: ordering.** Everything after a key's timestamp runs on one thread, and all macros (`&ak`, `&bk`, replace macros, `TYPING_MACRO`s) share a single FIFO behaviour queue. An `&bk` letter therefore waits behind the in-flight `&ak` letter and its AK-layer activation, and comes out in typing order. A raw `&kp` never enters the queue: it reaches HID at delivery and overtakes queued output 🧪 T-21-h. The order is FIFO per queued item, not strict across nesting: a macro nested inside another (the `ak_Y` at the end of a replace macro) adds its steps only when its parent's item runs, so a buffered key delivered before then is typed before them 🧪 T-21-c. Originally created as `&bkp` in Sep 2023 for these out-of-order races.

**Dropped keys: unverified.** The other original rationale, that the 10ms tap stops keys from being dropped, is a host-side claim. The native tests have no host, so it is neither proven nor refuted.

**Dead window after a replace macro.** `REPLACE_CHAR_WITH_BIGRAM(X, Y)` runs 8 outer + 4 nested queue items. With F = the replace key's delivery: ⌫ at F (it consumes the old AK layer), X at F+10, Y at F+30, `l_akY` ON at F+40. Between F+10 and F+40 no AK layer is on, so a key delivered in that window resolves on the base layer; one delivered before F+10 still sees the old AK layer. Example: C, then P 20ms later, then N 25ms after P types "tpn", not "tpd" (🧪 T-21-a, RVA-ex33-cpn; both ends ⚖️ on the board).

**`&bsk` (Buffered Sticky Key):** Wraps `&sk` with `macro_press` + `macro_pause_for_release` + `macro_release`. Holds the sticky key active until the physical key is released.

**`&bm` (Buffered Mod):** For modifiers in macros. Uses `macro_press`/`macro_release` with a pause to hold the modifier across multiple key events.

**When to use `&kp` vs `&bk`:** Use `&bk` in normal typing flow (AK layers, alpha bindings, combo outputs). Use `&kp` when you need a key to actually be **held** -- example: `lk_wispr` uses `&kp` on the hold side so the Globe key stays pressed while the combo is held. `&bk` would tap-and-release immediately, which is wrong for hold behaviors.

## Linger Keys -- Tap vs Hold

_Lineage: The concept of tap-vs-hold character variants comes from Hands Down. The `LK` macro, the preprocessor generation, and the `&kp` hold pattern are custom._

Linger keys are `zmk,behavior-hold-tap` with `tap-preferred` flavor and `tapping-term-ms = linger_term` (100ms).

**Timing.** The 100ms term counts from the finger press (the key's original timestamp), not from when the combo engine hands the key over (16ms later on most linger positions, 11ms on RT0) 🧪 T-15-c. Keys pressed while a linger key is undecided don't decide it: they wait and are typed after its tap or linger output 🧪 T-15-d/e/f. **Forced tap:** a linger key pressed ≤ 9ms after an adaptive letter is decided TAP at that letter's delivery and can never linger, however long it is held (🔮 board band; native ≤ 10ms 🧪 T-16-a, S-A_RT2-d10). When the letter and the linger key form a 2-key combo (A→RM0 `entr2`, U→RB0 `magicBracketsL`), that combo is predicted to fire instead 🧮.

**The `LK` macro:**

```c
#define LK(NAME, TAP_BINDING, LINGER_BINDING) \
lk_##NAME: lk_##NAME { \
    bindings = <LINGER_BINDING>, <TAP_BINDING>; \  // NOTE: reversed!
};
```

**Critical subtlety:** The macro takes `(TAP, LINGER)` but ZMK hold-tap expects `<HOLD, TAP>`. The macro reverses them internally. Forgetting this would swap behaviors.

**Two patterns:**

- **Standard** (`&bk` / `&bk`): Both sides tap a key. Used for character variants (e.g., `sqtDqt`: tap = single quote, linger = double quote).
- **Hold pattern** (`&kp` / `&bk`): Hold side actually holds the key. Used for `lk_wispr` (tap = Opt+R, hold = Globe key held for transient dictation). This is the only linger key using this pattern.

**Live linger keys** (NAQUADAH, from source; tap · linger):

- Alpha: RT0 `&MagicSlash` (`/` · `~/`; shifted `#` · `~/.`), RT1 `dotcol` (`.` · `:`), RT2 `equalDash` (`=` · `-`), RT4 `sqtDqt` (`'` · `"`), RM0 `comsemi` (`,` · `;`), RB0 `&MagicUnder` (`_` · `|`; shifted `*` · `\`)
- Combos: `tab` (Tab · ⌘Tab), `magicCloseQuitCb` (close tab · quit app), `wispr` (Opt+R · Globe held), `typeGrav` (`` ` `` · code block), `magicBracketsL`/`R` (`(` · `[` and `)` · `]`; shifted `<` · `{` and `>` · `}`)
- Windows layer: `tab_linwin` (Tab · Alt+Tab), `magicCloseQuitCb_linwin`; nav layers: `magicSwitchSpaceL`/`R`
- Defined but bound nowhere that compiles: `lk_qu`, `lk_th`/`lk_sh`/`lk_gh` (their combos sit in the commented-out `h_digraphs/combos.dtsi`), `magicArrowL`/`R` (combos commented out), `lk_repeat`, and the accent/pair hold-taps under "UNUSED"

## Combo System -- Two Live Timeout Tiers

_Lineage: Basic combo use comes from Hands Down. The tiered timeout system, layer scoping macros, and preprocessor generation are custom._

All combos are generated by preprocessor macros expanding `COMBO_LAY_BASE(LAYERS, NAME, BINDINGS, KEYPOS, TIMEOUT)`.

**Timeout tiers:**

| Tier | Timeout | Use case |
|------|---------|----------|
| Adjacent | 16ms | Keys physically next to each other, same hand. Extremely tight -- virtually no misfires. 22 combos compiled 📜. |
| Non-adjacent | 18ms | Same hand, keys further apart. 2ms more for the wider finger spread. 5 combos compiled (`delWord`, `capsWord`, `delWordTrans` and variants) 📜. |
| Two-hand | 30ms | Defined (`my_combo_timeout_two_hnds`) but **no consumers**: its only users, the pronoun combos (`COMBO_LAY_TWO_HAND`), are commented out in `layout.dtsi` 📜. |

**Timing rules** (🧪 T-22, T-09, S-M_LT3-*, RVB-bspc-*, ARB-F2):

- **Acceptance:** a combo fires iff its keys' timestamps are at most T − 1 apart (16ms tier: gaps 0–15 in, 16 out).
- **Hold:** a key waits for its longest live combo before it reaches the keymap (16ms on most keys, 18ms on A E I H, 11ms -- the hack -- on the 8 hack-only keys). A combo key pressed too late (gap ≥ T) starts its own wait.
- **Under the hack**, a 2-key combo completed within 11ms that is the only real combo left fires at its own deadline, not at completion: M+W 5ms apart gives Z at t+16. Completed between 11ms and T − 1 (same condition), it fires at the completing press.
- **`bspc` / `del` always fire at t+18** (or at your next key event), hack or not: `delWord` / `capsWord` (18ms) on the same keys stay alive.
- **The hack is a hold, not a tier:** it never fires and never shortens or splits other combos.
- **Out-of-order 3-key combos can stall:** RM1 then RM3 12ms later, without RM2, types nothing until your next key press or release, then "a" and "i".

**Layer scoping:**

- `COMBO_ANY_*` -- Active on all layers (`l_all`): space, enter (`entr`, `entr2`), tab, `esc2`, `magicCloseQuitCb`, settings. Backspace is **not** one of them: `bspc`, `del` and `delWord` are layer-scoped to `l_alpha_aks l_nav l_num l_nav_linwin l_numsym` (layers 0–25, 28, 29, 31), so they are absent on `l_mod`, fn and cfg.
- `COMBO_LAY_*` -- Active on specific layers. The AK consistency hack combo uses `l_alpha_aks`. Some UI combos are alpha-only to avoid conflicts with transposed keys on other layers.

**Interaction with AKs:** The AK consistency hack uses a combo (see [ak-combo-hack.md](ak-combo-hack.md)). `CONFIG_ZMK_COMBO_MAX_COMBOS_PER_KEY=30` and `CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO=36` are tuned for this. Upstream ZMK v0.3.0+ silently drops combos with 20 or more keys, so there the hack does not exist and the keyboard behaves as hack off 📜.

## Callum-Style Mods

_Lineage: One-shot mod concept from Callum's layout. The `moAndBuffer` macro, `skm`/`htls` behaviors, and timing tuning are custom._

Replaced Home Row Mods in Sep 2024.

**`skm` (sticky key mod):** A `behavior-sticky-key` with `ignore-modifiers` and `release-after-ms = 1500`. Tap to activate a one-shot mod; it expires 1500ms after the key **press**, not after the tap 🧪 T-17-b2, T-19-d. `ignore-modifiers` allows stacking -- tap Shift, tap Ctrl, next key gets both.

**`htm` (hold-tap mod):** The mod keys on `l_mod` (Ctrl, Alt, Gui, Shift on each home row) are `&htm` hold-taps, not bare `skm` taps: tap-preferred, 130ms term (`action_mod_tapping_term`), `hold-while-undecided`. The modifier goes down when the key is **delivered** (after any `l_mod` combo hold), and a tap converts it to an `skm` sticky mod 🧪 T-19-a.

**`htls` (hold-tap layer sticky):** The main thumb key behavior (LH1), hold-preferred with a 90ms term (`action_lay_tapping_term`). Hold activates the mod layer via `moAndBuffer`: at 90ms when held alone, or at once when any other key is pressed while it is undecided. Tap gives a sticky Shift via `skms` **only when nothing else was pressed**; any interrupting key makes it a hold 🧪 T-17-a/c. **Forced tap:** LH1 pressed ≤ 9ms after an adaptive letter is decided TAP at that letter's delivery: a sticky Shift, never `l_mod`, however long the thumb is held (🔮 board band; native 🧪 RVA-htls-forcedtap-d5).

**`moAndBuffer`:** A macro that presses `&mo l_mod`, pauses for release, waits `action_mod_tapping_term` (130ms), then releases. The buffer keeps `l_mod` on after the thumb lifts, so a mod key pressed just before the release still resolves on `l_mod`. Counted from the thumb **release** R: `l_mod` turns off at R+130, and the behaviour queue stays parked until R+260. The first queued letter (`&ak`, `&bk`, macros) delivered in (R, R+260) prints at R+260, then one per 10ms; raw `&kp` is not parked; letters typed during the park don't adapt to each other 🧪 T-18-a, T-18-c, RVB-park-two. A sticky Shift armed before the release survives the park and shifts the late letter 🧪 T-18-f.

**The ordering rules:** order decides the outcome, as long as each mod key reaches the keymap before R+130:
- Correct: Mod Layer Press → Mod 1 → Mod 2 → Mod Layer Release
- Correct: Mod Layer Press → Mod 1 → Mod 2 press → Mod Layer Release → Mod 2 release
- Incorrect: Mod Layer Press → Mod 1 → Mod Layer Release → Mod 2 after R+130 (too late -- layer gone)

**Delivery, not press, counts.** A mod key resolves on `l_mod` only if it is delivered before R+130. Ctrl, Alt and Gui sit in no `l_mod` combo, so they are delivered at the press and keep the full 130ms 🧮. The ⌘ keys on `l_mod` that sit in any-layer combos are held 16ms and lose the buffer's last 16ms 🧮.

**The Shift trap (LM1 / RM1).** Shift sits in the Enter combos (`entr` LM1+LM0, `entr2` RM0+RM1), which are live on `l_mod`, so Shift goes down 16ms after its press (or at its key-up, if sooner) 🧪 T-17-a4, RVA-callum-relaxed180. A Shift pressed in the buffer's last ~16ms and still held at R+130 is delivered after the layer is off and resolves on base as the letter under it: "t" (LM1) or "a" (RM1), parked to R+260 (capitalised only if an earlier sticky Shift is still pending). A quick Shift tap released before R+130 is delivered at its key-up and stays Shift 🧪 T-18-g, RVA-callum-close245, T-18-f.

**Home row mods still exist** (`hml`/`hmr`), bound only on the fn layer (`layers_C_extra.dtsi:71`): `behavior-hold-tap` with `hold-trigger-key-positions` for cross-hand activation. Uses `&bm` (buffered mod) for hold, `&bk` for tap. The variants for S, C, N, T, E, A, M (`hml_S` … `hmr_M`) that tap the AK macro instead of plain `&bk` are defined but bound nowhere that compiles for NAQUADAH 📜.

## Mod Morphs -- Conditional Behavior

`zmk,behavior-mod-morph` with 0 binding cells. Changes output based on held modifiers.

**Pattern:** Normal press = binding A, with modifier held = binding B.

- `CmmaSemi` -- comma normally, semicolon with Shift (dot/colon is not a mod morph but the linger key `dotcol`)
- `MagicBracketsL` -- combines with linger keys: unshifted gives paren/bracket (tap `(` / linger `[`), shifted gives angle-bracket/brace (tap `<` / linger `{`)

The plain mod morphs use `&bk` on both sides to stay in the AK system's output queue; the `Magic*` ones (`MagicSlash`, `MagicUnder`, `MagicGrave`, `MagicBracketsL/R`) put a linger key on each side (`mod_morph/behaviors.dtsi`).

## Timing Architecture

_Lineage: Entirely custom. Every constant was derived through empirical testing over 2+ years._

Most timing constants live in `config/layout/CONFIG.h`; the sticky-mod lifetime (1500ms, `mods/behaviors.dtsi`) and the macros' `wait-ms` are set in place. They form an interdependent system.

**Core relationships:**

```
ak_tap_time (10ms) < max(hold_key_event_delay 11ms, follower's combo 16/18ms)
                                                      -- a follower >= 11ms behind its trigger lands after the AK layer is on
linger_term (100ms) = my_ak_window (100ms)            -- linger and AK window aligned
action_lay_tapping_term (90ms) < linger_term (100ms)  -- layers activate before linger resolves
combo timeouts: 16ms, 18ms live                       -- 30ms (two-hand) defined, no consumers
```

The first line is the ordering that matters, and it only covers followers pressed ≥ 11ms after their trigger (margin at the start of that band: 1ms for hack-only followers, 6ms for 16ms followers). Faster rolls miss whatever these constants are (see *Adaptive Keys*). If `hold_key_event_delay` dropped to 10ms or less, only the hack-only followers would tie or miss at the start of that band; 16/18ms followers would keep ≥ 6ms 🧮.

**Macro internals:** `tap-ms` (via `TEMP_macro_tap_time`, or `ak_tap_time` in `&ak`; both 10ms) controls press-to-release duration. `wait-ms` controls the pause between macro steps: 0 in `&ak`, `&bk` and the replace macros, 10ms in `TYPING_MACRO`; a few one-off macros set their own: `logseqPageRef` 100ms (the `RB2 RB3 RB4` combo); `dotcom`/`dotcouk`, `AppSwitch` and the `pair*` macros 50ms, defined but bound nowhere that compiles 📜.

**The 500ms HRM tapping term:** Intentionally high. With cross-hand `hold-trigger-key-positions`, the actual hold detection is much faster -- the 500ms is a safety ceiling, not the usual activation time.

## Config Hierarchy -- Layout / Keyboard / Unit / Side

_Lineage: Entirely custom. Created Oct 2026 when a second Chocofi unit arrived, ahead of a 42-key board and a Charybdis._

Four axes that change independently, one place each:

| Axis | What | Where | Changes |
|---|---|---|---|
| 🧠 Layout | Bindings, AKs, combos, layers | `config/layout/` | All the time |
| ⌨️ Keyboard model | Geometry, key positions, hardware settings | `config/keyboards/<model>/` | New board bought |
| 🏷️ Unit | One physical keyboard: name, per-unit tweaks | `config/units/<unit>.conf` | Almost never |
| ↔️ Side | Central / peripheral, sleep | `config/keyboards/<model>/<shield>_<side>.conf` | Never |

```
$ build_and_flash.sh chocofi-pro right
  targets.txt: chocofi-pro → keyboard chocofi, nice_nano_v2, corne_right nice_view_adapter nice_view
  ZMK_CONFIG      = config/keyboards/chocofi/       → corne.keymap, corne.conf, corne_right.conf
  EXTRA_CONF_FILE = config/units/chocofi-pro.conf   → merged last, wins

Kconfig cascade (later wins):  corne.conf → corne_right.conf → units/chocofi-pro.conf
Devicetree:                    corne.keymap → positions.dtsi + ../../layout/layout.dtsi + physical layout
```

- **One setting, one level.** The keyboard name is only in `units/`; overrides between levels stay rare and commented in each file's header.
- **Files named by shield, folder named by model.** ZMK's `keymap-module/modules/modules.cmake` finds `<shield>.keymap` / `<shield>.conf` / `<shield>_<side>.conf` in `ZMK_CONFIG`, so `keyboards/chocofi/` holds `corne.*`.
- **Build dirs per unit and side** (`zmk/app/build/<unit>/<side>`), so switching units never reuses a cached config.
- **Key positions are per keyboard.** Combos and AKs use names (`LT0`, `RM2`), resolved by the model's `positions.dtsi`.
- **Planned, not built:**
  - A 42-key model becomes canonical: every layer written with 42 entries through a `KEYS(...)` macro; 36-key keyboards drop the outer columns. Outer-column names `LT5`… ; combos on them behind `#ifdef`.
  - `CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO` (= all keys, for the AK hack) moves to each model's `.conf`: 36 vs 42.
  - Charybdis: own `keyboards/` folder with trackball overlay + config.
- **Verified on creation:** rebuilt Chocofi had an identical `zephyr.dts` and a `.config` differing only in the name.

## Orchestrator Pattern -- `layout.dtsi`

_Lineage: Entirely custom. Created during the Great Restructuring (Oct 2023) as `corne.keymap`; became `layout/layout.dtsi` with the config hierarchy (Oct 2026)._

`layout.dtsi` is an include-only coordinator, included by each keyboard's keymap after its `positions.dtsi`. Inclusion order is strict and load-bearing:

1. `CONFIG.h` -- timing constants (must be first, everything depends on them)
2. `preprocessor_macros.c` -- macro definitions
3. Layer aliases, feature aliases (key position aliases come from the keyboard, before this file)
4. Default behavior config
5. **Macros section** -- all macro definitions
6. **Behaviors section** -- all custom behaviors (depend on macros)
7. **Combos section** -- all combos (depend on behaviors)
8. **Keymap section** -- layer definitions (depend on everything above)

**Layout selection:** All three layouts (`NAQUADAH`, `PROMETHIUM`, `RHODIUM`) are `#define`d in CONFIG.h. The `#if defined` cascade in `layout.dtsi` picks the first match. Since all three are defined, whichever appears first in the `#if` chain wins -- currently NAQUADAH.

## Layer System -- Three Tiers, 32-Layer Limit

Layers are a `uint32_t` bitmask (bits 0-31). Currently at exactly 32 layers -- the absolute maximum.

**Tier A -- Alpha (layers 0-1):** Base typing. `l_alpha` (macOS) and `l_alpha_linwin` (Windows/Linux). Keys use `&ak` macros that tie into Tier B.

**Tier B -- AK layers (layers 2-24):** One per AK trigger. 23 active layers. Each has replacement bindings at specific positions, transparent (`________`) everywhere else. Disabled AKs use layer ID `999` to free slots.

**Tier C -- Utility (layers 25-31):** nav, mod, fn, num, numsym, cfg, nav_linwin. Shared across all layouts.

**Layer groups:** `l_alpha_aks` = all alpha + AK layers. `l_all` = everything. Used for combo scoping.

## Preprocessor Metaprogramming

_Lineage: Entirely custom. Created Mar 2024 to eliminate boilerplate._

`config/layout/features/__BASE__/preprocessor_macros.c` is the metaprogramming hub.

| Macro | Purpose |
|-------|---------|
| `REPLACE_CHAR_WITH_BIGRAM(A, B)` | Generates AK replacement behavior |
| `COMBO_LAY_BASE(LAYERS, NAME, BINDINGS, KEYPOS, TIMEOUT)` | Base combo definition + 6 convenience wrappers |
| `LK(NAME, TAP, LINGER)` | Generates linger key hold-tap (note: reverses binding order) |
| `TYPING_MACRO(NAME, BINDINGS)` | Shorthand for `ZMK_MACRO` with standard timing |
| `________` / `xxxxxxxx` | Transparent / none aliases |

These macros eliminated massive boilerplate (87 lines down to 36 for linger keys alone when `LK` was introduced).

## Key Position Naming

Defined per keyboard in `keyboards/<model>/positions.dtsi` (Chocofi: `keyboards/chocofi/positions.dtsi`). Format: `{L|R}{T|M|B|H}{0-4}`.

```
╭─────────────────────╮ ╭─────────────────────╮
│ LT4 LT3 LT2 LT1 LT0 │ │ RT0 RT1 RT2 RT3 RT4 │
│ LM4 LM3 LM2 LM1 LM0 │ │ RM0 RM1 RM2 RM3 RM4 │
│ LB4 LB3 LB2 LB1 LB0 │ │ RB0 RB1 RB2 RB3 RB4 │
╰───────╮ LH2 LH1 LH0 │ │ RH0 RH1 RH2 ╭───────╯
        ╰──────────────╯ ╰──────────────╯
```

- L/R = hand, T/M/B = top/middle/bottom row, H = thumb
- 0 = innermost (index), 4 = outermost (pinky)
- Group aliases: `KEYS_L`, `KEYS_R`, `THUMBS_L`, `THUMBS_R`, `ALL_KEYS`

## Hardware Configuration

`keyboards/chocofi/corne.conf` tuned for the AK system:

- `CONFIG_ZMK_COMBO_MAX_COMBOS_PER_KEY=30` -- many combos per key (AKs + regular)
- `CONFIG_ZMK_BEHAVIORS_QUEUE_SIZE=512` -- large queue for macro event cascades
- `CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO=36` -- for the AK consistency hack (all keys)
- `CONFIG_ZMK_HID_SEPARATE_MOD_RELEASE_REPORT=y` -- clean mod release in separate HID report
