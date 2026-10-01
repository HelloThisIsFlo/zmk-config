# 📒 CLAIMS — ledger with verdicts + prioritised test plan

> Extends `E-claims.md` (141 rows, same ids). Verdicts are preliminary: **holds / contradicted / ambiguous / untestable**, each with a one-line reason and a source cite. Firmware = fork `4211ad74` = upstream `6e03a0bb`; line refs as in MODEL.md.
> Verdict shorthand: `holds*` = holds with a nuance the page must carry; `(→T-xx)` = the test that confirms or settles it.

---

## 🔥 Contradictions that matter for the page (lead with these)

1. **Both hero examples fail on the running firmware.** Docs' M→T at 5 ms (E-38) and page's C→P at 6 ms (E-39) are MISSES with the hack: both keys wait for the hack rung at 11 ms, key 1's `&ak` stamps its keycode *now*, key 2 is re-raised with its old timestamp → `is_quick_tap` (`require-prior-idle-ms = -1`, `combo.c:141-143`) → 0 candidates → key 2 resolves on the base layer at 11 ms while the layer arrives at 21. And the page's "without the hack" C→P panel (E-21/E-22) is a HIT: C has no real combo → delivered at 0, layer at 10, P waits for its own 16 ms combos → resolved at 22 on `l_akC`. (→T-02, T-23)
2. **Key 1 is not "released from the normal combo" at Δ when Δ ≤ 10** (E-29/E-32/E-34): key 2 shares the hack with it, so the set is not emptied; both leave at key 1 + 11. The Δ-flush exists only for 11 ≤ Δ < k1 (`combo.c:439-441`).
3. **Key 2 is never "delayed 11 ms after its own press"** (E-30/E-31/E-35/E-40/E-119): Δ ≤ 9 → 0 ms after key 1 (bypass); Δ = 10 → stranded until the next press/release (`work.c:967` refuses the schedule while CANCELING); Δ ≥ 11 → `Δ + max(11, k2)`.
4. **The hack's benefit is narrow and its cost is broad** (E-24/E-41/E-42/E-124): it rescues only the 12 pairs whose follower sits on a hack-only position (LT4/LM4/LB4/LH0) for 11 ≤ Δ ≤ k1+10; every follower in a real combo already adapted for all Δ without it; with it, all 23 pairs miss at Δ ≤ 9 and stall at 10.
5. **The "1 ms margin" story is misplaced** (E-42/E-43/E-10): the real margin is `max(11,k2) − 10 ≥ 1` and only exists for Δ ≥ 11; the failure region below 11 is untouched by `hold_key_event_delay − ak_tap_time`. The slider's "adds N ms of unnecessary latency" applies only to the 8 hack-only positions.
6. **Lone-key latency is the LONGEST candidate, not 11** (E-28/E-125): 11 / 16 / 18 ms by position (`combo.c:472-481`). The hack adds latency only to hack-only positions.
7. **Real combos completed inside the hack window do not fire at completion** (E-25): they fire at their own 16/18 ms deadline or at the next key event (`combo.c:448-452`, observed A2 S7); a 3-key combo pressed out of order stalls until a release (`combo.c:409-418, 473`).
8. **"Without the hack all buffered keys are released at once at 16 ms" is wrong** (E-16/E-17/E-18/E-20): a non-member key empties the set at Δ, key 1 is delivered then, key 2 is re-raised and gets its own timer (or bubbles if it has no combo).
9. **The docs' caveat is right in effect for Δ ≤ 9 but the artifact's mechanism is wrong** (E-44/E-45/E-122/E-121): "released simultaneously" is exactly the bypass; "held 11 ms from its own timestamp" never happens (bypass or strand).
10. **Callum buffer** (E-103/E-109/E-110/E-102): layer stays 130 ms after thumb RELEASE (macro `pause_for_release`), not after hold detection; the behaviour queue is parked until release + 260 (`bq:45-48`), so the page's late key is emitted ≈ 100 ms late and SHIFTED (sticky Shift persists) — not lowercase "a"; `l_mod` keys are `&htm` (mod down from press, `ht:522-526`), not bare `skm` taps.
11. **`htls` is hold-preferred** (E-100): any key pressed before 90 ms → HOLD (`ht:333-347`), so "tap < 90 ms = sticky shift" holds only when nothing else is pressed.
12. **Page content references uncompiled things** (E-135/E-140/E-80/E-09): th/sh/gh linger combos and I'm/I'll two-hand combos are `//` in `corne.keymap:86-87`; the 30 ms tier has zero consumers; thumb LH0 is `&blt_akR` (tap = AK-R), not a plain NAV key.
13. **`&bk` rationale** (E-71/E-72/E-73): the mechanism is the single FIFO behaviour queue (raw `&kp` after a multi-step macro would jump ahead of queued output); the 10 ms explains why not 0 (host drops), not why `&bk` instead of `&kp`. (→T-21)
14. **Artifact-only claims**: v0.3 19-key drop is true upstream and irrelevant to the board (E-127, F); simulator Case B is wrong (E-121); "ties depend on Zephyr scheduling" (E-128) — no exact-ms tie exists in the 2-key model (bypass vs strand discretises it).
15. **Small doc drifts**: macro `wait-ms` is 0 not "typically 10" (E-12); `MAX_KEYS_PER_COMBO=36` is at `corne.conf:44` not `:58` (E-51); `REPLACE_CHAR_WITH_BIGRAM` = 8 queue items + 4 nested, not "backspace, two taps, a shift release" (E-98).
16. **New facts no source states**: a linger key or hold-tap pressed ≤ 9 ms after an `&ak` alpha is force-decided TAP (`ht:142-149`, same −1 skew); the AK window seen from the next key-down is 105–110 ms (not 100) and is pinned by any held modifier (`sk:269-281`); native_posix shifts the bypass boundary to Δ ≤ 10 (timer +1 ms) — page numbers must say which target they describe.

