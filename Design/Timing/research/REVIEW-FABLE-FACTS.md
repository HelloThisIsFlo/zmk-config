# 🔎 REVIEW-FABLE-FACTS — correctness gate on `FACTS.md`

> Reviewer: Fable 5.1 · 2026-10-01 · target [`../FACTS.md`](../FACTS.md) (the website specification)
> Method: every `case [hh:mm:ss.mmm,uuu] … fragment` pointer re-read in `tests/timing/logs/<case>.raw.log` (script `scratchpad/fable-check/check_cites.py`); every `file:line` pointer re-read in `zmk-config/config`, the fork `zmk/app/src`, Zephyr (container) and upstream; every worked-example board column re-derived from its native line with the hop rule; every must-NOT row traced to its killer; the five flagged tensions settled with evidence.

## 🎯 Result first

- **Log pointers: 236 checked, 236 exist and say what the fact says**
  - 231 matched by the script (timestamp line exists in that case's raw log and carries every quoted fragment)
  - 5 flagged by the script are table rows whose case is only in a bullet above the table; each re-read by hand: T-11-c `[00:00:01.159,000]` (pos 3 pressed `[00:00:01.147,000]`, +12), T-17-a4 `[00:00:00.079,000]`, S-M_LT3-d14/d15/d16 `[00:00:00.028,000]` / `[00:00:00.030,000]` / `[00:00:00.049,000]`
- **Source pointers: 24 checked, 24 hold** (one needs a HEAD note, below)
- **Worked examples: 18 tables, every board cell = native − hops crossed** (key-driven instants +0, rung-delivered `&ak` two hops before its layer)
- **Must-NOT rows: 49, every killer kills the exact claim** (two generic rows now carry the `bspc`/`del` exception)
- **Tensions: 5 flagged, 5 settled** — each `[!warning]` replaced by a one-line `[!note]` with its evidence
- **Tags: no 🧪 overclaimed** (every 🧪 names a line that exists); one untagged inference tagged 🧮
- **Mermaid: `@mermaid-lint/cli@0.53.1 --no-semantic` → 5 diagrams, 0 errors, 0 warnings**

## ⚖️ Tensions settled

| # | topic | resolution | evidence |
|---|---|---|---|
| 1 | stall join window: fact 7 "~10 ms" vs ⏸ legend / caveat "within 11 ms" | **up to 10 ms after the follower's own press** (gap 11 does not join); legend, fact 7 and caveat now agree | 📜 `combo.c:228` `candidate->timeout_at > timestamp` (strict, the T − 1 rule; same rule 🧪 T-22-a/b); the follower's fresh hack candidate expires at `ts + 11` · 🧪 RVB-strand-join: follower `[00:00:00.012,000]`, third press `[00:00:00.020,000] … capturing position event 0` (gap 8 joins), no rung line at native 24 ms, flush `[00:00:00.073,000]` |
| 2 | `bspc`/`del` at t+18 vs three generic "fires at its own 16 ms deadline" lines | the generic lines now carry the exception: "at its own deadline, or at a longer sibling's — `bspc`/`del`: t+18, hack or not" | 🧪 RVB-bspc-d12 `[00:00:00.031,000] … remaining_candidates=0 timestamp=30` + `keycode 0x2A` (gap 12, t+19 native) · RVB-bspc-d5-nohack `[00:00:00.024,000] … keycode 0x2A` (gap 5, hack off, t+19 native) · 📜 `combo.c:448-452` (complete with ≥ 2 alive → pending, no cleanup) |
| 3 | thumb-up stamp "5–15 ms" (§2 caveat) vs "+4.5…15" (Ex 6.1) | not one quantity: a **press** from idle debounces in 4–5 ms (5–6 while polling) → stamp +4.5…15; a **release** always runs on the 1 ms poll (the key is held) → 5–6 ms + BLE 0.5–9 → **≈ 5.5–15**. Caveat corrected to ≈ 5.5–15; Ex 6.1 unchanged | 📜 C §1 (`zmk,kscan-gpio-matrix.yaml:22-37`: `debounce-press-ms 5`, `debounce-release-ms 5`, `debounce-scan-period-ms 1`; integrator flips on the 6th sample; release 5.0–6.0) · 🧮 BLE term C §3 |
| 4 | Concept-1 change rows "latency only on the 8 hack-only keys" vs §1 fact 3 (rolls < 11 ms wait on every position) | rows now say: typed alone, +11 only on the 8 hack-only keys; in a roll under 11 ms the first key waits to 11 on every position (11 − gap) | 🧪 T-02-a `[00:00:00.018,000] … keycode 0x04` (t+12) vs T-02-b-nohack `[00:00:00.012,000] … keycode 0x04` (t+6), same events, 16 ms position · T-23-a M (16 ms LT2) `[00:00:00.017,000] … keycode 0x10` (t+12) |
| 5 | Concept-2 row "Shift on LM1/RM1 → 't'" vs §2 fact 12 (LM1 "t", RM1 "a"); is RM1's late letter shifted? | row now reads **"t" (LM1) / "a" (RM1)**; both resolve to the base `&ak` letter. The capital in RVA-callum-close245 comes from the scenario's own earlier Shift tap (a sticky), not from the mod key → §2 fact 12 gets that sub-bullet | 🧪 RVA-callum-close245 `[00:00:00.215,000] … 13 new sticky_key` (LM1 tap → sticky Shift) → `[00:00:00.362,000] … layer_id: 0 position: 16` (base `&ak A`) → `[00:00:00.483,000] … keycode 0x04` + `Modifiers set to 0x02` · T-18-g: zero `0xE1` lines, `[00:00:00.504,000] … Modifiers set to 0x00` → plain "t" |

## 🛠️ Every change

| where | was wrong / missing | evidence | fix |
|---|---|---|---|
| Legend, ⏸ row | "any letter pressed within 11 ms of the follower … joins" — off by one (T − 1 rule) | tension 1 | "a letter pressed up to 10 ms after the follower's own press (inside its 11 ms hack window, T − 1 rule)" |
| §1 fact 1 pointer | `adaptive_keys/combos.dtsi:64-65` is right at HEAD `83aa2ab`; the working tree has an uncommitted 6-line 2026-10 header note that moves the macro to 70-71 | `git show HEAD:…combos.dtsi` l.64-65 vs worktree l.70-71 | pointer annotated "at HEAD `83aa2ab` (… shifts it to 70-71)" |
| §1 headline callout | board band and net trade carried no evidence marker | MODEL_v2 (d): board bands BOARD-ONLY | "— 🔮 board band (native ❌ ≤ 10 · ✅ 11, 🧪 T-04, S-*)" · "— 🔮 board bands · 🧪 T-23, PAIRS classes" |
| §1 fact 7 | "(a press within ~10 ms joins the wait)" — vague anchor | tension 1 | "a press up to 10 ms after the follower's own press" |
| §1 must-NOT "hack never interferes" | truth column had no `bspc`/`del` exception | tension 2 | exception + RVB-bspc-* added to the killers |
| §1 `[!warning]` "when a fast real combo fires" | flagged tension | tension 2 | replaced by `[!note] Resolved …` |
| §1 caveat "letter … joins the stall" | "within 11 ms" | tension 1 | "up to 10 ms after … (its 11 ms hack window, T − 1 rule)"; evidence line now names the follower press, the joining press, the missing rung and `combo.c:228` |
| §1 `[!warning]` "how close a press must be" | flagged tension | tension 1 | replaced by `[!note] Resolved …` |
| §2 headline callout | no markers | §2 facts 4, 5, 11 | 🧪 T-18-a · 🧪 T-18-a, RVB-park-two · 🧪 T-18-g, RVA-callum-close245 · 🔮 exact edge ⚖️ |
| §2 fact 12 | "RM1 types 'a'" could be read as "unshifted" or "shifted" | tension 5 | sub-bullet: capitalised only by a sticky Shift armed earlier (close245 `[00:00:00.215,000] … 13 new sticky_key`); T-18-g plain "t" |
| §2 fact 14 | "· board arithmetic" (the 380) untagged | the 380 is derived from the page's round numbers, not a log | "· 🧮 board arithmetic (380)" |
| §2 caveat thumb-up stamp | "5–15 ms … 🧮 INFERRED" — lower bound and basis | tension 3 | "≈ 5.5–15 ms (release debounce 5–6 ms while the thumb is held + BLE ≈ 0.5–9 ms) — 📜 C §1 · 🧮 INFERRED (BLE)" |
| §2 `[!warning]` "thumb-up stamp delay" | flagged tension | tension 3 | replaced by `[!note] Resolved …` |
| §3 headline callout | no markers | §3 facts 1, 4, 11 | 📜 `macros.dtsi:25-39` · 🧪 T-12-a · 🧪 T-12-b, T-18-b · 🧪 T-21-a, ARB-F3 · 🔮 both ends ⚖️ |
| §4 headline callout | "≤ 9 ms → forced TAP" carried no 🔮 | §4 fact 6 BOARD-ONLY (native ≤ 10) | "— 🔮 board band (native ≤ 10, 🧪 T-16-a, S-A_RT2-d10)"; 📜/🧪 on the other two bullets |
| §5 headline callout | no markers | §5 facts 1–3, 11 | 📜 `zephyr.dts`, `corne.keymap:86-87` · 🧪 T-22 · 📜 src · 🧪 T-09-a |
| §5 must-NOT "Hack bar" | "real combos under 11 ms fire at their own deadline" — no `bspc`/`del` exception | tension 2 | "or at a longer sibling's (`bspc`/`del`: t+18, fact 5)" + RVB-bspc-* killers |
| §6 `[!note]` pipeline | no markers | §6 facts 2, 4 | 📜 `central.c:259-266`, `physical_layouts.c:178-182` · 📜 src · 🧪 log order |
| §6 pipeline diagram | kscan, stamp and BLE labels carried no markers | §6 facts 1 (📜), 2 (📜), 3 (🧮 distribution) | `· 📜` on the two kscan nodes and the stamp node; `· 🧮` on the BLE edge |
| §7 headline callout | no markers | §7 facts 2–7 | "— 🔮 board bands (native 🧪 T-23, S-*; D↔V 🧮)" |
| §7 class diagram | band nodes and the S2 node carried no markers | §7 facts 2, 4, 5, 6 (🧪 M→W), 7 (🧮 D↔V) | 🔮 on N1, N2, LG, HE bands; "M↔W · typeZ 🧪 / D↔V · tab 🧮" |
| 🔄 Concept 1 row "Every keypress is buffered 11 ms" | "the hack adds 11 only to 8 keys" — true only for a lone key | tension 4 | "typed alone … ; in a roll under 11 ms the first key waits to 11 on every position (fact 3)"; proof + T-02-a vs T-02-b-nohack |
| 🔄 Concept 1 row "Hack never interferes" | no `bspc`/`del` exception | tension 2 | exception + RVB-bspc-* |
| 🔄 Concept 1 row "Slider" | "latency only on hack-only keys" | tension 4 | "lone-key latency only on hack-only keys; in rolls under 11 ms the first key pays 11 − gap on every position" |
| 🔄 Concept 1 `[!warning]` "where the hack adds latency" | flagged tension | tension 4 | replaced by `[!note] Resolved …` |
| 🔄 Concept 2 row "Buffer ends at 130 for every mod" | "→ 't'" for both LM1 and RM1 | tension 5 | "→ the base letter: 't' (LM1) / 'a' (RM1)", proof + RVA-callum-close245 |
| 🔄 Concept 2 `[!warning]` "what a late RM1 Shift types" | flagged tension | tension 5 | replaced by `[!note] Resolved …` |
| ❓ OPEN #17 | listed ❓ although decided | orchestrator decision 2026-10-01 | "✅ decided · Page timelines in **engine time** — decided by the orchestrator 2026-10-01, Flo to veto · closes by: Flo's veto" |
| ❓ OPEN #18 | same | same | "✅ decided · Show **compiled things only** …, Flo to veto" |
| ❓ OPEN intro line | "🧪 RESOLVED rows stay listed" | #17/#18 now ✅ decided | "🧪 RESOLVED and ✅ decided rows stay listed" |

## ✅ Checked and found right (so the next reader can skip them)

- **Header "three clocks" + hop rule**: T-02 reconciliation `[00:00:00.018,000] … in 10ms` → `[00:00:00.029,000]` exists; every example's board column re-derived (Ex 1.1–1.4, 2.1–2.3, 3.1–3.3, 4.1–4.2, 5.1–5.2, 6.1, 7.1–7.3)
- **Key map**: compiled `build/right/zephyr/zephyr.dts` = 28 combos (22 × 16, 5 × 18, 1 × 11); hack = 36 keys on layers 0–24, timeout 11; hack-only positions computed from the DTS = {0, 5, 10, 20, 30, 31, 32, 33} = LT4 RT0 LM4 LB4 LH2 LH1 LH0 RH0 exactly as §1 fact 3; 18 ms tier = delWord ×2, delWordTrans ×2, capsWord as §5 fact 1
- **Source pointers**: `macros.dtsi:25-39` (`ak`), `behaviors.dtsi:21-27` (`blt_akR`), `CONFIG.h:6` (200), `aliases_layers_NAQUADAH.dtsi:30` (`l_akI 999`), `keymap.c:142-145`, `preprocessor_macros.c:69-77` (`LK`, tap-preferred, `linger_term`), `corne.keymap:86-87`, `hands_down/combos.dtsi:34` (bspc layer list) and `:55` (magicBracketsL RB0 RB1), `layers_C_extra.dtsi:41-43`, `corne.conf:44` (`MAX_KEYS_PER_COMBO=36`), `physical_layouts.c:178-182`, `central.c:259-266`, `usb_hid.c:139`, `app/Kconfig:142-143`, `hog.c:259-274`, `behavior_hold_tap.c:220-222`, `behavior_queue.c:35`, `combo.c:228/417/448-452`, Zephyr `timeout.c:122`, upstream `combo.c:100-101` (`LISTIFY(20, …)`), `zmk,kscan-gpio-matrix.yaml:22-37`
- **"+N native" claims re-derived from the press line**: T-01-r2-map RM1 `[00:00:01.107,000]` → `[00:00:01.126,000]` (+19); T-17-c `[00:00:00.121,000]` → `[00:00:00.212,000]` (+91), hold-tap created `[00:00:00.133,000]` (+12); T-17-b2 `[00:00:00.051,000]` → `[00:00:01.552,000]` (+1501); T-18-a `[00:00:00.242,000]` → `[00:00:00.373,000]` (+131) → `[00:00:00.504,000]` (+262); T-19-d `[00:00:00.062,000]` → `[00:00:01.563,000]`; T-14-c `[00:00:00.102,000]` ×3 (r↓, r↑, layer 17 ON) → OFF `[00:00:00.203,000]` (+101); T-15-c press `[00:00:00.101,000]`, created `[00:00:00.113,000]`, decided `[00:00:00.202,000]` (+101); T-16-a held `[00:00:00.012,000]` → `[00:00:00.324,000]` (312 ms); RVA-htls-forcedtap-d5 LH1↑ `[00:00:00.260,000]`, zero `layer 26` lines; RVA-callum-relaxed180 zero `keycode 0x04` lines
- **Must-NOT killers**: all 49 rows trace to a log or source that kills the exact claim (RVA-01's demotion already applied; the `&bk` "prevents drops" item is correctly a caveat, not a kill)
- **Caveats and OPEN #1–#16, #19–#24**: still true against MODEL_v2 and FIX-LOG; #7 and #15 correctly marked RESOLVED; #13's struck R13 strand matches FIX-R13-eqmin

## ❓ Left as is

- The `[!warning]` "PAIRS.md erratum" at the top is a notice, not a tension; it stays
- Board bands (⏸ 10, ⚖️ cells, ≤ 9 forced TAP, S−1 stalls) remain 🔮 by design; hardware (T-24) is the only closer
- The three multi-case tables (Ex 2.3, Ex 4.2, Ex 5.1) name their cases in the bullet above the table; a chaser must read the bullet first. Left in Flo's layout, verified by hand
- If the uncommitted `combos.dtsi` header note is committed, the §1 fact 1 pointer's parenthetical becomes the primary number (70-71)

---

_Checker script and edit script: `scratchpad/fable-check/check_cites.py`, `edit_facts.py` (exact-string replaces, each asserted unique)._
