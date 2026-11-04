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
| `D6.html` | Watch the letters land: slow-motion replay (1 s = 20 ms), hack on/off scenes in sync, letters fly into a text field at their typing moment | from both critics' "the hold wait never landed"; critic pass + fix round done (1 s = 6 ms, 0.8 s hold on each event, per-pair sentence per panel) |
| `D7.html` | Two presses, one gate: D2's playground reworked (opens where the hack wins, labels in place, rule stated, 0–40 strip below) | from Flo's "D2 is the keeper playground" + D2's critic; critic pass + fix round done (labels now sit right of the gate line when they don't fit left of it) |
| `D8.html` | What comes out: a real word (kept = K E P C, column = C O L U M T) typed at a chosen gap, hack on beside off, outcome not mechanism | from every critic's "why is mt wrong?"; critic pass + fix round done (both words always on screen, replay timed around the critical gap) |
| `D9.html` | Type it yourself: the browser times your own two-key roll and shows what the firmware would type at that gap, kept and column, hack on beside off | from "the ms stays abstract"; critic pass + fix round done (verdict sentence under your gap, strip first, mechanism behind a toggle) |
| `D10.html` | Your roll, and why: the jury's merge, D9 spine + D7 lanes driven by one gap, 0–9 ms drawn as combo territory | built last (22:10), no critic pass: budget |
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

## 🔍 Cold critic on D7 (Fable, 2026-11-04)

- Cold read after 60 s: "With the hack on, P→C adapts from 11 ms instead of needing 26, because the 2nd key is made to wait 11 ms and lands after the gate; the price is essentially nothing" (right on the fix; the cost is invisible on P→C)
- Confusions, ranked: (1) three statements about one bar ("waits 16", bar ends at 15, "✂ cut short") → one state sentence per 1st key; (2) "leaves at 11 / both leave at 11" unexplained, the hack visibly delays the 1st letter too; (3) margin arrows read as motion, not measurement → bracket; (4) "(P's layer)" is jargon; (5) on P→C the cost is invisible → "cost: none here, see M→T"; (6) the combos sentence mixes 10 and 15 ms; (7) phone 400 px: labels collide, ⚖️ a smudge, legend orphans "exact tie"; (8) "waits behind" reads as spatial → "held 11 ms by the hack"; (9) ⏸ sounds like a bug the reader will hit, but it's a prediction
- Keep: two lanes on one shared axis with one draggable Δ ("the best thing here"), verdict chip + the one-line margin sentence, the purple gate region from a dashed line, the "every gap at once" bar tied to the slider, "Wanted:" first
- Verdicts: ✅ no longer reads as "the hack is a problem" (first page to pass); gate idea landed; hold-wait half-landed (wording)
- Fix round applied: one state sentence per 1st key, bracket margin, phone pass (see git log)

## 🔍 Cold critic on D6 (Fable, 2026-11-04)

- Cold read after one watch: "C only gives pt if the t lands after a gate that opens 10 ms after p; with the hack C holds back and lands after the gate, without it C fires immediately and misses" (right; could not say what the hack is or why M→T differs)
- Confusions, ranked: (1) the replay is over in 1.5 s, every transition flashes past; (2) the two panels hide their one difference, nothing says why C waits with the hack and not without; (3) M→T contradicts the framing (hack only hurts there) with no per-pair sentence; (4) "P's layer" jargon; (5) "both leave at 11" unexplained; (6) verdict chip far from the typed box; (7) phone: the on/off comparison is never on screen at once, playhead hard to scrub by thumb, strip slivers 4 px; (8) the gate box grows with "now" and reads as a bar
- Keep: the typed box with the letter landing green/red ("instantly tells the outcome"), the three-row timeline with hatched holds and typed dots, the gap slider that auto-replays, the strip summary lines
- Verdicts: hold-wait landed (when scrubbing), cut-short landed clearly, the gate rule landed; what the page never states is *why* the 2nd letter is early or late
- ⚠️ the critic's suggested wording "the hack shortens T's 16 ms wait to 11" is wrong (hold = max(11, 16) = 16); not applied
- Fix round applied: slower replay with holds on events, per-pair sentence per panel, plain words, chip beside the typed box (see git log)

## 🔍 Cold critic on D8 (Fable, 2026-11-04)

