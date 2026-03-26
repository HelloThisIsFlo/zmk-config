# Adaptive Keys: Deep Dive

Complete reference for the AK mechanism in this keyboard config. Read this doc alone to understand how adaptive keys work end-to-end.

## Overview

Adaptive Keys (AKs) eliminate Same-Finger Bigrams (SFBs) — cases where two consecutive characters use the same finger. Instead of pressing two keys with one finger in sequence, the AK system detects the sequence and replaces the output.

- AKs are **not optional** — the layout is designed around them. Without AKs, the letter bindings don't make ergonomic sense.
- Naquadah has **23 active AK layers** (one per trigger key that has replacements).
- The system achieves a **0.082% SFB rate**.

## What Makes a Key Adaptive

The single distinction: **`ak_X` vs everything else.**

```c
// aliases.dtsi:4-31
#define ak_M &ak l_akM M    // adaptive — types M, activates l_akM
```

`ak_X` is an alias for `&ak l_akX X`. When you press a key bound to `ak_X`, two things happen:
1. The character X is typed
2. X's AK layer (`l_akX`) activates for 100ms

**Without `ak_X`, a key is just a regular key.** No AK layer activates, no replacements are possible.

On the **Naquadah alpha layer** (`layers_A_NAQUADAH_alpha.dtsi`):

```
╭───────────────────────────╮ ╭───────────────────────────╮
│ ak_X  ak_W  ak_M  ak_P  ak_K │ │  /·    .:    =-    -    '"  │
│ ak_C  ak_S  ak_N  ak_T  ak_B │ │  ,;   ak_A  ak_E  ak_I  ak_H │
│ ak_F  ak_G  ak_L  ak_D  ak_V │ │  _·   ak_U  ak_O  ak_Y  &bk J │
╰─────────╮ NUM   SFT   NAV    │ │  SPC  NSYM  TGL ╭───────────╯
          ╰────────────────────╯ ╰─────────────────╯
```

