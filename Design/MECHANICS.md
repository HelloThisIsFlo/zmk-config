# Keyboard Mechanics

> Technical reference for how the keyboard systems work under the hood.
> Organized by topic. This is a living document -- refined as patterns evolve.
> For implementation recipes ("I want to add X"), see [COOKBOOK.md](COOKBOOK.md).
>
> Last refined: 2026-02-26

## Lineage

The technical foundation draws from Alan Reiser's [Hands Down](https://sites.google.com/alanreiser.com/handsdown) project, which pioneered Adaptive Keys and linger keys for ZMK. The concepts were imported in Sep 2023 from Moutis' Hands Down ZMK derivative. Everything documented below -- the layer-per-AK architecture, the buffered key system, the timing web, the preprocessor metaprogramming, the orchestrator pattern -- was built from scratch on top of those concepts.

## Adaptive Keys -- The Core Innovation

_Lineage: The concept of detecting key sequences and replacing output originated in Hands Down. The implementation below -- layer-per-AK architecture, `&aksl`, the consistency hack, the timing constants -- is entirely custom._

The layout is designed around AKs. Without them, it's unusable. Each AK gets its own dedicated layer.

_**Deep dives:** [ak-deepdive.md](ak-deepdive.md) covers the full AK mechanism. [ak-combo-hack.md](ak-combo-hack.md) covers the consistency hack._

**How it works (brief):** Each adaptive key on the alpha layer uses `ak_X` (= `&ak l_akX X`), which types the character and activates the key's AK layer via `&aksl` for 100ms. The next keystroke within that window hits a replacement binding on the AK layer. For the full mechanism -- chaining, two replacement types, the `___X____` convention, and the `&bk` consistency role -- see [ak-deepdive.md](ak-deepdive.md).

**`REPLACE_CHAR_WITH_BIGRAM(A, B)`** -- the replacement mechanism. Steps:

1. Backspace (delete the first key already output)
2. Type BIGRAM_0 (first char of replacement)
3. Release both LSHFT and RSHFT (prevents unintended case changes)
4. Tap `ak_##BIGRAM_1` (second char, through the AK behavior so it can chain)

**The AK Consistency Hack.** A master combo on ALL 36 keys with timeout `hold_key_event_delay` (11ms). The problem: when a normal combo times out, ZMK releases all buffered keys simultaneously. The second key could fire before the AK layer activates. The solution: the master combo's 11ms timeout > `ak_tap_time` (10ms), guaranteeing the AK layer activates first. This 1ms margin is what makes the whole system reliable.

**Layer scoping.** The AK consistency hack combo uses `l_alpha_aks` (alpha + all AK layers). AKs can chain but don't trigger from utility layers.

**Disabled AKs.** Some AK layers are disabled by setting them to `999` (e.g., l_akI, l_akJ, l_akQ, l_akZ). Frees up layer IDs while keeping combo definitions intact.

## Buffered Behaviors -- `&bk`, `&bsk`, `&bm`

_Lineage: Invented in Sep 2023 to solve timing race conditions in the Hands Down AK system. Not present in the original Hands Down implementation._

**`&bk` (Buffered Key):** A `behavior-macro-one-param` that wraps `&kp` with `tap-ms = 10`. This 10ms delay between press and release ensures consistent key registration, especially during AK detection where multiple events fire in rapid sequence.

Raw `&kp` inside macros can cause race conditions -- keys arrive out of order or get dropped. The 10ms buffer prevents this. Originally created as `&bkp` in Sep 2023 to solve exactly this problem.

**`&bsk` (Buffered Sticky Key):** Wraps `&sk` with `macro_press` + `macro_pause_for_release` + `macro_release`. Holds the sticky key active until the physical key is released.

**`&bm` (Buffered Mod):** For modifiers in macros. Uses `macro_press`/`macro_release` with a pause to hold the modifier across multiple key events.

**When to use `&kp` vs `&bk`:** Use `&bk` in normal typing flow (AK layers, alpha bindings, combo outputs). Use `&kp` when you need a key to actually be **held** -- example: `lk_wispr` uses `&kp` on the hold side so the Globe key stays pressed while the combo is held. `&bk` would tap-and-release immediately, which is wrong for hold behaviors.

## Linger Keys -- Tap vs Hold

_Lineage: The concept of tap-vs-hold character variants comes from Hands Down. The `LK` macro, the preprocessor generation, and the `&kp` hold pattern are custom._

