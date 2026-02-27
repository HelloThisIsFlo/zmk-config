# Flo's Magic ZMK Config

ZMK firmware configuration for a Corne (Chocofi) split keyboard with Nice Nano v2 controllers. Three custom layouts -- Naquadah (active), Promethium, and Rhodium -- all built around an Adaptive Keys system that eliminates Same-Finger Bigrams.

### [**Explore the Interactive Timing Systems Visualization**](https://hellothisisflo.github.io/zmk-config/)
> See how Adaptive Keys, combos, linger keys, and all the timing systems interact -- with animated diagrams and detailed breakdowns.

## Design Documentation

Start here to understand the keyboard:

- **[`Design/PHILOSOPHY.md`](Design/PHILOSOPHY.md)** -- Why the keyboard works this way. Principles, preferences, ergonomic thinking.
- **[`Design/PHILOSOPHY_LOG.md`](Design/PHILOSOPHY_LOG.md)** -- The story of ergonomic decisions, chronological.
- **[`Design/MECHANICS.md`](Design/MECHANICS.md)** -- How the technical systems work under the hood.
- **[`Design/MECHANICS_LOG.md`](Design/MECHANICS_LOG.md)** -- The story of technical decisions, chronological.

The technical infrastructure is mature and stable. The ongoing work is iterating on bindings -- what key does what, adjusting combos, rethinking symbol placements, optimizing for ergonomics.

## Alpha Layout: Naquadah

> **The driving question:** What if we built a layout that _required_ adaptive keys?

Naquadah is a heavy variation of HandsDown Titanium -- so heavily modified it's practically unrecognizable. Its core principles are:
- Adaptive Keys are **NOT** optional (this layout is useless without AKs)
- It should feel like it "flows":
  - Extremely low SFB: **0.082%** (See `sfb.py` in `Analysis/Scripts`)
  - Low Redirects (~<2%)
  - IN Rolls >> OUT Rolls
  - The few SFBs left should ideally be on syllable breaks

### Naquadah and its 46 AKs
_Designed for heavy column-stagger keyboards (Chocofi)_

```
Naquadah layout:
================
   w  m  p  k              /  .  -  =
x                                      '
   s  n  t  v              ,  a  e  i
c                                      h
   g  l  d  b              _  u  o  y
f                                      j

                r      space

The position of the special chars is still in flux (only . , ' are fixed)

The 46 accompanying AKs:
============
## SFB AKs ###################################
"A- => AU"
"U- => UA"

"E= => EO"
"O= => OE"  # Better than OH because of "Oh! really?"

"GF => GS"

"LG => LL"
"LX => LG"  # To remove SFB caused by LG => LM (aLGorithm)

"NP => NN"  # NP is rarely used in "flow", essentially mostly in "input". The rest is "un-" words

"MT => MN"
"NX => NM"

"PN => PD"  # Essentially just for 'update'

"PC => PT"  # Better that "PN => PT" because of 'M->P->T' (and 'P->T->S' remains doable relatively easily)
"CP => TP"  # For 'ouTPut'

"SR => SW"
"WX => WS"

"YH => YI"  # More comfortable than YJ => YI
"XS => XC"

"WM => LM"
##############################################



## IMPOSSIBLE Movements (on Chocofi) #########
"SX => SF"
"MK => MB"
"KM => BM"  # Useful because of the "MK => MB" muscle memory
"PB => NB"  # & Use alt-fingering
##############################################


## Comfort AKs ###############################
"DV => LV"
"DK => LK"
"VD => VL"
"KD => KL"
"DB => LB"
"BD => BL"
"DF => DV"  # To remove SFB caused by DV => LV


"TV => NV"
"VT => VN"

"PG => PL"  # For M->P->L, but also for regular P->L
"GP => LP"
"KG => KL"
"GK => LK"
"BG => BL"  # For M->B(k)->L
##############################################


## Repeat AKs ################################
## Only for pinkies & ring fingers (skipped II because it's so rare)
"E. => EE"
"FG => FF"
"SD => SS"
"BC => BB"
"CG => CC"  # CD would technically work, but it would make using the terminal a nightmare
"GC => GG"
"PW => PP"  # Not using PM because of 6PM, 7PM, ...
"MW => MM"
"NW => NL"  # On 'NW' instead of 'NP' to keep the more comfortable 'NP' move for 'NN' (and 'WNL' awkward for 'doWNLoad in one move anyway)
"O. => OO"  # May need to increase the timing of adaptive keys to make this one more reliable
"RX => RR"
"TG => TT"
"DC => DD"
##############################################


## Special Cases #############################
"hE. => hEI"
"hEU => hEY"
##############################################
```

## Key Concepts

### Adaptive Keys
_Concept by [Alan Reiser](https://sites.google.com/alanreiser.com/handsdown/home/hands-down-neu) (Hands Down layouts)_

Keys that behave differently when pressed in quick succession, virtually eliminating all remaining SFBs. The system uses a layer-per-AK architecture -- each of the 46 AKs gets its own dedicated layer. Combos detect key sequences within a 100ms window, then macros replace the output with the intended bigram.

Very reliable -- no missed keys in over a year, tested at 200wpm+ burst typing. See [`Design/MECHANICS.md`](Design/MECHANICS.md) for the full technical breakdown.

### Callum-Style Mods
_Concept by [Callum](https://github.com/callum-oakley/qmk_firmware/tree/master/users/callum)_

Replaced home row mods after a year of tweaking -- love at first sight. One-shot mods on tap (chaining and stacking), regular hold behavior. The timing guarantee (correct order = correct result) removes all ambiguity.

### Other Concepts
- **Linger Keys** (Alan Reiser) -- Tap for one action, hold for a related action. Used for H-digraphs (`th`, `sh`, `gh`), bracket variants, and more.
- **Magic Parenthesis** -- One combo, four bracket types depending on hold duration and shift state.
- **Wispr Combo** (S+N) -- Dictation shortcut. Tap for Opt+R, hold for Globe key. Eliminated thumb strain from repeated layer activation.
- **Switch Device** -- Switches Bluetooth device and activates its associated layer.

## Architecture & Build

See [`CLAUDE.md`](CLAUDE.md) for full architecture documentation, file navigation, build and flash instructions, and the `/layout` skill for collaborative binding iteration.

## Credits

- **Alan Reiser** -- [Hands Down layouts](https://sites.google.com/alanreiser.com/handsdown). Adaptive Keys, linger keys, and the analytical foundation that made Naquadah possible.
- **Callum Oakley** -- [Callum-style mods](https://github.com/callum-oakley/qmk_firmware/tree/master/users/callum). One-shot mod system.
