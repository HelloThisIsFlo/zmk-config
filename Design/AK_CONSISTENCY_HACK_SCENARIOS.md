# AK Consistency Hack: 12-Scenario Analysis

## Context

When you press an AK key (Key1), the `&ak` macro does two things:
1. **Taps** the character (takes `ak_tap_time` = **10ms**)
2. **Activates** the AK sticky layer (lasts `my_ak_window` = 100ms)

If Key2 arrives before the AK layer activates (within that 10ms gap after Key1 starts
processing), Key2 hits the base layer instead of the AK layer. Wrong output.

The **COMBO_AK_CONSISTENCY_HACK** is an all-36-keys combo with an 11ms timeout. Since it
can never actually fire (nobody presses all 36 keys), it acts purely as a universal buffer:
every keypress is held for up to 11ms before being released.


## Timing Constants

| Constant                    | Value  | Description                            |
|-----------------------------|--------|----------------------------------------|
| `ak_tap_time`               | 10ms   | &ak macro tap duration                 |
| `hold_key_event_delay`      | 11ms   | Hack combo timeout (ak_tap_time + 1ms) |
| `my_combo_timeout_adjacent` | 16ms   | Smallest real combo timeout            |
| `my_ak_window`              | 100ms  | AK sticky layer duration               |

**Critical ordering**: `10ms < 11ms < 16ms << 100ms`


## Scenario Axes

**Key1's combo membership** (Key2 is never the combo partner):
- **(A) In a real combo**: Key1's position participates in a real combo (e.g., N is in an N+D combo)
- **(B) Not in a real combo**: Key1's position doesn't participate in any real combo

**Typing speed** (gap = time between Key1 and Key2 physical presses):
- **(1) Slow**: gap > ~110ms — AK overlay has expired before Key2
- **(2) Fast**: gap ≈ 20–100ms — normal typing, within AK window
- **(3) Extremely fast**: gap < ~16ms — combo-triggering speed


---
---

# WITHOUT the Hack

---

## A1: Key1 in real combo, Slow (gap > ~110ms)

> Example: press N (in a combo with D, 16ms timeout), then W 130ms later

```
t=0ms    N pressed → buffered by real combo (16ms timeout)
t=16ms   Combo times out → N released → &ak fires → taps 'n'
t=26ms   AK layer activates
t=126ms  AK layer expires
t=130ms  W pressed → fires immediately → hits base layer
```

**Result: ✅ CORRECT** — No AK transformation. Slow typing = normal output.


---

## A2: Key1 in real combo, Fast (16ms < gap < ~110ms)

> Example: press N, then W 50ms later

```
t=0ms    N pressed → buffered by real combo
t=16ms   Combo times out → N released → &ak fires → taps 'n'
t=26ms   AK layer activates
t=50ms   W pressed → fires immediately → hits AK layer ✓
```

**Result: ✅ CORRECT** — AK transformation works.

**⚠️ BUT there's a hidden failure sub-range.** When the gap falls between the combo timeout
and the AK layer activation (16–26ms), Key2 sneaks through:

> Example: press N, then W 20ms later

```
t=0ms    N pressed → buffered by real combo
t=16ms   Combo times out → N released → &ak fires → taps 'n'
t=20ms   W pressed → fires immediately → AK layer NOT ACTIVE (needs t=26ms)
t=26ms   AK layer activates — too late
```

**❌ FAILS for 16ms < gap < 26ms** — There's a 10ms vulnerability window after the combo
releases Key1 but before the AK layer activates. Key2 can slip through.


---

## A3: Key1 in real combo, Extremely fast (gap < 16ms)

> Example: press N, then W 8ms later

```
t=0ms    N pressed → buffered by real combo
t=8ms    W pressed → not in real combo → INVALIDATES combo
         → N released from buffer → &ak fires
         → W fires immediately (nothing is holding W)
t=8ms    Both N's &ak and W fire at the same instant
t=18ms   AK layer activates — too late
```

**Result: ❌ FAILS** — When Key2 invalidates the real combo, Key1 is released and Key2
fires in the same instant. The AK layer isn't ready for another 10ms.

This is the **core problem** the hack was designed to solve.


---

## B1: Key1 NOT in combo, Slow (gap > ~110ms)

> Example: press R (not in any real combo), then W 130ms later

```
t=0ms    R pressed → not in any combo → fires immediately → &ak runs
t=10ms   AK layer activates
t=110ms  AK layer expires
t=130ms  W pressed → fires immediately → hits base layer
```

**Result: ✅ CORRECT** — No AK transformation expected. Normal slow typing.


---

## B2: Key1 NOT in combo, Fast (10ms < gap < ~110ms)

> Example: press R, then W 50ms later

```
t=0ms    R pressed → fires immediately → &ak runs → taps 'r'
t=10ms   AK layer activates
t=50ms   W pressed → fires immediately → hits AK layer ✓
```

**Result: ✅ CORRECT** — AK works. Since Key1 isn't in any combo, it fires instantly.
The AK layer is ready 10ms later, and any normal typing speed is well past that.


