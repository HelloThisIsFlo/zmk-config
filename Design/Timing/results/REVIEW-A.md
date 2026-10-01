# 🔎 REVIEW-A — adversarial review of MODEL_v2.md + PAGE_FACTS.md

> Reviewer A · 2026-10-01 · targets `MODEL_v2.md` (566 l.) and `PAGE_FACTS.md` (622 l.)
> Method: every cited native log line in the ten truths and in PAGE_FACTS examples re-read in `results/*.raw.log` (helper `reviewA/g.py`); board arithmetic re-derived; source re-read (`combo.c`, `behavior_queue.c`, `behavior_sticky_key.c`, `behavior_hold_tap.c`, `central.c`, `physical_layouts.c`, `kscan_gpio_matrix.c`, compiled `zephyr.dts`, `cfg/`); old-page refs spot-checked in `Design/Visuals/index.html`.
> New native evidence: 4 own R2 cases `zmk/app/tests/ak-truth/RVA-*` (template `_rig_R2`, events-only overlay), logs `results/RVA-*.raw.log`.

## 🎯 Result first

- **Log lines: no fabricated or mis-timed quote found.** ~150 cited prefixes checked (T-02 … T-23, S-*, ARB-*, CORR-B) — all exist at the cited ms and mean what is claimed. Board translations in every worked example re-derived: all correct.
- **Defects are in claims, scope and consistency, not in the logs.** 4 major, 16 minor (RVA-01 … RVA-20).
- **Majors**
  - RVA-01 a "Must NOT say" item claims a native test killed a board-only claim.
  - RVA-02 the page's Callum "relaxed" and "close" scenarios are also wrong on Flo's keymap — PROVEN by new cases, not covered by PAGE_FACTS.
  - RVA-03 Callum thumb is force-TAPped (sticky Shift, never `l_mod`) when pressed ≤ 9 ms after any `&ak` letter — PROVEN by a new case, absent from both docs.
  - RVA-04 truth 9 / PAGE §6 fact 7 say sticky windows count from the original press — false for the AK layer (`aksl` is queue-stamped).
  - RVA-06 PAGE §1 fact 4 states the ≥ 11 ms guarantee without the no-shared-combo precondition.