Linger keys are `zmk,behavior-hold-tap` with `tap-preferred` flavor and `tapping-term-ms = linger_term` (100ms).

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

**Common linger keys:** `qu` (tap Q, linger Qu), `th`/`sh`/`gh` (H-digraph tap, extended suffix on linger), `magicArrowL/R` (single arrow tap, double on linger), `magicCloseQuit` (close tab tap, quit app linger).

## Combo System -- Three Timeout Tiers

_Lineage: Basic combo use comes from Hands Down. The three-tier timeout system, layer scoping macros, and preprocessor generation are custom._

All combos are generated by preprocessor macros expanding `COMBO_LAY_BASE(LAYERS, NAME, BINDINGS, KEYPOS, TIMEOUT)`.

**Timeout tiers:**

| Tier | Timeout | Use case |
|------|---------|----------|
| Adjacent | 16ms | Keys physically next to each other, same hand. Extremely tight -- virtually no misfires. |
| Non-adjacent | 18ms | Same hand, keys further apart. 2ms more for the wider finger spread. |
| Two-hand | 30ms | Keys on opposite hands. Much more generous -- hard to press simultaneously by accident. |

**Layer scoping:**

- `COMBO_ANY_*` -- Active on all layers (`l_all`). For universal actions like space, backspace, enter.
- `COMBO_LAY_*` -- Active on specific layers. The AK consistency hack combo uses `l_alpha_aks`. Some UI combos are alpha-only to avoid conflicts with transposed keys on other layers.

**Interaction with AKs:** The AK consistency hack uses a combo (see [ak-combo-hack.md](ak-combo-hack.md)). `CONFIG_ZMK_COMBO_MAX_COMBOS_PER_KEY=30` and `CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO=36` are tuned for this.

## Callum-Style Mods

_Lineage: One-shot mod concept from Callum's layout. The `moAndBuffer` macro, `skm`/`htls` behaviors, and timing tuning are custom._

Replaced Home Row Mods in Sep 2024.

**`skm` (sticky key mod):** A `behavior-sticky-key` with `ignore-modifiers`. Tap to activate a one-shot mod. `ignore-modifiers` allows stacking -- tap Shift, tap Ctrl, next key gets both.

**`htls` (hold-tap layer sticky):** The main thumb key behavior. Hold (>= 90ms `action_lay_tapping_term`) activates the mod layer via `moAndBuffer`. Tap (< 90ms) activates a sticky mod via `skms`.

**`moAndBuffer`:** A macro that presses `&mo l_mod`, pauses for release, waits `action_mod_tapping_term` (130ms), then releases. The 130ms buffer keeps the mod layer alive long enough for the hold-tap to complete -- without it, the layer could deactivate before the mod registers.

**The timing guarantee:** This architecture ensures you never have to think about timing. As long as the _order_ is correct, it works:
- Correct: Mod Layer Press → Mod 1 → Mod 2 → Mod Layer Release
- Correct: Mod Layer Press → Mod 1 → Mod 2 press → Mod Layer Release → Mod 2 release
- Incorrect: Mod Layer Press → Mod 1 → Mod Layer Release → Mod 2 (too late -- layer gone)

The 130ms buffer is what makes this forgiving -- it gives you a generous window after releasing the mod layer thumb key for any in-flight mod taps to resolve.

**Home row mods still exist** (`hml`/`hmr`): `behavior-hold-tap` with `hold-trigger-key-positions` for cross-hand activation. Uses `&bm` (buffered mod) for hold, `&bk` for tap. Some keys (S, C, N, T, E, A, M) use custom variants that tap the AK macro instead of plain `&bk`, enabling AKs from home-row positions.

## Mod Morphs -- Conditional Behavior

`zmk,behavior-mod-morph` with 0 binding cells. Changes output based on held modifiers.

**Pattern:** Normal press = binding A, with modifier held = binding B.

- `CmmaSemi` -- comma normally, semicolon with Shift
- `DotColn` -- dot normally, colon with Shift
- `MagicBracketsL` -- combines with linger keys: unshifted gives bracket/paren (tap/linger), shifted gives brace/angle-bracket (tap/linger)

All mod morphs use `&bk` for their bindings to maintain timing consistency with the AK system.

## Timing Architecture

