# Known Inconsistencies

> Documented inconsistencies in the codebase, tracked for future cleanup.
> Each category includes an exhaustive inventory so the fix can be done in one pass.

---

## 1. `lk` vs `lk_bk` Duplication and Alias Scatter

### The Problem

Two functionally identical linger key behaviors exist:
- `lk` — hand-written at the top of `linger_keys/behaviors.dtsi`
- `lk_bk` — macro-generated via `LK(bk, &bk, &bk)` in the same file

Both have identical definitions: `bindings = <&bk>, <&bk>;` with `tap-preferred` flavor and `linger_term` timing.

Aliases that use these behaviors are scattered across two files with inconsistent naming conventions. There's also a duplicate alias (`sqtdqt` vs `sqtDqt`).

### Exhaustive Inventory

#### Behavior Definitions (both in `linger_keys/behaviors.dtsi`)

| Behavior | How Defined | Lines |
|----------|-------------|-------|
| `lk` | Hand-written | 2-9 |
| `lk_bk` | `LK(bk, &bk, &bk)` macro | 33 |

#### All `&lk` Usages

**`#define` aliases in `aliases.dtsi`:**
- `#define dotcol  &lk COLON DOT` (line 25)
- `#define comsemi &lk SEMI CMMA` (line 26)
- `#define sqtdqt  &lk DQT SQT` (line 27) — lowercase naming

**`#define` aliases in `linger_keys/behaviors.dtsi`:**
- `#define tabAlttab &lk LA(TAB) TAB` (line 29)
- `#define tabCmdtab &lk LG(TAB) TAB` (line 30)

**Inside mod-morph behavior bindings (`mod_morph/behaviors.dtsi`):**
- `MagicBracketsL`: `<&lk LEFT_BRACKET LEFT_PARENTHESIS>, <&lk LEFT_BRACE LESS_THAN>` (line 170)
- `MagicBracketsR`: `<&lk RIGHT_BRACKET RIGHT_PARENTHESIS>, <&lk RIGHT_BRACE GREATER_THAN>` (line 178)
- `MagicUnder` (shifted side): `<&lk BSLH STAR>` (line 143)

**Inside experimental behaviors (`__EXPERIMENT__/behaviors.dtsi`):**
- `aB_cD`: `<&lk C A>, <&lk D B>` (line 20)

#### All `&lk_bk` Usages

**`#define` aliases in `linger_keys/behaviors.dtsi`:**
- `#define sqtDqt  &lk_bk DQT SQT` (line 38) — camelCase naming
- `#define equalDash  &lk_bk MINUS EQUAL` (line 39)

#### The Duplicate: `sqtdqt` vs `sqtDqt`

| Alias | File | Behavior | Used By |
|-------|------|----------|---------|
| `sqtdqt` (lowercase) | `aliases.dtsi` | `&lk` | `layers_A_alpha.dtsi` (generic layout) |
| `sqtDqt` (camelCase) | `linger_keys/behaviors.dtsi` | `&lk_bk` | `layers_A_NAQUADAH_alpha.dtsi` |

Other layouts handle this differently:
- Promethium: uses `&bk SQT` directly (no linger)
- Rhodium: disabled (FIXME comment)

#### `equalDash` — Only in `lk_bk`

- Defined: `linger_keys/behaviors.dtsi` as `&lk_bk MINUS EQUAL`
- Used: `layers_A_NAQUADAH_alpha.dtsi` only
- Other layouts use `&DashEqual` (a mod-morph) instead

### Resolution (Decided, Not Yet Actioned)

1. **Use `&lk_bk` everywhere** for single-char linger aliases. Replace all `&lk` usages in `#define` aliases with `&lk_bk`.
2. **Consolidate aliases into `linger_keys/behaviors.dtsi`**. Remove the linger-key-related `#define`s from `aliases.dtsi` (`dotcol`, `comsemi`, `sqtdqt`). The `aliases.dtsi` file keeps its HRM aliases — only linger key aliases move.
3. **Remove duplicates**: delete `sqtdqt` (lowercase) from `aliases.dtsi`, keep only `sqtDqt` in `linger_keys/behaviors.dtsi`.
4. **Standardize naming**: all linger aliases use camelCase (`dotCol`, `comSemi`, `sqtDqt`, `equalDash`).
5. **Keep hand-written `lk` behavior** for use inside mod-morph bindings (e.g., `MagicBracketsL`'s `&lk LEFT_BRACKET LEFT_PARENTHESIS`), where inline keycodes read more naturally than `&lk_bk`. But `#define` aliases for layers must use `&lk_bk`.

---

## 2. `h_digraphs/` as a Separate Feature Module

### The Problem

The `h_digraphs/` folder exists as its own feature module with `macros.dtsi` and `combos.dtsi`, implying h-digraphs are a distinct concept. In reality, they're just combo-triggered linger keys — the same pattern as any other combo that fires an LK. The separate folder is a historical artifact from importing Hands Down's original structure, where h-digraphs were a named concept.

### What's in `h_digraphs/`

- `h_digraphs/macros.dtsi` — digraph macros (`Th`, `Sh`, `Ch`, `Wh`, `Gh`, `Ph`, `Sch`, `Tch`, plus linger variants `tion`, `sion`, `ght`)
- `h_digraphs/combos.dtsi` — 8 combos (3 with linger via LK: `th`, `sh`, `gh`; 5 plain: `sch`, `tch`, `ch`, `wh`, `ph`)

### Resolution (Not Yet Actioned)

Low priority — the folder structure works fine, it's just conceptually misleading. The macros and combos should be absorbed into the main `macros.dtsi` and `combos.dtsi` files, and the `h_digraphs/` folder removed. They're just combo-triggered linger keys — no reason for a separate feature module.

---

## 3. Missing Preprocessor Macros for Some Behavior Types

### The Problem

Some behavior types have preprocessor macros that eliminate boilerplate:
- **Linger keys**: `LK(NAME, TAP, LINGER)` — one line generates a full hold-tap behavior
- **Combos**: `COMBO_LAY_ONE_HAND(...)`, `COMBO_ANY_TWO_HAND(...)` — one line generates a full combo
- **Typing macros**: `TYPING_MACRO(NAME, BINDINGS)` — one line generates a full ZMK macro

But other behavior types require writing out the full ZMK definition manually:
- **Mod-morphs**: 7 lines of boilerplate per definition (`compatible`, `label`, `#binding-cells`, `bindings`, `mods`)
- **Magic keys** (mod-morph + linger): even more boilerplate since they combine multiple behaviors

This makes some recipes (like Recipe 6: Magic Key) verbose compared to others.

### Resolution (Not Yet Actioned)

Create preprocessor macros in `__BASE__/preprocessor_macros.c` for the remaining behavior types. For example:
- `MOD_MORPH_SHIFT(NAME, NORMAL, SHIFTED)` — generates a shift-based mod-morph
- `MOD_MORPH_ALT(NAME, NORMAL, SHIFTED)` — generates an alt-based mod-morph
- Potentially a `MAGIC_KEY(NAME, TAP, LINGER, SHIFT_TAP, SHIFT_LINGER)` that generates the full mod-morph + LK chain
