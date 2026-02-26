# Design TODOs

> Ideas and future work for the Design/ documentation system.

---

## Visual Diagrams for Timing Guarantees

**Priority:** Would love to do this

**Idea:** Build interactive visual representations of the keyboard's timing
systems -- mermaid diagrams, HTML animations, or similar. Have an agent explore
the mechanics and present them visually.

**Concepts to cover:**

1. **AK Consistency Hack** -- The 1ms margin timing guarantee
   - Show the race condition: what happens without the hack (second key fires
     before AK layer activates)
   - Show the solution: master combo's 11ms timeout > ak_tap_time 10ms
   - Animate the timeline: key press → ak_tap_time → AK layer active →
     hold_key_event_delay expires → second key fires → hits replacement binding

2. **Callum Mod Timing Guarantee** -- The 130ms buffer
   - Show the moAndBuffer lifecycle: mod layer press → mods activated →
     mod layer release → 130ms buffer keeps layer alive → mods resolve
   - Show correct vs incorrect ordering
   - Animate why the buffer makes it forgiving

3. **AK Keystroke Flow** -- Full adaptive key replacement sequence
   - From first key press through combo detection, AK layer activation,
     REPLACE_CHAR_WITH_BIGRAM macro (backspace → replacement → shift release),
     to final output

4. **Linger Key Hold-Tap Resolution** -- Tap vs hold decision
   - Show linger_term (100ms) threshold
   - The &bk vs &kp difference on the hold side (wispr pattern)

5. **Combo Timeout Tiers** -- The three-tier system visualized
   - Adjacent (16ms) vs non-adjacent (18ms) vs two-hand (30ms)
   - Why tighter = fewer misfires

**Format ideas:**
- Mermaid sequence diagrams (renderable in GitHub markdown)
- Interactive HTML page with animated timelines
- SVG diagrams with timing annotations
- Could be a standalone `Design/Visuals/` directory
