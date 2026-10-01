# 🔎 CHECK — MODEL.md fact preservation

Independent check of the restyled [MODEL.md](../MODEL.md) against its source, `scratchpad/investigation/MODEL_v2.md` (643 lines → 1344 lines).

> [!important] Verdict
>
> - **0 facts lost** · **2 altered** · **3 fixed** in place (the 2 alterations + 1 stale pointer)
> - Every number, condition, status tag, proof pointer, quoted log line and ⛔ struck claim survives
> - Mermaid: 4/4 diagrams parse · callouts: bullets only (Patterns A–D) · legend used consistently

## 🧾 What was checked

- **Mechanical, source vs target**, as multisets
  - Log stamps `[00:00:…]`: 219 = 219 · quoted log lines: 219 = 219 (176 unique)
  - Test IDs (`T-`, `S-`, `ARB-`, `RVA-`/`RVB-`, `FIX-`, `CB-`): all 201 present · only addition `T-01` (RIG pointer)
  - `file:line` refs: 42 = 42
  - ⛔ struck claims: all 61 present
    - The only strikes dropped are the tag name itself (legend row, Refuted heading), now carried by ⛔
  - Interval/range tokens: 21 = 21
- **Status mapping, line by line**
  - Every `INFERRED` (39) → 🧮 at the same statement
  - Every `BOARD-ONLY` (13) → 🔮
    - The 3 extra 🔮 restate cells the source's own BOARD-ONLY list covers
    - They're the derived-cells bullet, the mechanism diagram, and the dead-window ends row
  - Every `PROVEN(src)` (38) → 📜 · no source-only proof relabelled 🧪
  - Every `OPEN` (17) → ❓ or the OPEN pointer
- **By hand, item by item**
  - Ten things #1–#10, §(a)–(n), every table row (landscape, `&ak` offsets, Δ ON/OFF, E_b, per-pair, replace-macro), the PAIRS erratum, every caveat, the Confidence lists and the decision items
- **Links**
  - All `results/…`, `research/…`, `PAIRS.md` and `FACTS.md` targets exist
  - The `PAGE_FACTS.md` OPEN pointer → `FACTS.md` § ❓ OPEN is present at the end of FACTS.md

## 🛠️ Fixed

| # | kind | where | source said | target had | now |
|---|---|---|---|---|---|
| 1 | altered (condition dropped) | 🧩 R10 Late-deadline stall | "**If** a later key drops the candidate that owns the armed deadline and a later one survives, the old timer early-returns…" | "A later key drops … survives → …" (an unconditional statement) | "If a later key drops …" |
| 2 | altered (claim added) | intro line | "Supersedes `MODEL.md` (v1). Where v1 and this file differ, this file wins." | "This is the single source of truth for the Timing docs; …" (FACTS.md is the page spec) | "Supersedes the v1 model; where v1 and this file differ, this file wins." |
| 3 | stale pointer | Shorthand → Evidence IDs | `results/*.raw.log`, `CORR-B/*.raw.log` | same; neither path exists in the repo | kept, + "Raw logs in this repo → `../../tests/timing/logs/`" (same pattern as PAIRS.md) |

## ❓ Left for review

- **`TESTS.md` link is dead** (footer)
  - README, FACTS and PAIRS link it too
    - So it's a planned sibling, not a MODEL defect
  - Resolves once TESTS.md is written
- **Two ⚠️ "Source tension" callouts were added by the restyle**
  - Both are accurate and drop nothing; both ask for a reviewer decision
  - #9 "RM1 "a"" vs ⛔ "late key types lowercase "a"" (RVA-callum-close245 logs a shifted "A")
  - `k_sys_work_q` claim tagged 🧮 in Time convention but 📜 in Pipeline
- **🧮 has two roles in the shared legend**
  - Status "inferred" and actor "kscan/debounce"
  - Visible in the pipeline diagram; it comes from the legend itself, so it was left as is
