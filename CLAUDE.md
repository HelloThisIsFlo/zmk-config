# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ZMK firmware configuration for a Corne (Chocofi) split keyboard with Nice Nano v2 controllers. The project centers on three custom keyboard layouts (Naquadah, Promethium, Rhodium) built around an **Adaptive Keys (AKs) system** that eliminates Same-Finger Bigrams.

## Build & Flash

There are no local tests. The only validation is successful compilation.

```bash
# Build and flash (requires local ZMK checkout at ../zmk)
../zmk/build_and_flash.sh left    # Build + flash left half
../zmk/build_and_flash.sh right   # Build + flash right half

# Flash from GitHub Actions artifact (keyboard must be in bootloader mode)
./flash.sh left
./flash.sh right
```

**Build success**: ends with `Linking C executable zephyr/zmk.elf` and `Wrote X bytes to zmk.uf2`. The error `cp: directory /Volumes/NICENANO does not exist` is expected when the keyboard is not plugged in.

**Build failure**: look for `devicetree error:` with parse errors — check the column number for exact location.

GitHub Actions builds automatically on pushes to `config/**`. Uses a custom ZMK fork at `https://github.com/HelloThisIsFlo/zmk`.

## Formatting

**Do not auto-format files.** This is an explicit project decision (`.vscode/settings.json` has `formatOnSave: false`). The `.dtsi` files use careful manual alignment.

## Architecture

### Orchestrator Pattern

`config/corne.keymap` is the central orchestrator. It includes all features in strict dependency order via `#include` directives. **Inclusion order matters** — aliases before macros, macros before behaviors, behaviors before combos, combos before layers.

### Layout Selection

Layouts are selected via `#define` in `config/CONFIG.h`. The active layout is whichever is defined last (all three are currently defined, so NAQUADAH wins due to `#if defined` priority in `corne.keymap`).

### Feature Module Structure

Each feature under `config/features/` follows a consistent pattern with optional files:
- `aliases.dtsi` — name definitions
- `macros.dtsi` — macro sequences
- `behaviors.dtsi` — custom behaviors
- `combos.dtsi` — key combinations

### Key Directories

- `config/features/__BASE__/` — Core infrastructure: key position aliases, layer aliases per layout, preprocessor macro definitions, default behavior config
- `config/features/hands_down/` — Main layout implementation: alpha layers, adaptive keys, mods, linger keys, combos, h-digraphs, pronouns
- `config/features/hands_down/adaptive_keys/` — The AK system (the core innovation)
- `config/features/__EXPERIMENT__/` — Experimental features (enabled via `#define EXPERIMENT` in CONFIG.h)
- `config/features/hands_down/zz__INVESTIGATE__zz/` — Experimental/disabled features

### Layer System

Layers are numbered 0–31 (uint32_t bitmask). Per layout, there are three tiers:
- **Layer A** (`layers_A_*_alpha.dtsi`) — Base alpha layer + Linux/Windows variant
- **Layer B** (`layers_B_*_adaptive_keys.dtsi`) — 23 adaptive key layers (one per AK trigger)
- **Layer C** (`layers_C_extra.dtsi`) — Shared layers: nav, mod, fn, num, numsym, cfg

### Key Position Naming

Defined in `__BASE__/aliases_key_positions.dtsi`. Format: `{L|R}{T|M|B|H}{0-4}` where L/R=hand, T/M/B=top/middle/bottom row, H=thumb, 0=innermost.

```
╭─────────────────────╮ ╭─────────────────────╮
│ LT4 LT3 LT2 LT1 LT0 │ │ RT0 RT1 RT2 RT3 RT4 │
│ LM4 LM3 LM2 LM1 LM0 │ │ RM0 RM1 RM2 RM3 RM4 │
│ LB4 LB3 LB2 LB1 LB0 │ │ RB0 RB1 RB2 RB3 RB4 │
╰───────╮ LH2 LH1 LH0 │ │ RH0 RH1 RH2 ╭───────╯
        ╰──────────────╯ ╰──────────────╯
```

### Preprocessor Macros

`config/features/__BASE__/preprocessor_macros.c` defines key macros used throughout:
- `________` / `xxxxxxxx` — transparent / none key shortcuts
- `COMBO_ANY_ONE_HAND`, `COMBO_ANY_TWO_HAND`, `COMBO_LAY_*` — combo definition helpers with pre-set timeouts
- `REPLACE_CHAR_WITH_BIGRAM(A, B)` — generates AK replacement macros
- `LK(NAME, TAP, LINGER)` — generates linger key behaviors
- `TYPING_MACRO(NAME, BINDINGS)` — shorthand for typing macros

### Timing Constants

All timing lives in `config/CONFIG.h`:
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
