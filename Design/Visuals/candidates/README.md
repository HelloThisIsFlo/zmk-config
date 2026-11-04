# 🎨 Hack diagram candidates

> [!important] What this folder is
>
> - Candidate explanations of the **AK consistency hack** (the 36-key `&none` combo, `combos.dtsi:49-50`), built 2026-11-04 for Flo to pick one from
> - Every page draws the **same proven numbers** from `../../Timing/FACTS.md` (board engine time); only the shape of the explanation differs
> - One candidate is kept in the end (or a merge); the chosen one feeds the website rebuild. Nothing here is the website
> - Published as a chooser artifact: https://claude.ai/artifact/JFXJx8aZr2c9o7ya7waR9x (same files, `index.html` is the chooser)

## 🗂️ Files

| File | Shape | Status |
|---|---|---|
| `index.html` | Chooser: one card per candidate, shared legend | artifact page (no doctype on purpose: the artifact wraps it) |
| `D1.html` | Build-up in three steps: one key, two keys without the hack, with it | reviewed by Flo (gut, tired) |
| `D2.html` | One race, two rows: hack on above, hack off below, drag Δ | reviewed by Flo (gut, tired) |
| `D3.html` | Outcome map: every pair class 0–130 ms at once, cursor + mini-timeline | reviewed by Flo (gut, tired) |
| `test_outcome.js` | `node test_outcome.js` checks D3's pure `outcome()` against 11 FACTS cases and prints the bands | passes |

- Open any page locally: `python3 -m http.server` in this folder, then `http://127.0.0.1:8000/index.html`
- Each `D*.html` is standalone (own doctype, inline CSS/JS, light + dark tokens, phone width ok)

## 🗣️ Flo's gut feedback (2026-11-04, not a validation of accuracy)

- **D2**: interactivity "really good", keep as a playground **after** an explanation. Reads as "the hack is the problem" because M→T comes first; P→C reveals the rescue at 11–26 ms. Must say: ≤ 10 ms is combo territory, intentional trade; 11–26 ms is where the inconsistency really was. Grey hold bar, the 10 ms, red/green arrows shown but not explained
- **D1**: likes the progressive steps, the design, the red/green band strip. Too much text. Step 1 "one key alone" / "lone T" not understood. Same hack-as-villain problem
- **D3**: "a lot"; style more basic; the jump at 30 ms when the P→C mini-timeline disappears is jarring. Strips maybe as a summary, not a lead
- Wants several candidates, not one merge; each next candidate comes from critic feedback, no pre-planned list

## 🔁 How a candidate is made

1. Builder writes `Dn.html` reusing a page's unit-tested `outcome(pair, hackOn, delta)`
2. Fresh-eyes critic opens it cold: "what confused you, ranked"
3. One fix round, then a card in `index.html`, publish, commit