- **Left hand**: all 15 alpha keys are adaptive (`ak_X`)
- **Right hand**: A, E, I, H, U, O, Y are adaptive; punctuation keys and J use `&bk` or custom behaviors
- **Thumbs**: none are adaptive (they're layer switches, shift, space, etc.)
- Some adaptive keys have **disabled AK layers** (e.g., `l_akI = 999`) — the key still goes through the `&ak` macro for timing consistency, but the layer activation is a no-op

## The `&ak` Behavior

Defined in `adaptive_keys/macros.dtsi:25-39`. A two-parameter macro:

```dts
ak: ak {
    compatible = "zmk,behavior-macro-two-param";
    #binding-cells = <2>;
    wait-ms = <0>;
    tap-ms = <ak_tap_time>;    // 10ms (CONFIG.h:27)
    bindings =
        <&macro_param_2to1>,
        <&macro_tap &kp MACRO_PLACEHOLDER>,   // Step 1: type the character
        <&macro_tap_time 0>,
        <&macro_param_1to1>,
        <&macro_tap &aksl MACRO_PLACEHOLDER>; // Step 2: activate AK layer
};
```

Step by step for `ak_M` = `&ak l_akM M`:
1. **Tap `&kp M`** — takes `ak_tap_time` (10ms) to complete
2. **Set tap-time to 0** — so the next step executes instantly
3. **Tap `&aksl l_akM`** — activates the sticky layer for M

The 10ms tap time is critical — it can't be 0 (causes missed keypresses on some hardware). This delay is what creates the race condition that the consistency hack solves (see `ak-combo-hack.md`).

## The `&aksl` Sticky Layer

Defined in `adaptive_keys/behaviors.dtsi:1-9`:

```dts
aksl: aksl {
    compatible = "zmk,behavior-sticky-key";
    #binding-cells = <1>;
    release-after-ms = <my_ak_window>;  // 100ms (CONFIG.h:8)
    bindings = <&mo>;
    // No quick-release — layer stays until next &kp releases
};
```

Key properties:
- **Wraps `&mo`** — activates the AK layer as a momentary layer
- **100ms window** (`my_ak_window`) — the AK layer deactivates after 100ms if no key is pressed
- **No `quick-release`** — this is deliberate. Without quick-release, the AK layer stays active until the next `&kp` _releases_ (not just presses). This means the next `&ak` macro can activate its own layer _before_ the current one deactivates, enabling seamless chaining.

## AK Layers

Each adaptive key gets its own layer (e.g., `l_akM` = layer 13). These layers are defined in `layers_B_NAQUADAH_adaptive_keys.dtsi`.

AK layers are **mostly transparent**. Only positions that need a replacement have explicit bindings. Everything else is `________` (`&trans`), falling through to the alpha layer below.

### Four Binding Types on AK Layers

| Binding | What it does | Chain continues? |
|---------|-------------|-----------------|
| `________` | Transparent — falls through to alpha, where `ak_X` fires | Yes (alpha's `ak_X` activates next AK layer) |
| `&bk Z` | Types Z, exits AK ecosystem | **No** |
| `ak_Z` | Types Z AND activates Z's AK layer | **Yes** |
| `XX_to_YY` | Retroactive first-char change (via `REPLACE_CHAR_WITH_BIGRAM`) | **Yes** (always chains) |

### The `&bk` Behavior

Defined in `adaptive_keys/macros.dtsi:77-87`. A simple one-param tap macro:

```dts
bk: bk {
    compatible = "zmk,behavior-macro-one-param";
    tap-ms = <TEMP_macro_tap_time>;  // 10ms
    bindings =
        <&macro_param_1to1>,
        <&macro_tap &kp MACRO_PLACEHOLDER>;
};
```

`&bk Z` types Z with no AK layer activation — the chain ends. But chain termination is only half the story. `&bk` exists primarily as a **consistency mechanism** that keeps all key events in ZMK's macro processing pipeline.

**Why not just use `&kp`?** ZMK processes macro events in a serialized pipeline — events within and between macros maintain strict ordering. A raw `&kp` outside a macro bypasses this pipeline. When an `&ak` macro is still in flight (typing a character, activating an AK layer), a raw `&kp` from the next keystroke can fire out of order or race with those in-flight events. `&bk` wraps `&kp` in a macro, keeping it in the ordered pipeline so output arrives in the correct sequence.

**The rule:**
- **`&bk`** for all normal typing flow — alpha layer bindings, AK layer bindings, combo outputs
- **`&kp`** only inside macros (already serialized: `&ak` internals, `REPLACE_CHAR_WITH_BIGRAM` internals) or for behaviors that need actual key hold (e.g., `lk_wispr`'s Globe key)

**Evidence — `&bk` is used everywhere in the typing path:**
- AK layers (`layers_B_NAQUADAH_adaptive_keys.dtsi`): ALL non-transparent, non-`ak_X` bindings use `&bk` — zero raw `&kp`
- Alpha layer (`layers_A_NAQUADAH_alpha.dtsi`): non-adaptive keys use `&bk` (`&bk MINUS` at RT3, `&bk J` at RB4)
- Combo outputs (`combos.dtsi`): all use `&bk` (`&bk Q`, `&bk Z`, `&bk SPACE`, `&bk RETURN`, etc.)
- Raw `&kp` appears only in: `&ak` macro internals (`macros.dtsi:33`), `REPLACE_CHAR_WITH_BIGRAM` internals (`preprocessor_macros.c:20/22`), and `lk_wispr` hold side

## Two Replacement Types

### Type 1: Second Character Changes

The simpler, more common type. The AK layer binds a different character at the triggering position.

**Example: M→T produces MN**
- M is at LT2, T is at LM1 on the alpha layer
- Bindings on `l_akM` (`layers_B_NAQUADAH_adaptive_keys.dtsi:123-132`):
  - LM1 (T's position) → `&bk N`

Step-by-step:
1. Press M → `ak_M` fires → types **M**, activates `l_akM`
2. Press T → on `l_akM`, position LM1 has `&bk N` → types **N**, chain ends
3. Output: **MN** (not MT)

The binding can be either `&bk Z` (chain ends) or `ak_Z` (chain continues):
- `&bk N` at LM1 on `l_akM` → M→T = MN, done
- `ak_B` at LT0 on `l_akM` → M→K = MB, and B's AK layer activates (for chaining, see below)

### Type 2: First Character Changes (`REPLACE_CHAR_WITH_BIGRAM`)

The first character already typed gets retroactively replaced. Defined in `__BASE__/preprocessor_macros.c:12-28`:

```c
#define REPLACE_CHAR_WITH_BIGRAM(BIGRAM_0, BIGRAM_1)  \
    // Creates: &replace_char_with_bigram_##BIGRAM_0##BIGRAM_1
    bindings =
        <&macro_tap &kp BACKSPACE>,         // 1. Delete the first char
        <&macro_tap &kp BIGRAM_0>,          // 2. Type the replacement first char
        <&macro_release &kp LSHFT>,         // 3. Clear any held shifts
        <&macro_release &kp RSHFT>,
        <&macro_tap ak_##BIGRAM_1>;         // 4. Type second char via ak_ (chains!)
```

**Always chains** — step 4 uses `ak_BIGRAM_1`, which activates BIGRAM_1's AK layer.

**Example: C→P produces TP**
- C is at LM4, P is at LT1 on the alpha layer
- Alias: `CP_to_TP` → `&replace_char_with_bigram_TP` (`aliases.dtsi:66`)
- Created by: `REPLACE_CHAR_WITH_BIGRAM(T, P)` (`macros.dtsi:21`)
- Binding on `l_akC` (`layers_B_NAQUADAH_adaptive_keys.dtsi:27`): LT1 → `CP_to_TP`

Step-by-step:
1. Press C → `ak_C` fires → types **C**, activates `l_akC`
2. Press P → on `l_akC`, position LT1 has `CP_to_TP`:
   - Backspace (deletes the C)
   - Types **T**
   - Clears shifts
   - `ak_P` → types **P**, activates `l_akP`
3. Output: **TP** (not CP). Chain continues — next key hits `l_akP`.

### Naming Convention for Type 2

`XX_to_YY` where:
- **X** = the trigger key (whose AK layer we're on)
- **Y** = the key being pressed
- **ZW** = the output bigram

Comments in `aliases.dtsi:64-87` note symmetry relationships (e.g., `CP_to_TP /* Symmetry on PT(c) */`).

## Chaining

Chaining happens when an AK layer binding uses `ak_Z` instead of `&bk Z`. The next key typed can _also_ hit a replacement.

**3-key chain example: M→K→G produces MBL** (comment at `layers_B_NAQUADAH_adaptive_keys.dtsi:126`)

Setup on AK layers:
- `l_akM`: LT0 (K's position) → `ak_B` (not `&bk B`)
- `l_akB`: LB3 (G's position) → `&bk L`

Step-by-step:
1. Press M → `ak_M` → types **M**, activates `l_akM`
2. Press K → on `l_akM`, LT0 has `ak_B` → types **B**, activates `l_akB`
3. Press G → on `l_akB`, LB3 has `&bk L` → types **L**, chain ends
4. Output: **MBL** (not MKG)

Key insight: the choice at step 2 is deliberate. Using `ak_B` (instead of `&bk B`) means the system knows the user might continue the chain. If `&bk B` were used instead, step 3 would fall through to alpha and type G.

### Why Chaining Works (No Quick-Release)

The `&aksl` behavior has no `quick-release` (`behaviors.dtsi:7-8`). This means:
- When K is pressed in step 2, `l_akM` doesn't deactivate until K's `&kp` _releases_
- By that time, `ak_B` has already fired and `l_akB` is active
- There's no gap between AK layers — seamless handoff

### `REPLACE_CHAR_WITH_BIGRAM` Always Chains

Type 2 replacements end with `ak_BIGRAM_1`, so the chain always continues. Example:
- C→P (= TP via `CP_to_TP`) chains into `l_akP`
- If the next key hits a replacement on `l_akP`, that replacement also fires

## The `___X____` Convention

Defined in `aliases.dtsi:34-61`:

```c
// For these keys, I could use '________' (&trans) instead of the ak_X macros,
// but the ak_X macros make the ak key visible on the keymap-drawer
#define ___M____ ak_M
```

`___X____` is used on X's own AK layer at X's own position. For example, `___M____` at LT2 on `l_akM`.

- **Functionally equivalent to `________`** — transparent would fall through to alpha's `ak_M`, which does the same thing
- **Exists for keymap-drawer visibility** — when rendering the layout visually, `___M____` shows the key identity explicitly, while `________` would show as blank
- Easy to spot: `___X____` always appears exactly once per AK layer, at the key's own position

Special case: `__hE____` (`aliases.dtsi:61`) for the composite H→E adaptive key (`ak_hE` = `&ak l_akhE E`).

## Two Consistency Mechanisms

The AK system relies on two separate mechanisms to keep keystroke processing reliable:

| Mechanism | What it solves | Scope |
|-----------|---------------|-------|
| `&bk` | Individual key ordering — keeps events in ZMK's macro processing pipeline | Every keystroke in the typing flow |
| Combo hack | Combo-resolution ordering — delays keys released simultaneously by the combo system | Keys participating in combos |

`&bk` is the more fundamental mechanism — it applies universally to every key in the typing path. The combo hack addresses the specific edge case where combo resolution releases multiple buffered keys at once, which would bypass `&bk`'s ordering guarantees. See [ak-combo-hack.md](ak-combo-hack.md) for the full combo hack mechanism.

## The `ak_hE` Composite Adaptive

`ak_hE` (`aliases.dtsi:12`) is a special "two-deep" entry point:

```c
#define ak_hE &ak l_akhE E
```

- Used on `l_akH` at E's position (RM2) — so H→E activates `l_akhE`
- `l_akhE` has its own replacements (e.g., `&bk Y` at RB1 — U's alpha position — so H→E→U produces HEY)
- This enables 3-character sequences starting with HE to be adaptive

## File Map

| File | What it contains |
|------|-----------------|
| `config/CONFIG.h` | All timing constants: `ak_tap_time` (10ms), `hold_key_event_delay` (11ms), `my_ak_window` (100ms) |
| `adaptive_keys/macros.dtsi:25-39` | `&ak` behavior — the core two-param macro |
| `adaptive_keys/macros.dtsi:77-87` | `&bk` behavior — simple tap, exits AK ecosystem |
| `adaptive_keys/behaviors.dtsi:1-9` | `&aksl` — sticky layer that creates the detection window |
| `adaptive_keys/aliases.dtsi:4-31` | `ak_X` aliases — entry points into the AK system |
| `adaptive_keys/aliases.dtsi:34-61` | `___X____` aliases — self-reference convention |
| `adaptive_keys/aliases.dtsi:64-87` | `XX_to_YY` aliases — Type 2 replacement mappings |
| `adaptive_keys/combos.dtsi` | Consistency hack (see `ak-combo-hack.md`) |
| `hands_down/layers_A_NAQUADAH_alpha.dtsi` | Alpha layer — where `ak_X` bindings live |
| `hands_down/layers_B_NAQUADAH_adaptive_keys.dtsi` | All 23 AK layers with their replacement bindings |
| `__BASE__/preprocessor_macros.c:12-28` | `REPLACE_CHAR_WITH_BIGRAM` macro definition |
| `__BASE__/aliases_layers_NAQUADAH.dtsi` | Layer numbering (l_akA=2 through l_akY=24) and `l_alpha_aks` group |
