# Behavior Cookbook

> Implementation recipes for adding new key behaviors.
> Each recipe answers: "I want X — what pattern do I use, and what code goes where?"
>
> For how these systems work under the hood, see [MECHANICS.md](MECHANICS.md).

## Conventions

- **`XXX`** — dummy binding cell value (defined as `0` in preprocessor_macros.c). Use whenever a binding cell is passed to a macro that ignores it.
- **`&bk`** — buffered key. Use instead of `&kp` for all character output in behaviors. See MECHANICS.md for why.
- **Include order matters**: macros.dtsi -> behaviors.dtsi -> combos.dtsi -> layers. If something silently doesn't work, check that the thing you're referencing is `#include`d earlier in `corne.keymap`.

## File Locations

| What | Where |
|------|-------|
| Typing macros | `config/features/hands_down/macros.dtsi` |
| Linger key behaviors | `config/features/hands_down/linger_keys/behaviors.dtsi` |
| Mod-morph behaviors | `config/features/hands_down/mod_morph/behaviors.dtsi` |
| AK macros | `config/features/hands_down/adaptive_keys/macros.dtsi` |
| AK aliases | `config/features/hands_down/adaptive_keys/aliases.dtsi` |
| AK consistency hack | `config/features/hands_down/adaptive_keys/combos.dtsi` |
| AK layers (per layout) | `config/features/hands_down/layers_B_*_adaptive_keys.dtsi` |
| H-digraph combos | `config/features/hands_down/h_digraphs/combos.dtsi` |
| Mods behaviors | `config/features/hands_down/mods/behaviors.dtsi` |
| Thumb / HRM behaviors | `config/features/hands_down/mods/behaviors.dtsi` |
| Alpha layers | `config/features/hands_down/layers_A_*.dtsi` |

---

## Single-Key Behaviors

### Recipe 1: Simple Key

**I want:** a key that types one character.

**Template:**
```dtsi
// In the layer file, use directly:
&bk KEYCODE
```

**Example:** `&bk J` in `layers_A_NAQUADAH_alpha.dtsi`

---

### Recipe 2: Shift Changes Output (Mod-Morph)

**I want:** a key that types one thing normally, another when shifted.

**Files:** `mod_morph/behaviors.dtsi` + layer file

**Template:**
```dtsi
// In mod_morph/behaviors.dtsi:
MyName: MyName {
    compatible = "zmk,behavior-mod-morph";
    label = "MyName";
    #binding-cells = <0>;
    bindings = <&bk NORMAL_KEY>, <&bk SHIFTED_KEY>;
    mods = <(MOD_LSFT|MOD_RSFT)>;
};

// In layer file:
&MyName
```

**Example:** `CmmaSemi` — tap=`,` shift=`;`

---

### Recipe 3: Alt Changes Output (Mod-Morph)

**I want:** a key that types one thing normally, another when alt is held.

Same as Recipe 2, but change `mods`:
```dtsi
    mods = <(MOD_LALT|MOD_RALT)>;
```

**Example:** `DqtLbkt` — tap=`"` alt=`[`

---

## Linger Behaviors

### Recipe 4: Linger, Both Single Chars

**I want:** a key that types one char on tap, a different char on linger (hold).

**Files:** `linger_keys/behaviors.dtsi` (the `#define` line) + layer file

**Template:**
```dtsi
// In linger_keys/behaviors.dtsi — create a #define alias (no new LK needed, reuse lk_bk):
#define myAlias  &lk_bk LINGER_KEY TAP_KEY

// In layer file:
myAlias
```

**How it works:** `lk_bk` is a generic LK with `&bk` for both tap and linger. The two binding cells become the keycodes for each.

**Gotcha:** binding order is reversed — linger first, tap second. The `LK` macro and `&lk` behavior both follow this convention (inherited from ZMK hold-tap where hold comes first).

**Example:** `#define sqtDqt &lk_bk DQT SQT` — tap=`'` linger=`"`

**Known inconsistency:** some older aliases use `&lk` instead of `&lk_bk`. See [INCONSISTENCIES.md](INCONSISTENCIES.md).

---

### Recipe 5: Linger, With Macros

**I want:** a key where tap or linger (or both) produce multi-character sequences.

Use this recipe whenever **any** output is more than one character. If one output is a single char, wrap it with Recipe 15 (single-char wrapper) to keep the `XXX XXX` pattern consistent.

**Files:** `macros.dtsi` + `linger_keys/behaviors.dtsi` + layer file