- Cold read after the first replay: "with the hack on, K-E-P-C at 15 ms gives kept; without it kepc, so the hack fixes 11–26 ms gaps". The hack looks like a pure win
- Confusions, ranked: (1) the cost is hidden behind the second word chip, "a trade I cannot see"; (2) the replay spends 2 s on K E P and the only moment that matters lasts 100 ms; (3) blue keycaps unexplained, the press flash invisible; (4) "which is enough" / "before P's adaptive layer is on" don't share one sentence; (5) the ⏸ chip says nothing about the letter; (6) "?" for the tie; (7) phone strip 10 px rows and labels; (8) footer is a wall of numbers
- Keep: the two typed boxes side by side with the last letter coloured ("the whole claim in one glance"), verdict chips under them, the strip with the cursor + zone, the per-gap sentence, dark mode
- Verdicts: wanted output understood (why C becomes T stays opaque, by design); reads as "the hack is free" (the opposite risk); as a first page, nearly: fix 1 mandatory
- Fix round applied: both words on screen at once, replay re-timed around the critical gap, phone strip (see git log)

## 🧮 Correctness audit of D4–D7 against FACTS (Fable, 2026-11-04)

- All four `outcome()` blocks agree with MODEL's Δ tables (holds 16/16/16/0, 11 for C under the hack, 1st letter at min(Δ, hold), gate +10, close +110, every band edge). Only text was off
- ❌ fixed: D4 stage 2 title "every key waits 11 ms" → "at least 11 ms"; D6 "makes C wait 11 ms, like every key" → the 11 ms floor; D5 bug: at exactly 10 ms the detail showed "both leave at 11" (code `d <= 10`, must be `d <= 9`)
- ⚠️ fixed everywhere: the rescued band is **11–25 ms** (26 is a tie without the hack), the pages said 11–26; "6 pairs untouched/unchanged" → "type the same with the hack on or off" and the 3 band-less pairs named; "(X C F, thumbs)" → "a thumb" (only LH0 is a follower in the H0 pairs); D7 "upstream ZMK" → "v0.3+"; ≤ 9 ms wording "typed together" → "both leave the engine at 11, t read on the base layer"; ⏸ "waits for your next key-up or a later press"
- Kept on purpose: "the intended trade" (Flo's own judgement, 2026-11-04: "it's a trade-off that I'm happy to make"); "where real typing happens" was replaced by Flo's words "where the inconsistency was"
- Not fixed, cosmetic: D5 strip tails "… ✅ to ~115" are hedged with ~ (✅ ends at 114, ⚖️ at 115)

## 🔍 Cold critic on D9 (Fable, 2026-11-04)

- Cold read after 60 s: "the board turns kepc into kept and columt into column if you roll fast enough; the hack makes kept work in a band where it used to fail while breaking column only for super-fast rolls" (right)
- Confusions, ranked: (1) first roll gave 2 ms and four red tiles, "I broke it?": nothing next to the number says which zone you landed in; (2) "Wanted: the adapted letter" read three times, nothing says kept is the goal; (3) "the pair the hack fixes / costs" is the thesis but muted grey; (4) the mechanism paragraphs compete with the strip, skipped; (5) a slow roll pins "you" at 40 and shows the same red as the cost; (6) "Use 15 ms instead" reveals a slider it doesn't promise; (7) ⏸ needs a verdict word; (8) phone copy says "roll two keys" with no keyboard
- Keep: the two-word on/off tile grid with underline vs squiggle ("instant"), the 4-row strip with the "you" box and the zones ("the best element on the page"), the clickable history pills and the ±2 ms line, dark mode
- Verdicts: measuring the gap made it real; reads as "a reasonable trade, slightly in its favour"; would send to a friend after fix 1
- Fix round applied: verdict sentence under the gap, strip moved under the pad with the mechanism behind a "why?" toggle, intro rewritten, phone copy (see git log)

## 🧑‍⚖️ Jury verdict on D4–D9 (Fable, cold, 2026-11-04; a starting point, not a decision)

| # | Page | 60 s: fix + cost + intent | mechanism | phone | little reading | alone | One line |
|---|---|---|---|---|---|---|---|
| 1 | **D9** Type it yourself | 5 | 2 | 3 | 4 | 4 | goal first, your own gap, verdict sentence names the zone; mechanism behind a toggle |
| 2 | **D7** Two presses, one gate | 3 | 5 | 4 | 3 | 4 | best drawing of the why; the cost is invisible until you click M→T |
| 3 | **D5** What the hack trades | 4 | 4 | 3 | 4 | 4 | one sentence + map say the trade; why-lanes collide at 400 px; never says "intentional" |
| 4 | **D4** Problem first | 3 | 5 | 3 | 4 | 4 | everything labelled in place, ghost bar for the cut hold; three clicks to the price, first screen a red ❌ |
| 5 | **D8** What comes out | 4 | 2 | 4 | 4 | 3 | the two words side by side are the claim in one glance; replay slow to reach the letter that matters |
| 6 | **D6** Watch the letters land | 2 | 5 | 3 | 3 | 2 | the only page where "a letter waits behind its hold" lands (motion); 5 s replay, cost never on screen |

- 🎯 **Recommendation: one page, D9 spine + D7 why**
  - Spine = D9 as is (goal line, pad, gap number, verdict sentence, pills, 4-row strip with "you", on/off word tiles, slider for phones)
  - Replace D9's "why?" toggle text with D7's two lanes driven by the same gap; default the lanes to the pair the reader's gap actually changes (≤ 9 → M→T, 11–25 → P→C); lift D4's dashed ghost of the uncut hold
  - Promote the "intended trade" callout to right under the verdict sentence when the gap is ≤ 9 ms
  - Fallback if the merge is too much: D9 first, D7 linked as "why?"
- ⚠️ **What every page still fails at**: the 0–9 ms cost band is the same red as a failure, and "intentional" lives in a footer → draw 0–9 as "combo territory" (hatched/grey, ⌨️ label) with the one-line reason beside it
- 🗑️ Delete without regret: D6 (motion win, but nobody watches it twice), D8 (contained in D9), D5 (map = the strip, lanes = a smaller D7), D4 (keep only the ghost-bar idea)
- 👀 D8 replay "stuck at ke / colu" seen by the jury: checked, not reproducible (words complete by 2.5 s at 1100 and 400 px, background tab too); the replay runs on timers, not animation frames. Only a window that draws no frames hides the letters (the `drop` keyframe fades from opacity 0). Hardening if ever needed: drop `opacity: 0` from that keyframe

## 🔚 Where this stopped (2026-11-04 ~21:50)
- Nine candidates in the artifact (version 12) and in this folder; usage guard reached ~96 % weekly before the 23:00 reset
- ⚠️ From ~21:35 the SSH push was refused (the SSH agent socket had no identities); the commits went up over HTTPS with the GitHub CLI's login instead (`git -c credential.helper='!gh auth git-credential' push https://github.com/HelloThisIsFlo/zmk-config.git main`). The SSH agent still needs a look
- Next: Flo reads the jury table, opens D9 then D7, decides merge vs sequence; then the website rebuild from `../../Timing/FACTS.md`

## 🔍 Cold critic on D10 (Fable, 2026-11-04, time-boxed)

- Cold read: "a tool that measures my two-key gap and tells me the hack rescues kept between 11–25 ms and deliberately sacrifices column under 10 ms; the timeline below half-proves it" (right)
- Confusions, ranked: (1) Rule says "gate = 1st letter + 10 ms" but the lanes show "gate opens at 25" for a 15 ms roll: the text never says a letter is typed up to 16 ms after its press; (2) the pair switch flips on its own when the gap changes; (3) at 7 ms "▨ given up · kepc" vs "❌ base letter · kepc" for the same word; (4) opening the slider replaces the measured gap with 15; (5) ⏸ / ⚖️ cells unlabeled
- Keep: the big live gap + verdict sentence ("best part of the page"), the four strips with "you" and the hatched 0–9 band ("reads instantly"), the word cards, the chips, the mobile layout
- Verdicts: the 0–9 band now reads as a deliberate trade ✅; the why panel explains the gate but never states the holds in words; "with fix 1 I would send it to a friend"

## 🔁 How a candidate is made

1. Builder writes `Dn.html` reusing a page's unit-tested `outcome(pair, hackOn, delta)`
2. Fresh-eyes critic opens it cold: "what confused you, ranked"
3. One fix round, then a card in `index.html`, publish, commit
