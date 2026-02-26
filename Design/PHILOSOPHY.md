# Keyboard Philosophy

> This is a living document. It captures how I think about my keyboard layout --
> my approach, principles, preferences, and hard-won insights. It gets refined
> over time as my thinking evolves. Future agents should read this to understand
> my mindset before making suggestions.
>
> Last refined: 2026-02-26

## Core Identity

The driving question behind Naquadah: **"What if we built a layout that _required_ adaptive keys?"**

Naquadah is a heavy variation of HandsDown Titanium -- so heavily modified it's practically unrecognizable. It runs on a Corne (Chocofi) split keyboard with heavy column stagger and Nice Nano v2 controllers.

The technical infrastructure (adaptive keys system, combo framework, linger keys, mod morphs, Callum-style mods) is mature and stable. The keyboard has been iterated on for years. The work now is almost entirely about **refining bindings** -- what key does what, where symbols live, which combos and adaptive keys to add or adjust.

## Design Principles

In rough priority order:

1. **Adaptive Keys are NOT optional.** The layout is designed around them. Without AKs, the layout is unusable. This is the foundational commitment.
2. **Flow above all.** Typing should feel fluid and effortless:
   - Extremely low SFB (currently 0.082% with 46 AKs)
   - Low redirects (~<2%)
   - Inward rolls >> outward rolls
   - The few remaining SFBs should ideally fall on syllable breaks
3. **Comfort over theory.** If something feels wrong, it IS wrong, regardless of what the frequency data says. Physical comfort always wins.
4. **Callum-style mods.** After a year with home row mods, Callum-style was "love at first sight." One-shot on tap (chaining/stacking), regular hold behavior. Never going back.
5. **Combos for frequent actions.** If something is done often enough to cause strain, it deserves a combo on the base layer -- don't force layer activation for high-frequency actions.

## Ergonomic Preferences

- **Positional comfort hierarchy:** home row > top row > bottom row
- **Finger awareness:** conscious of pinky and ring finger fatigue; index fingers can handle more
- **Thumb strain is real.** Repeated layer activation for frequent shortcuts causes thumb pain. When this happens, the solution is usually a combo on the base layer instead.
- **One-handed operation matters.** The left hand often operates solo while the right hand is on the trackpad. Left-hand combos and the mod layer are designed with this in mind.
- **Heavy column stagger** (Chocofi) makes certain movements impossible or uncomfortable that might work on flat keyboards -- AKs in the "impossible movements" category address this.

## What Works Well

- **AK system:** Very reliable, no missed keys in over a year, tested at 200wpm+ burst. The layer-per-AK architecture works.
- **Callum-style mods:** Replaced HRMs and never looked back. The timing guarantee (correct order = correct result) removes all ambiguity.
- **Linger keys:** Great for dual-purpose keys (tap for one thing, hold for related thing).
- **Magic parenthesis:** One combo, four bracket types based on hold duration and shift state.
- **Tight combo timeouts (16-18ms adjacent, 30ms two-hand):** Virtually no misfires during normal typing.
- **Combos for frequent app shortcuts:** The S+N dictation combo is a good example -- eliminated thumb strain from repeated layer activation.

## Pain Points & Open Questions

- Symbol placement is still in flux (only `.` `,` `'` are considered fixed)
- Always looking for better ways to handle high-frequency shortcuts without layer activation strain

## Approach to Change

- **Think together, don't just execute.** I prefer collaborative brainstorming -- discuss trade-offs, consider alternatives, reason about ergonomics before committing to a change.
- **Muscle memory has a cost.** Every change means retraining. The ergonomic gain must justify the disruption.
- **Ripple effects matter.** A single key swap can affect adaptive keys, combos, linger keys, and mod morphs. Always trace the full impact.
- **The only validation is a successful build** -- there are no tests. Flash and try it.
- **Willingness to experiment.** I'll try things, live with them, and revert if they don't feel right. The decision journal tracks these experiments.

## Workflow Preferences

- **No auto-formatting** -- manual alignment in `.dtsi` files is intentional and meaningful
- **Direct pushes to main** -- no branching workflow for this repo
- **Separate commits for unrelated changes**
- **Collaborative brainstorming** over directive execution
