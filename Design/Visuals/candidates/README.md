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
| `D4.html` | Problem first, three steps: P→C without the hack, with it, then the price on M→T; every element labelled in place | from Flo's feedback; critic pass + fix round done |
| `D5.html` | What the hack trades: map of the two groups that differ + race-lane "why" under the scrubber | from the critic's verdict; critic pass + fix round done |
| `D6.html` | Watch the letters land: slow-motion replay (1 s = 20 ms), hack on/off scenes in sync, letters fly into a text field at their typing moment | from both critics' "the hold wait never landed"; critic pass pending |
| `D7.html` | Two presses, one gate: D2's playground reworked (opens where the hack wins, labels in place, rule stated, 0–40 strip below) | from Flo's "D2 is the keeper playground" + D2's critic; critic pass pending |
| `test_outcome*.js` | `node test_outcome.js` (D3), `_d4.js`, `_d5.js` check each page's pure `outcome()` against 11 FACTS cases and print the bands | all pass |

- Open any page locally: `python3 -m http.server` in this folder, then `http://127.0.0.1:8000/index.html`
- D2's own `outcome()` lacks the window-closing edge (fails 4 of the 11 edge cases past 110 ms; harmless on its 0–60 axis); D4–D7 carry the complete one
- Each `D*.html` is standalone (own doctype, inline CSS/JS, light + dark tokens, phone width ok)

## 🗣️ Flo's gut feedback (2026-11-04, not a validation of accuracy)

- **D2**: interactivity "really good", keep as a playground **after** an explanation. Reads as "the hack is the problem" because M→T comes first; P→C reveals the rescue at 11–26 ms. Must say: ≤ 10 ms is combo territory, intentional trade; 11–26 ms is where the inconsistency really was. Grey hold bar, the 10 ms, red/green arrows shown but not explained
- **D1**: likes the progressive steps, the design, the red/green band strip. Too much text. Step 1 "one key alone" / "lone T" not understood. Same hack-as-villain problem
- **D3**: "a lot"; style more basic; the jump at 30 ms when the P→C mini-timeline disappears is jarring. Strips maybe as a summary, not a lead
- Wants several candidates, not one merge; each next candidate comes from critic feedback, no pre-planned list

## 🔍 Cold critic on D1–D3 (Fable, 2026-11-04, fresh eyes, judging the explanation not the facts)

- 🧠 **Hardest idea, hidden by all three pages**: a key's letter is delayed by its own combo hold, and the second press ends the first hold early (`aOut = min(Δ, hold)`). Readers saw the trigger's bar shrink while dragging and thought the page was glitching
  - Suggested device: a race with a gate (the layer-on line); each letter waits behind a barrier (its hold); the second press visibly knocks the trigger's barrier shorter
- **D1**: keep the stage progression, the drag + live verdict pill, the stacked on/off strips. Fix: stage 1's lone T and the detached C strip (introduce C in stage 2), four competing timer labels (keep two: hold end, layer on), "45 pairs" vs D3's "34" with no visible sum, 9 px SVG text and a 20 px handle at 400 px
- **D2**: cold read was the opposite of the intent ("hack on = broken") because it opens on M→T at 8 ms. Keep the two lanes on a shared axis and the margin arrow once labelled. Fix: no title or claim above the fold, pointer drag selects axis text, the arrow never says what it measures, no view of the whole range
- **D3**: cold read was right ("trades 0–9 on 34 pairs for 11–25 on 11"). Keep the headline as a conclusion, the on/off strip per group, scrubber + detail. Fix: uneven ticks read as a log axis (the cost looks tiny), scrub line through the headings, five concepts before the one asked about, grey bars labelled only in a tooltip
- ⚖️ **Better starting shape for the next candidate: D3** (strips answer "when" for every pair at once; the mechanics can live underneath as the "why")
- Screenshots: `.playwright-mcp/critic-D*.png` (gitignored, local only)

### 🧭 Candidates seeded from this
- **D4** (from Flo's feedback): problem first. P→C without the hack, then with it, then the price on M→T; every drawing element labelled in place, almost no prose
- **D5** (from the critic): D3 collapsed to the two groups that differ, even ticks with a cut tail, headings outside the plot, a race-lane "why" below the scrubber that shows the barrier cut short

## 🔍 Cold critic on D4 (Fable, 2026-11-04)

- Cold read after 60 s: "Pressing C soon after P gives pc or pt depending on a few ms, and the hack is going to fix that" (right)
- Confusions, ranked: (1) reader assumed fast = adapted, so the red `pc` strip looked like the adapted case failing → say which output is wanted before "unreliable"; (2) the 4-row summary boxes span all rows, including the off rows they don't apply to; (3) stage 2 shows the hack with no on/off comparison in the picture, the layer line doesn't move, so "the hack moved nothing"; (4) stage 3 switches to M→T with no sentence saying it's the other kind of pair; (5) the key distinction (C in no combo vs T held by its own combos) lives only in 11 px grey annotations; (6) ⏸ and ⚖️ legend too terse; (7) phone annotations grey on grey; (8) "same roll, two results", "36-key combo that never fires" unglossed
- Keep: the stage tabs with the live verdict pill ("that pill is the page"), the band strip with the mirrored handle, stage 3's on/off chips
- Still reads as "the hack is a problem"? Slightly: first screen is a red ❌ pill and the red box sits above the green one across every row; "the words say trade-off, the colour says loss"
- Fix round applied the three top fixes + legend, gloss, phone contrast (see git log)

## 🔍 Cold critic on D5 (Fable, 2026-11-04)

- Cold read after 60 s: "The hack makes 11 P→C-type pairs adapt from 11 ms instead of 26, and in exchange 34 M→T-type pairs stop adapting under 10 ms" (right)
- Confusions, ranked: (1) no legend for ✗mt / ✓mn, "why is typing mt wrong?"; claim sentence is jargon ("rolls", "reliable what"); (2) cost/fix boxes span rows where nothing differs; (3) the rule is never stated ("2nd letter adapts only if it leaves after the gate"), "+10" unlabelled, gate has two names; (4) "held 16 ms by its combos" reads as a finger holding the key, nothing says the circled p is the moment the letter is typed; (5) label pile-up at 7 and 10 ms, unreadable at 400 px; (6) phone axis "gap, ms 0" merges; (7) ⏸ / ⚖️ slivers unlabelled on the map
- Keep: one scrubber driving map and lanes, per-lane verdict pill + coloured one-sentence verdict, the 10 ms ⏸ case ("clearest moment on the page"), dark + 400 px hold
- Did the "why" panel click? Half: ✂ cut-short and the +10 gate landed; "a letter waits behind its hold" did not
- Fix round applied: plain-words claim + legend, boxes on the differing rows only, the rule stated once, label staggering (see git log)

### 🧭 What both critics agree on (drives the next candidate)
- The reader must be told **which output is wanted** before anything is called a failure
- The **rule** must be stated in words once: 2nd letter adapts only if it leaves after the gate (1st letter + 10 ms)
- **"A letter waits behind its hold, then is typed"** has not landed in any static drawing; the circled letter must read as the typing moment

## 🔁 How a candidate is made

1. Builder writes `Dn.html` reusing a page's unit-tested `outcome(pair, hackOn, delta)`
2. Fresh-eyes critic opens it cold: "what confused you, ranked"
3. One fix round, then a card in `index.html`, publish, commit