---

## B3: Key1 NOT in combo, Extremely fast (gap < 10ms)

> Example: press R, then W 5ms later

```
t=0ms    R pressed → fires immediately → &ak runs → taps 'r'
t=5ms    W pressed → fires immediately → AK layer NOT ACTIVE (needs t=10ms)
t=10ms   AK layer activates — too late
```

**Result: ❌ FAILS** — W fires before the AK layer is ready.

In practice this requires typing two keys within 10ms of each other (~600+ WPM equivalent
for that pair). This essentially never happens in real typing outside of intentional combos.


---
---

# WITH the Hack

The hack combo (ALL_KEYS, 11ms timeout) captures every keypress. Since it includes all 36
keys, no keypress can "slip through" without being buffered.

---

## A1 (hack): Key1 in real combo, Slow (gap > ~110ms)

> Example: press N (combo with D), then W 130ms later

```
t=0ms    N pressed → buffered by real combo AND hack combo
t=11ms   Hack combo times out → but real combo still active → N stays buffered
t=16ms   Real combo times out → N released → &ak fires → taps 'n'
t=26ms   AK layer activates
t=126ms  AK layer expires
t=130ms  W pressed → captured by hack combo (new instance)
t=141ms  Hack times out → W released → hits base layer
```

**Result: ✅ CORRECT** — Same outcome as without hack. W delayed by 11ms, still lands on
base layer. No difference in behavior.


---

## A2 (hack): Key1 in real combo, Fast (gap > 11ms, within AK window)

> Example: press N, then W 50ms later

```
t=0ms    N pressed → buffered by real combo AND hack combo
t=11ms   Hack times out for N → real combo still holding → N stays buffered
t=16ms   Real combo times out → N released → &ak fires → taps 'n'
t=26ms   AK layer activates
t=50ms   W pressed → captured by hack combo (new instance)
t=61ms   Hack times out → W released → AK layer active ✓
```

**Result: ✅ CORRECT** — AK works.

**The hack also fixes the 16–26ms failure sub-range from A2-without-hack:**

> Example: press N, then W 20ms later

```
t=0ms    N pressed → buffered by real combo AND hack combo
t=11ms   Hack times out for N → real combo still holds → N stays buffered
t=16ms   Real combo times out → N released → &ak fires → taps 'n'
t=20ms   W pressed → captured by hack combo → BUFFERED (not fired immediately!)
t=26ms   AK layer activates
t=31ms   Hack times out for W → W released → AK layer active ✓
```

**✅ FIXED!** The 11ms hack delay on W bridges the 10ms AK activation gap. Without the hack
W would fire at t=20ms (before AK layer). With the hack, W fires at t=31ms (after AK layer).


---

## A3 (hack): Key1 in real combo, Extremely fast (gap < 16ms)

This is the scenario the hack was primarily designed for.
It splits into two sub-ranges based on whether Key2 arrives before or after the hack timeout.

### Sub-range: 11ms < gap < 16ms ✅

> Example: press N, then W 13ms later

```
t=0ms    N pressed → buffered by real combo AND hack combo
t=11ms   Hack times out → but real combo still active → N stays in buffer
         ┗━ KEY MOMENT: hack combo is DONE with N. Only the real combo holds N now.
t=13ms   W pressed → not in real combo → INVALIDATES real combo
         → N released (the only thing holding it) → &ak fires → taps 'n'
         → W captured by hack combo (new instance — previous one timed out)
         ┗━ KEY MOMENT: N and W are on INDEPENDENT timers now!
t=23ms   AK layer activates (13ms + 10ms)
t=24ms   Hack times out for W → W released → AK layer active ✓
```

**✅ CORRECT!** This is the sweet spot. The hack combo has already expired for Key1 (11ms
passed), so Key1 is only held by the real combo. When Key2 invalidates the real combo:
- Key1 is released (starts &ak, needs 10ms for AK layer)
- Key2 is independently captured by a fresh hack combo instance (held for 11ms)

Since both countdowns start from the same moment (t=13ms, when Key2 was pressed), and
11ms > 10ms, Key2 is **guaranteed** to arrive after the AK layer activates. The margin is
exactly 1ms — the buffer built into `hold_key_event_delay = ak_tap_time + 1`.

### Sub-range: gap < 11ms ❌

> Example: press N, then W 5ms later

```
t=0ms    N pressed → buffered by real combo AND hack combo
t=5ms    W pressed → not in real combo → INVALIDATES real combo
         BUT: hack combo still active (5ms < 11ms timeout)
         N is still claimed by the hack combo.
         W joins the hack combo too (all keys are members).
         → Both N and W are held by the same hack combo instance
t=11ms   Hack combo times out → N AND W released AT ONCE
t=11ms   N's &ak fires, W fires — AK layer not active yet
t=21ms   AK layer activates — too late
```

**❌ FAILS (minor caveat)** — Both keys are captured by the same hack combo instance.
When it times out, they release together — the same "AT ONCE" problem.