---

## 📋 Ledger (E-01 … E-141)

### A. Constants and invariants

| id | verdict | reason |
|---|---|---|
| E-01 | holds | `CONFIG.h:27` = 10; `&ak` `tap-ms = <ak_tap_time>` (`adaptive_keys/macros.dtsi:30`) |
| E-02 | holds | `CONFIG.h:28` = 11 = hack `timeout-ms` (`zephyr.dts` combo node) |
| E-03 | holds* | `aksl release-after-ms = 100`; window counted from layer-ON (delivery + 10), not from the press (`sk:182`) |
| E-04 | holds | `CONFIG.h:4` = 100 → every `lk*` `tapping-term-ms` |
| E-05 | holds | rationale only; both 100 by config |
| E-06 | holds | `CONFIG.h:15` = 90 → `htls` |
| E-07 | holds* | 130 also = `htm` tapping term and `moAndBuffer` wait (`mods/behaviors.dtsi:38`, `mods/macros.dtsi:19`) |
| E-08 | holds | 90 < 100 by config; consequence claim untested but consistent with `ht:333-347` |
| E-09 | holds* | numbers match `CONFIG.h:9-11`; the 30 ms tier has zero compiled consumers (`corne.keymap:86-87`) |
| E-10 | holds* | numbers true; the causal story (10 < 11 makes it work) is wrong for Δ ≤ 10 — see contradiction 5 |
| E-11 | ambiguous | judgement; if `hold_key_event_delay ≤ ak_tap_time`, pairs at 11 ≤ Δ with k2 = 0 would indeed miss (`D_B = Δ + 11 ≤ layer`) |
| E-12 | contradicted | `&ak`, `&bk`, `REPLACE_CHAR_WITH_BIGRAM` use `wait-ms = <0>`; only `TYPING_MACRO` uses 10 (`preprocessor_macros.c:62`) |
| E-13 | untestable | history |
| E-14 | holds | `CONFIG.h:5`; `hml/hmr` unbound on Naquadah alpha |

### B. Combo-engine model

| id | verdict | reason |
|---|---|---|
| E-15 | holds* | captured iff ≥1 candidate; buffering is per candidate SET, not per combo (`combo.c:424-437`) |
| E-16 | contradicted | (b)/(c): element 0 RELEASEd, others RAISEd with their own timestamps and a fresh candidate set (`combo.c:273-289`); "at once" only when the re-raised key has no candidates or bypasses |
| E-17 | contradicted | same as E-16 |
| E-18 | contradicted | same as E-16 |
| E-19 | holds | ladder end for a 16 ms candidate = ts1 + 16 (`combo.c:155, 477`) |
| E-20 | contradicted | T (non-member of typeQ/typeZ) empties M's set at 5 → M delivered at 5, T re-raised with its own timer (16 → 21); nothing waits to 16 together (→T-23) |
| E-21 | contradicted | C (LM4) has no real combo → delivered at 0; P waits for space/typeQ (16) → 22; result TP (→T-23) |
| E-22 | contradicted | P's `&ak` fires at 22, layer on at 10 → P hits `l_akC` |
| E-23 | holds* | true for followers with no real combo (bubble 0 ms after key 1); false for followers in a real combo |
| E-24 | contradicted | "always" false: a follower with its own combo is captured for 16–18 ms and lands after the layer (`combo.c:145-161` on re-raise) |
| E-25 | contradicted | detection unaffected, timing not: a combo completed at Δ < 11 fires at 16/18 or on release (`combo.c:448-452`, A2 S7); 3-key out-of-order stalls (→T-09, T-10) |
| E-26 | untestable | design judgement; consequence: pairs with k2 > 0 that worked at Δ ≤ 9 without the hack now miss |
| E-27 | holds | needs 36 keys; buffer capped at 30 anyway (`combo.c:263`) |
| E-28 | holds* | ≥ 11 is a lower bound; actual = max(11, real combos) = 11/16/18 (`combo.c:477`, G probe) |

### C. The consistency hack

