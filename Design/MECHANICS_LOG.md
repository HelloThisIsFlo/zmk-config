# Mechanics Log

> Chronological log of technical and architectural decisions. Not layout
> choices (those go in the Philosophy Log) -- this captures the engineering:
> architecture shifts, timing discoveries, infrastructure evolution, and
> the technical reasoning behind how things work.
>
> Newest entries first.

---

## 2026-02-26 -- Hold pattern for linger keys (&kp vs &bk)

**Context**: The wispr dictation combo (S+N) needed two modes: tap for Opt+R
(toggle dictation) and hold for Globe key (transient dictation -- dictate while
held, stop on release). Existing linger keys all use `&bk` on both sides,
which taps keys. But for transient dictation, the Globe key needs to actually
be held, not tapped.

**Decision**: Created `lk_wispr` with `bindings = <&kp>, <&bk>` -- using `&kp`
on the hold side instead of the standard `&bk`. This is the first linger key
in the codebase with this pattern.

**Reasoning**: `&bk` wraps `&kp` in a macro that does `macro_tap` (press +
immediate release). This is perfect for outputting characters but wrong for
hold behaviors. `&kp` on the hold side of a hold-tap stays pressed when the
hold-tap resolves as "hold" and releases when the physical key is released.
ZMK's hold-tap lifecycle management does the right thing: press Globe on hold
detection, release Globe on combo release. macOS sees this as "Globe key is
being held" and activates transient dictation.

**Outcome**: Works perfectly. Opens a new pattern -- any future linger key that
needs true key holding (not just character output) can use `&kp` on the hold
side.

---
---

# Previously on... (Sep 2023 -- Feb 2026)

> This mechanics log started on February 26, 2026, but the engineering
> underneath the keyboard has been evolving for over two years and 600+ commits.
> Here's the technical story.

**Sep 2023 -- The buffered key invention.** The project starts by importing
Adaptive Key and linger key concepts from Moutis' Hands Down ZMK derivative --
Alan Reiser's Hands Down project pioneered the idea of detecting key sequences
and replacing output to eliminate Same-Finger Bigrams. With the AK concept in
place alongside a standard Corne template and basic Home Row Mods, a critical
timing problem surfaces almost immediately: AK detection fires macros that
output keys, but without careful timing, keypresses arrive out of order or get
dropped entirely. The solution is deceptively simple -- `&bkp` (buffered key
press), a custom ZMK behavior that wraps `&kp` in a macro with a 10ms tap
delay. That tiny buffer ensures every keypress registers cleanly, in order.
This was not part of the original Hands Down implementation -- it was invented
here to make AKs actually reliable. Within days, all relevant `&kp` calls are
migrated to `&bkp`. The buffered key concept (renamed to `&bk` in its modern
form) remains the foundation of the entire system. Every character output in
the codebase flows through it.

**Sep-Oct 2023 -- The AK layer-per-character system.** While the concept of
Adaptive Keys came from Hands Down, the imported system had no prescribed
architecture for scaling them. Early experiments quickly surface a design
question: how do you detect a two-key sequence and replace it? The answer
becomes one of the project's most pivotal architectural decisions -- and is
entirely novel engineering. Each AK trigger key gets its own dedicated ZMK
layer (l_akA through l_akY). When you type a key, the `&ak` behavior taps the
character and activates the corresponding AK layer via `&aksl` (sticky layer).
While that layer is active -- for the duration of the `my_ak_window` -- pressing
a second key can hit a replacement binding instead of the default. The
`REPLACE_CHAR_WITH_BIGRAM` macro standardizes the replacement: backspace the
first character, type the correct pair, and explicitly release shift to prevent
case contamination. This layer-per-AK architecture, the `&aksl` behavior, and
the scaling model are all original to this project. The architecture scales
cleanly to 23+ AK layers without any combinatorial explosion. But there's a
race condition: what if the second key fires before the AK layer activates?
Enter the AK Consistency Hack -- another original invention -- a master combo
bound to all 36 keys with an 11ms timeout. It exploits a 1ms margin over
`ak_tap_time` (10ms), guaranteeing the AK layer is always live before any
second key event can register.

**Oct 2023 -- The Great Restructuring.** The codebase undergoes a complete
architectural overhaul. Monolithic files (`flo_config.h`, `flo_behaviors.dtsi`,
`flo_macros.dtsi`, `flo_combos.dtsi`) are decomposed into a feature-module
architecture. `config/features/__BASE__/` takes on core infrastructure.
`config/features/hands_down/` holds the main layout implementation. Each
feature follows a consistent pattern: `aliases.dtsi`, `macros.dtsi`,
`behaviors.dtsi`, `combos.dtsi`. The `corne.keymap` file transforms into a
strict orchestrator -- nothing but `#include` directives in exact dependency
order. Aliases before macros, macros before behaviors, behaviors before combos,
combos before layers. Get the order wrong and things silently break. This
restructuring takes about a week and touches nearly every file, but the payoff
is a codebase where you can find anything by name and add features without
touching unrelated code.

**Oct 2023--Sep 2024 -- The HRM engineering era.** Home Row Mods are the
modifier system for almost a year, and they demand constant technical tuning.
Tap-preferred vs balanced flavor. `hold-while-undecided` for visual feedback.
`require-prior-idle-ms` added to reduce misfires, then removed when it causes
missed intentional mods. Cross-hand `hold-trigger-key-positions` -- hold only
triggers when the opposite hand presses a key, dramatically reducing false
activations. Split thumb keys into separate timing groups. The buffered mod
(`&bm`) is introduced for hold behaviors, mirroring what `&bk` does for taps.
Special HRM variants are created for AK-participating keys (S, C, N, T, E, A,
M) that tap the `&ak` macro instead of plain `&bk`, so the AK system works
through the modifier layer. It's clever, but the complexity is a warning sign.