**Template:**
```dtsi
// 1. In macros.dtsi — define macros for each output:
TYPING_MACRO(myTapMacro,    &kp A &kp B)
TYPING_MACRO(myLingerMacro, &kp C &kp D)
// If one output is a single char, use Recipe 15 to wrap it:
// TYPING_MACRO(myTapMacro, &kp A)

// 2. In linger_keys/behaviors.dtsi — create LK and alias:
LK(myName, &myTapMacro, &myLingerMacro)
#define myAlias  &lk_myName XXX XXX

// 3. In layer file:
myAlias
```

**Why `XXX XXX`:** both bindings are macros that ignore their binding cell parameter. This is the convention for all custom LKs — never mix `XXX` and real keycodes.

**When to use this vs Recipe 4:** if both outputs are single chars, use Recipe 4 (simpler). The moment any output is multi-char, use this recipe.

**Example:** `LK(magicArrowL, &arrowLeftSingle, &arrowLeftDouble)` — tap=` <- ` linger=` <= `

**Note:** if you need this linger key triggered by a combo, just create the alias per this recipe, then use it as the binding in a combo (Recipe 8).

**Note:** if this linger key will also be wrapped in a mod-morph (shift changes output), use Recipe 6 or 7 instead — it's a magic key. Use `magic` naming for all components, even if the shifted side is simple for now.

---

## Magic Keys (Shift + Linger = 4 Outputs)

### Recipe 6: Magic Key, All Single Chars

**I want:** a key with 4 outputs: tap, linger, shift+tap, shift+linger — all single characters.

**Files:** `mod_morph/behaviors.dtsi` + layer file

**Template:**
```dtsi
// In mod_morph/behaviors.dtsi:
/*
S L => Output
-------------
_ _ => TAP_CHAR
_ X => LINGER_CHAR
X _ => SHIFT_TAP_CHAR
X X => SHIFT_LINGER_CHAR
*/
MyMagic: MyMagic {
    compatible = "zmk,behavior-mod-morph";
    label = "MyMagic";
    #binding-cells = <0>;
    bindings = <&lk LINGER_KEY TAP_KEY>, <&lk SHIFT_LINGER_KEY SHIFT_TAP_KEY>;
    mods = <(MOD_LSFT|MOD_RSFT)>;
};

// In layer file:
&MyMagic
```

**Gotcha:** `&lk` binding order is linger first, tap second (same as Recipe 4). In the template: `&lk LINGER_KEY TAP_KEY` — remember, linger comes first.

**Example:** `MagicBracketsL` — tap=`(` linger=`[` shift+tap=`{` shift+linger=`<`

**Note:** if any output is a multi-character sequence, use Recipe 7 instead.

---

### Recipe 7: Magic Key, With Macro Outputs

**I want:** a key with 4 outputs where some are multi-character sequences.

**Files:** `macros.dtsi` + `linger_keys/behaviors.dtsi` + `mod_morph/behaviors.dtsi` + layer file

**Template:**
```dtsi
// 1. In macros.dtsi — define macros for all outputs:
TYPING_MACRO(myLingerMacro,      &kp A &kp B)
TYPING_MACRO(myShiftLingerMacro, &kp C &kp D)
// Single-char outputs get wrapped too (Recipe 15) for XXX XXX consistency:
TYPING_MACRO(myTapMacro,         &kp X)
TYPING_MACRO(myShiftTapMacro,    &kp Y)

// 2. In linger_keys/behaviors.dtsi — create LKs and aliases:
LK(myUnshifted, &myTapMacro, &myLingerMacro)          // tap=X    linger=AB
#define myUnshifted  &lk_myUnshifted XXX XXX
LK(myShifted,   &myShiftTapMacro, &myShiftLingerMacro) // tap=Y    linger=CD
#define myShifted  &lk_myShifted XXX XXX

// 3. In mod_morph/behaviors.dtsi:
MyMagic: MyMagic {
    compatible = "zmk,behavior-mod-morph";
    label = "MyMagic";
    #binding-cells = <0>;
    bindings = <&lk_myUnshifted XXX XXX>, <&lk_myShifted XXX XXX>;
    mods = <(MOD_LSFT|MOD_RSFT)>;
};

// 4. In layer file:
&MyMagic
```

**Example:** `MagicSlash` — tap=`/` linger=`~/` shift+tap=`#` shift+linger=`~/.`

---

## Combos

### Recipe 8: Adding a Combo

**I want:** two (or more) keys pressed together to produce an output.

**Files:** combo file (e.g., `combos.dtsi` or `h_digraphs/combos.dtsi`)

