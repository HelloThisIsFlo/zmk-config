# ⏱️ AK Timing — what the firmware really does

> [!important] What this folder is
>
> - The **proven timing model** of the adaptive-key system: how the combo engine, the `&ak` macro, sticky layers, hold-taps and the Callum buffer behave, millisecond by millisecond
> - Established 2026-09-28 → 2026-10-01 from the fork's source (ZMK `6e03a0bb`, Zephyr 3.5) and **181 native_posix test cases**, 58 of them on the real NAQUADAH keymap
> - It **replaces** the explanations in `ak-combo-hack.md`, the `combos.dtsi` comment block and the timing sections of `MECHANICS.md`, which were wrong in their core claim
> - Status: **banked, under review**. Nothing here is committed yet; the website rebuild comes after review

## 🏷️ Legend (same in every file here)

| Glyph | Meaning |
|---|---|
| 🧪 | Proven by a test (`T-xx`, `S-xx`, `ARB-xx`, `RV-xx`), log line cited |
| 📜 | Proven by reading the source that built the board (`file:line`) |
| 🔮 | Predicted on hardware: mechanism proven, the band itself not measured |
| 🧮 | Inferred, not executed |
| ⛔ | Refuted, kept struck through so nobody re-states it |
| ❓ | Open |
| ✅ ❌ ⏸ ⚖️ 🟪 | Outcome of a key sequence: adapted · base letter · stall · tie/unresolved on hardware · a real combo fires instead |

- All numbers are **board engine time**: milliseconds on the right half's clock, from the trigger key's timestamp `t`
- Native test logs run every relative timer **+1 ms** late; an `&ak` key delivered by a combo rung crosses two timers before its layer is on
  - `FACTS.md` prints both columns; `TESTS.md` explains the arithmetic

## 🎯 The ten things to believe now

1. 🧱 **A lone key is held by its longest live combo, not a flat 11 ms**
   - 11 ms on the 8 hack-only keys (X C F / thumbs LH2 LH1 LH0 RH0 / RT0), 16 ms on most, 18 ms on A E I H
   - A key-up before the hold ends releases it at once
   - 🧪 `T-11`, `T-12-a`, `T-01-r2-map`
2. ⏱️ **`&ak` types the letter at delivery D, arms the AK layer at D+10, drops it at D+110**
   - A lone T: press `t`, letter at `t+16`, layer on at `t+26`, off at `t+126`
   - 🧪 `T-12-a`
3. 🧨 **Rolls ≤ 9 ms miss, on 45 of 54 pairs, with the hack on**
   - Both keys leave the engine together at the trigger's 11 ms rung; the follower lands on the **base** layer, the AK layer arrives 10 ms later
   - M→T at 5 ms types `mt`; C→P at 6 ms types `cp`
   - 🧪 `T-02`, `T-04`, `T-23-a/b`