**Mar 2024 -- Preprocessor macro consolidation.** A major DRY initiative
transforms the codebase from "configured firmware" to "metaprogrammed
firmware." Combo definitions, linger keys, and typing macros are all abstracted
into preprocessor macros in `__BASE__/preprocessor_macros.c`. The
`COMBO_LAY_BASE` macro and its six convenience wrappers (`COMBO_ANY_ONE_HAND`,
`COMBO_LAY_TWO_HAND`, etc.) replace pages of repetitive combo boilerplate. The
`LK(NAME, TAP, LINGER)` macro generates complete hold-tap behaviors for linger
keys -- 87 lines collapse to 36. `TYPING_MACRO(NAME, BINDINGS)` standardizes
macro creation. `REPLACE_CHAR_WITH_BIGRAM` is centralized here too. After this,
adding a new combo is a one-liner. Adding a new linger key is a one-liner. The
metaprogramming layer makes the system dramatically more maintainable -- and
dramatically more opaque to anyone reading it for the first time.

**Sep 2024 -- The Callum revolution (technical side).** The entire modifier
system is ripped out and replaced. HRMs give way to Callum-style one-shot mods.
The technical architecture: `skm` (sticky key mod) with `ignore-modifiers` for
stacking, `htls` (hold-tap layer sticky) for the thumb key's tap/hold decision,
and the crucial `moAndBuffer` macro that keeps the mod layer alive for 130ms
after hold detection. That buffer exists because of a race condition -- without
it, the layer can deactivate before the mod has time to register on the target
key. The mod layer (`l_mod`) becomes a dedicated layer with keyboard shortcuts,
accessible via thumb hold. The engineering is cleaner than HRMs: fewer special
cases, no cross-hand timing heuristics, no ambiguity about whether a home row
key was meant as a letter or a modifier.

**Oct 2024 -- Multi-layout architecture.** With Naquadah departing entirely from
Hands Down Titanium's letter placement, the system is generalized to support
multiple layouts simultaneously: Naquadah, Promethium, Rhodium. Per-layout
files follow a strict naming convention: `layers_A_{LAYOUT}_alpha.dtsi` for the
base alpha layer, `layers_B_{LAYOUT}_adaptive_keys.dtsi` for AK layers. Layer
aliases (`aliases_layers_{LAYOUT}.dtsi`) map abstract layer names to concrete
numbers. Layout selection works via a `#define` cascade in CONFIG.h -- all three
are defined, and whichever appears first in the `#if defined` chain in
`corne.keymap` wins. Layer C (nav, mod, fn, num, numsym, cfg) is shared across
all layouts. The architecture means adding a new layout requires only new A/B
layer files and an alias mapping. Everything else -- combos, linger keys, mods,
the entire AK infrastructure -- just works.

**2023--2025 -- Combo timeout refinement.** Combo timeouts evolve through months
of daily-driver testing, one millisecond at a time. Early values start at 10ms
(too tight -- missed combos during fast typing), climb to 15ms, then 20ms. The
two-hand timeout gets its own value early (30ms), acknowledging that
coordinating across a split keyboard takes longer than same-hand combos. The
adjacent vs non-adjacent distinction emerges later -- keys next to each other
can be pressed more precisely than keys separated by a finger. Multiple 1ms
adjustments based on typing feel: "just 1ms more for consistency," "1ms less,
too many misfires." Final stable values: adjacent 16ms, non-adjacent 18ms,
two-hand 30ms. These numbers are the product of hundreds of hours of real
typing. They haven't changed in months.

**Throughout -- The timing web.** The timing constants in CONFIG.h form an
interdependent system where every value justifies its existence relative to the
others. `ak_tap_time` (10ms) must be strictly less than `hold_key_event_delay`
(11ms) -- that's the 1ms AK consistency margin, and if those values ever swap,
the whole AK system breaks. `linger_term` (100ms) equals `my_ak_window`
(100ms) -- aligned intentionally so that AK detection and linger key resolution
operate on the same timescale. `action_lay_tapping_term` (90ms) is less than
`linger_term` -- layers activate before linger keys resolve, ensuring layer
switches win the race. The 500ms HRM tapping term (now vestigial) was a safety
ceiling, not the usual activation time; cross-hand detection made actual
activation much faster. Every millisecond in this system was justified through
real-world testing. Change one, and you'd better understand what it's coupled
to.

**Throughout -- Hardware config evolution.** `corne.conf` evolved in lockstep
with the features, always reactively. `CONFIG_ZMK_COMBO_MAX_COMBOS_PER_KEY`
grew from the default to 30 as more AKs and feature combos were added -- each
bump triggered by a mysterious build failure where combos silently stopped
working. `CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO` was set to 36 for the AK
consistency hack (a combo across literally every key on the board).
`CONFIG_ZMK_BEHAVIORS_QUEUE_SIZE` climbed to 512 to handle the cascade of macro
events that AK replacements generate -- a single AK fires a backspace, two
character taps, and a shift release, each buffered. These aren't arbitrary
round numbers. Each was increased exactly when the system hit a limit, debugged
from symptoms that ranged from dropped keys to combos that worked on one half
but not the other.

**Feb 2026 -- This log begins.** The technical infrastructure is mature. Two
years of timing tuning, architectural iteration, and real-world testing have
produced a system that's fast, reliable, and -- if you understand the
conventions -- surprisingly easy to extend. The work now is capturing the
hard-won engineering knowledge so it survives across sessions.