**Template:**
```dtsi
// One-hand, on specific layers:
COMBO_LAY_ONE_HAND(LAYERS, comboName, BINDING, POS1 POS2)

// One-hand, on all layers:
COMBO_ANY_ONE_HAND(comboName, BINDING, POS1 POS2)

// Two-hand — keys on opposite halves (longer timeout for sync delay and hand coordination):
COMBO_ANY_TWO_HAND(comboName, BINDING, POS1 POS2)
```

**The binding can be anything** — a `&bk` keycode, a `&macro`, a mod-morph like `&MagicSlash`, or a linger key alias from Recipe 4/5. The combo doesn't care what it triggers.

**Examples:**
- Simple key: `COMBO_ANY_ONE_HAND(space, &bk SPACE, LT1 LT0)`
- Linger key: `COMBO_LAY_ONE_HAND(l_alpha_aks, th, thAlias, LM2 LM1)` — fires a linger key alias (tap=Th, linger=tion)

**Key positions:** defined in `__BASE__/aliases_key_positions.dtsi`. Format: `{L|R}{T|M|B|H}{0-4}`.

---

## Adaptive Keys

### Recipe 9: AK — Second Character Changes

> ⚠️ **Partially reviewed** — structure is correct but examples may need improvement.

**I want:** typing XY to produce XZ instead (only the second character changes).

This is the simpler, more common AK type. X stays as-is; the next keystroke's output is replaced.

**Files:** `layers_B_*_adaptive_keys.dtsi`

**Prerequisites:** trigger key X must have an AK entry (`#define ak_X &ak l_akX X` in `adaptive_keys/aliases.dtsi`) and an AK layer in the layers file.

**Steps:**

On X's AK layer (`l_akX`), at Y's key position, place the replacement:

```dtsi
// Chain ends (most common):
&bk Z       // types Z, no AK layer activates

// Chain continues (when Z has its own AK replacements):
ak_Z        // types Z AND activates l_akZ
```

**Example:** M→T produces MN

```dtsi
// On l_akM in layers_B_NAQUADAH_adaptive_keys.dtsi:
// At LM1 (T's alpha position):
&bk N
```

**Chaining example:** M→K produces MB, chain continues into B's AK layer:

```dtsi
// On l_akM, at LT0 (K's alpha position):
ak_B    // NOT &bk B — use ak_B so the chain continues
```

See [ak-deepdive.md](ak-deepdive.md) for the full chaining mechanism.

---

### Recipe 10: AK — First Character Changes (`REPLACE_CHAR_WITH_BIGRAM`)

> ⚠️ **Partially reviewed** — structure is correct but examples may need improvement.

**I want:** typing XY to produce AB instead (the already-typed first character is retroactively replaced).

The macro deletes X, types A, then fires `ak_B` — so this type **always chains**.

**Files:** `adaptive_keys/macros.dtsi` + `adaptive_keys/aliases.dtsi` + `layers_B_*_adaptive_keys.dtsi`

**Prerequisites:** same as Recipe 9.

**Steps:**
```dtsi
// 1. In adaptive_keys/macros.dtsi — instantiate the replacement:
REPLACE_CHAR_WITH_BIGRAM(A, B)
//    Creates &replace_char_with_bigram_AB which:
//    backspace → type A → clear shifts → fire ak_B (chains!)

// 2. In adaptive_keys/aliases.dtsi — readable alias:
#define XY_to_AB  &replace_char_with_bigram_AB

// 3. On l_akX in layers_B_*_adaptive_keys.dtsi, at Y's position:
XY_to_AB
```

