# AK Consistency Hack: Deep Dive

How a 36-key combo that never fires makes adaptive keys reliable.

Source: the comment block in `adaptive_keys/combos.dtsi:1-63` — this doc refines and structures that explanation.

## The Problem

When a key participates in a combo, ZMK **buffers** the keypress until the combo resolves. There are three outcomes:

1. **Combo completes** — all combo keys pressed → combo fires. Works fine.
2. **Combo times out** — not all keys pressed within timeout → buffered keys released **at once**.
3. **Non-combo key pressed** — a key outside the combo is pressed → buffered keys released **at once**.

Scenarios 2 and 3 break AKs. Here's why:

The `&ak` macro needs **10ms** (`ak_tap_time`) to type the character before it can activate the AK layer. When combo resolution releases two buffered keys simultaneously, the second key arrives _before_ the first key's AK layer activates. The second key hits the alpha layer instead of the AK layer — no replacement happens.

**Timeline without the hack** (two keys pressed near-simultaneously):
```
t=0ms   Key A pressed (buffered by combo system)
t=5ms   Key B pressed (buffered by combo system)
t=16ms  Combo times out → both keys released AT ONCE
t=16ms  &ak fires for A: starts typing A
t=16ms  &ak fires for B: starts typing B ← hits alpha, NOT l_akA!
t=26ms  A's &kp completes, l_akA activates ← too late, B already fired
```

## The Solution

A combo that includes **all 36 keys** with an 11ms timeout (`hold_key_event_delay`).

```c
// combos.dtsi:64-65
#define COMBO_AK_CONSISTENCY_HACK \
  COMBO_LAY_BASE(l_alpha_aks, ak_consistency_hack, &none, ALL_KEYS, hold_key_event_delay)
```

- **Binding**: `&none` — does nothing if somehow fired
- **Keys**: `ALL_KEYS` — all 36 key positions (both hands + thumbs)
- **Layers**: `l_alpha_aks` — alpha layers + all AK layers
- **Timeout**: `hold_key_event_delay` = 11ms (`CONFIG.h:28`)

This combo **never fires** — you'd need to press all 36 keys within 11ms. But its existence means every single keypress is buffered for 11ms by the combo system, because every key is part of this combo.

## Step-by-Step Flow

What happens when two keys are pressed in sequence (e.g., M then T):

```
t=0ms    M pressed
         → Captured by both "normal" combos AND the consistency hack combo
         → M is buffered (not yet sent to &ak)

t=5ms    T pressed
         → NOT part of any "normal" combo that includes M
         → But IS part of the consistency hack combo (all keys are)
         → T is buffered by the hack combo

t=5ms    The "normal" combo resolves (non-combo key T broke it)
         → M is released from the normal combo
         → M's &ak fires: starts typing M

t=11ms   Hack combo times out for M (11ms after M was pressed)
         → But M was already released at t=5ms, so this is a no-op for M

t=15ms   M's &kp completes (10ms after t=5ms)
         → l_akM activates

t=16ms   Hack combo times out for T (11ms after T was pressed)
         → T is released from the hack combo
         → T fires → hits l_akM (which is now active) → replacement works!
```

The critical guarantee: **T is delayed by at least 11ms** after M starts processing, because the hack combo buffers T for its full timeout. Since `&ak` only needs 10ms to complete, the AK layer is always ready.

**Relationship to `&bk`:** The combo hack solves ordering at the combo-resolution level — when the combo system releases multiple buffered keys simultaneously. At the individual-key level, `&bk` (see [ak-deepdive.md](ak-deepdive.md)) keeps all keypresses in ZMK's macro processing pipeline, preventing raw `&kp` from racing with in-flight macro events. Together, these two mechanisms make the AK system reliable.

## The Timing Invariant

```
ak_tap_time (10ms)  <  hold_key_event_delay (11ms)  <<  combo timeouts (16-30ms)  <<  my_ak_window (100ms)
```

| Constant | Value | Source | Role |
|----------|-------|--------|------|
| `ak_tap_time` | 10ms | `CONFIG.h:27` | Time for `&ak` to type the character |
| `hold_key_event_delay` | 11ms | `CONFIG.h:28` | Hack combo timeout (= ak_tap_time + 1ms buffer) |
| `my_combo_timeout_adjacent` | 16ms | `CONFIG.h:9` | Shortest "real" combo timeout |
| `my_combo_timeout_non_adjc` | 18ms | `CONFIG.h:10` | Non-adjacent combo timeout |
| `my_combo_timeout_two_hnds` | 30ms | `CONFIG.h:11` | Two-hand combo timeout |
| `my_ak_window` | 100ms | `CONFIG.h:8` | How long the AK layer stays active |

The invariant ensures:
- The hack always provides enough delay for `&ak` to complete (10 < 11)
- Real combos have strictly longer timeouts than the hack, so the hack never interferes with real combo detection (11 < 16)
- The AK window is long enough that replacements fire comfortably within it (11 << 100)

## Minor Caveat

The **one** scenario where a race can still occur: two keys pressed within 11ms of each other.

If both M and T are pressed within 11ms, they're captured by the _same_ hack combo timeout window. When the hack resolves, both are released simultaneously — the same problem as before.

**Why this doesn't matter:** 11ms is faster than any "real" combo timeout (16ms minimum). If two keys arrive that close together, the user intended a combo, not an AK sequence. The normal combo system handles it correctly. There's no scenario where you'd want an AK replacement for two keys pressed <11ms apart.

## Configuration

The hack requires ZMK to support a 36-key combo:

```ini
# corne.conf:58
CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO=36
```

Without this setting, ZMK would reject the combo definition at compile time.

The hack combo is scoped to `l_alpha_aks` layers only (alpha + all AK layers). It doesn't affect nav, mod, num, or other non-alpha layers.
