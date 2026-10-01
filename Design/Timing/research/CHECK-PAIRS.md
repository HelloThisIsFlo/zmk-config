# ✅ CHECK — PAIRS.md fact preservation

- **Source:** scratchpad `investigation/PAIRS.md` (674 l.)
- **Target:** `Design/Timing/PAIRS.md` (restyled, 1134 → 1148 l. after fixes)
- **Result:** 1 lost · 2 altered · 9 fixed (incl. 6 target defects) · 0 open fact losses

## 🧪 What was checked

- **54-row pair table** → script compare of every cell
  - Cols #, class, layer, trigger, follower, k2, shared combos, hack-only, miss → adapted: identical on all 54
  - Hand column: identical (`R-R (central)` → `R-R`, `L-L (both via BLE)` → `L-L`)
  - Band columns moved to 📊 Band profiles: every row's 4 band cells = its profile's cells; `thumb` / `rep-E` / `rep-R` verbatim
  - Profile counts: S3-18 1 · S3-16 1 · S2 4 · H0 11 · N-110 23 · N-112 6 · N-108 1 · N-105 4 · thumb/rep 3 = 54
- **21 validation rows** → every predicted / observed / ✓ / board cell present in its per-case section
  - Only change: † added on 3 board cells ("≈5 % MISS")
- **21 verbatim log blocks** → byte-identical (order regrouped by pair)
- **Prose sections** → every fact checked by hand
  - Status, legend, Result first, class table, rules table, mechanism column, upper edge values, caveats, rig, bracket picture, deviations, hands/BLE, corrections, the closing page paragraph, keycodes, layer ids
  - Status markers PROVEN / INFERRED / source → 🧪 / 🧮 / 📜: all carried over
- **Mermaid** → `@mermaid-lint/cli@0.53.1`: 2 diagrams, 0 errors, 0 warnings
- **Links** → all `results/` and `research/` targets exist; `MODEL.md` exists; `TESTS.md` missing (see Open)

## ❌ Lost (fixed)

- **6 fragile pairs table, D→V and V→D rows**
  - Source: "Δ ≤ 15 fires the combo on board and native, **Z** or **Tab**, instead of any letter"
  - Target kept "instead of any letter" for Z rows only → added to both Tab rows

## ✏️ Altered (fixed)

- **Proof pointer for MODEL (c)/(d)/(e)**
  - Tip callout said `MODEL.md` holds "MODEL (c), (d) and (e), cited by section letter"
  - `MODEL.md` has no lettered sections; the letters are v1's (`research/MODEL-v1-predictions.md`: (c) `&ak` path, (d) hack theorem, (e) linger/Callum)
  - Fix: letters now point to v1; R1–R9 stay on `MODEL.md` (R6/R7/R9 match in both)
- **Status scope of 📡 Hands and BLE**
  - Restyle nested it as H3 under "🚧 Caveats (🧮 INFERRED unless marked)"
  - The source had it as its own section, not under that umbrella; it holds computed counts ("Computed for all 54 pairs", 42 L-L / 12 R-R)
  - Fix: back to its own H2; its one INFERRED line keeps its explicit 🧮

## 🛠️ Target defects (fixed)

- **⛔ R13 restated as live**
  - Target showed "🧮 New: hack-OFF Δ = 0 strand" unflagged, and its added "Two source statements disagree" callout used it as a live conflict
  - R13 is refuted (`FIX-LOG.md` l.17-20, 🧪 FIX-R13-eqmin; `MODEL.md` R13 and "Erratum for PAIRS.md"; `FACTS.md` l.26)
  - Fix: heading struck + ⛔, source bullets kept verbatim, refutation bullet added, conflict marked as no longer standing, erratum item added
- **Erratum incomplete vs the canonical one in `MODEL.md`**
  - Missing: S-N_LT4-d11 "no sub-ms risk" (outcome-only, RVA-12) → † added on that board line + erratum item
  - Missing: R-thumb / repeat "no Δ band" needs an idle queue at the thumb-up → erratum item
  - Erratum footnote now links `FIX-LOG.md` and the full `MODEL.md` list
- **Legend:** "⚖️ sub-ms tie" → "⚖️ tie / unresolved on hardware" (shared legend; CORRECTIONS-FINAL F1)
- **Decorative actor emoji in a leaf bullet:** "Both keys leave 🧩 the combo engine…" → 🧩 removed
- **Dead script paths:** footer lists `results/S.mkcases.py`, `S.run.sh`, `S.excerpt.py`, `S-*.raw.log` (not in `Design/Timing/results/`)
  - Kept verbatim; added the repo location → `tests/timing/` `tools/` · `logs/` (21) · `cases/` (21)

## ❓ Open (not fixed, for Flo)

- `TESTS.md` link → missing file; planned in `README.md` map (also linked from `FACTS.md`)
- Verbatim source wording kept, though F1 calls it unsafe
  - "sub-ms coin flip" (🪟 Upper window edge)
  - "⚖️ = sub-ms tie" (Band notation)
- In-body `results/S.*` paths (🛠️ Rig, 🗂️ evidence filter) kept as written; only the footer maps them to `tests/timing/`
- Two "kept as written" flags from the restyle stand
  - S2 board "same" vs pair table `HIT 16…109 · ⚖️110`
  - Deviation item 3 "to the ms" vs items 1–2 (t+23 vs t+70)
- Shared legend collision, not PAIRS-specific: 🧮 = INFERRED and 🧮 = kscan/debounce