**Example:** C→P produces TP (instead of CP)
- `REPLACE_CHAR_WITH_BIGRAM(T, P)` in macros.dtsi
- `#define CP_to_TP &replace_char_with_bigram_TP` in aliases.dtsi
- On `l_akC`, at LT1 (P's alpha position): `CP_to_TP`

**Note:** always chains — after the replacement, B's AK layer (`l_akB`) is active. See [ak-deepdive.md](ak-deepdive.md) for details.

---

### Recipe 11: AK on Home-Row Mod Key

> ⚠️ **Not yet reviewed** — this recipe hasn't been verified for accuracy.

**I want:** a key that acts as a home-row mod (hold=modifier) but also triggers AKs on tap.

**Note:** this pattern isn't currently active in the layout, but documents a known technique for future use.

**Files:** `mods/behaviors.dtsi`

**Template:**
```dtsi
// 1. Create an AK macro wrapper:
ZMK_MACRO(ak_X_macro, wait-ms = <0>; tap-ms = <0>; bindings = <&ak l_akX X>;)

// 2. Create a custom HRM that taps the AK macro instead of &bk:
hml_X: hml_X {
    compatible = "zmk,behavior-hold-tap";
    label = "hml_X";
    #binding-cells = <2>;
    tapping-term-ms = <my_tapping_term_main>;
    hold-trigger-key-positions = <THUMBS_R KEYS_R>;  // or THUMBS_L KEYS_L for right hand
    hold-trigger-on-release;
    flavor = "balanced";
    bindings = <&bm>, <&ak_X_macro>;
};

// 3. Define alias for layer file:
#define hml_LCTRL_X  &hml_X LCTRL XXX
```

**Example:** `hml_S` — tap=ak_S (activates AK layer + types S), hold=buffered modifier

---

## Thumb Cluster

### Recipe 12: Layer-Tap With AK

> ⚠️ **Not yet reviewed** — this recipe hasn't been verified for accuracy.

**I want:** a thumb key that activates an AK on tap and a layer on hold.

**Files:** `adaptive_keys/behaviors.dtsi`

**Template:**
```dtsi
// 1. Create AK macro wrapper:
ZMK_MACRO(ak_X_macro, wait-ms = <0>; tap-ms = <0>; bindings = <&ak l_akX X>;)

// 2. Create hold-tap:
blt_akX: blt_akX {
    compatible = "zmk,behavior-hold-tap";
    #binding-cells = <2>;
    flavor = "tap-preferred";
    tapping-term-ms = <my_tapping_term_thumb>;
    bindings = <&mo>, <&ak_X_macro>;
};

// 3. Define alias:
#define myThumbKey  &blt_akX l_myLayer XXX
```

**Example:** `nav_akR` — tap=AK-R, hold=nav layer

---

### Recipe 13: Sticky Shift + Mod Layer (Action Button)

> ⚠️ **Not yet reviewed** — this recipe hasn't been verified for accuracy.

**I want:** a thumb key that triggers sticky shift on tap and activates a mod/action layer on hold.

**Files:** `mods/macros.dtsi` + `mods/behaviors.dtsi`

**How it works:** uses `htls` (hold-tap-layer-sticky), which combines `&moAndBuffer` (hold: activates layer with timing buffer) and `&skms` (tap: sticky shift that doesn't ignore modifiers).

**Template:**
```dtsi
// Already defined — just create a new alias with your layer and modifier:
#define myActionButton  &htls l_myLayer LSHIFT
```

**Example:** `#define tapStickyShiftHoldModsLayer &htls l_mod LSHIFT`

**Gotchas:**
- `moAndBuffer` currently has `l_mod` hardcoded. To use a different layer, you'd need to parameterize it or create a new macro.
- The modifier parameter (e.g., `LSHIFT`) is passed to `&skms` for the tap (sticky) behavior. You can change it to `LCTRL`, `LALT`, etc. — but `&skms` was designed for shift. For other modifiers, verify `skms` behavior suits your needs or create a variant.

---

## Utility

### Recipe 14: Typing Macro

**I want:** a key sequence (multiple keypresses fired in order).

**Files:** `macros.dtsi`

**Template:**
```dtsi
TYPING_MACRO(myMacro, &kp KEY1 &kp KEY2 &kp KEY3)
```

**What it expands to:** a `ZMK_MACRO` with standardized timing (wait=10ms, tap=10ms).

**Example:** `TYPING_MACRO(arrowRightSingle, &kp SPACE &kp MINUS &kp GREATER_THAN &kp SPACE)` → ` -> `

---

### Recipe 15: Single-Char Wrapper Macro

**I want:** a macro that types a single character, for use as an LK binding.

**Why:** `LK(name, TAP, LINGER)` takes behavior references. When both tap and linger should be macros, all custom LKs follow the `XXX XXX` pattern. If one output is a single char, wrap it in a TYPING_MACRO instead of using `&bk` directly — this keeps the pattern consistent and avoids the hybrid `XXX KEYCODE` anti-pattern.

**Why `&kp` and not `&bk`:** `&bk` exists to solve a key-ordering problem that occurs when `&kp` is used directly in behaviors (hold-taps, mod-morphs, etc.). It solves this by wrapping `&kp` in a macro internally. Since `TYPING_MACRO` already *is* a macro, `&kp` works correctly inside it — using `&bk` here would be double-wrapping (a macro inside a macro), which is unnecessary.

**Files:** `macros.dtsi`

**Template:**
```dtsi
// In macros.dtsi (near other single-char wrappers):
// Single-char wrappers: LK needs macro bindings (not &bk),
// so we wrap single keys to keep all Magic LKs using the same XXX XXX pattern
TYPING_MACRO(typeMyKey, &kp KEYCODE)
```

**Example:** `TYPING_MACRO(typeSlash, &kp FSLH)` — used in `LK(magicSlashHome, &typeSlash, &tildeSlash)`