_Lineage: Entirely custom. Every constant was derived through empirical testing over 2+ years._

All timing constants live in `config/CONFIG.h`. They form an interdependent system.

**Core relationships:**

```
ak_tap_time (10ms) < hold_key_event_delay (11ms)     -- 1ms margin for AK consistency
linger_term (100ms) = my_ak_window (100ms)            -- linger and AK window aligned
action_lay_tapping_term (90ms) < linger_term (100ms)  -- layers activate before linger resolves
combo timeouts: 16ms < 18ms < 30ms                    -- tighter = less misfire risk
```

**Macro internals:** `tap-ms` in macros (via `TEMP_macro_tap_time`) controls press-to-release duration. `wait-ms` controls pause between macro steps. Both typically 10ms for reliable key registration.

**The 500ms HRM tapping term:** Intentionally high. With cross-hand `hold-trigger-key-positions`, the actual hold detection is much faster -- the 500ms is a safety ceiling, not the usual activation time.

## Orchestrator Pattern -- `corne.keymap`

_Lineage: Entirely custom. Created during the Great Restructuring (Oct 2023)._

`corne.keymap` is an include-only coordinator. Inclusion order is strict and load-bearing:

1. `CONFIG.h` -- timing constants (must be first, everything depends on them)
2. `preprocessor_macros.c` -- macro definitions
3. Key position aliases, layer aliases, feature aliases
4. Default behavior config
5. **Macros section** -- all macro definitions
6. **Behaviors section** -- all custom behaviors (depend on macros)
7. **Combos section** -- all combos (depend on behaviors)
8. **Keymap section** -- layer definitions (depend on everything above)

**Layout selection:** All three layouts (`NAQUADAH`, `PROMETHIUM`, `RHODIUM`) are `#define`d in CONFIG.h. The `#if defined` cascade in `corne.keymap` picks the first match. Since all three are defined, whichever appears first in the `#if` chain wins -- currently NAQUADAH.

## Layer System -- Three Tiers, 32-Layer Limit

Layers are a `uint32_t` bitmask (bits 0-31). Currently at exactly 32 layers -- the absolute maximum.

**Tier A -- Alpha (layers 0-1):** Base typing. `l_alpha` (macOS) and `l_alpha_linwin` (Windows/Linux). Keys use `&ak` macros that tie into Tier B.

**Tier B -- AK layers (layers 2-24):** One per AK trigger. 23 active layers. Each has replacement bindings at specific positions, transparent (`________`) everywhere else. Disabled AKs use layer ID `999` to free slots.

**Tier C -- Utility (layers 25-31):** nav, mod, fn, num, numsym, cfg, nav_linwin. Shared across all layouts.

**Layer groups:** `l_alpha_aks` = all alpha + AK layers. `l_all` = everything. Used for combo scoping.

## Preprocessor Metaprogramming

_Lineage: Entirely custom. Created Mar 2024 to eliminate boilerplate._

`config/features/__BASE__/preprocessor_macros.c` is the metaprogramming hub.

| Macro | Purpose |
|-------|---------|
| `REPLACE_CHAR_WITH_BIGRAM(A, B)` | Generates AK replacement behavior |
| `COMBO_LAY_BASE(LAYERS, NAME, BINDINGS, KEYPOS, TIMEOUT)` | Base combo definition + 6 convenience wrappers |
| `LK(NAME, TAP, LINGER)` | Generates linger key hold-tap (note: reverses binding order) |
| `TYPING_MACRO(NAME, BINDINGS)` | Shorthand for `ZMK_MACRO` with standard timing |
| `________` / `xxxxxxxx` | Transparent / none aliases |

These macros eliminated massive boilerplate (87 lines down to 36 for linger keys alone when `LK` was introduced).

## Key Position Naming

Defined in `__BASE__/aliases_key_positions.dtsi`. Format: `{L|R}{T|M|B|H}{0-4}`.

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

`corne.conf` tuned for the AK system:

- `CONFIG_ZMK_COMBO_MAX_COMBOS_PER_KEY=30` -- many combos per key (AKs + regular)
- `CONFIG_ZMK_BEHAVIORS_QUEUE_SIZE=512` -- large queue for macro event cascades
- `CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO=36` -- for the AK consistency hack (all keys)
- `CONFIG_ZMK_HID_SEPARATE_MOD_RELEASE_REPORT=y` -- clean mod release in separate HID report
