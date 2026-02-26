# Decision Journal

> Chronological log of keyboard design decisions, experiments, and philosophy
> shifts. Not code changes (git has that) -- this captures the reasoning,
> experiments tried, and lessons learned.
>
> Newest entries first.

---

## 2026-02-26 -- S+N combo for dictation (Opt+R)

**Context**: I use a dictation app constantly, triggered by Opt+R. The old way
was to activate the mod layer (thumb hold) then press Alt + R from there. Doing
this dozens of times a day was causing noticeable thumb pain from the repeated
layer activation.

**Decision**: Added a two-key combo on S+N (LM3+LM2, adjacent home row left
hand) that fires `LA(R)` directly from the alpha layer. Scoped to `l_alpha_aks`
only to avoid conflict with the transposed Bspc combo on S+N that exists on
nav/num layers.

**Reasoning**: S+N is a comfortable adjacent home row combo (ring + middle
finger). The position was free on the alpha layer. The 16ms adjacent combo
timeout means no misfire risk during normal typing. This completely eliminates
the layer activation that was causing thumb strain -- a direct two-finger tap
replaces a thumb hold + key sequence.

**Outcome**: Immediately felt more ergonomic. "Oh my God, this is so much more
ergonomic."

---
---

# Previously on... (Sep 2023 -- Feb 2026)

> This decision journal started on February 26, 2026, but the keyboard has been
> evolving for over two years and 600+ commits. Here's the story so far.

**Sep 2023 -- The beginning.** Project starts with a Corne (Chocofi) split
keyboard and Nice Nano v2 controllers. Early weeks are pure exploration:
Gallium, Sturdy, Recurva, Dhorf, Whorf -- trying every layout that looks
promising. Sturdy becomes the first real baseline.

**Sep 2023 -- Hands Down enters the picture.** Importing features from Alan
Reiser's Hands Down ZMK fork is transformational. Suddenly the architecture has
adaptive layers, bigram analysis, and sophisticated mod handling. The Adaptive
Keys concept -- detecting rapid key sequences and replacing them -- takes root.
Early AK window tuning starts at 50ms, experiments through 70-90ms.

**Oct 2023 -- Apr 2024 -- The HRM era.** Six months of wrestling with Home Row
Mods. Tap-preferred, positional variants, cross-hand detection, `require-prior-
idle-ms` added then removed. HRMs work, but there's always a nagging edge case.
The timing dance never fully goes away.

**Sep 2024 -- The Callum revolution.** After a year of HRM tweaking, a proof of
concept: Callum-style one-shot mods. Tap to chain/stack, hold for regular mods.
"Love at first sight." By October, all HRMs are gone. The keyboard becomes
dramatically more reliable for mod combinations. This is one of those decisions
that never gets revisited -- it was just right.

**Oct 21, 2024 -- Naquadah is born.** The bold question: "What if we built a
layout that _required_ adaptive keys?" Not AKs as optimization, but AKs as
foundation. Naquadah starts as a heavy variation of Hands Down Titanium, quickly
becoming unrecognizable from its origin. All AKs are reset and redesigned from
scratch against bigram corpus analysis.

**Oct 24, 2024 -- RC1.** First release candidate. 31 AKs across four
categories: SFB elimination, impossible movements, comfort, and repeat keys.
The `sfb.py` analysis script is born. Target: sub-0.1% SFB rate.

**Nov 7, 2024 -- RC2 goes live.** Deployed with all AKs. Heavy experimentation
follows -- AK targets shift, comfort variants multiply, repeat keys get refined
based on real typing. NP becomes NN, GP becomes LP.

**Nov 9, 2024 -- RC3 takes over.** Becomes the de facto standard for over a
year. Small refinements accumulate: AU/UA vowel pairs, OE tweaks, new comfort
AKs (CP->TP, PC->PT, PN->PD). The layout is settling.

**Oct 2025 -- RC4.** Symbol row reorganization. Top-right gets `/` `.` `-` `=`
`'`. Linger keys for quote and equals. AK count grows to 46. The layout
reaches 0.082% SFB -- same-finger bigrams virtually eliminated.

**Throughout 2024-2025 -- Architecture matures.** The codebase evolves in
parallel: `corne.keymap` becomes a strict orchestrator with dependency-ordered
includes. Features get modularized into `config/features/`. Preprocessor macros
(`COMBO_*`, `REPLACE_CHAR_WITH_BIGRAM`, `LK`, `TYPING_MACRO`) eliminate
boilerplate. The three-tier layer system (alpha / AK / extra) stabilizes.

**The dead layouts.** Before Naquadah: Promethium (comfort-focused), Rhodium
(lighter on AKs), Vibranium (early experiment). All three remain `#define`d in
CONFIG.h as historical artifacts. Naquadah wins the cascade.

**Feb 26, 2026 -- This journal begins.** The technical infrastructure is mature.
The work now is refining bindings, and capturing the thinking behind every
change so the years of accumulated wisdom don't get lost between sessions.
