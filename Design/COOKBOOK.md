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
| AK combos (per layout) | `config/features/hands_down/adaptive_keys/combos_NAQUADAH.dtsi` |
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

Use this recipe whenever **any** output is more than one character. If one output is a single char, wrap it with Recipe 14 (single-char wrapper) to keep the `XXX XXX` pattern consistent.

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
// Single-char outputs get wrapped too (Recipe 14) for XXX XXX consistency:
TYPING_MACRO(myTapMacro,         &kp X)
TYPING_MACRO(myShiftTapMacro,    &kp Y)

// 2. In linger_keys/behaviors.dtsi — create LKs:
LK(myUnshifted, &myTapMacro, &myLingerMacro)          // tap=X    linger=AB
LK(myShifted,   &myShiftTapMacro, &myShiftLingerMacro) // tap=Y    linger=CD

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

### Recipe 9: Standard AK (SFB Elimination)

**I want:** typing `XY` gets replaced with `AB` to eliminate a same-finger bigram.

**Files:** `adaptive_keys/macros.dtsi` + `adaptive_keys/aliases.dtsi` + `adaptive_keys/combos_LAYOUTNAME.dtsi`

**Steps:**
```dtsi
// 1. In adaptive_keys/macros.dtsi — define the replacement:
REPLACE_CHAR_WITH_BIGRAM(A, B)
//    This creates &replace_char_with_bigram_AB which:
//    backspace → type A → clear shift → activate ak_B

// 2. In adaptive_keys/aliases.dtsi — create a readable alias:
#define XY_to_AB  &replace_char_with_bigram_AB

// 3. In adaptive_keys/combos_LAYOUTNAME.dtsi — add the combo on X's AK layer:
COMBO_LAY_BASE(l_akX, XY_to_AB_cb, XY_to_AB, KEY_POSITION_OF_Y, my_combo_timeout_adjacent)
```

**Prerequisites:** the trigger key X must already have `#define ak_X &ak l_akX X` in aliases and an AK layer defined in `layers_B_*_adaptive_keys.dtsi`.

**Example:** `REPLACE_CHAR_WITH_BIGRAM(S, B)` + `#define CB_to_SB &replace_char_with_bigram_SB`

---

### Recipe 10: AK on Home-Row Mod Key

**I want:** a key that acts as a home-row mod (hold=modifier) but also triggers AKs on tap.

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

### Recipe 11: Layer-Tap With AK

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

### Recipe 12: Sticky Shift + Mod Layer (Action Button)

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

### Recipe 13: Typing Macro

**I want:** a key sequence (multiple keypresses fired in order).

**Files:** `macros.dtsi`

**Template:**
```dtsi
TYPING_MACRO(myMacro, &kp KEY1 &kp KEY2 &kp KEY3)
```

**What it expands to:** a `ZMK_MACRO` with standardized timing (wait=10ms, tap=10ms).

**Example:** `TYPING_MACRO(arrowRightSingle, &kp SPACE &kp MINUS &kp GREATER_THAN &kp SPACE)` → ` -> `

---

### Recipe 14: Single-Char Wrapper Macro

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
