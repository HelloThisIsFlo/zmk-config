# 🗺️ Concepts — the map

What the timing page covers, in plain words, and where each thing is explained. No numbers here; those live in the reviewed documents linked below.

> [!note] Layering
>
> - **This file** — the map
> - [`FACTS.md`](FACTS.md) — what the website may say: facts with proof, worked examples on real keys, must-not-say lists
> - [`MODEL.md`](MODEL.md) — how the firmware actually works, every statement tagged with its evidence
> - [`PAIRS.md`](PAIRS.md), [`TESTS.md`](TESTS.md), [`results/`](results/) — the evidence itself

| Concept | In one sentence | Read |
|---|---|---|
| ⌨️ **Adaptive keys** | A key whose output depends on the key typed just before it, so two letters that would use the same finger become something easier to type | FACTS §3 · MODEL "⌨️ The `&ak` keystroke" |
| ⏳ **Buffered keys and the queue** | Why most keys go through one output queue, what `&bk` is for, and what that means for the order things come out | FACTS §3 · MODEL ten things #8 |
| 🧩 **The consistency hack** | The trick meant to make adaptive keys work at any typing speed, and what it really does | FACTS §1 · MODEL "📐 The hack as a theorem" · README "⚖️ The exactly 10 ms cell" |
| 🧷 **Per-pair fragility** | Not every adaptive pair behaves the same; which ones are fragile and why | FACTS §7 · PAIRS |
| 📏 **Combo timeout tiers** | How close together two keys must be pressed to count as a combo instead of two letters | FACTS §5 · MODEL "📏 Combo tiers" |
| ✋ **Linger keys** | A key that does one thing when tapped and another when held a little longer | FACTS §4 · MODEL "✋ Linger keys" |
| 🎛️ **The Callum mod buffer** | The thumb that opens the modifier layer and keeps it usable for a moment after you let go | FACTS §2 · MODEL "🎛️ Callum mods" |
| 🚚 **Pipeline and transport** | The path from a switch closing to a letter reaching the computer: which half does what, where time goes | FACTS §6 · MODEL "🚚 Pipeline" |

Each FACTS section has the same four parts: facts the page may state · worked examples · what the page must not say · caveats.