| id | verdict | reason |
|---|---|---|
| E-29 | contradicted | at Δ = 5 key 2 shares the hack → set not emptied → M delivered at 11 by the timer; the Δ-release happens only for 11 ≤ Δ < k1 (→T-02, T-05) |
| E-30 | contradicted | key 2: bypass (Δ ≤ 9), stranded (Δ = 10), or Δ + max(11,k2) (Δ ≥ 11); never "11 after its own press" unless k2 = 0 and Δ ≥ 11 |
| E-31 | contradicted | hack deadline is anchored to key 1 only (`combo.c:155`); key 2 gets its own hack deadline only after re-raise |
| E-32 | contradicted | M's kp at 11, layer at 21 (not 15) |
| E-33 | contradicted | T lands 0 ms after M for Δ ≤ 9 (bypass) |
| E-34 | contradicted | P is a hack member → does not invalidate; C released at 11 by the timer |
| E-35 | contradicted* | P re-raised at 11 bypasses (Δ = 6 ≤ 9) → resolved at 11, not 17 |
| E-36 | contradicted | `&kp C` 11–21, `l_akC` from 21 |
| E-37 | contradicted | P resolves on base at 11 → "CP" (→T-23 with real keymap) |
| E-38 | contradicted | predicted MISS ("MT") — the canonical example is inside the bypass band (→T-23) |
| E-39 | contradicted | with hack MISS, without hack HIT — reversed (→T-23) |
| E-40 | contradicted | only for Δ ≥ 11 |
| E-41 | contradicted | guarantee fails for Δ ≤ 10 |
| E-42 | contradicted | the 1 ms is `max(11,k2) − 10` for Δ ≥ 11; reliability in practice comes from bigrams rarely being ≤ 10 ms apart |
| E-43 | contradicted | verdict logic ignores the Δ ≤ 10 band; extra latency applies only to hack-only positions |
| E-44 | holds* | Δ ≤ 9: simultaneous back-to-back delivery, key 2 on base (correct); Δ = 10: stranded, not simultaneous |
| E-45 | holds* | Δ ≤ 9 yes; mechanism = quick-tap bypass, not shared timer expiry per se |
| E-46 | untestable | field statistic; consistent with rolls rarely ≤ 10 ms |
| E-47 | holds | hack `layers = <0…24>` (`zephyr.dts`); utility layers unaffected |
| E-48 | ambiguous | two mechanisms are real (combo flush ordering; FIFO queue), but "together make it reliable" overstates: see contradiction 4 (→T-21) |
| E-49 | holds* | multi-key flush does deliver keys back-to-back; `&bk` cannot fix layer timing, only output order |
| E-50 | holds | `adaptive_keys/combos.dtsi:64-65`, `aliases_key_positions.dtsi:61-65` |
| E-51 | contradicted* | value at `corne.conf:44`; without it GCC truncates the 36-element initialiser with a warning (INFERRED), not a hard rejection |
| E-52 | holds | presentation; "buffer only" correct |

### D. `&ak`, `&aksl`, `&bk` internals

| id | verdict | reason |
|---|---|---|
| E-53 | holds | `adaptive_keys/macros.dtsi:25-39` |
| E-54 | holds | `queue_add(kp↓, wait = tap_ms = 10)` (`behavior_macro.c:172`) |
| E-55 | holds | `macro_tap_time 0` → aksl↓/↑ chain with wait 0 |
| E-56 | holds* | layer at delivery + 10 (+1 tick), not press + 10 (`bq:45-48`) |
| E-57 | untestable | host behaviour (M1); native_posix cannot see it |
| E-58 | holds | the 10 ms hole is real; the hack fills it only for Δ ≥ 11 |
| E-59 | holds | `adaptive_keys/behaviors.dtsi:1-9` |
| E-60 | holds* | 100 ms from layer-ON; and pinned by any keycode down incl. modifiers (`sk:269-281`) |
| E-61 | holds | no quick-release → released on consuming key's UP after HID (`sk:303-308, 323-337`) |
| E-62 | holds | K's kp↑ releases `l_akM`, `aksl B↓` in the same tick activates `l_akB` (→T-12) |
| E-63 | holds | `bq:61-63` synchronous drain, `k_work_schedule(10)` |
| E-64 | holds | `macros.dtsi:77-87` |
| E-65 | holds | `&bk` arms nothing |
| E-66 | holds* | true effect: serialised through the one FIFO queue |
| E-67 | holds | single msgq + one delayable (`bq:22-25`); raw `&kp` bypasses it |
| E-68 | holds* | out-of-order only vs multi-step macros still in flight (replace/typing macros); vs a lone `&ak` it is a harmless rollover (→T-21) |
| E-69 | holds | convention consistent with E-67 |
| E-70 | holds* | alpha also has morph/linger wrappers (RT0, RT1, RM0, RB0) |
| E-71 | ambiguous | 10 ms tap length explains "why not 0" (host drops), not why `&bk` over `&kp`; "out of order or dropped" attributed to the wrong cause (→T-21) |
| E-72 | holds | the mechanism (`bq`), see E-67/E-68 |
| E-73 | holds* | sub-case of E-72 (hold-tap/morph bindings run outside a macro context) |
| E-74 | holds* | everything except `&ak`'s inner `&kp` and `lk_wispr` hold goes through a macro; all through the queue |
| E-75 | untestable | history |

### E. AK layers, replacement types, chaining, layout facts

| id | verdict | reason |
|---|---|---|
| E-76 | holds | layers 2–24 (`aliases_layers_NAQUADAH.dtsi:21-46`) |
| E-77 | untestable | analysis figure |
| E-78 | holds* | "for 100 ms" = from layer-ON, extendable by consumption (E-60) |
| E-79 | holds | `layers_A_NAQUADAH_alpha.dtsi:16-18` |
| E-80 | contradicted | LH0 = `&blt_akR l_nav XXX`, tap = `&ak l_akR R` (`adaptive_keys/behaviors.dtsi:20-28`) |
| E-81 | holds* | labels are approximations of `&mo l_num`, `&htls`, `&blt_akR` / `&blt l_numsym SPACE`, `&mo l_numsym`, `&togMacPc` |
| E-82 | holds | `&mo 999` → `set_layer_state` `-EINVAL` silently (`keymap.c:142-145`); sticky slot consumed until next keycode |
| E-83 | holds | config |
| E-84 | holds | config + keymap fallthrough (`keymap.c:669-671`) |
| E-85 | holds | `layers_B:128` |
| E-86 | holds | `layers_B:127` |
| E-87 | holds | traced: M@16, K@76 → B, `l_akB` on @86, G@136 → L (→T-12) |
| E-88 | holds | `preprocessor_macros.c:12-28` |
| E-89 | holds | three refs verified by E |
| E-90 | holds | config |
| E-91 | holds | illustrative |
| E-92 | holds | nested `&ak P` arms `l_akP` at F+40 |
| E-93 | untestable | rationale; the releases are no-ops when Shift is up (`hid.c:60-64`) |
| E-94 | holds | config |
| E-95 | holds | config |
| E-96 | holds* | hack absent on 25–31; `&ak` still triggers if a utility-layer key is `&trans` over an alpha `&ak` |
| E-97 | holds | defined, unbound |
| E-98 | contradicted* | queue holds bspc tap (2), B0 tap (2), two shift releases (2), `&ak` tap (2) + 4 nested = 12 items; 512 still ample |

