# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What We're Working On

The technical infrastructure of this keyboard config is mature and stable. The main work these days is **iterating on the bindings** — tweaking what key does what, adjusting combos, rethinking symbol placements, optimizing for ergonomics.

At the start of a session, offer to load the `/layout` skill to help brainstorm and make binding changes together. Most sessions will be about this.

## Design Documents

Four documents in `Design/` capture the keyboard philosophy, technical mechanics, and decision history:
- `Design/PHILOSOPHY.md` — The user's approach, principles, and preferences (living summary, refined over time)
- `Design/PHILOSOPHY_LOG.md` — Chronological log of ergonomic/binding decisions and experiments (append-only, newest first)
- `Design/MECHANICS.md` — How the technical systems work under the hood (living reference, organized by topic)
- `Design/MECHANICS_LOG.md` — Chronological log of technical/architectural decisions (append-only, newest first)
- `Design/COOKBOOK.md` — Implementation recipes for adding new key behaviors ("I want X — what pattern do I use?")

These are maintained collaboratively during layout sessions. See the `/layout` skill for when and how to update them.

## Project Overview

ZMK firmware configuration for split keyboards, currently two Chocofi units (36-key Corne, nice!nano v2 or Pro Micro nRF52840 clones). One shared layout, built per physical keyboard (see *Config Hierarchy*). The project centers on three custom keyboard layouts (Naquadah, Promethium, Rhodium) built around an **Adaptive Keys (AKs) system** that eliminates Same-Finger Bigrams.

## Build & Flash

There are no local tests. The only validation is successful compilation.

```bash
# Requires local ZMK checkout at ../zmk. Auto-starts the zmk-devcontainer.
../zmk/build_and_flash.sh <unit> left|right|both          # Build, then prompt to double-tap reset on each half
../zmk/build_and_flash.sh <unit> reset                     # Flash settings_reset to both halves
../zmk/build_and_flash.sh chocofi-pro both --no-flash      # Build only (verify compilation)
../zmk/build_and_flash.sh chocofi-pro both --pristine      # Full rebuild (after adding a .conf file or editing targets.txt)
```

Units (physical keyboards) are listed in `config/targets.txt`: `chocofi-og`, `chocofi-pro`. Running the script with no arguments lists them. If the board is already in bootloader mode when the build finishes, it's flashed right away.

**Split roles**: the **right** half is central (keymap + host Bluetooth + the working nice!view), the left is peripheral. Set in `config/keyboards/chocofi/corne_left.conf` / `config/keyboards/chocofi/corne_right.conf`, which also hold per-side overrides (left sleeps after 2h, right after 20 min from `keyboards/chocofi/corne.conf`). Changing roles requires `reset` on both halves, then re-pairing.

**Build success**: ends with `Linking C executable zephyr/zmk.elf` and `Wrote X bytes to zmk.uf2`.

**Build failure**: look for `devicetree error:` with parse errors — check the column number for exact location.

Builds run locally in the `zmk-devcontainer` Docker container (no CI build). Uses a custom ZMK fork at `https://github.com/HelloThisIsFlo/zmk`.

## Formatting

**Do not auto-format files.** This is an explicit project decision (`.vscode/settings.json` has `formatOnSave: false`). The `.dtsi` files use careful manual alignment.

## Architecture

### Config Hierarchy

Four independent axes, one folder each:

```
config/
  layout/              🧠 bindings, keyboard-agnostic: layout.dtsi (orchestrator), CONFIG.h, features/
  keyboards/chocofi/   ⌨️ one folder per model = ZMK config dir: corne.keymap, positions.dtsi, corne*.conf
  units/               🏷️ one .conf per physical keyboard (name + per-unit tweaks)
  targets.txt          🎯 unit → keyboard, board, shields
```

- Kconfig levels cascade, later wins: `keyboards/<model>/corne.conf` → `corne_<side>.conf` → `units/<unit>.conf`
- Each setting lives in exactly one level; the keyboard name lives only in `units/`
- Files in `keyboards/chocofi/` keep `corne.*` names: ZMK finds keymap/conf files by shield name
- `keyboards/<model>/corne.keymap` = positions + `#include "../../layout/layout.dtsi"` + physical layout
- Planned: a 42-key model becomes canonical (layout written for 42, 36-key boards drop the outer columns); Charybdis with trackball later. See `Design/MECHANICS.md` → Config Hierarchy