- **Status upgrades from the new cases:** RM1 Shift lag + closing edge on `l_mod` (OPEN #7) and the Ex 3.3 trigram (OPEN #15) are now PROVEN on native.

## 🧪 New cases (R2 = Flo's keymap, hack ON)

| case | events (abs ms) | decisive lines | result |
|---|---|---|---|
| `RVA-htls-forcedtap-d5` | LM1 (T) 5 · LH1 10 (Δ 5) · LM1↑ 60 · LH1↑ 260 | `[00:00:00.017,000] … 31 decided tap (hold-preferred decision moment quick-tap)` → `[00:00:00.017,000] … keycode 0xE1` (sticky) · no `layer 26` line anywhere; only `layer 19` ON `[00:00:00.028,000]` / OFF `[00:00:00.129,000]` | LH1 held 250 ms never turns on `l_mod` |
| `RVA-callum-relaxed180` | page "relaxed": LH1 100–221 · LM1 tap 200–215 · RM1 280–311 (t+180) | `[00:00:00.280,000] … capturing position event 16` → `[00:00:00.297,000] … remaining_candidates=0 timestamp=296` → `layer_id: 26 position: 16, binding name: hold_tap_mod` → `keycode 0xE1`; `grep -c 'keycode 0x04'` = 0 | RM1 = Shift on `l_mod` (entr2 lag +17 native), **no "A"** |
| `RVA-callum-close245` | page "close": same, RM1 345–376 (t+245) | `[00:00:00.345,000] … capturing position event 16` → `[00:00:00.352,000] … layer 26 state 0` → `[00:00:00.362,000] … layer_id: 0 position: 16, binding name: flo,behavior-adaptive-key` → `[00:00:00.483,000] … keycode 0x04` + `Modifiers set to 0x02` | identical to "late": shifted "A" at R+262 native (board 380) |
| `RVA-ex33-cpn` | C 20 · P 40 (Δ 20) · N 65 (P+25) | P `[00:00:00.057,000] … layer_id: 4 position: 3 … bigram-TP` (F) · `[00:00:00.068,000] layer 4 state 0` · N `[00:00:00.082,000] … layer_id: 0 position: 12` · p↓ `[00:00:00.090,000] … 0x13` · `[00:00:00.101,000] layer 16 state 1` + `keycode 0x11` · `[00:00:00.112,000] layer 16 state 0` / `layer 14 state 1` | "tpn" — Ex 3.3 PROVEN; every board cell of Ex 3.3 = native − hops |

- md5: htls-forcedtap `b0302a44…`, relaxed180 `b34d7623…`, close245 `a17d60f5…`, ex33 `b27d4087…`. All `run-test.sh` PASS (auto-accept), one `Exiting` each.

## ✅ Ten truths — verdicts

| # | verdict | evidence / note |
|---|---|---|
| 1 longest live candidate | ✅ confirmed | T-12-a `[00:00:00.118,000] … 0x17` (+17), T-01-r2-map `[00:00:01.119,000]` hack rung → `[00:00:01.124,000]` 16 → `[00:00:01.126,000] … 0x04` (+19), T-17-a4 `[00:00:00.079,000]`, T-17-a3 `[00:00:00.062,000] … 0xE0`. `zephyr.dts`: on layer 26 only space/entr/entr2/tab/esc2/magicCloseQuitCb/settings live (0–31); bspc/del/delWord exclude 26. RM1 on `l_mod` now PROVEN (RVA-callum-relaxed180 `[00:00:00.297,000]`). |
| 2 `&ak` offsets | ✅ confirmed | T-12-a `[.118]` / `[.129] layer 19 state 1` / `[.230] layer 19 state 0`; board 16/26/126 = native − 1/2/3 hops. |
| 3 fast-roll MISS for 45 pairs | ✅ confirmed (native); board STALL correctly tagged BOARD-ONLY | T-23-a `[00:00:00.017,000] … layer_id: 0 position: 13`, T-23-b `[00:00:00.018,000] … layer_id: 0 position: 3`, S-N_LT4-d10 / S-O_RT3-d10 `[.022]`. Source re-check (`combo.c:141-143`, `bq:34-35`): right-hand now_flush = T+11 → Δ 10 not a quick tap → R9. |
| 4 band 11 … E_b−1 | ✅ confirmed | T-04-d11 `[.033]`/`[.034]`, T-05 `[.037]`/`[.038]`, S-N_LT4-d11, T-12-b-d111 `[00:00:00.178,000] … layer_id: 19`, d112 `[00:00:00.179,000] … layer 19 state 0` first. E_b formula re-derived for all 5 groups. |
| 5 six fragile pairs | ✅ confirmed | T-23-d1/d5/d6, S-L_LB3-d14/d17, S-H_RM2-d16/17/18, S-M_LT3-d5/14/15/16. Shared combos match `zephyr.dts` (magicCloseQuitCb LB3/LB2/LB1; capsWord RM1–RM4; typeZ LT3/LT2; tab LB1/LB0). |
| 6 hack is a trade | ⚠️ weakened | Numbers right, but board Δ 10 is STALL (often late HIT), not a cost; "latency cost only on 8 positions" contradicts truth 7; "identical ON/OFF" is outcome-only (S2 Δ ≤ 10 fires t+16 ON vs t+Δ OFF). → RVA-07. |
| 7 real combos under the hack | ✅ confirmed (nit) | T-09-a `[00:00:00.023,000]` vs T-09-c `[00:00:00.012,000]`, T-22-a/b, T-10-a/e, ARB-F2. Nit: "fires at its own deadline" — or at the next release/unrelated press (R7); no 2-key 18 ms combo exists. |
| 8 one queue, FIFO per item | ✅ confirmed | T-21-a (8+4 items, `count: 10`), T-21-c/e/h, T-13-b `[.104]`, T-13-fix-e-park `[.073]`, ARB-F3-a/b/c/d. |
| 9 timestamps never move | ⚠️ weakened | Combo/hold-tap/`skms` parts PROVEN (T-15-c `[.202]`, T-17-c `[.212]`, T-17-b2 `[01.552]`). "sticky windows count from the original press" is false for `aksl` (→ RVA-04). "Shift in the last ~16 ms types t" needs LM1 + held past R+130 (→ RVA-10). |
| 10 targets & transport | ✅ confirmed as tagged | T-07-d11 `[.022]` layer before `Row:`, T-12-b-d112, T-15-c; hands per PAIRS (42 L-L / 12 R-R); BLE quantisation INFERRED as tagged. |

## 🧨 Findings

### RVA-01 · major · PAGE_FACTS §1 Must-NOT (l. 119)
- **Quote:** "~~"At 10 ms the board types the base letter"~~ — … Killed by T-04-d10 (native) + R9 source (T-02-c, T-03)".
- **Problem:** no test can kill a board-only claim. T-04-d10 shows the *native* base letter (`[00:00:00.022,000] … layer_id: 0 position: 3, binding name: key_press`). The board STALL is INFERRED (OPEN #1, T-24a). MODEL (d) itself says left-hand triggers can floor now_flush to deadline+1 and turn the cell into a MISS — 42/54 pairs are L-L, so the "killed" sentence is partly true on the board.
- **Fix:** move to caveats as "predicted STALL, not measured; may be MISS for left-hand triggers".

### RVA-02 · major · PAGE_FACTS §2 Ex 2.2 + "What changed" Concept 2 (l. 168-183, 543-553)
- **Problem:** only the page's "late" scenario is corrected. The page has three (`index.html:2036-2050`: relaxed `nextKey 180`, close `245`, late `260`; success lane "A (shifted!)"). On Flo's keymap RM1 is `&htm LSHIFT` on `l_mod` (`layers_C_extra.dtsi:42`) inside `entr2` (layers 0–31):
  - relaxed 180 → RM1 resolves on `l_mod` → a Shift, no letter. PROVEN `RVA-callum-relaxed180` `[00:00:00.297,000] … layer_id: 26 position: 16, binding name: hold_tap_mod`, 0 × `keycode 0x04`.
  - close 245 → delivered at 261 > 250 → base `&ak A` → parked → identical to late. PROVEN `RVA-callum-close245` `[00:00:00.362,000] … layer_id: 0 position: 16` → `[00:00:00.483,000] … 0x04` + `Modifiers set to 0x02`.
  - The page's success/fail split at R+130 doesn't exist for RM1. The effective edge is R+114, and any letter delivered in (R, R+260) prints at R+260.
- **Fix:** add both scenarios to the Concept 2 table and Ex 2.2.

### RVA-03 · major · MODEL (i) l. 431 / (g) l. 381-387 · PAGE §2 facts 1-2 + Must-NOT l. 198 · §4 facts 6-7
- **Problem:** the forced-TAP band is scoped to "linger key, R thumb". LH1 `&htls` (hold-preferred, `require-prior-idle-ms` default −1, hack-only) is hit too. Pressed ≤ 9 ms (board; ≤ 10 native) after any `&ak` letter, it is decided TAP at the letter's delivery: sticky Shift, `l_mod` never on, however long held. PAGE §2 fact 1 "held alone it turns on `l_mod` at press + 90" and the Must-NOT qualifier "only when nothing else is pressed first" both miss it. Same mechanism for RH0 `&blt l_numsym SPACE` (INFERRED).
- **Evidence:** `RVA-htls-forcedtap-d5` `[00:00:00.017,000] … 31 decided tap (hold-preferred decision moment quick-tap)` → `… keycode 0xE1`; LH1 held until `[00:00:00.260,000]`, no `layer 26` line.
- **Board:** band ≤ 9; Δ 10 → STALL (same now_flush rule).

### RVA-04 · major · MODEL truth 9 (l. 68) · PAGE §6 fact 7 (l. 423)
- **Quotes:** "Combo deadlines, hold-tap terms and sticky windows count from the original press timestamp." · "every term, window and deadline counts from it."
- **Problem:** `aksl` is invoked by the behaviour queue with `timestamp = k_uptime_get()` (`behavior_queue.c:34-35`). `release_at = event.timestamp + 100` is set at that invocation (`behavior_sticky_key.c:181-186`). So the AK window counts from layer ON (D+10), not from the press. Read literally, both sentences bring back the killed claim "The AK layer is active for 100 ms after the key press" (PAGE §3 Must-NOT l. 285) and contradict truth 2.
- **Evidence:** T-12-a press `[00:00:00.101,000]`, OFF `[00:00:00.230,000]` = press + 129 native (not press + 101).
- **Fix:** scope to combo deadlines, hold-tap terms and hold-tap-invoked stickies (`skms`/`skm`, T-17-b2, T-19-d).

### RVA-05 · minor · MODEL (i) l. 435 vs PAGE §4 caveat l. 351, Ex 4.2 note l. 339, OPEN #14 · MODEL (k) l. 474
- **The four statements:**
  - MODEL (i): "Board Δ = 10: stranded to the next event, then HOLD (term already expired)".
  - PAGE §4 caveat: "then decides normally".
  - PAGE Ex 4.2 note: "typed on l_akA → late 'u'".
  - OPEN #14: lists both.
- **What the firmware does on Flo's keymap:** l_akA RT2 = `&bk U` (`sweep_pairs.json`), not a hold-tap. The stranded RT2 gives "u" if the next event E ∈ [T+21, ~T+121). It gives `lk_bk` with an expired term (immediate HOLD "-") only when E is past the layer. MODEL's unconditional HOLD only matches the T-16 R1 schedule.
- **Also:** (k) lists "forced-TAP Δ = 10" among ⚖️ tie cells, while (i)/(d) treat Δ 10 as a deterministic STALL (same now_flush comparison; A→RT2 is R-R).

### RVA-06 · major · PAGE §1 fact 4 (l. 46) · fact 10 (l. 52) · §4 fact 6 (l. 311)
- **Fact 4:** "If the follower is pressed 11 ms or later … the hack guarantees the AK layer is on". No class precondition, and no upper bound E_b. False for the 6 shared-combo pairs:
  - L→G key MISS to 14 (board), T-23-d1 `[00:00:00.030,000] … layer_id: 0 position: 21`.
  - H→E key MISS to 16 (board).
  - S2 pairs type Z/Tab to 15.
  - PAGE §7 says the opposite of fact 4.
- **Fact 10:** "every follower that has its own combo (34 pairs) adapts at every gap" is almost word-for-word the §1 Must-NOT on l. 116.
- **§4 fact 6:** the forced-TAP rule ignores letter + linger-key combos. A→RM0 (`entr2`) and U→RB0 (`magicBracketsL`) fire the combo, not a forced tap.

### RVA-07 · minor · MODEL truths 6/7, (d) S2 heading l. 273 · PAGE §1 facts 3, 12, 13, 14
- **Latency:** "Latency cost: +11 ms on the 8 hack-only positions only" and "every other key is unchanged" contradict truth 7 / fact 13 (fast real combos delayed by T−Δ).
- **S2 pairs:** "changes nothing for the 6 pairs" and "S2 hack ON = OFF" hold for the outcome only. Z fires at t+16 with the hack (S-M_LT3-d5 `[00:00:00.022,000]`) vs at completion without it (R7; T-09-c `[00:00:00.012,000]`).
- **Δ 10:** "costs 34 pairs every roll ≤ 10 ms" vs fact 7: board Δ 10 is a STALL, usually a late HIT.
- **Truth 7 nit:** fires at the deadline or at the next release / unrelated press.

### RVA-08 · minor · MODEL (c) l. 242 · PAGE §3 fact 15 (l. 231), §7 fact 9, MODEL (e) R-thumb row
- **Problem:** "0 ms tap … R↓, R↑ and l_akR ON all in the thumb-up ms" needs an idle queue. With a busy queue the nested `&ak` queues:
  - S-S_LH0-d10: R↓ `[00:00:00.033,000] … 0x15`, R↑ `[00:00:00.044,000]`, `layer 17 state 1` `[00:00:00.044,000]`.
  - So the layer comes on +10 (native +11) after R↓, and a key captured by the thumb hold-tap would then resolve before `l_akR`.
- PAIRS deviation 2 records this; neither target does. "No Δ band" for the R thumb carries the same precondition.

### RVA-09 · minor · PAGE §3 fact 8 (l. 224), MODEL (h) l. 418
- **Problem:** "A modifier pressed inside the window pins … every key typed meanwhile adapts" is PROVEN only on R1 with a raw `&kp LSHIFT` (T-20-a `[00:00:00.119,000] … layer_id: 0 position: 11, binding name: key_press`). Flo's alpha has no raw modifier. His are:
  - `htls` sticky Shift: ≤ 1 letter (T-20-c).
  - `l_mod` `&htm`: INFERRED, OPEN #10; there `l_mod` is the top layer and LT*/LB* are `&kp LG(…)`.
- **Fix:** the page fact needs the rig caveat.

### RVA-10 · minor · PAGE §2 facts 5, 12 + Must-NOT l. 201 · MODEL truth 9 · PAGE §1 fact 2
- **Fact 5:** "any letter typed in (R, R+260) appears at R+260". It is delivery that counts. A letter pressed in the last 16–18 ms is delivered after R+260 and is not parked.
- **Fact 12 / truth 9:** "Shift pressed in the last ~16 ms becomes t" holds only if LM1 is held past R+130. Delivery = min(key-up, press+16): T-18-f delivers at key-up `[00:00:00.215,000]`. RM1 would give "a", not "t".
- **§1 fact 2:** "holds every press for at least 11 ms" is false for taps shorter than 11 ms. The release flushes at its own ms (R6).

### RVA-11 · minor · stale statuses
- **RM1 Shift on `l_mod`:** lag and closing edge are tagged INFERRED in MODEL landscape l. 210, (g) l. 390, (n) l. 531, PAGE §2 fact 10, caveat l. 208 and OPEN #7.
  - Now PROVEN: `RVA-callum-relaxed180` `[00:00:00.280,000]` → `[00:00:00.297,000]` (+17 native).
  - Edge: `RVA-callum-close245` `[00:00:00.352,000] layer 26 state 0` → `[00:00:00.362,000] … layer_id: 0 position: 16`.
- **Ex 3.3 trigram (l. 266, OPEN #15):** PROVEN by `RVA-ex33-cpn`.

### RVA-12 · minor · MODEL (e) "PAIRS.md, first-class" l. 337 / PAGE sources
- **Problem:** PAIRS.md still prints the struck numbers, and neither target lists an erratum.
  - l. 70: "δ ∈ (0.03, 1.05] … ~95 % … ~5 %".
  - l. 77: "STALL S−1 (≈5 % MISS)".
  - Validation rows S-H_RM2-d17 / S-N_LT4-d10 / S-A_RT2-d10: "≈5 % MISS". H→E and A→RT2 are R-R pairs, where MODEL v2 says now_flush is deterministic.
  - S-N_LT4-d11: "no sub-ms risk" for an L-L pair.

### RVA-13 · minor · PAGE §4 fact 5 (l. 310) · MODEL (f) l. 372
- **Problem:** "on linger, right after the linger output" for `&ak`/`&bk` letters cites T-15-e, whose captured follower is a raw `&kp` (`[00:00:00.142,000] … layer_id: 0 position: 3, binding name: key_press`).
- No queued follower on the HOLD path was run. MODEL's "captured keys in the same instant" is true for raw `&kp` only. Flo's letters are queued, so they land at +10.

### RVA-14 · minor · MODEL (g) l. 407
- **Quote:** "Ctrl/Alt/Gui keep the full 130. INFERRED (R1 analogs PROVEN: T-18-b2 … R+119; T-18-fix-b-htm232 …)".
- **Problem:** neither run is an analog of a no-combo key at the R+130 edge.
  - htm232 is a combo-held position (`remaining_candidates=0 timestamp=371` → `[00:00:00.372,000]`), i.e. the R+130−k edge.
  - b2 is mid-window.
- "PROVEN analogs" overstates.

### RVA-15 · minor · PAGE Ex 1.4 (l. 97)
- **Problem:** cites S-O_RT3-d11, S-A_RT2-d11 and T-05, which are key-first cases with Δ < dA. C is hack-only, so Δ 11 = dA: the rung-vs-key case. The matching proof is T-04-d11 (R1 hack-only trigger, Δ 11, `[00:00:00.033,000]`/`[00:00:00.034,000]`). Outcome unchanged.

### RVA-16 · minor · PAGE header l. 10, §6 facts 3 + 10 · MODEL time convention l. 27
- **BLE range:** "0.5–9 ms BLE" (header, MODEL) vs "0–7.5 ms" (§6 fact 3).
- **"End-to-end"** covers the input side only. Host transport (USB poll, BLE HID interval) is omitted.
- **§6 fact 10** "identical … through current main" vs MODEL (m): upstream moved the left-hand stamp to the workqueue.

### RVA-17 · minor · MODEL (d) l. 262 vs PAGE §6 caveat l. 452
- **Quote:** "Both timers armed in one handler → margin ≈ 1.01 ms at any phase."
- **Problem:** not true for a BLE-stamped follower.
  - The stamp is taken in the BT RX callback (`central.c:263-266`).
  - The combo timer is armed later on sysworkq as `K_MSEC(T_B+11 − k_uptime_get())` (`combo.c:417`).
  - If a ms boundary passes in between, it becomes `K_MSEC(10)` and ties the layer's tick. The tick was armed first, so the outcome stays HIT.
- **Consequences:** the margin is ~0, not ~1 ms, for some presses of the 11 H0 pairs (all L-L). It also contradicts PAGE's own "left-left 1 ms margins … phase-sensitive".

### RVA-18 · minor · MODEL (f) l. 364
- **Quote:** "the RB0 morph (`magicBracketsL`)".
- **Problem:** `magicBracketsL` is the combo (RB0 RB1, `combos.dtsi:55`). The morph is `MagicUnder` (`mod_morph/behaviors.dtsi:139`), as PAGE §4 fact 9 says. The 16 ms fact itself is correct.

### RVA-19 · minor · MODEL R11 l. 197
- **Quote:** "records a phantom LONG_MAX deadline but schedules nothing … PROVEN(src work.c:967)".
- **Problem:** this is a board-only path.
  - `first_candidate_timeout()` returns `LONG_MAX` (`combo.c:198`), compared with `LLONG_MAX` (`:412`).
  - On native_posix_64 they are equal → `timeout_task_timeout_at = 0` + cancel.
  - On the 32-bit board they differ → schedule refused (CANCELING/DELAYED) → phantom `2^31−1`.
- My re-trace agrees there is no outcome effect. But no native test can exercise this path, so the tag should say source-only, board path.

### RVA-20 · minor · PAGE key map l. 16-33 · MODEL R10 l. 195
- **Key map:** misses RM3 `I` (`&ak 999 I`; del 16, delWord 18, capsWord 18 → 18), which Ex 5.2 uses.
- **R10 bullet:** the PROVEN(ARB-F2) tag also covers "RM1, RM3 @+12, RM2 → delWord only at the first release". ARB-F2 has no RM2, so that sentence is INFERRED, as PAGE §5 fact 9 says.

## 📋 Checks that passed (no finding)

- **Native vs board arithmetic in Ex 1.1–1.4, 2.1–2.3, 3.1–3.3, 4.2, 5.1–5.2, 6.1, 7.1–7.3:** every board cell = native − hops crossed. The (c) and (j) tables match T-12-a / T-21-a / T-23-c.
- **Must-NOT kills verified:** T-02-a, T-23-a/b/c, T-02-b, T-06-c, T-11, T-09-a, T-23-e5, PAIRS, T-17-a/c, T-18-a/f/g, T-19-a, T-17-a4, T-17-b2, T-12-a/b, T-07-d5, T-20-d, T-21-a/c/f, T-14-c, T-13-d, T-16-a, T-15-c/d/e/f, T-22-b, ARB-F2. Exception: RVA-01. The `&bk` "10 ms prevents drops" item is a reframing, not a kill (l. 292).
- **Combo inventory** (compiled `T-23-a-MT-d5/zephyr/zephyr.dts`): 28 = 22×16 + 5×18 + 1×11. Layer sets match R12 / (l) / §5 fact 12. `corne.conf:39-44` match R12.
- **Per-pair table vs PAIRS.md:** classes, counts (34/11/2/4/1/2), hands (42/12), S values and E_b (105/108/110/112/115; OFF 94/126) all agree.
- **RIG offsets:** +1 per relative timer, ladder re-anchoring (no drift), two hops for a rung-delivered `&ak`, three for sticky OFF — consistent everywhere.
- **Upstream (m):** consistent with F §2 (`LISTIFY(20,…)`, ≥ 20-key combos dropped, 2 `#warning`s).
- **Old-doc line refs spot-checked:** PAGE:1158, 1855, 2003, 2035-2050, 2075-2103, MECH:30, MECH:32, MECH:143, MLOG:160-162, DEEP:86, DEEP:120.