### F. Callum mod buffer

| id | verdict | reason |
|---|---|---|
| E-99 | holds | `mods/behaviors.dtsi:45-55`; no hold-while-undecided |
| E-100 | contradicted* | hold-preferred: any other key DOWN before 90 → HOLD (`ht:333-347`); tap only if uninterrupted (→T-17) |
| E-101 | holds | `mods/macros.dtsi:1-25` |
| E-102 | holds | 130 after RELEASE (pause_for_release splits the macro, `behavior_macro.c:125-130`) |
| E-103 | contradicted | see E-102 |
| E-104 | holds | rationale consistent with `htm` tap-preferred 130 |
| E-105 | holds* | ordering 3 fails only if Mod2 arrives > 130 ms after release; within 130 it works |
| E-106 | holds | sticky `skm`/`skms` 1500 ms outlive the layer |
| E-107 | holds* | modelled numbers right; add: queue parked to release + 260 (→T-18) |
| E-108 | holds | no hold-while-undecided on `htls` |
| E-109 | contradicted | letter is SHIFTED (sticky Shift alive), Ctrl is on LM4/RM4, output is deferred to release + 260 (→T-18) |
| E-110 | contradicted | keys are `&htm MOD MOD`: `&kp MOD` down from press, `skm` only on tap (`ht:522-526, 444-464`) |
| E-111 | holds | 1500 ms (`mods/behaviors.dtsi:7,18`) |
| E-112 | holds | config |
| E-113 | untestable | history |

### G. Artifact-only engine claims

| id | verdict | reason |
|---|---|---|
| E-114 | holds | `combo.c:424-437` |
| E-115 | holds | the 0 ms hand-off is the bypass (R8) |
| E-116 | holds | `combo.c:273-289` |
| E-117 | holds | `combo.c:155, 477` (last expiry) |
| E-118 | holds* | true for Δ ≤ 10; for 11 ≤ Δ < k1 the set IS emptied at key 2's press and M is delivered at Δ |
| E-119 | contradicted | key 2 does not wait ≥ 11 after re-raise: bypass (Δ ≤ 9) or strand (Δ = 10) |
| E-120 | holds | case A matches the engine |
| E-121 | contradicted* | hack-alive branch wrong (`d2 = 11` bypass / strand); other branches right |
| E-122 | holds* | conclusion right (fast bigrams miss), mechanism wrong ("held 11 from own timestamp") |
| E-123 | holds | the docs' example is a miss |
| E-124 | contradicted* | with the hack on, key 2's own combos are ignored for Δ ≤ 9 (bypass); the claim holds with the hack OFF |
| E-125 | holds* | extra latency only on the 8 hack-only positions; combo keys unchanged |
| E-126 | holds* | "16 = wait after re-raise" only for Δ ≥ 11 |
| E-127 | holds | TRUE for v0.3.0+ (`LISTIFY(20,…)`, F §2); N/A to the board |
| E-128 | contradicted* | no exact-ms tie in the 2-key model; sub-ms phase ties exist at Δ = 11 with k2 = 0 (≈0.05 %) |
| E-129 | holds | F: combo semantics identical fork → main |
| E-130 | holds | `layers_B:117` |

### H. Linger keys

| id | verdict | reason |
|---|---|---|
| E-131 | holds* | term counts from the ORIGINAL timestamp (`ht:619, 636`); ≤ 100 tap, ≥ 101 hold; exactly 100 = board coin flip (→T-15) |
| E-132 | holds | `preprocessor_macros.c:76` |
| E-133 | holds | config |
| E-134 | holds | config |
| E-135 | contradicted | `h_digraphs/combos.dtsi` not included (`corne.keymap:86`); `lk_qu`, `magicArrow*` commented |
| E-136 | holds | config |
| E-137 | holds* | verdict depends only on duration (tap-preferred), but interrupting keys are held until the decision; an `&ak` ≤ 9 ms earlier forces TAP (→T-15, T-16) |

### I. Combo tiers and examples

| id | verdict | reason |
|---|---|---|
| E-138 | untestable | rationale; left-hand 16 ms tier is exposed to the 7.5 ms BLE grid (C §5) |
| E-139 | holds* | `bspc` is `COMBO_LAY_ONE_HAND` over 9 layers, not `COMBO_ANY_*` |
| E-140 | contradicted* | first six compiled; `pnIm`/`pnIll` not (`corne.keymap:87`) |
| E-141 | holds | `corne.conf:39,40,42,44,49` |

---

## 🧪 Test plan (prioritised)

### Common rig R1 — synthetic 3×4 mock (native_posix_64, Zephyr 3.5, fork `run-test.sh`)