### Orchestrator Pattern

`config/layout/layout.dtsi` is the central orchestrator. It includes all features in strict dependency order via `#include` directives. **Inclusion order matters** — aliases before macros, macros before behaviors, behaviors before combos, combos before layers.

### Layout Selection

Layouts are selected via `#define` in `config/layout/CONFIG.h`. The active layout is whichever is defined last (all three are currently defined, so NAQUADAH wins due to `#if defined` priority in `layout.dtsi`).

### Feature Module Structure

Each feature under `config/layout/features/` follows a consistent pattern with optional files:
- `aliases.dtsi` — name definitions
- `macros.dtsi` — macro sequences
- `behaviors.dtsi` — custom behaviors
- `combos.dtsi` — key combinations

### Key Directories

- `config/layout/features/__BASE__/` — Core infrastructure: layer aliases per layout, preprocessor macro definitions, default behavior config
- `config/layout/features/hands_down/` — Main layout implementation: alpha layers, adaptive keys, mods, linger keys, combos, h-digraphs, pronouns
- `config/layout/features/hands_down/adaptive_keys/` — The AK system (the core innovation)
- `config/layout/features/__EXPERIMENT__/` — Experimental features (enabled via `#define EXPERIMENT` in CONFIG.h)
- `config/layout/features/hands_down/zz__INVESTIGATE__zz/` — Experimental/disabled features

### Layer System

Layers are numbered 0–31 (uint32_t bitmask). Per layout, there are three tiers:
- **Layer A** (`layers_A_*_alpha.dtsi`) — Base alpha layer + Linux/Windows variant
- **Layer B** (`layers_B_*_adaptive_keys.dtsi`) — 23 adaptive key layers (one per AK trigger)
- **Layer C** (`layers_C_extra.dtsi`) — Shared layers: nav, mod, fn, num, numsym, cfg

### Key Position Naming

Defined per keyboard in `keyboards/<model>/positions.dtsi`. Format: `{L|R}{T|M|B|H}{0-4}` where L/R=hand, T/M/B=top/middle/bottom row, H=thumb, 0=innermost.

```
╭─────────────────────╮ ╭─────────────────────╮
│ LT4 LT3 LT2 LT1 LT0 │ │ RT0 RT1 RT2 RT3 RT4 │
│ LM4 LM3 LM2 LM1 LM0 │ │ RM0 RM1 RM2 RM3 RM4 │
│ LB4 LB3 LB2 LB1 LB0 │ │ RB0 RB1 RB2 RB3 RB4 │
╰───────╮ LH2 LH1 LH0 │ │ RH0 RH1 RH2 ╭───────╯
        ╰──────────────╯ ╰──────────────╯
```

### Preprocessor Macros

`config/layout/features/__BASE__/preprocessor_macros.c` defines key macros used throughout:
- `________` / `xxxxxxxx` — transparent / none key shortcuts
- `COMBO_ANY_ONE_HAND`, `COMBO_ANY_TWO_HAND`, `COMBO_LAY_*` — combo definition helpers with pre-set timeouts
- `REPLACE_CHAR_WITH_BIGRAM(A, B)` — generates AK replacement macros
- `LK(NAME, TAP, LINGER)` — generates linger key behaviors
- `TYPING_MACRO(NAME, BINDINGS)` — shorthand for typing macros

### Timing Constants

All timing lives in `config/layout/CONFIG.h`:
- `my_ak_window` (100ms) — adaptive key detection window
- `linger_term` (100ms) — tap-hold decision time
- Combo timeouts: adjacent=16ms, non-adjacent=18ms, two-hand=30ms
- `ak_tap_time` (10ms) and `hold_key_event_delay` (11ms) — AK macro internals

## Adaptive Keys

AKs are **not optional** — the layouts are designed around them. They work by using combos to detect key sequences within the `my_ak_window` (100ms), then executing macros that replace the typed output.

Categories: SFB elimination, comfort improvements, repeat keys, impossible movements, special cases.

Each AK gets its own layer (l_akA through l_akY). The `aksl` behavior (adaptive key sticky layer) activates the appropriate AK layer for the detection window.

## Analysis Tools

`Analysis/Scripts/sfb.py` calculates Same-Finger Bigram rates. Layout definitions are in `Analysis/Scripts/layout_naquadah_RC*.py`. Bigram frequency data is in `Analysis/Data/`.
