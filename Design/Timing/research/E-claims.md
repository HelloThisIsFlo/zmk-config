# E — Claims Ledger: what the existing explanations assert

> Purpose: every atomic factual claim the current explainers make about AK timing, so each can be verified or refuted by the source-tracing readers.
> Scope rule: **no truth judgements here.** Only (a) what each source says, (b) where two sources disagree, (c) config-level anchors (what the keymap *config* literally contains, checked by reading `zmk-config/config`), never firmware-behaviour verdicts.
> Everything in the "INFERRED" sections is derivation from a source's own stated model, labelled as such.

## 📌 Read me first

- 🧾 **Ledger = 141 rows (E-01…E-141)**, grouped A–J below. Conflicts column names the opposing row(s).
- 🔥 **Five contested cores** (details in §Conflict map, tests in §Testable):
  - **When is key 1 delivered?** Docs + page: at Δ (moment key 2 "breaks" key 1's normal combo). Artifact: at 11 ms (hack expiry from key 1); "the engine has no per-combo release". → E-29/E-38/E-45 vs E-118.
  - **Per-key vs from-key-1 timers.** Docs: hack timeout counted per key (T released at Δ+11). Artifact: candidates expire from key 1; key 2 is *re-raised* with its original timestamp and then waits max(its real combo, 11) from that timestamp. → E-30/E-40 vs E-116/E-117/E-119.
  - **Does the hack guarantee success for Δ < 11?** Docs' worked example (Δ=5) says yes; docs' own caveat says two keys <11 ms apart are "released simultaneously" but that "doesn't matter because they intended a combo"; artifact says "bigrams faster than ~10 ms still miss" and that the docs' example sits inside the caveat. → E-38/E-44/E-48/E-88 vs E-122/E-123.
  - **What happens *without* the hack?** Page/docs: both keys released at once at the 16 ms combo timeout. Artifact: a non-member key 2 empties the candidate set → immediate flush at Δ, key 2 re-raised; key 2 then waits for *its own* combos. → E-21/E-22 vs E-116/E-124.
  - **Is the hack "free" for real combos?** Docs: "never interferes with real combo detection (11 < 16)". Artifact: silent (model excludes key 2 completing a combo). Neither says when a real 2-key combo actually fires with a 36-key candidate always present. → E-47, open question Q-1.
- 🧷 **Config-level anchors that several claims silently depend on** (checked in `zmk-config/config`, not firmware):
  - `corne.keymap:86-87`: `h_digraphs/combos.dtsi` and `pronouns/combos.dtsi` are **commented out** (since commit 839f7f6, 2024-09-05). So `th/sh/gh` linger combos and the `I'm`/`I'll` two-hand pronoun combos the page lists as examples are not compiled. The page was built 2026-02-26, after that.
  - With those excluded, the alpha positions whose **only** combo is the hack are: `LT4 (X)`, `LM4 (C)`, `LB4 (F)`, `RT0 (/)`, `LH0-2`, `RH0` (INFERRED from `hands_down/combos.dtsi`, `combos_linwin.dtsi`, `__EXPERIMENT__/combos.dtsi` (all commented)). The page's Concept 1 example key **C** is therefore hack-only, yet its timeline shows "C buffered by combo".
  - `layers_A_NAQUADAH_alpha.dtsi:20`: thumb `LH0` = `nav_akR` = `&blt_akR l_nav XXX`, tap side = `&ak l_akR R` (`adaptive_keys/behaviors.dtsi:20-28`). The deep dive says "Thumbs: none are adaptive"; the page labels it `NAV`.
  - `layers_C_extra.dtsi:42`: `l_mod` home row is `&htm LCTRL/LALT/LGUI/LSHIFT` (LM4..LM1) mirrored `LSHIFT/LGUI/LALT/LCTRL` (RM1..RM4). `htm` = hold-tap, `tapping-term-ms = action_mod_tapping_term` (130), `hold-while-undecided`, hold=`&kp`, tap=`&skm` (`mods/behaviors.dtsi:35-43`). No source describes `htm`; the page's Concept 2 treats the mod key as a bare `skm` tap.
  - `skm` `release-after-ms = <1500>` hardcoded (`mods/behaviors.dtsi:7`), not `sticky_key_release_timeout` (1000, `CONFIG.h:12`). No source states a sticky-mod lifetime.
  - `corne.conf:44` holds `CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO=36` (docs cite `corne.conf:58`). `corne.conf:42` `CONFIG_ZMK_COMBO_MAX_PRESSED_COMBOS=20` is mentioned by no source.
  - AK-path macros use `wait-ms = <0>` (`&ak` macros.dtsi:29, `&bk` :81, `REPLACE_CHAR_WITH_BIGRAM` preprocessor_macros.c:17); only `TYPING_MACRO` uses `wait-ms = <10>`. MECHANICS says "both typically 10ms".

## 🗂 Sources and provenance

| Tag | File | Last change | Notes |
|---|---|---|---|
| PAGE | `Design/Visuals/index.html` (2398 lines) | d7da2d6 2026-02-27 (content: da87197 2026-02-26 "Clarify combo invalidation in Concept 1, add two-hand combo examples") | Deployed GitHub Pages site. Prose at :1154-1581, data/timelines at :1592-2332 |
| HACK | `Design/ak-combo-hack.md` (118 lines) | ad76e43 2026-03-26 | "refines and structures" CMT |
| DEEP | `Design/ak-deepdive.md` (280 lines) | ad76e43 2026-03-26 | |
| MECH | `Design/MECHANICS.md` (216 lines) | 5000fba 2026-03-26 "Fix misleading AK claims in MECHANICS.md" | |
| MLOG | `Design/MECHANICS_LOG.md` (189 lines) | 2026-02-26 | Narrative history |
| COOK | `Design/COOKBOOK.md` (464 lines) | 2026-03-27 | Recipes 9-15 relevant |
| CMT | `config/features/hands_down/adaptive_keys/combos.dtsi:1-63` | be0f8b5 2024-03-09 (origin 98299f8 2023-10-19) | The original explanation, predates the fork point |
| ART | `scratchpad/investigation/artifact-ak-timeline-prose.md` | artifact built 2026-09-27 | Claims to be built from **v0.3** `combo.c`, `behavior_queue.c`, `&ak`; running fork = upstream 6e03a0bb 2024-09-12 (from brief) |
| INC | `Design/INCONSISTENCIES.md` | 2026-03-26 | Not in the brief; read because COOK cites it. Only `lk`/`lk_bk` duplication, no timing claims |

## 🧭 The five page concepts (keep what works)

| # | Concept | Mental model it teaches | Interactive it uses (index.html) |
|---|---|---|---|
| 1 | **The AK Consistency Hack** — "How a 1ms margin makes 23 adaptive keys reliable" | Race: combo resolution hands two keys to the keymap at once; `&ak` needs 10 ms before the layer is up; a never-firing 36-key combo with an 11 ms timeout holds key 2 back; `10 < 11` is *the* margin. | Two stacked swim-lane timelines (0-30 ms ruler, 5 ms ticks) "Without / With the Consistency Hack", lanes Physical / Combo / Buffer or Master / &ak Macro / Layer / P resolves; play-pause-reset with a red now-cursor (4 s real time); SVG keyboard highlights LM4 then LT1 (pressed → combo-member → ak-success/ak-fail); HID output boxes (`CP` vs `C̶TP`); gold annotation "ak_tap_time (10ms) < hold_key_event_delay (11ms)"; slider 5-20 ms for `hold_key_event_delay` with verdict text driven by `margin = v - 10` (:1999-2020). |
| 2 | **The Callum Mod Buffer** — "A 130ms safety net that makes mods forgiving" | Order matters, timing doesn't: thumb hold arms `l_mod`; after thumb release the layer stays 130 ms; failure = layer gone (mod positions revert to alpha), not sticky mod gone. | Three scenario pills (Relaxed 180 / Close 245 / Late 260 ms next-key); swim lanes Thumb (LH1) / Hold-Tap / Mod Layer / Buffer / Mod Key / Next Key over a 30 ms-tick ruler; play cursor; output `A` vs `a`; pass/fail badge. Lanes are generated from `TIMING` constants (:2055-2080). |
| 3 | **AK Keystroke Flow** — "The full adaptive key replacement pipeline" | Pipeline C → `&ak` → `l_akC` up → P lands on `CP_to_TP` → `REPLACE_CHAR_WITH_BIGRAM(T,P)` (backspace, T, release shifts, `ak_P`) → `TP`, chain continues on `l_akP`. | Six-stage vertical waterfall (6 s), each stage revealing micro-step chips; "Screen" display `C` → `C̶` → `T` → `TP`; keyboard highlights LM4/LT1 layer-active then ak-success. No time axis. |
| 4 | **Linger Keys** — "The 100ms tap-vs-hold decision" | Hold-tap, tap-preferred, 100 ms fork; `LK(TAP, LINGER)` reverses to ZMK's `<HOLD, TAP>`. | Press-and-hold virtual key driving a radial gauge (0-200 ms visual range; flips to LINGER at 100); output `'` or `"`; code block showing `LK(bk, &bk, &bk)` and `#define sqtDqt &lk_bk DQT SQT`; card list of "Active Linger Keys". |
| 5 | **Combo Timeout Tiers** — "Tighter timeouts = fewer misfires" | Three tiers 16/18/30 by finger geometry, plus the hack drawn as a 4th, dimmed 11 ms bar "all 36 keys (buffer only)". | Animated horizontal bars (width = ms/30); eight clickable example-combo cards that light the member keys on the SVG keyboard. |

Sidebar on every concept: collapsible "CONFIG.H Constants" panel (:1129-1137) listing 9 constants; interactive SVG keyboard with Naquadah labels (:1609-1618).

## 📒 Ledger

Column key: **id** · **claim** (numbers verbatim) · **source:location** · **conflicts_with** (row ids; "cfg:" = config-level anchor note, not a firmware verdict).

### A. Constants and invariants

| id | claim | source | conflicts_with |
|---|---|---|---|
| E-01 | `ak_tap_time` = 10 ms | PAGE:1129,1593; HACK:87 (`CONFIG.h:27`); DEEP:53,269; ART table | cfg: `CONFIG.h:27` ✓ |
| E-02 | `hold_key_event_delay` = 11 ms, "= ak_tap_time + 1ms buffer" | PAGE:1130; HACK:42,88 (`CONFIG.h:28`); ART table | cfg: `CONFIG.h:28` ✓ (comment says exactly that) |
| E-03 | `my_ak_window` = 100 ms, "how long the AK layer stays active" | PAGE:1132; HACK:92 (`CONFIG.h:8`); DEEP:24,86; ART table | cfg: `CONFIG.h:8` ✓ |
| E-04 | `linger_term` = 100 ms | PAGE:1131; MECH:54,138 | cfg: `CONFIG.h:4` ✓ |
| E-05 | `linger_term (100) = my_ak_window (100)` "aligned intentionally … same timescale" | MECH:138; MLOG:162-164 | cfg: `CONFIG.h:8` comment "makes sense to have it equal to the linger term" ✓ |
| E-06 | `action_lay_tapping_term` = 90 ms | PAGE:1133,1245; MECH:103,139 | cfg: `CONFIG.h:15` ✓ |
| E-07 | `action_mod_tapping_term` = 130 ms | PAGE:1134,1247; MECH:105 | cfg: `CONFIG.h:14` ✓ ("Slightly longer than htls, to allow for rolls"). Also used as `htm` tapping-term and `slm` release (`mods/behaviors.dtsi:28,38`) — no source mentions |
| E-08 | `action_lay_tapping_term (90) < linger_term (100)` "layers activate before linger resolves" / "layer switches win the race" | MECH:139; MLOG:164-166 | — |
| E-09 | Combo timeouts adjacent 16 / non-adjacent 18 / two-hand 30 ms | PAGE:1135-1137,1501-1504; HACK:89-91 (`CONFIG.h:9-11`); MECH:82-86; MLOG:154-155 | cfg: `CONFIG.h:9-11` ✓ |
| E-10 | Invariant chain `ak_tap_time (10) < hold_key_event_delay (11) << combo timeouts (16-30) << my_ak_window (100)` | HACK:82; CMT:46 (`ak_tap_time < hold_key_event_delay << ak_window`); MECH:137 | — |
| E-11 | "if those values ever swap, the whole AK system breaks" | MLOG:160-162 | — |
| E-12 | `TEMP_macro_tap_time` = 10 ms controls press-to-release in macros; `wait-ms` controls pause between steps; "Both typically 10ms" | MECH:143; DEEP:111 | cfg: `&ak`/`&bk`/`REPLACE_CHAR_WITH_BIGRAM` all `wait-ms = <0>`; only `TYPING_MACRO` has `wait-ms = <10>` (`preprocessor_macros.c:62`) |
| E-13 | Combo timeout history: 10 → 15 → 20 ms; two-hand 30 "early"; final 16/18/30, "haven't changed in months" | MLOG:146-156 | — |
| E-14 | 500 ms HRM tapping term is a "safety ceiling", now vestigial | MECH:145; MLOG:166-168 | cfg: `my_tapping_term_main 500` `CONFIG.h:5` ✓; HRM behaviours still defined `mods/behaviors.dtsi:91-188` |

### B. Combo-engine model (how ZMK buffers and releases)

| id | claim | source | conflicts_with |
|---|---|---|---|
| E-15 | "When a key participates in a combo, ZMK buffers the keypress until the combo resolves" | HACK:9; CMT:8 | E-114 (agrees, but ART: buffering is per *candidate set*, not per combo) |
| E-16 | Three outcomes: (a) all keys pressed → combo fires; (b) times out → buffered keys released **at once**; (c) a key not in the combo is pressed → buffered keys released **at once** | HACK:11-13; CMT:8-15 | E-116 (ART: flush = first key delivered, others *re-raised*, "in the same call"; outcome (c) only when the *set* empties) |
| E-17 | "When a combo times out or is invalidated (e.g., a non-member key is pressed), ZMK releases all buffered keys **simultaneously**" | PAGE:1161-1162 | E-116 |
| E-18 | "when a normal combo times out, ZMK releases all buffered keys simultaneously" | MECH:30 | E-116 |
| E-19 | Combo timeout for scenario (b) in the no-hack example = 16 ms after first key | HACK:23; PAGE:1861 | — |
| E-20 | (no hack) Two keys 5 ms apart both sit in the buffer until the 16 ms timeout, then `&ak` fires for both at t=16 | HACK:19-27 | E-116/E-124 (ART: key 2 non-member → flush at Δ=5, key 2 re-raised) |
| E-21 | (no hack, page fail panel) C at 0, P at 6, "Keys buffered by active combos" 0-16, "Both released at once!" 16-17, `&kp C` 16-26, `&aksl l_akC` 26-28, `l_akC active` 26-30, "P fires on ALPHA!" 16-18, output `CP` | PAGE:1855-1876, 1937-1943 | E-116/E-124; cfg: C (LM4) is in no compiled real combo, so "buffered by active combos" has no real-combo basis in the running config (see §INFERRED) |
| E-22 | (page fail panel) the second key's `&ak` fires at the same instant as the first key's → "P fires on ALPHA" | PAGE:1874 | E-124 (ART: re-raised key 2 waits for its own combos: P is in `space`/`typeQ` 16 ms combos) |
| E-23 | (page, generic) "Without help, the second key fires before the layer is ready — a race condition" | PAGE:1162-1163 | — |
| E-24 | "all the keys are released AT ONCE in scenario b) and c) → the second key press will **always** be triggered BEFORE the adaptive layer is activated" | CMT:24-25 | E-124 (ART: only when key 2 has no candidates of its own) |
| E-25 | Non-hack combos have "strictly longer timeouts than the hack, so the hack never interferes with real combo detection (11 < 16)" | HACK:96 | Q-1 (no source states *when* a real 2-key combo fires while the 36-key candidate is alive) |
| E-26 | "There's no scenario where you'd want an AK replacement for two keys pressed <11ms apart" / such presses are "wanting … a normal combo" | HACK:105; CMT:59-61 | E-122 (ART treats <~10 ms bigrams as real misses); E-38 (docs' own example uses Δ=5) |
| E-27 | The hack "never fires — you'd need to press all 36 keys within 11ms" | HACK:44; CMT:32 | — |
| E-28 | "every single keypress is buffered for 11ms by the combo system, because every key is part of this combo" / "whenever a key is pressed it will ALWAYS be delayed by the timeout of COMBO_AK_CONSISTENCY_HACK" | HACK:44; CMT:31-32 | E-125 (ART agrees for hack-only keys, but says keys in real combos "waited 16-30" already); E-29 (docs' own step-by-step delivers M at 5, not 11) |

### C. The consistency hack — mechanism and worked timelines

| id | claim | source | conflicts_with |
|---|---|---|---|
| E-29 | Step 5: "The 'normal' combo releases the original `&ak` key" when a non-member key arrives (key 1 delivered at the moment key 2 is pressed) | CMT:43-44; HACK:60-62 (t=5 ms "M is released from the normal combo → M's &ak fires: starts typing M") | E-118 (ART: "the engine has no per-combo release, so M actually waits until 11 ms") |
| E-30 | Step 7: "After `hold_key_event_delay`, the second key is released" — counted from the **second key's own press** (T at 5 → released at 16, "11ms after T was pressed") | CMT:45; HACK:70-72 | E-117 (ART: timers count from key 1; key 2 re-raised at 11 with timestamp Δ, then waits max(k2, 11) from Δ) — same 16 only when key 2 has no real combo |
| E-31 | t=11 "Hack combo times out for M … no-op for M" (hack timer treated per key) | HACK:64-65 | E-117 |
| E-32 | t=15 "M's &kp completes (10ms after t=5) → l_akM activates" | HACK:67-68 | E-118 (ART: layer at 21) |
| E-33 | "T is delayed by **at least 11ms** after M starts processing … Since &ak only needs 10ms … the AK layer is always ready" | HACK:75 | E-118/E-122 (ART: T delayed 11 after *its own* raise, but M starts at 11 not 5 → T lands only Δ after M) |
| E-34 | (page success panel) "C buffered by combo" 0-6; "P invalidates → C released" at 6 | PAGE:1887-1888, 1927-1935 | E-118; cfg: P is a *member* of the hack, so by the page's own rule (non-member invalidates) P does not invalidate the hack that also holds C |
| E-35 | (page success panel) "Master: ALL_KEYS buffers P (11ms)" 6-17 | PAGE:1891 | E-117 (agrees on 17 only if P has no real combo; P has `space`/`typeQ` 16 ms → ART 22) |
| E-36 | (page success panel) `&kp C` 6-16, `&aksl` 16-17, `l_akC active` 16-30 | PAGE:1894-1898 | E-118 (ART: 11-21, layer 21) |
| E-37 | (page success panel) "P hits l_akC!" 17-20, output `C̶ T P` | PAGE:1901, 1957 | — |
| E-38 | Docs' canonical example: M then T **5 ms apart** succeeds (`MN`) | HACK:48-73 | E-123 (ART: "the worked example … sits inside [the caveat]"); E-44 (docs' own caveat says <11 ms pairs are released simultaneously) |
| E-39 | Page's canonical example: C then P **6 ms apart** succeeds (`TP`) with hack, fails (`CP`) without | PAGE:1172, 1855-1903 | E-124 (ART model: without hack C→P at 6 ms also succeeds because P waits for its own 16 ms combos) |
| E-40 | Key 2 "is delayed by at least 11ms" ⇒ layer up "1ms before the second key fires" | PAGE:1164; HACK:75 | E-118 |
| E-41 | Guarantee framing: "guaranteeing the AK layer activates 1ms before the second key fires" | PAGE:1164; MECH:30 ("guaranteeing the AK layer activates first. This 1ms margin is what makes the whole system reliable"); MLOG:78-80 ("guaranteeing the AK layer is always live before any second key event can register") | E-44 (docs' own caveat), E-122 |
| E-42 | "This 1ms margin is what makes the entire Adaptive Keys system reliable" | PAGE:1218; MECH:30; MLOG:79 | E-125 (ART: the margin that matters is 11 vs 10 after re-raise, not 1 ms of slack on key 1) |
| E-43 | Slider semantics: margin = `hold_key_event_delay − 10`; <0 "FAILURE. Second key fires N ms before AK layer activates"; 0 "RISKY … Race condition likely"; +1 "PERFECT … production value"; >1 "Safe, but adds N ms of unnecessary input latency" | PAGE:2003-2020 | E-125 (ART: the whole 11 ms is added latency for hack-only keys, not just the margin) |
| E-44 | Caveat: "The **one** scenario where a race can still occur: two keys pressed within 11ms of each other … captured by the *same* hack combo timeout window … both are released simultaneously" | HACK:101-103; CMT:56-58 | E-38/E-39 (both worked examples are inside 11 ms yet shown succeeding); E-122 (ART says it is a real miss, boundary ~10 ms) |
| E-45 | In the caveat case both keys "are released simultaneously — the same problem as before" | HACK:103; CMT:58 | E-116/E-117 (ART: not simultaneous — key 2 is re-raised and waits ≥11 from its own timestamp) |
| E-46 | Reliability: "99.9% reliable" | CMT:51 | — |
| E-47 | The hack "doesn't affect nav, mod, num, or other non-alpha layers" (scoped to `l_alpha_aks`) | HACK:118; MECH:32 | cfg: `l_alpha_aks` = `l_alpha l_alpha_linwin l_akA…l_akY` (`aliases_layers_NAQUADAH.dtsi:59`) ✓ |
| E-48 | Combo hack vs `&bk`: hack solves "ordering at the combo-resolution level"; `&bk` solves "individual-key level" ordering; "Together, these two mechanisms make the AK system reliable" | HACK:77; DEEP:242-251 | E-71/E-72/E-73 (three different rationales for `&bk`) |
| E-49 | "The combo hack addresses the specific edge case where combo resolution releases multiple buffered keys at once, which would bypass `&bk`'s ordering guarantees" | DEEP:251 | — |
| E-50 | Hack definition: `COMBO_LAY_BASE(l_alpha_aks, ak_consistency_hack, &none, ALL_KEYS, hold_key_event_delay)`; binding `&none`; keys `ALL_KEYS` (36); timeout 11 | HACK:33-42; CMT:64-65 | cfg ✓ (`combos.dtsi:64-65`; `ALL_KEYS` in `aliases_key_positions.dtsi`) |
| E-51 | Requires `CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO=36` at `corne.conf:58`; "Without this setting, ZMK would reject the combo definition at compile time" | HACK:109-116 | cfg: it is at `corne.conf:44`; E-127 (ART: on v0.3 the combo is "silently dropped", i.e. not a compile error) |
| E-52 | The hack is drawn as a 4th tier bar: "11ms — all 36 keys (buffer only)" | PAGE:1527-1531 | — |

### D. `&ak`, `&aksl`, `&bk` internals

| id | claim | source | conflicts_with |
|---|---|---|---|
| E-53 | `&ak` = `zmk,behavior-macro-two-param`, `wait-ms 0`, `tap-ms = ak_tap_time` (10); bindings: `macro_param_2to1`, `macro_tap &kp X`, `macro_tap_time 0`, `macro_param_1to1`, `macro_tap &aksl l_akX` | DEEP:46-60; PAGE:1329-1334 | cfg ✓ `adaptive_keys/macros.dtsi:25-39` |
| E-54 | Step 1 "Tap `&kp M` — takes `ak_tap_time` (10ms) to complete" | DEEP:64; CMT:20-22 | — |
| E-55 | Step 2 "Set tap-time to 0 — so the next step executes instantly" | DEEP:65 | — |
| E-56 | "the associated adaptive layer will only be activated `ak_tap_time` ms after the key is pressed" | CMT:22; PAGE:1162 | E-115 (ART agrees: "armed 10 ms after key **delivered**, not when delivered") |
| E-57 | `tap-time = 0` "causes missed key presses (on M1 macbook air)" / "on some hardware" | CMT:20; DEEP:68 | — |
| E-58 | "This delay is what creates the race condition that the consistency hack solves" | DEEP:68 | — |
| E-59 | `&aksl` = `zmk,behavior-sticky-key`, `release-after-ms = my_ak_window`, `bindings = <&mo>`, **no** `quick-release` | DEEP:72-81 | cfg ✓ `adaptive_keys/behaviors.dtsi:1-9` |
| E-60 | "the AK layer deactivates after 100ms if no key is pressed" | DEEP:86 | — |
| E-61 | Without quick-release "the AK layer stays active until the next `&kp` *releases* (not just presses)" → "the next `&ak` macro can activate its own layer *before* the current one deactivates, enabling seamless chaining" | DEEP:87, 211-216; behaviors.dtsi:7-8 comment | — |
| E-62 | "When K is pressed in step 2, `l_akM` doesn't deactivate until K's `&kp` releases; by that time `ak_B` has already fired and `l_akB` is active; there's no gap" | DEEP:213-216 | — |
| E-63 | `&ak` "parks": behavior queue runs the `&kp` press immediately and parks for the 10 ms tap; `&aksl` runs after | ART "The macro parks" | — |
| E-64 | `&bk` = `behavior-macro-one-param`, `tap-ms = TEMP_macro_tap_time` (10), `macro_tap &kp` | DEEP:106-116; MECH:40 | cfg ✓ `macros.dtsi:77-87` (an earlier press/pause/release variant is commented out at :42-59) |
| E-65 | `&bk Z` "types Z, exits AK ecosystem — the chain ends" | DEEP:100, 118 | — |
| E-66 | `&bk` "exists primarily as a consistency mechanism that keeps all key events in ZMK's macro processing pipeline" | DEEP:118 | — |
| E-67 | "ZMK processes macro events in a serialized pipeline — events within and between macros maintain strict ordering. A raw `&kp` outside a macro bypasses this pipeline" | DEEP:120 | — (no mechanism cited; Q-6) |
| E-68 | "When an `&ak` macro is still in flight … a raw `&kp` from the next keystroke can fire out of order or race with those in-flight events" | DEEP:120 | — |
| E-69 | Rule: `&bk` for all normal typing flow; raw `&kp` only inside macros or for real holds (`lk_wispr` Globe) | DEEP:122-124; MECH:48; COOK:11 | — |
| E-70 | Evidence: AK layers have zero raw `&kp`; alpha non-adaptive keys use `&bk` (`&bk MINUS` RT3, `&bk J` RB4); combo outputs use `&bk`; raw `&kp` only in `&ak` internals (`macros.dtsi:33`), `REPLACE_CHAR_WITH_BIGRAM` (`preprocessor_macros.c:20/22`), `lk_wispr` hold | DEEP:126-130 | cfg: alpha also has `&MagicSlash`, `dotcol`, `comsemi`, `&MagicUnder` (mod-morph/lk wrappers) at `layers_A_NAQUADAH_alpha.dtsi:16-18` |
| E-71 | Rationale A: `&bk`'s "10ms delay between press and release ensures consistent key registration … Raw `&kp` inside macros can cause race conditions — keys arrive out of order or get dropped. The 10ms buffer prevents this" | MECH:40-42; MLOG:52-54 | E-72, E-73 (different rationales) |
| E-72 | Rationale B: `&bk` keeps events in the serialized macro pipeline vs raw `&kp` *outside* macros racing in-flight `&ak` | DEEP:118-120 | E-71, E-73 |
| E-73 | Rationale C: "`&bk` exists to solve a key-ordering problem that occurs when `&kp` is used directly **in behaviors (hold-taps, mod-morphs, etc.)** … Since `TYPING_MACRO` already *is* a macro, `&kp` works correctly inside it" | COOK:452 | E-71, E-72 |
| E-74 | "Every character output in the codebase flows through [`&bk`]" | MLOG:58-59 | — |
| E-75 | `&bk` "was invented here to make AKs actually reliable" (Sep 2023, as `&bkp`) | MLOG:52-57; MECH:38 | — |

### E. AK layers, replacement types, chaining, layout facts

| id | claim | source | conflicts_with |
|---|---|---|---|
| E-76 | Naquadah has **23** active AK layers; page title "23 adaptive keys" | DEEP:10; PAGE:1158; MECH:170 | cfg: `l_akA`=2 … `l_akY`=24 → 23 ids ✓ (`aliases_layers_NAQUADAH.dtsi:21-46`) |
| E-77 | SFB rate 0.082% | DEEP:11 | — |
| E-78 | `ak_X` = `&ak l_akX X`: types X and activates `l_akX` for 100 ms | DEEP:19-24; MECH:21 | cfg ✓ `adaptive_keys/aliases.dtsi:4-31` |
| E-79 | Left hand: all 15 alpha keys adaptive; right hand A, E, I, H, U, O, Y adaptive; punctuation and J use `&bk`/custom | DEEP:39-40 | cfg ✓ `layers_A_NAQUADAH_alpha.dtsi:16-18` |
| E-80 | "Thumbs: none are adaptive (they're layer switches, shift, space, etc.)"; page labels LH0 `NAV` | DEEP:41; PAGE:1616 | cfg: LH0 = `nav_akR` → tap = `&ak l_akR R` (`alpha.dtsi:20`, `adaptive_keys/behaviors.dtsi:20-28`); COOK:399 example "nav_akR — tap=AK-R, hold=nav layer" |
| E-81 | Page keyboard labels: thumbs `NUM SFT NAV` / `SPC SYM MAC`; deep-dive diagram `NUM SFT NAV` / `SPC NSYM TGL` | PAGE:1616-1617; DEEP:35 | cfg: `&mo l_num`, `tapStickyShiftHoldModsLayer`, `nav_akR` / `&blt l_numsym SPACE`, `&mo l_numsym`, `&togMacPc` (`alpha.dtsi:20`) |
| E-82 | Disabled AK layers set to `999` (l_akI, l_akJ, l_akQ, l_akZ); key still goes through `&ak` "for timing consistency", activation is a no-op | DEEP:42; MECH:34,170 | cfg ✓ `aliases_layers_NAQUADAH.dtsi:30,31,38,47`; ak_I on alpha RM3 |
| E-83 | Layer map: `l_akM` = 13; alpha 0-1; AK 2-24; utility 25-31; exactly 32 layers | DEEP:91,280; MECH:166-172 | cfg ✓ |
| E-84 | Four binding types on AK layers: `________` (chain continues via alpha `ak_X`), `&bk Z` (ends), `ak_Z` (continues), `XX_to_YY` (always continues) | DEEP:97-102 | — |
| E-85 | Type 1 example M→T = `MN`: `l_akM` LM1 → `&bk N` | DEEP:136-147; COOK:282-288 | cfg ✓ `layers_B_NAQUADAH_adaptive_keys.dtsi:128` |
| E-86 | M→K = `MB` with `ak_B` at LT0 on `l_akM` (chain continues) | DEEP:150; COOK:290-295 | cfg ✓ `:127` |
| E-87 | 3-key chain M→K→G = `MBL`: `l_akB` LB3 → `&bk L`; comment at `layers_B:126` | DEEP:197-209 | cfg ✓ `:17` (`l_akB` bottom row LB3) and `:126` comment "For M -> B(k) -> L" |
| E-88 | `REPLACE_CHAR_WITH_BIGRAM(A,B)` = backspace → type A → release LSHFT, RSHFT → `macro_tap ak_B`; "always chains" | DEEP:154-167; MECH:23-28; COOK:307-317; PAGE:1372-1381 | cfg ✓ `preprocessor_macros.c:12-28` (`wait-ms 0`, `tap-ms 10`) |
| E-89 | Type 2 example C→P = `TP`: `CP_to_TP` = `&replace_char_with_bigram_TP` (`aliases.dtsi:66`), instantiated `REPLACE_CHAR_WITH_BIGRAM(T, P)` (`macros.dtsi:21`), bound on `l_akC` LT1 (`layers_B:27`) | DEEP:169-182; COOK:327-330; PAGE:1295-1298 | cfg ✓ all three line refs |
| E-90 | Page stage 1: "Finger presses LM4 (left middle row, pinky). Binding: `ak_C`" | PAGE:1316 | cfg ✓ |
| E-91 | Page stage 4: "At ~50ms, finger presses LT1" (P) | PAGE:1359 | — (illustrative) |
| E-92 | Page stage 6: output `C̶` → Backspace → `TP`; "because the chain used `ak_P`, `l_akP` is now active" | PAGE:1390-1393 | — |
| E-93 | Shift releases exist to "prevent unintended case changes" / "explicitly release shift to prevent case contamination" / "(safety)" | MECH:27; MLOG:72-73; PAGE:1379 | — |
| E-94 | `___X____` = `ak_X`, used at X's own position on `l_akX`, "functionally equivalent to `________`", exists for keymap-drawer visibility; `__hE____` special | DEEP:224-240 | cfg ✓ `aliases.dtsi:34-61` |
| E-95 | `ak_hE` = `&ak l_akhE E`, used on `l_akH` at RM2; `l_akhE` has `&bk Y` at RB1 → H→E→U = `HEY` | DEEP:253-263 | cfg ✓ `aliases.dtsi:12`; `layers_B:95` |
| E-96 | "AKs can chain but don't trigger from utility layers" | MECH:32 | — |
| E-97 | HRM variants for S, C, N, T, E, A, M tap the `&ak` macro; HRMs "still exist" | MECH:114; MLOG:104-106; COOK:336-367 ("not currently active") | cfg: defined `mods/behaviors.dtsi:101-188`, not bound on Naquadah alpha |
| E-98 | `CONFIG_ZMK_BEHAVIORS_QUEUE_SIZE=512` because "a single AK fires a backspace, two character taps, and a shift release, each buffered" | MLOG:178-180; MECH:214 | cfg: macro emits backspace tap, BIGRAM_0 tap, **two** shift releases, then nested `&ak` (kp tap + aksl tap) |

### F. Callum mod buffer

| id | claim | source | conflicts_with |
|---|---|---|---|
| E-99 | `htls` thumb key is **hold-preferred**, "resolves on interrupt or after `action_lay_tapping_term` = 90ms" | PAGE:1245 | cfg ✓ `flavor = "hold-preferred"`, `tapping-term-ms = action_lay_tapping_term` (`mods/behaviors.dtsi:45-55`); no `hold-while-undecided` |
| E-100 | `htls`: "Hold (>= 90ms) activates the mod layer via `moAndBuffer`. Tap (< 90ms) activates a sticky mod via `skms`" | MECH:103; COOK:411 | E-99 (hold-preferred ⇒ an interrupting press before 90 ms also resolves as *hold*, not tap — MECH's "< 90 ms = tap" is only true without interruption) |
| E-101 | `moAndBuffer`: presses `&mo l_mod`, pauses for release, waits `action_mod_tapping_term` (130 ms), then releases | MECH:105; PAGE:1246-1247; COOK:411,422 | cfg ✓ `mods/macros.dtsi:1-25` (`macro_press &mo l_mod`, `macro_pause_for_release`, `macro_wait_time action_mod_tapping_term`, `macro_tap &none`, `macro_release &mo l_mod`; `l_mod` hardcoded) |
| E-102 | Buffer counted "after releasing the mod layer thumb key" / "waits for the thumb release, then keeps the layer alive for an extra 130ms" | MECH:112; PAGE:1246-1247, 2057 (`bufferEnd = thumbRelease + 130`) | E-103 |
| E-103 | "`moAndBuffer` macro … keeps the mod layer alive for 130ms **after hold detection**" | MLOG:126-127 | E-102 (macro waits 130 after *release*) |
| E-104 | Without the buffer "the layer could deactivate before the mod registers" (race) | MECH:105; MLOG:127-129 | — |
| E-105 | Order rule: Press → Mod1 → Mod2 → Release ✓; Press → Mod1 → Mod2 press → Release → Mod2 release ✓; Press → Mod1 → Release → Mod2 ✗ "(too late — layer gone)" | MECH:107-110 | E-107 (page's "late" case still lands 130 ms *after* release, so it is the 4th ordering with a >130 ms gap, not MECH's 3rd) |
| E-106 | Failure mode = the *layer* disappears (mod positions revert to alpha); "Already-armed sticky mods (like a Shift tapped via `skm`) remain active" | PAGE:1249-1251 | E-109 |
| E-107 | Page timelines: thumb hold 0-120; hold-tap "Deciding..." 0-90, "HOLD!" at 90; `&mo l_mod active` 90-250; buffer bar 120-250; "Shift (skm)" tap at 100; next key at 180 (relaxed ✓), 245 (close ✓), 260 (late ✗) | PAGE:2035-2080 | — |
| E-108 | Mod layer becomes active at t=90 (tapping-term expiry), not at thumb press | PAGE:2065-2069 | cfg: `htls` has no `hold-while-undecided` (commented out :53-54) — consistent with page |
| E-109 | Late case output: "Ctrl gone → types 'a'!", lane label "Ctrl? → hits alpha 'A'!", output lowercase `a` "unwanted letter!", badge "Layer expired — mod key became alpha!" | PAGE:2077-2103 | E-106 (a sticky Shift armed at 100 would still be active at 260 → by the page's own statement the letter would be shifted); cfg: on `l_mod`, Ctrl is LM4/RM4 (alpha C/H); RM1 (alpha A) is **LSHIFT** (`layers_C_extra.dtsi:42`) |
| E-110 | Mod keys on the layer are "`skm`" taps: `skm` = sticky-key with `ignore-modifiers` → stacking "tap Shift, tap Ctrl, next key gets both" | MECH:101; PAGE:2075 | cfg: layer keys are `&htm MOD MOD` (hold-tap 130 ms, hold=`&kp`, tap=`&skm`, `hold-while-undecided`) — no source describes `htm` |
| E-111 | Sticky mods have no stated lifetime in any source | — | cfg: `skm`/`skms` `release-after-ms = <1500>` (`mods/behaviors.dtsi:7,18`) |
| E-112 | Thumb is LH1 (`tapStickyShiftHoldModsLayer` = `&htls l_mod LSHIFT`) | PAGE:2061; COOK:419 | cfg ✓ `alpha.dtsi:20`, `mods/behaviors.dtsi:56` |
| E-113 | "Replaced Home Row Mods in Sep 2024" | MECH:99; MLOG:121 | — |

### G. Artifact-only engine claims (ART, 2026-09-27)

| id | claim | source | conflicts_with |
|---|---|---|---|
| E-114 | Rule 1 "One buffer, one candidate set": first key builds the set of every combo containing it; while non-empty the key sits in a buffer and the keymap does not see it; "No per-combo buffering" | ART rules | E-15/E-29 |
| E-115 | Headline: "&ak needs 10 ms before the adaptive layer is armed, and the combo engine can hand the next key to the keymap 0 ms after the first one" | ART headline | — |
| E-116 | Rule 2 "A new key filters the set": each further key removes candidates not containing it; if empty → flush: first buffered key delivered, others **re-raised as if just pressed, with original timestamps, in the same call** | ART rules | E-16/E-17/E-20/E-45 |
| E-117 | Rule 3 "Timers count from key 1": candidate expires at (time of first buffered key + its timeout); "When the **last** one expires, engine flushes the same way" | ART rules | E-30/E-31; Q-2 (flush on last expiry vs another rule) |
| E-118 | "In [ak-combo-hack.md], M is described as released at 5 ms 'from the normal combo'; the engine has no per-combo release, so M actually waits until 11 ms" | ART caveats | E-29/E-32/E-38 |
| E-119 | "key 2 always waits ≥11 ms after it is raised. 11 > 10, layer up when it lands" | ART "hack fills the hole" | E-122 (ART's own caveat: the re-raise happens at 11, so key 2 lands only Δ after key 1) |
| E-120 | Simulator: Case A (key 1 no candidates) d1=0; key 2 at Δ: d2 = Δ + max(k2, hack?11:0) | ART simulate() | — |
| E-121 | Simulator Case B (Δ < lastExpiry): if hack alive (Δ<11) → d1 = 11, d2 = Δ + max(k2, 11); else d1 = Δ, d2 = Δ + max(k2, hack?11:0). Case C (Δ ≥ lastExpiry): d1 = lastExpiry, d2 = Δ + max(k2, hack?11:0). layerAt = d1 + 10; ok if d2 > layerAt, race if equal, miss if less | ART simulate() | — |
| E-122 | "Bigrams faster than ~10 ms still miss": key 2 re-raised at key 1's 11 ms expiry, held 11 from its own timestamp → lands only Δ after key 1; layer needs 10 | ART caveats | E-38/E-40/E-41/E-44 |
| E-123 | "the worked example in Design/ak-combo-hack.md (M then T, 5 ms apart) sits inside [the caveat]" | ART caveats | E-38 |
| E-124 | "Key 2 in a slower combo helps": after re-raise key 2's own combos are candidates again, so a key in a 30 ms combo waits 30 and never misses; "This is why some pairs 'just worked' before the hack" | ART caveats | E-22/E-24 |
| E-125 | "Every alpha keystroke delayed by 11 ms (keys already in combos waited 16–30; keys not in combos now wait 11 instead of 0)" | ART caveats | E-43 (page: only margin above 10 is "unnecessary latency") |
| E-126 | Constants roles: `hold_key_event_delay` = "minimum wait for any raised key on alpha layers"; 16 ms = "also how long a key in one waits after a re-raise" | ART table | — |
| E-127 | "On ZMK v0.3 the combo is silently dropped. The engine only builds combos with up to 19 key positions"; fix = "4 groups of 9 keys and one 18-key combo per pair of groups (6 combos)" | ART caveats | E-51; brief: running fork is 6e03a0bb (2024-09-12), not v0.3 → not applicable to the board unless the fork shares the limit |
| E-128 | Model limits: two keys only; key 2 never completes a combo with key 1; ties shown as ties; "Exact-tie ordering in Zephyr depends on which work item was scheduled first" | ART limits | Q-3 |
| E-129 | Same three rules "in 2024 fork and v0.3" | ART heading | — (asserted, not shown) |
| E-130 | Artifact example pair L→G → `LL` if `l_akL` active | ART headline | cfg ✓ `layers_B:117` (LB3 on `l_akL` = `&bk L`) |

### H. Linger keys

| id | claim | source | conflicts_with |
|---|---|---|---|
| E-131 | Linger keys = `behavior-hold-tap`, `tap-preferred`, `tapping-term-ms = linger_term` (100); "Release before 100ms = tap. Hold past 100ms = linger" | PAGE:1414-1416; MECH:54 | cfg ✓ `preprocessor_macros.c:69-77`, `linger_keys/behaviors.dtsi:2-9` |
| E-132 | `LK(NAME, TAP, LINGER)` emits `bindings = <LINGER>, <TAP>` — reversed to match ZMK `<HOLD, TAP>` | PAGE:1416-1417,1446-1451; MECH:58-65; COOK:105 | cfg ✓ `:76` |
| E-133 | `sqtDqt` at RT4: tap `'` linger `"`; `#define sqtDqt &lk_bk DQT SQT`; `LK(bk, &bk, &bk)` | PAGE:1422-1424,1453-1455; COOK:107 | cfg ✓ `linger_keys/behaviors.dtsi:39-40`; INC: duplicate `sqtdqt` via `&lk` exists |
| E-134 | `equalDash`: tap `=` linger `-` | PAGE:1468-1469 | cfg ✓ `&lk_bk MINUS EQUAL` (`:41`) |
| E-135 | Active linger keys include `th` (th/tion), `sh` (sh/sion), `gh` (gh/ght); MECH "Common linger keys: qu, th/sh/gh, magicArrowL/R, magicCloseQuit"; COOK example `COMBO_LAY_ONE_HAND(l_alpha_aks, th, thAlias, LM2 LM1)` | PAGE:1471-1482; MECH:72; COOK:250 | cfg: `lk_th/sh/gh` only bound in `h_digraphs/combos.dtsi`, **not included** (`corne.keymap:86`); `lk_qu` unused (combos.dtsi:17 commented); `magicArrow*` combos commented (combos.dtsi:60-61); `magicCloseQuit` ✓ (:45) |
| E-136 | `wispr`: tap Opt+R, hold Globe via `&kp` on hold side — "the only linger key using this pattern" | PAGE:1484-1485; MECH:70; MLOG:12-34 | cfg ✓ `linger_keys/behaviors.dtsi:11-18`, `combos.dtsi:46` |
| E-137 | Page gauge: verdict computed purely from hold duration vs 100 (no interrupt modelling) | PAGE:2247,2286 | Q-7 (tap-preferred + interrupting key) |

### I. Combo tiers and examples

| id | claim | source | conflicts_with |
|---|---|---|---|
| E-138 | Tier rationale: adjacent 16 "accidental simultaneous presses extremely unlikely" / "virtually no misfires"; non-adjacent 18 "+2ms for the wider reach"; two-hand 30 "opposite-hand coordination varies more … accidental cross-hand presses very rare" / "hard to press simultaneously by accident"; COOK: two-hand "longer timeout for sync delay and hand coordination" | PAGE:1501-1504; MECH:84-86; COOK:242 | — |
| E-139 | `COMBO_ANY_*` on all layers (`l_all`) "for universal actions like space, backspace, enter"; `COMBO_LAY_*` layer-scoped | MECH:90-91; COOK:237-243 | cfg: `bspc` is `COMBO_LAY_ONE_HAND(l_alpha_aks l_nav l_num l_nav_linwin l_numsym, …)` (`combos.dtsi:34`), not `COMBO_ANY_*` |
| E-140 | Example cards: Space LT1+LT0 (16); Enter LM1+LM0 (16); Backspace RM1+RM2 (16); Q LT2+LT1 (16); Delete Word RM1+RM2+RM3 (18); Caps Word RM1-RM4 (18); I'm LT2+RM3 (30, "pronoun combo"); I'll LB2+RM3 (30) | PAGE:1540-1580 | cfg: first six ✓ (`combos.dtsi:24,25,34,15,36,67`); `pnIm`/`pnIll` positions ✓ (`pronouns/combos.dtsi:4-7`) but file **not included** (`corne.keymap:87`) |
| E-141 | Hardware: `MAX_COMBOS_PER_KEY=30`, `BEHAVIORS_QUEUE_SIZE=512`, `MAX_KEYS_PER_COMBO=36`, `HID_SEPARATE_MOD_RELEASE_REPORT=y`; each bumped "exactly when the system hit a limit" | MECH:93,211-216; MLOG:172-183 | cfg ✓ `corne.conf:39,40,44,49`; `MAX_PRESSED_COMBOS=20` (`:42`) unmentioned |

## ⚔️ Conflict map (same scenario, each source's own model)

**INFERRED** — I apply each source's stated rules to the same inputs. Nothing here is a firmware result. `k2` = key 2's real-combo timeout in the *running* config (h_digraph/pronoun combos excluded).

| Scenario | PAGE / HACK / CMT model | ART model (E-120/E-121) |
|---|---|---|
| Page hero: C(LM4) at 0, P(LT1) at 6, hack **on** | C→keymap 6 (P "invalidates" C's combo); `l_akC` 16; P→keymap 17 (6+11); **ok, +1 ms** | C hack-only → set {hack}; Δ<11 → d1 = 11; layer 21; P re-raised ts 6 with {space 16, typeQ 16, hack 11} → d2 = 22; **ok, +1 ms — but for a different reason (P's own 16 ms combos)**. If P had no real combo: d2 = 17 → **miss −4** |
| Docs hero: M(LT2) at 0, T(LM1) at 5, hack on | M→keymap 5; `l_akM` 15; T 16; **ok +1** | M {typeQ, typeZ, hack}; d1 = 11; layer 21; T re-raised ts 5 with {entr 16, hack} → d2 = 21 → **tie/race**; if k2 = 0 → 16 → **miss −5** |
| Page fail panel: C at 0, P at 6, hack **off** | both "buffered by active combos" to 16, released together; P on alpha → `CP` | C has **no** candidates in running config → delivered at 0; layer 10; P {space, typeQ} → 22 → **ok +12 → `TP`**. Even if C were in a real combo, P (non-member) empties the set → C at 6, layer 16, P 22 → ok |
| Lone C (hack-only) | delivered after 11 (E-28) | 11 |
| Lone K (LT0; one real combo `space` 16) | 11 (E-28) or unstated | Case A/C: lastExpiry = 16 → **16** (E-117); Q-2 asks whether the real engine flushes earlier |
| Lone X (LT4, hack-only), any layer in `l_alpha_aks` | 11 | 11 ("wait 11 instead of 0", E-125) |

Observations the synthesizer should carry forward (still not verdicts):
- The page and the docs share one model (per-combo release at key-2 press; hack timer per key). The artifact's model differs on **both** axes. They happen to agree on key 2's delivery (Δ+11) only when key 2 has no real combo.
- Under the artifact model the page's *without-hack* panel does not fail for its own example, and the docs' *with-hack* example is a tie. Under the docs' model both succeed by exactly 1 ms.
- Both older docs contain the caveat (E-44) that contradicts their own worked examples (E-38/E-39); the artifact is the first source to say so (E-123).

## ❓ Open questions (ambiguous from the sources; each with the test that settles it)

- **Q-1 Real combos under a 36-key candidate.** No source says when a 2-key real combo fires while the hack is a live candidate: at the second press, at 11 ms (hack expiry), or at 16 ms. Docs only say "never interferes" (E-25). Test T-05.
- **Q-2 Flush rule.** ART: flush when the *last* candidate expires (E-117). The docs never model a lone key. Whether the engine flushes earlier (e.g. when fewer than two candidates remain, which would deliver a one-real-combo key at 11 rather than 16) is unknown from reading. Test T-06.
- **Q-3 Ties.** Δ=5 M→T is an exact tie under ART (d2 = layerAt = 21). ART says ordering depends on Zephyr work-item scheduling (E-128). Test T-03 at Δ=5 repeatedly.
- **Q-4 Re-raise timestamp semantics.** ART: re-raised key keeps its original timestamp, so its combos are already partly expired (E-116). Docs: hack timer restarts at the key's own press (same arithmetic for k2=0, different for k2>0). Test T-02.
- **Q-5 Key-1 delivery path.** Whether the first buffered key is *released downstream* (no second pass through the combo module) or *re-raised* like the others changes nothing in ART's arithmetic but matters for a test harness that hooks position events. Trace `release_pressed_keys()` in the fork.
- **Q-6 `&bk` rationale.** Three incompatible explanations (E-71/72/73). None cites a mechanism in `behavior_queue.c`. Test T-11.
- **Q-7 Linger interrupt.** Page gauge ignores interrupting keys; `tap-preferred` semantics under interruption are unstated. Test T-12.
- **Q-8 Callum buffer origin.** 130 ms after *release* (macro, page, MECH) vs after *hold detection* (MLOG). Test T-09.
- **Q-9 Layer-arm instant.** All sources say "10 ms after key 1 delivered" (E-56/E-63) but none states whether `&aksl` runs at the `&kp` release edge (t+10) or a tick later, nor whether `wait-ms 0` adds anything. Test T-13 (boundary Δ).
- **Q-10 v0.3 19-key limit.** Only ART claims it (E-127); irrelevant to the board unless the fork shares it. Grep the fork's combo generation macros for a 19/20 bound.
- **Q-11 Page examples that reference uncompiled combos** (E-135, E-140) — a content fact for the redesign, not a timing question: decide whether to show only compiled combos.

## 🧪 Testable claims (most contested; native_posix sketches)

| id | claim under test | sketch |
|---|---|---|
| T-01 | Key 1 delivery time when key 2 (non-member of key 1's real combos) arrives at Δ<11: **Δ** (E-29/E-34) vs **11** (E-118) | Naquadah keymap + hack. `ZMK_MOCK_PRESS(LM4)` t=0, `ZMK_MOCK_PRESS(LT1)` t=6, releases at 40/46. Assert first HID report containing `C` at t=6 (docs) or t=11 (ART). Repeat with key 1 in real combos: LT2 (M) t=0, LM1 (T) t=5 → `M` report at 5 vs 11 |
| T-02 | Key 2 delivery after flush: **Δ+11 regardless** (E-30) vs **Δ+max(k2,11)** (E-117/E-124) | M t=0, T t=5 (T in `entr` 16 ms): `T`/`N` report at 16 (docs) vs 21 (ART). Control: pick a hack-only key 2 (e.g. key 1 = LB2 L, key 2 = LM4 C, Δ=5) → both models 16 |
| T-03 | Hack guarantees replacement for Δ<11 (E-38/E-40/E-41) vs "bigrams faster than ~10 ms still miss" (E-122) | Sweep Δ=1…20 for M→T and C→P; record output string per Δ. Docs predict `MN`/`TP` for all Δ. ART predicts for k2=16: miss Δ≤4, tie Δ=5, ok Δ≥6; for k2=0: miss Δ≤10, ok Δ≥11. Run Δ=5 ≥20× for Q-3 |
| T-04 | Without the hack, C→P at 6 ms fails with both keys released at 16 (E-21/E-22) vs succeeds because P waits for its own combos (E-124) | Build variant with `COMBO_AK_CONSISTENCY_HACK` removed. C t=0, P t=6. Assert `C` report at 0 (ART, C hack-only) vs 16 (page); final text `TP` (ART) vs `CP` (page) |
| T-05 | Hack "never interferes with real combo detection" (E-25): does `space` fire at the second press or only at 11/16 ms? | LT1 t=0, LT0 t=3, both released t=30. Assert `SPACE` report time: 3 (instant), 11 (hack expiry), or 16 (space timeout). Also LT2 t=0, LT1 t=3 (`typeQ`, with `space` and `typeZ` as sibling candidates) |
| T-06 | Lone-key latency and flush rule (E-28 vs E-117/E-125; Q-2) | Press-hold single keys, measure press-report time: LM4 C (hack-only) → 11 both models; LT0 K (exactly one 16 ms combo) → 16 (ART) vs 11 (fewer-than-two flush); LT1 P (two 16 ms combos) → 16; RM4 H (`capsWord` 18) → 18 vs 11 |
| T-07 | `&aksl` no-quick-release chaining: `l_akM` stays up until K's `&kp` **releases**, so `ak_B` arms `l_akB` with no gap; M→K→G = `MBL` (E-61/E-62/E-87) | M t=0 (rel 30), K t=60 (rel 200), G t=120 (before K release) → expect `MBL` (docs: K delivered ~71, `l_akB` armed ~81, window to ~181); G t=250 (after K release and after the window) → expect `MBG`; K t=60 rel 70, G t=90 → `MBL`. Log `l_akM`/`l_akB` layer-state changes to see whether `l_akM` drops at K's release (200) or at K's press |
| T-08 | Every alpha keystroke on `l_alpha_aks` delayed ≥11 ms; utility layers not (E-28/E-47/E-125) | Single press LT4 (X) on alpha → report at 11; `&mo l_nav` held then a nav key → report at 0 |
| T-09 | Mod layer alive until thumb release + 130 (E-101/E-102) vs hold-detect + 130 (E-103); failure is layer loss, sticky mods persist (E-106) vs lowercase `a` (E-109) | LH1 press 0 rel 120; RM1 tap 100-105 (`htm LSHIFT` tap → `skm`); RM2 tap at 245 → expect sticky LGUI armed (layer alive) then release; at 260 → expect `E` typed **shifted** (sticky shift still armed) — page says lowercase. Also probe 225 (=90+130+5) to separate E-102 from E-103 |
| T-10 | `htls` hold-preferred: interrupting press before 90 ms resolves as hold (layer), not sticky shift (E-99 vs E-100) | LH1 press 0, RM1 press 30 rel 40, LH1 rel 60 → expect `l_mod` active at 30 (RM1 = `htm LSHIFT` → sticky shift) vs `skms LSHIFT` then alpha `A` |
| T-11 | `&bk` prevents out-of-order/dropped output vs raw `&kp` after an in-flight `&ak` (E-67/E-68/E-71) | Two keymap variants: RB4 = `&bk J` vs `&kp J`. `ak_M` t=0, J t=2 (both inside hack window → delivered 11 and 13). Assert report order `M`,`J` and no drops in both; any difference validates a rationale |
| T-12 | Linger fork at 100 ms with tap-preferred (E-131/E-137) | RT4 press 0 rel 60 → `'`; press 0 rel 150 → `"`; press 0, RM1 press 50, RT4 rel 120 → `'` then `A` (tap-preferred under interrupt); press 0, RM1 press 105 → `"` then `A` |
| T-13 | Layer arm instant = key-1 delivery + 10 exactly (E-56/E-63; Q-9) | Hack off, key 1 hack-only (C) so d1 = 0; key 2 hack-only too (e.g. C→X if any replacement exists, else use a synthetic 2-key keymap: key A = `ak_A`, key B = `&bk` on `l_akA`) with no combos → d2 = Δ. Sweep Δ = 9, 10, 11 → expect miss, tie, ok |

## 📎 Appendix — page numbers that are *only* animation choreography (not claims)

- `TimelineAnim.duration` 4000/4000/6000 ms and fractional `t` triggers (0.08, 0.16 …) are real-time pacing, not modelled milliseconds. The modelled numbers are the `start`/`end` fields in `failLanes`/`successLanes` (:1855-1903) and the `scenarios` object (:2035-2051).
- Concept 3 `data-delay` values (100-750 ms) are reveal delays; the waterfall has no time axis and makes no timing claim beyond "~50ms" (E-91).
- Concept 4 gauge visual range 0-200 ms (:2241) is presentation.