- Directory `app/tests/ak-truth/<case>/` with `native_posix_64.keymap`, `native_posix_64.conf`, `events.patterns`, `keycode_events.snapshot`; run `./run-test.sh tests/ak-truth/<case>` from `/workspaces/zmk/app` in `zmk-devcontainer`; for timestamps run `build/tests/ak-truth/<case>/zephyr/zmk.exe --no-rt` (prefix `[hh:mm:ss.mmm,uuu]`).
- `native_posix_64.conf` (additive to the board conf): `CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO=12`, `CONFIG_ZMK_COMBO_MAX_COMBOS_PER_KEY=30`, `CONFIG_ZMK_COMBO_MAX_PRESSED_COMBOS=20`, `CONFIG_ZMK_BEHAVIORS_QUEUE_SIZE=512`.
- Mock: `&kscan { rows = <3>; columns = <4>; }`, position `p` → `ZMK_MOCK_PRESS(p/4, p%4, ms)`; `ms` = gap AFTER the event (+1 on native); event 0's `ms` is also the boot delay; pad the last event ≥ 300 so 100 ms timers fire.
- Nodes (verbatim shapes from Flo's config, D §12): `ak` (two-param macro, wait 0, tap 10, `param_2to1`, `tap &kp`, `tap_time 0`, `param_1to1`, `tap &aksl`), `bk` (one-param, wait 0, tap 10), `aksl` (sticky `&mo`, release-after 100), `lk` (hold-tap tap-preferred 100, `<&bk>, <&bk>`), `ak_R_macro` (macro wait 0 tap 0, `<&ak 3 H>`), `blt_akR` (hold-tap tap-preferred 200, `<&mo>, <&ak_R_macro>`), `moAndBuffer` (one-param macro: `press &mo 4`, `pause_for_release`, `wait_time 130`, `tap &none`, `release &mo 4`), `htls` (hold-preferred 90, `<&moAndBuffer>, <&skms>`), `skms` (sticky `&kp` 1500, no ignore-modifiers), `htm` (tap-preferred 130, hold-while-undecided + linger, `<&kp>, <&skm>`), `skm` (sticky `&kp` 1500, ignore-modifiers).
- Combos: `hack` = `<0 1 2 3 4 5 6 7 8 9 10 11>` 11 ms `&none` layers `<0 1 2 3>`; `R16` = `<0 2>` 16 ms `&bk C`; `S16` = `<4 5>` 16 ms `&bk V`; `Q18` = `<4 5 6>` 18 ms `&bk W`; `W30` = `<7 8>` 30 ms `&bk Z`; `V16` = `<6 11>` 16 ms `&bk Y`.
- Layer 0 (base): `0 &ak 1 A` (k1 = 16) · `1 &ak 2 B` (hack-only, k = 0) · `2 &kp C` · `3 &kp D` (hack-only, plain) · `4 &kp E` (18) · `5 &kp F` (18) · `6 &kp G` (18) · `7 &ak 3 H` (k1 = 30) · `8 &kp I` (30) · `9 &lk X Y` (hack-only; tap Y, linger X) · `10 &blt_akR 5 0` (thumb; swap to `&htls 4 LSHIFT` for Callum tests) · `11 &kp J` (16).
- Layer 1 `akA`: `1 &bk K` (k2 = 0) · `3 &bk L` (k2 = 0, plain follower) · `11 &bk M` (k2 = 16) · `4 &bk N` (k2 = 18) · `7 &bk O` (k2 = 30) · rest `&trans`.
- Layer 2 `akB`: `0 &bk P` (k2 = 16) · `3 &bk Q` (k2 = 0) · `4 &bk R` (18) · `7 &bk S` (30) · rest `&trans`.
- Layer 3 `akH`: `1 &bk T` (k2 = 0) · `0 &bk U` (16) · rest `&trans`.
- Layer 4 `mod`: `5 &htm LCTRL LCTRL` · rest `&trans`. Layer 5 `nav`: all `&trans`.
- `events.patterns` (keep it wide, filter per test in the snapshot): `s/.*hid_listener_keycode_/kp_/p`, `s/.*set_layer_state: //p`, `s/.*filter_timed_out_candidates: //p`, `s/.*combo: //p`, `s/.*decide_hold_tap: //p`, `s/.*behavior_queue_process_next: Processing next queued behavior in/queue wait/p`.
- Hack-OFF variants = same keymap with the `hack` node deleted.

### Rig R2 — Flo's real keymap (G §4 recipe)

- `#include <layouts/foostan/corne.dtsi>`, define `default_transform` (42) and `five_column_transform` (36) verbatim from `boards/shields/corne/corne.dtsi`, then `#include "/workspaces/zmk-config/config/corne.keymap"`; conf = the five `corne.conf` lines (`MAX_COMBOS_PER_KEY=30`, `MAX_PRESSED_COMBOS=20`, `MAX_KEYS_PER_COMBO=36`, `BEHAVIORS_QUEUE_SIZE=512`, `HID_SEPARATE_MOD_RELEASE_REPORT=y`).
- Position `p` → `ZMK_MOCK_PRESS(p/10, p%10+1, ms)` for p < 30; thumbs 30–35 → `(3, p−27)`. Keys used: LT2 M = (0,3), LM1 T = (1,4), LM4 C = (1,1), LT1 P = (0,4), LB2 L = (2,3), LT4 X/G-follower = (0,1), LH1 = (3,4), RM1 = (1,7).
- Reading native times: every timer +1; a key with mock timestamp `t` and longest candidate `k` is delivered at `t + k + 1`; layer on at delivery + 11; hack flush handler runs at `t + 12` with `timestamp=t+11` in its log line.

### Tests

Times below are native_posix wall times relative to key 1's position timestamp `t` unless a raw `[prefix]` is given; board = subtract the +1s and add δ.

- **T-01 Harness baseline (+1 per timer, mock gap = ms+1)** — R1, no combos. `PRESS(0,3,100) RELEASE(0,3,10) PRESS(0,2,50) RELEASE(0,2,10)`. Expect `kp_pressed 0x07` D at `[.101]`, released `.112`, `kp_pressed 0x06` C at `.163`, released `.174`, `Exiting` `.185`. Purpose: pin the offsets every later expectation uses (G1, C1).
- **T-02 Sub-11-ms bigram, `&ak` key 1 → quick-tap bypass (the disputed case)** — R1, hack on. `PRESS(0,0,5) PRESS(0,1,60) RELEASE(0,0,40) RELEASE(0,1,300)` (A at t, B-key at t+6). Expect at `t+12`: `remaining_candidates=0 timestamp=t+11`, `releasing position event 0`, `kp_pressed 0x04` (A), `reraising position event 1`, **no** `capturing position event 1`, `kp_pressed 0x05` (B) at `t+22` (queued behind A's tap), `layer 1 state 1` at `t+22`, no `kp_pressed 0x0E` (K). Purpose: settle E-29/E-30/E-38 (contradictions 1–3); MISS predicted.
- **T-03 Stranded second key (CANCELING trap), plain `&kp` key 1** — R1, hack on. `PRESS(0,3,5) PRESS(0,1,60) RELEASE(0,3,40) RELEASE(0,1,300)` (D at t, B at t+6). Expect `kp_pressed 0x07` at `t+12`, `reraising position event 1`, `capturing position event 1`, **no** `filter_timed_out` line between `t+12` and D's release, `kp_pressed 0x05` (B) at `t+67` (= D release), then `kp_released 0x07` in the same ms. Purpose: confirm A2 H1 and that R8 (not R9) governs Flo's `&ak` keys.
- **T-04 Δ sweep 9 / 10 / 11 / 12 around the boundary** — R1, hack on, key 1 = pos 1 (`&ak B`, hack-only), key 2 = pos 3 (`&bk Q` on akB, k2 = 0). Four runs `PRESS(0,1,Δ−1) PRESS(0,3,60) RELEASE(0,1,40) RELEASE(0,3,300)`. Expect native: Δ = 9, 10 → `kp_pressed 0x07` (D, base) with no `capturing position event 3`; Δ = 11 → B delivered at `t+11` (key-first: `remaining_candidates=0 timestamp=t+11` logged from the key path at `[t+11]`), `layer 2 state 1` at `t+22`, `kp_pressed 0x14` (Q) at `t+23`; Δ = 12 → B at `t+12` (timer), layer `t+23`, Q at `t+24`. Board prediction differs at Δ = 10 (STALL: Q only at B's release) — hardware check listed in T-24. Purpose: MODEL (d) boundary.
- **T-05 Key 1 in a 16 ms combo, 11 ≤ Δ < 16 → flush at key 2's press** — R1, hack on. `PRESS(0,0,12) PRESS(0,3,60) RELEASE(0,0,40) RELEASE(0,3,300)` (A at t, D-key at t+13). Expect `remaining_candidates=1 timestamp=t+11` at `[t+12]` (hack dropped, R16 kept), then at `[t+13]`: `capturing position event 3`, `releasing position event 0`, `kp_pressed 0x04` (A), `reraising position event 3`, `capturing position event 3`; `layer 1 state 1` at `t+24`; `kp_pressed 0x0F` (L) at `t+25`. Purpose: E-29 holds in this band; margin = 1 ms.
- **T-06 Key 2 in a 30 ms combo** — R1. (a) hack on, `PRESS(0,0,20) PRESS(1,3,80) RELEASE(0,0,40) RELEASE(1,3,300)` (A, H-key at t+21): A at `t+17` (ladder 11→16), layer `t+28`, H-key delivered `t+52` (30 + 1 from its own timestamp) → `kp_pressed 0x12` (O). (b) hack on, Δ = 6 → bypass → `kp_pressed 0x0B` (H) at `t+22`, no O. (c) hack off, Δ = 6 → A at `t+7`, layer `t+18`, O at `t+38`. Purpose: E-124 (holds only without the hack).
- **T-07 Key 1 with no real combo (k1 = 0), hack off** — R1 hack off, key 1 = pos 1, key 2 = pos 3. Runs Δ = 5, 11, 12: expect `kp_pressed 0x05` (B) at `t` (bubble, no capture line), `layer 2 state 1` at `t+11`; Δ = 5 → D at `t+6` (base, MISS); Δ = 11 → record order of the two same-tick items (D press vs `layer 2 state 1` at `[t+11]`) — expected mock-timer-first → D (MISS, TIE band); Δ = 12 → Q. Purpose: hack-off table column k1 = 0, k2 = 0; same-tick ordering on native.
- **T-08 Release while buffered** — R1, hack on. (a) `PRESS(0,0,5) PRESS(0,1,3) RELEASE(0,0,50) RELEASE(0,1,300)` (A t, B t+6, A↑ t+10): expect at `[t+10]` `releasing position event 0`, `kp_pressed 0x04`, `reraising position event 1`, then `releasing position event 1` (dupe cleanup), `kp_pressed 0x05` (B, base), `kp_released 0x04`; no `filter_timed_out` at `t+12` with remaining 0 for these keys. (b) B released first (`RELEASE(0,1,…)` before A↑): B↓ delivered at B↑, base. Purpose: R6, "release-while-buffered → immediate, on base".
- **T-09 Combo completion under the hack** — R1, hack on. (a) `PRESS(0,2,5) PRESS(0,0,100) RELEASE…` (C then A at +6 completes R16): expect `remaining_candidates=2` at `[t+6]` then `remaining_candidates=1 timestamp=t+11`, `remaining_candidates=0 timestamp=t+16`, `kp_pressed 0x06` (combo `&bk C`… use R16's binding `&bk C` → 0x06) at `t+17`; no A/C base keycodes; release of the combo on the FIRST key up, second key up swallowed. (b) Δ = 13 → fires at `t+13` (single surviving candidate). (c) hack off, Δ = 6 → fires at `t+6`. Purpose: E-25/Q-1.
- **T-10 Late-deadline stall (3-key combo out of order)** — R1, hack on. `PRESS(1,0,11) PRESS(1,2,3) PRESS(1,1,100) RELEASE(1,0,10) RELEASE(1,1,10) RELEASE(1,2,300)` (E t, G t+12, F t+16). Expect `remaining_candidates=… ` at `[t+12]` leaving Q18 only, **no** `filter_timed_out` line at `t+19`, `kp_pressed 0x1A` (W = Q18) only at `[t+117]` (E's release), press stamped `t`. Control: order E, F, G within 11 ms → W at `t+19`. Purpose: R10.
- **T-11 Solo-key latency = longest candidate** — R1, hack on, one list with 300 ms separators: pos 1 → `kp_pressed 0x05` at `t+12`; pos 0 → at `t+17` (`remaining_candidates=1 timestamp=t+11`, `=0 timestamp=t+16`); pos 4 → `t+19`; pos 7 → `t+31`. Hack off: pos 1 → `t`, others unchanged. Purpose: E-28/E-125/Q-2.
- **T-12 `&ak` timeline, window end, chaining** — R2 (real keymap). (a) LM1 alone `PRESS(1,4,100) RELEASE(1,4,300)`: `kp_pressed 0x17` at `t+17`, `kp_released` + `layer 19 state 1` at `t+28`, `layer 19 state 0` at `t+129`. (b) window edge: LM1 at t, LT2 (M is `&trans` on l_akT? use LB3 G → `&bk T` on l_akT) at Δ = 110 and 112 → adapted at 110 (`kp_pressed 0x17` second time at Δ+17), base at 112. (c) chain M→K→G (`PRESS(0,3,60) PRESS(0,5,60) PRESS(2,2,300)` releases interleaved) → HID M, B, L; `layer 13 state 0` and `layer 3 state 1` in the same ms (K's kp↑). Purpose: (c) offsets, E-61/E-62/E-87, 105–110 ms window.
- **T-13 Sticky layer visible in the same dispatch?** — R1. (a) `&ak` flush: T-02 already shows the re-raised key resolves on base. (b) nested-sync thumb: `PRESS(2,2,30) PRESS(0,1,30) RELEASE(2,2,10) RELEASE(0,1,300)` (thumb t, B-key t+31 captured by hold-tap, thumb↑ t+62): expect `decided tap (tap-preferred decision moment key-up)` at `[t+62]`, `kp_pressed 0x0B` (H) and `kp_released 0x0B` in the same ms with **no** `queue wait 10ms` between, `layer 3 state 1` same ms, then `Releasing key position event for position 1`, `kp_pressed 0x17` (T = akH follower) — adapted. Control: bind pos 10 to a hold-tap whose tap is `&ak 3 H` directly → `kp_released 0x0B` at `t+73`, layer at `t+73`, and the captured key resolves on base (B). Purpose: settle B vs D on T7b; R-thumb 0 ms tap.
- **T-14 Nested macro 0 ms tap (thumb alone)** — R1. `PRESS(2,2,50) RELEASE(2,2,300)`: `kp_pressed 0x0B` and `kp_released 0x0B` both at `[t+51]`, `layer 3 state 1` at `t+51`, `layer 3 state 0` at `t+152`. Purpose: D Q3 / B §4.4 rule 3b (host-drop risk for R).
- **T-15 Linger key boundary + interrupt** — R1, pos 9. Runs: release at +99, +100, +101 (`PRESS(2,1,n) RELEASE(2,1,300)`): expect `decided tap … key-up` + `kp_pressed 0x1C` (Y) for 99 and 100, `decided hold … timer` + `kp_pressed 0x1B` (X) at `t+101` for 101 (timer fires before the up). Interrupt: `PRESS(2,1,40) PRESS(0,3,40) RELEASE(2,1,10) RELEASE(0,3,300)` → at `t+81`: Y↓, `Releasing key position event for position 3`, D↓ deferred to `t+91` (after Y↑ at the queue tick). Held 150 with D at +40 → X↓ at `t+101`, D↓ right after. Also confirm the hold-tap is created at `t+12` (`new undecided hold_tap` after the hack rung) yet decides on `t+100`, not `t+112`. Purpose: E-131/E-137/Q-7.
- **T-16 Hold-tap forced TAP after an `&ak` (quick-tap skew)** — R1. `PRESS(0,1,5) PRESS(2,1,300) RELEASE(0,1,10) RELEASE(2,1,300)` (B at t, linger at t+6, held 300): expect at `[t+12]` `kp_pressed 0x05`, `reraising position event 9`, `new undecided hold_tap`, `decided tap (tap-preferred decision moment quick-tap)`, `kp_pressed 0x1C` (Y) — never X. Control Δ = 12: `decided hold (… timer)` → X at `t+112`. Purpose: B T-06, new fact for the page.
- **T-17 `htls` hold-preferred** — R1 with pos 10 = `&htls 4 LSHIFT`. (a) `PRESS(2,2,30) PRESS(1,1,20) RELEASE(1,1,10) RELEASE(2,2,300)`: `decided hold (hold-preferred decision moment other-key-down)` at `[t+31]`, `layer 4 state 1` same ms, `kp_pressed LCTRL (0xE0)` same ms (htm hold-while-undecided). (b) `PRESS(2,2,50) RELEASE(2,2,300)`: `decided tap … key-up` at `t+51`, `kp_pressed 0xE1` (LSHIFT sticky). (c) hold 120 alone: `decided hold … timer` at `t+90`, i.e. `[t+91]`, not `t+102`. Purpose: E-99/E-100/E-108.
- **T-18 Callum buffer 130 vs 260** — R1 with `&htls`. `PRESS(2,2,120) RELEASE(2,2,140) PRESS(0,1,10) RELEASE(0,1,300)` (thumb t–t+121, B-key at t+262): expect `layer 4 state 0` at `[t+252]` (121+131), `queue wait 130ms` twice, B-key delivered `t+274` but `kp_pressed 0x05` only at `[t+382]` (= release + 261). Variant: htm (pos 5) tapped at 240 → resolves on layer 4 (`kp_pressed 0xE0`); at 262 → alpha F, and if a `skms` shift was armed at 100 the `kp_pressed 0x09` carries `explicit_mods 0x02`. Purpose: contradiction 10.
- **T-19 `htm` mechanics** — R1, layer 4 forced via `&mo 4` on pos 3 for the test. Tap: `PRESS(1,1,50) RELEASE(1,1,10) PRESS(0,2,200) RELEASE(0,2,300)`: `kp_pressed 0xE0` at press, no `kp_released 0xE0` at tap end (sticky takes over, count 2→1), C pressed with `explicit_mods 0x01`, `kp_released 0xE0` after C's up. Hold with captured key: `PRESS(1,1,50) PRESS(0,2,100) RELEASE(0,2,10) RELEASE(1,1,300)` → C delivered at `t+131` (timer HOLD) with ctrl down. Purpose: E-110.
- **T-20 Modifier pins the AK layer** — R1 with pos 11 = `&kp LSHIFT` for this test. `PRESS(0,0,50) PRESS(2,3,300) PRESS(0,1,10) RELEASE(0,1,50) RELEASE(2,3,10) RELEASE(0,0,300)`: expect `layer 1 state 1` at `t+28`, **no** `layer 1 state 0` at `t+129`, `kp_pressed 0x0E` (K, adapted, shifted) at ~`t+362`, `layer 1 state 0` only after `kp_released 0xE1`. Control with `ignore-modifiers` on `aksl` → `state 0` at `t+129`, B typed. Purpose: E-60 nuance.
- **T-21 `&bk` vs raw `&kp` after a multi-step macro** — R1 plus `replace_char_with_bigram_LB` verbatim on layer 1 pos 4 and a follower pos 3 = `&bk L` vs `&kp L` (two builds). `PRESS(0,0,30) PRESS(1,0,15) PRESS(0,3,300)…` (A, then E-key at +31 triggers the replace, then D-key at +47 while the macro is in flight): `&bk` build → HID order `A, BSPC, L, B, L`; raw build → `A, BSPC, L, L, B` (raw L jumps ahead of the queued B). Purpose: E-71/E-72/E-73/Q-6.
- **T-22 Combo window edge + timer log artefact** — R1, R16 only. `PRESS(0,0,14) PRESS(0,2,10)…` (gap 15) → `kp_pressed 0x06` (C via R16); `PRESS(0,0,15)…` (gap 16) → A then C-key base, `remaining_candidates=0 timestamp=t+16` at `[t+17]`. Purpose: C2/C3/G2/G3 for the tier bars.
- **T-23 Flo's hero examples on the real keymap** — R2. (a) M→T Δ = 5: `PRESS(0,3,4) PRESS(1,4,60) RELEASE(0,3,40) RELEASE(1,4,300)` → `kp_pressed 0x10` (M) at `t+12`, `kp_pressed 0x17` (T) at `t+22`, no N (0x11). (b) C→P Δ = 6 with hack → C at `t+12`, P (0x13) at `t+22`, no BSPC/T. (c) C→P Δ = 6 hack off (comment the `COMBO_AK_CONSISTENCY_HACK` line in a copy of `combos.dtsi` via a test overlay `#undef`/delete-node `/delete-node/ &combo_ak_consistency_hack;`) → C at `t+1`, P delivered `t+23` → BSPC, T, P sequence. (d) L→G Δ = 13 with hack → `kp_pressed 0x0F` at `t+13`, `0x0F` again (G-follower `&bk L`) at `t+25`; Δ = 5 → L then G (0x0A). (e) hack off L→G Δ = 20 → L at `t+17`, G base at `t+20` (MISS); Δ = 28 → adapted. Purpose: contradictions 1, 4; the page's actual example numbers.
- **T-24 Hardware-only checks (not native)** — enable `CONFIG_ZMK_USB_LOGGING=y` on the right half temporarily: (a) STALL at Δ = 10: hold an `&ak` letter, press a hack-only follower 10 ms later (jig), keep both down 1 s → follower appears only at a release; (b) left/right differential latency histogram (`Trigger key position state change` vs `Row:` log times) and the 7.5 ms comb; (c) confirm `k_uptime_get()` in the hack handler = deadline (not +1) via the `timestamp=` line vs prefix. Purpose: MODEL (a)/(d) board-vs-native bands.

### Coverage map (contradiction → test)

| Item | Tests |
|---|---|
| Sub-11-ms bigram | T-02, T-03, T-23 |
| Exact tie at 10/11 | T-04, T-07, T-24a |
| Key 2 in a 30 ms combo | T-06 |
| Key 1 in no real combo | T-04, T-07, T-11 |
| Release while buffered | T-08 |
| Combo completion / stall | T-09, T-10, T-22 |
| Linger tap vs hold boundary | T-15, T-16 |
| Sticky layer visible in same dispatch | T-02 (no), T-13 (yes via nested sync) |
| Lone-key latency | T-11, T-12 |
| Callum 130/260, htm | T-17, T-18, T-19 |
| `&bk` rationale | T-21 |
| Transport (hardware) | T-24 |

Total: **24 tests** (23 native_posix, 1 hardware bundle).
