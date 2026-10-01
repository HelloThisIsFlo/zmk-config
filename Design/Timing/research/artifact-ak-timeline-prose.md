# Yesterday's artifact ("The AK consistency hack, on a timeline") — prose + model, extracted

Source: https://claude.ai/artifact/28r9YhpB8FTQti4TXYvZE5 (built by another agent, 2026-09-27, claims to be "built from the v0.3 source of combo.c, behavior_queue.c, and the &ak macro").

## Headline claims

- "after typing a character, &ak needs 10 ms before the adaptive layer is armed, and the combo engine can hand the next key to the keymap 0 ms after the first one. The hack makes sure that never happens."
- Key 1 = adaptive trigger (L), key 2 (G) arrives Δ ms later. If key 2 lands while l_akL is active → replacement (LL). Else plain LG.

## "The three rules the engine follows" (claimed same in 2024 fork and v0.3)

1. **One buffer, one candidate set.** First key pressed builds a set of candidates: every combo that includes it. While set non-empty, key sits in a buffer and keymap does not see it. No per-combo buffering.
2. **A new key filters the set.** Each further key removes every candidate that does not also include it. If set becomes empty, engine flushes: first buffered key delivered, any others **re-raised** as if just pressed, with original timestamps, in the same call.
3. **Timers count from key 1.** Candidate expires at (time of first buffered key + its timeout). When the last one expires, engine flushes the same way.

## "Then &ak opens a 10 ms hole"

- **The macro parks.** &ak queues &kp L press, a 10 ms tap, then &aksl l_akL. Behavior queue runs the press immediately and parks for the tap. Adaptive layer armed 10 ms after key delivered, not when delivered.
- **The flush is instant.** Flush delivers key 1 and re-raises key 2 back to back. If key 2 finds no candidates of its own, it reaches keymap 0 ms after key 1, straight into the hole.
- **The hack fills the hole.** A combo on all 36 keys means every key, including a re-raised one, always has ≥1 candidate. So key 2 always waits ≥11 ms after it is raised. 11 > 10, layer up when it lands.

## Simulator model (simulate() logic, transcribed)

Inputs: hack on/off (11 ms), k1 = key 1's real-combo timeout (0/16/30), k2 = key 2's real-combo timeout (0/16/30), Δ = gap.

- cands1 = {k1 real combo (to=k1) if k1} ∪ {hack (to=11) if hack}. lastExpiry = max(to).
- Case A: cands1 empty → d1 = 0 (key 1 delivered instantly). Key 2 at Δ starts own set: k2Wait = max(k2, hack?11:0); d2 = Δ + k2Wait.
- Case B: Δ < lastExpiry (key 2 arrives while key 1 buffered):
  - alive = cands whose to > Δ; keep = alive ∩ {hack}.
  - If hack alive (Δ < 11): both buffered together; d1 = 11 (flush when hack expires, counted from key 1). Key 2 re-raised at 11 with original timestamp Δ → its own cands: real k2 (expires Δ+k2), hack (expires Δ+11). d2 = Δ + max(k2, 11).
  - Else (no hack alive): d1 = Δ (flush at key 2's press), key 2 re-raised at Δ, d2 = Δ + max(k2, hack?11:0).
- Case C: Δ ≥ lastExpiry → d1 = lastExpiry; key 2 fresh at Δ; d2 = Δ + max(k2, hack?11:0).
- layerAt = d1 + 10. Verdict: ok if d2 > layerAt; race if d2 == layerAt; miss if d2 < layerAt.

## Caveats section (claims)

- Every alpha keystroke delayed by 11 ms (keys already in combos waited 16–30; keys not in combos now wait 11 instead of 0).
- **Bigrams faster than ~10 ms still miss.** If key 2 arrives while hack still holds key 1, both held until key 1's 11 ms expires. Key 2 then re-raised and held 11 ms from its *own* timestamp → lands only Δ ms after key 1. Layer needs 10. "Your combos.dtsi comment already names this caveat, but the worked example in Design/ak-combo-hack.md (M then T, 5 ms apart) sits inside it." Also: "In that doc, M is described as released at 5 ms 'from the normal combo'; the engine has no per-combo release, so M actually waits until 11 ms."
- **Key 2 in a slower combo helps.** After re-raise, key 2's own combos become candidates again, so a key in a 30 ms combo waits 30 ms and never misses. "This is why some pairs 'just worked' before the hack."
- **On ZMK v0.3 the combo is silently dropped.** "The engine only builds combos with up to 19 key positions. The same guarantee needs a set of combos that covers every pair of keys, e.g. 4 groups of 9 keys and one 18-key combo per pair of groups (6 combos)."

## Constants table (claims)

| Constant | Value | Role |
|---|---|---|
| ak_tap_time | 10 ms | behavior queue parks between &kp press and sticky layer. "The hole." |
| hold_key_event_delay | 11 ms | hack combo timeout; minimum wait for any raised key on alpha layers |
| my_combo_timeout_adjacent | 16 ms | shortest real combo; also how long a key in one waits after a re-raise |
| my_combo_timeout_two_hnds | 30 ms | longest real combo |
| my_ak_window | 100 ms | how long sticky layer stays armed |

Model limits stated: two keys only; key 2 never completes a combo with key 1; timer ties shown as ties. "Exact-tie ordering in Zephyr depends on which work item was scheduled first."