4. ✅ **Those 45 pairs adapt from 11 ms up to ~105–115 ms** (the edge depends on the pair's combo holds)
   - Margin at the band start: 1 ms for hack-only followers, 6 ms for 16 ms followers (a BLE-stamped hack-only follower can shrink to ≈ 0 ms, still ✅ 🧮)
   - 🧪 `T-04-d11/d12`, `T-05`, `S-*-d11`, `T-12-b`
5. 🧷 **6 pairs stay fragile past 10 ms, hack or not: trigger and follower share a real combo**
   - L→G key (`magicCloseQuitCb` 16 ms): `lg` to 14 ms, ⏸ at 15, adapted `ll` from 16
   - H→E key (`capsWord` 18 ms): base to 16 ms, ⏸ at 17 (E is typed either way; only the third key shows it)
   - M↔W and D↔V are themselves 2-key combos: any roll ≤ 15 ms types Z / Tab
   - 🧪 `T-23-d/e`, `S-L_LB3-*`, `S-H_RM2-*`, `S-M_LT3-*`
6. 🔁 **The hack is a trade**
   - Costs the 34 ordinary pairs every roll ≤ 9 ms, and a ⏸ stall at 10 (without it they never miss below the window edge)
   - Rescues the 11 pairs whose follower is a hack-only key, for gaps of 11–25 ms (without it they miss to 25 ms)
   - Lone-key latency: +11 ms only on the 8 hack-only keys (the rest are held 16/18 ms anyway); but in any roll ≤ 10 ms key 1 waits to `t+11` on every position, and a fast 2-key combo waits for its own deadline (#7)
   - Upstream ZMK v0.3+ silently drops the 36-key combo → behaves like "hack off"
   - 🧪 `T-23-c/e`, `S-*-nohack` · 📜 `F-upstream-diff`
7. 🕰️ **Real combos accept gaps ≤ T−1 and, under the hack, a fast 2-key combo fires at its own deadline (or your next key event), not at completion**
   - M+W 5 ms apart → Z at `t+16`; `bspc`/`del` always fire at `t+18` (delWord/capsWord stay alive)
   - RM1 then RM3 without RM2 → nothing until your next key event, then `a` `i`
   - 🧪 `T-09`, `T-22`, `ARB-F2-*`, `RVB-bspc-*`
8. 🧵 **One thread, one behaviour queue, FIFO per item**
   - Raw `&kp` overtakes queued output; a nested macro joins only when its parent item runs
   - Callum thumb release R: `l_mod` off at R+130, queued output parked until **R+260**
   - After a replace macro: base layer live for (F+10, F+40), the dead window
   - 🧪 `T-18`, `T-21`, `ARB-F3-*`
9. 🎯 **Timestamps never move; the layer is chosen at delivery**
   - Shift on LM1/RM1 sits in the Enter combo on `l_mod`: +16 ms; pressed in the buffer's last ~16 ms and still held at R+130 it resolves on base as `&ak T` / `&ak A`, parked to R+260 (shifted "A" when the earlier sticky Shift is still pending, never a lowercase "a")
   - The AK layer is pinned only by a keycode delivered after arming, until that key's up or the next `&ak`-typed key
   - 🧪 `T-17`, `T-18-g`, `T-20`, `RVA-callum-*`
10. 🖐️ **Native vs board**
    - Native resolves same-ms ties timer-first; on the board every ⚖️ cell is **undetermined** (right-hand pairs: 10–200 µs firmware latencies with opposite signs; left-left pairs: a BLE-phase race up to ~1 ms)
    - No AK pair crosses hands; 42 of 54 are left-left and arrive quantised to ~7.5 ms by BLE 🧮
    - 🧪 `T-07-d11`, `T-12-b-d112` · 📜 `C-timestamps-transport`

## 🧩 The hack, in six lines

- The hack is a 36-key combo with an 11 ms timeout and a `&none` binding; it never fires. Its only effect: **every key on layers 0–24 has at least one combo candidate** → every press is captured and held 11 ms, unless a key-up or a non-sharing press flushes it earlier 📜
- `&ak` types its letter at delivery and arms the AK layer **10 ms later** (the queue tick). A follower delivered in that gap lands on base. That gap is the whole problem 🧪
- Follower ≥ 11 ms after the trigger (and sharing no real combo with it): it reaches the keymap after its own hold (≥ 11 ms from its own press) → after the layer is on → ✅ up to the window edge. This is the case the hack rescues, for followers that had no combo of their own 🧪
- Follower ≤ 9 ms: it shares the hack with the trigger, so the trigger's set is not emptied; both wait for the rung at `t+11`. The trigger's letter is stamped **now**; the follower keeps its **old** timestamp → ZMK's quick-tap check (`require-prior-idle-ms = −1`) treats it as a quick tap → zero candidates → straight to the keymap, on base → ❌ 🧪
- Follower sharing a real combo with the trigger: same story at that combo's deadline (16/18) instead of 11 → fragile to 14–16 ms whatever the hack does; when the pair *is* a 2-key combo (M↔W, D↔V) that combo fires instead 🧪
- The old docs' "key 2 is delayed 11 ms after its own press, so the layer is always ready" is ⛔: true only for gaps ≥ 11 ms, where it was never the problem

## ⚖️ The "exactly 10 ms" cell

- Why 10 is special: the bypass condition is `last_tapped − 1 > follower_ts` → true for gaps ≤ 9, **false at 10** 📜 `combo.c:141-143`
- At 10 the follower is **re-captured** by the combo engine, but this happens inside the timer handler that just ran `cleanup()`, which cancelled the very work item that is executing → Zephyr marks it `CANCELING` → the follower's new deadline is **refused** → no timer 📜 `work.c:492-511, 966-968`
- So the follower sits in the buffer until the **next release**, or the **next press that shares none of its live candidates**, flushes it: ⏸ STALL. A press inside its own fresh 11 ms hack window (to `t+21`) joins the stall instead (`RVB-strand-join`). If the AK layer is still on at the flush (`t+21` … `≈t+121`) it adapts late; otherwise base 🧪 mechanism (`T-03` with a raw `&kp` trigger, `T-02-c` with the check disabled)
- Native cannot show it: its rung runs 1 ms late, so `last_tapped` is 1 ms later and 10 still bypasses → ❌ in every native log. On the board a right-hand trigger's rung runs on time → 🔮 STALL; a left-hand trigger's rung inherits its BLE stamp's sub-ms phase and can land a ms late → ❌ for an unmeasured fraction. Unmeasured on hardware (`T-24a`)
- Same shape at S−1 for the shared-combo pairs: L→G at 15, H→E at 17

## 🗂️ Map

| Read | When |
|---|---|
| [`CONCEPTS.md`](CONCEPTS.md) | You want the big picture first: the seven concepts the page covers, one block each, one minute |
| [`MODEL.md`](MODEL.md) | You want the mechanism: pipeline, combo-engine rules, `&ak` path, the hack theorem and Δ tables, every statement tagged |
| [`FACTS.md`](FACTS.md) | You build the website or rewrite a doc: facts allowed, worked examples on real keys, must-NOT-say lists, what changed |
| [`PAIRS.md`](PAIRS.md) | Which of the 54 pairs are fragile and why; the sweep evidence |
| [`TESTS.md`](TESTS.md) | How the proof was made: rigs, harness arithmetic, log formats, index of every test case |
| [`results/`](results/) | One write-up per test family with verbatim log lines, the reconciliations, the reviews |
| [`research/`](research/) | The raw reader reports and the pre-test model, superseded |
| [`../../tests/timing/`](../../tests/timing/) | The test cases themselves, the runner and the raw logs |

## 🧪 How it was proven

- Eight parallel source readings of the fork (combo engine ×2, behaviour pipeline, transport, config expansion, claims ledger, upstream diff, harness), synthesised into a predictive model
- 181 test cases (22 planned test families, a 21-run pair sweep, arbitration and review probes), all native_posix, two rigs: a synthetic 3×4 mock and the real keymap included verbatim
- Every case re-run after the move into `tests/timing/`: 180 PASS, 1 never had a snapshot, 180/180 raw logs byte-identical to the originals
- Every deviation from the prediction reconciled against source; the model rewritten with a status on every line; two independent adversarial reviews, 39 fixes applied
- Re-run anything: `tests/timing/run.sh <case>` (details in [`TESTS.md`](TESTS.md))

## ❓ Open

- 24 open items listed at the end of [`FACTS.md`](FACTS.md); the ones that matter are hardware-only (the 10 ms stall band, the direction of ⚖️ cells, BLE phase) and need USB logging on the board
- Two decisions taken for the site: timelines in engine time; compiled things only

## ⏭️ Not done yet

- Website rebuild from `FACTS.md` (after review)
- Rewrite of `ak-combo-hack.md`, `MECHANICS.md` timing sections, the `combos.dtsi` comment (after review; superseded markers are in place)
- Hardware measurements (`T-24`)

---

_Firmware: fork `4211ad74` = upstream `6e03a0bb` (2024-09-12) + tooling, Zephyr 3.5, right half central. Investigation run with Claude (Fable 5.1 for source tracing, synthesis and verification; Opus 5.5 for test execution and restyling)._
