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