**This is what you were asking about!** Yes, N IS held by the hack combo, and yes, when
W arrives at 5ms, N is still in the hack combo. The hack combo claims both keys and
releases them together. The hack can't help here.

**Why it's acceptable**: At <11ms gap, you're typing at combo speed. Any real combo (minimum
16ms timeout) would trigger at this speed. You're never intending an AK transformation when
chording two keys that fast.


---

## B1 (hack): Key1 NOT in combo, Slow (gap > ~110ms)

> Example: press R, then W 130ms later

```
t=0ms    R pressed → captured by hack combo (only combo it's in)
t=11ms   Hack times out → R released → &ak fires → taps 'r'
t=21ms   AK layer activates
t=121ms  AK layer expires
t=130ms  W pressed → captured by hack combo (new instance)
t=141ms  Hack times out → W released → hits base layer
```

**Result: ✅ CORRECT** — Same outcome as without hack, everything shifted by 11ms.


---

## B2 (hack): Key1 NOT in combo, Fast (gap > 11ms, within AK window)

> Example: press R, then W 50ms later

```
t=0ms    R pressed → captured by hack combo
t=11ms   Hack times out → R released → &ak fires → taps 'r'
t=21ms   AK layer activates
t=50ms   W pressed → captured by hack combo (new instance)
t=61ms   Hack times out → W released → AK layer active ✓
```

**Result: ✅ CORRECT** — AK works. Same as without hack but with 11ms shift on each key.


---

## B3 (hack): Key1 NOT in combo, Extremely fast (gap < 11ms)

> Example: press R, then W 5ms later

```
t=0ms    R pressed → captured by hack combo
t=5ms    W pressed → captured by SAME hack combo instance (5ms < 11ms)
t=11ms   Hack times out → R AND W released AT ONCE
t=11ms   R's &ak fires, W fires — AK layer not active
t=21ms   AK layer activates — too late
```

**Result: ❌ FAILS (minor caveat)** — Same as B3 without hack: both keys fire before
AK layer is ready. The hack doesn't help (both keys are in the same hack instance).

Without the hack this also fails (B3 without hack: threshold 10ms). The hack shifts the
threshold from 10ms to 11ms — a 1ms difference that is completely irrelevant in practice.


---
---

# Summary

| Scenario | Speed | Without Hack | With Hack | Hack helps? |
|----------|-------|:------------:|:---------:|:-----------:|
| **A1** In combo | Slow | ✅ | ✅ | — |
| **A2** In combo | Fast | ⚠️ Fails 16–26ms | ✅ Always works | **YES** |
| **A3** In combo | Extreme | ❌ Fails < 16ms | ✅ 11–16ms / ❌ < 11ms | **YES** (partial) |
| **B1** No combo | Slow | ✅ | ✅ | — |
| **B2** No combo | Fast | ✅ | ✅ | — |
| **B3** No combo | Extreme | ❌ Fails < 10ms | ❌ Fails < 11ms | — |


## Key Insights

### What the hack actually does

The hack gives **every key a reason to be buffered for 11ms**. This matters in two ways:

1. **Fixes A2's hidden failure window** (16–26ms gap): Without the hack, after the real combo
   times out, Key2 can arrive during the 10ms while &ak is still activating the AK layer.
   The hack holds Key2 for 11ms, bridging this gap.

2. **Fixes A3 for the 11–16ms range**: When Key2 arrives after the hack timeout (11ms) but
   before the real combo timeout (16ms), the hack has already expired for Key1 (so Key1
   is only held by the real combo). Key2's arrival invalidates the real combo, releasing
   Key1, while Key2 is independently captured by a fresh hack combo instance. Both
   countdowns — Key1's 10ms AK activation and Key2's 11ms hack delay — start from the same
   moment. Since 10 < 11, the AK layer always wins by 1ms.

### Why N isn't held by the hack combo (your question!)

In Scenario A3, the answer depends on timing:

- **gap > 11ms**: The hack combo has **already timed out** for N by the time W arrives.
  N is only still buffered because the real combo (16ms timeout) is holding it. The hack
  combo is gone. When W invalidates the real combo, N is released and W starts its own
  independent hack combo instance. They're on separate timers.

- **gap < 11ms**: N **IS** still held by the hack combo! W joins the same instance. They
  release together. This is the minor caveat — and it's the scenario you were asking about.
  The hack simply can't help when both keys arrive within its 11ms window.

### The 1ms margin

The entire system rests on one relationship:

```
hold_key_event_delay (11ms) > ak_tap_time (10ms)
```

That 1ms buffer is what guarantees the AK layer activates before Key2 is released, in every
scenario where the hack can help. The `+1` in `hold_key_event_delay = ak_tap_time + 1ms` is
doing all the heavy lifting.

### The cost

Every keypress is delayed by 11ms. This adds 11ms of input latency to all typing. At human
perception thresholds (~50–100ms), this is imperceptible.
