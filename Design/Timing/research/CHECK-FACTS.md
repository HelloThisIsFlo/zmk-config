# 🔍 CHECK — FACTS.md fact preservation

> [!note] Verdict
>
> - **0 lost · 1 altered · 5 fixed** (1 altered fact + 4 defects)
> - Source = scratchpad `investigation/PAGE_FACTS.md` (648 lines) · target = [FACTS.md](../FACTS.md)
> - Mermaid: 5 / 5 diagrams parse (`@mermaid-lint/cli@0.53.1 --no-semantic`)

## ✅ What was ticked

- **Every numbered fact**: §1 1–15 · §2 1–20 · §3 1–19 · §4 1–9 · §5 1–12 · §6 1–10 · §7 1–10
- **Every worked example**: Ex 1.1–1.4, 2.1–2.3, 3.1–3.3, 4.1–4.2, 5.1–5.2, 6.1, 7.1–7.3
  - All table rows verbatim
  - Ex 5.1 rows only gained 🟪 / ✅ glyphs
- **Every must-NOT row**: 11 + 12 + 8 + 4 + 6 + 4, struck text intact, killer intact
- **Every caveat**, the key map (17 rows), the erratum, the change tables, ART, docs-to-fix, OPEN 1–24
- **Mechanical diff, source ≤ target for every token**
  - native log times · test ids (`T-`, `S-`, `ARB-`, `RVA-`, `RVB-`, `FIX-`) · `file:line` · keycodes · `E-xx` · `OPEN #n`
  - every code span, every quoted string, every `~~struck~~` claim
  - `INFERRED` 40 = 40 · `BOARD-ONLY` 15 = 15 · "predicted" 3 = 3
  - `PROVEN(…)` → 🧪 / 📜 by kind

## 🛠️ Fixed

| # | Kind | Item (source text) | Was in target | Now |
|---|---|---|---|---|
| 1 | altered | §3 fact 18: "`l_akR` lives from thumb-up to thumb-up + 100 (idle queue; busy queue: from R↑, 10 ms after R↓)" | "Idle queue · busy queue: from R↑, 10 ms after R↓" → reads as if both cases start at R↑ | "That is with an idle queue" + "Busy queue: from R↑, 10 ms after R↓" |
| 2 | defect | OPEN #3 status "INFERRED mechanism, unmeasured" | sat in the "Closes by" column | moved into the item text · Closes by = — |
| 3 | legend | OPEN #7 "PROVEN(RVA-callum-relaxed180, RVA-callum-close245)" | raw `PROVEN(…)` | 🧪 RVA-callum-relaxed180, RVA-callum-close245 |
| 4 | legend | OPEN #15 "PROVEN(RVA-ex33-cpn)" | raw `PROVEN(…)` | 🧪 RVA-ex33-cpn |
| 5 | legend / marker | OPEN #19 "native mechanism PROVEN RVB-strand-join" · §4 callout's 2-key-combo exception (§4 fact 6: INFERRED, S2 rule) | raw PROVEN · exception stated with no marker | 🧪 RVB-strand-join · "(… 2-key combo, 🧮 INFERRED)" |

## ⚠️ Remaining (not fixed, by design)

- **[TESTS.md](../TESTS.md) link is dangling**
  - Linked from the "Chase a proof pointer" tip, also from README
  - Expected from a sibling restyle; `MODEL.md` already landed
- **Summary diagrams carry fewer markers than the facts**
  - §7 diagram: "D↔V · tab 🟪 any roll under 16" has no 🧮 (§7 fact 7 is INFERRED)
  - §1 callout: "❌ ≤ 9 ms" has no 🔮 (§1 fact 7 marks the whole band BOARD-ONLY)
  - The facts keep their markers
- **Five "Source inconsistency" callouts were added by the restyle**
  - They flag real tensions in the source (bspc/del t+18 vs "own deadline", ~10 vs 11 ms stall join, 5–15 vs 4.5…15 stamp delay, hack latency roll exception, RM1 "t" vs "a")
  - Source wording kept verbatim; the reviewer decides
- **Emoji outside the legend appear only as signposts**
  - Diagram landmarks: 🖐️ input, 🧵 central thread, 💻 host, ⏱️ stamp, 🗂️ pairs
  - Pointers back to section headers: 🗣️ 🎬 ⚠️ 🔄
  - No decorated leaf bullets · no prose inside callouts
