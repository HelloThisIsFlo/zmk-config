# 🧩 AK consistency hack

A 36-key combo that never fires, and what it really does to adaptive keys.

> [!important] The headline
>
> - **An 11 ms hold that makes adaptation reliable from 11 ms up, at the cost of rolls under 11 ms**
> - 🟩🟨 **45 ordinary pairs** → ❌ ≤ 9 ms · ⏸ 10 ms · ✅ 11 ms → window edge 🔮
>   - Native: ❌ ≤ 10 · ✅ 11 🧪
> - ⚖️ **Net trade on the 54 pairs** → 🔮 board bands · 🧪 `T-23`, PAIRS classes
>   - Costs 34 pairs every roll ≤ 9 ms
>   - Rescues 11 pairs for rolls of 11–25 ms
>   - 6 shared-combo pairs: same outcome hack or not

- **Legend**
  - Evidence: 🧪 proven by test · 📜 proven by source · 🔮 predicted on hardware, not measured · 🧮 inferred · ⛔ refuted · ❓ open
  - Outcomes: ✅ adapted · ❌ base letter · ⏸ stall · ⚖️ tie, undetermined on hardware · 🟪 a real combo fires instead
- **One clock:** board engine time, ms from the trigger key's timestamp `t`
  - Native test logs run every relative timer +1 ms late

## 🔧 What the hack is

```c
#define COMBO_AK_CONSISTENCY_HACK \
  COMBO_LAY_BASE(l_alpha_aks, ak_consistency_hack, &none, ALL_KEYS, hold_key_event_delay)
```

- 🔑 **Keys** → `ALL_KEYS`, all 36 positions
- ⏱️ **Timeout** → `hold_key_event_delay` = 11 ms
- 🗂️ **Layers** → `l_alpha_aks` = layers 0–24
- 🚫 **Binding** → `&none`: it never fires 📜

| What | Where |
|---|---|
| The macro | `config/layout/features/hands_down/adaptive_keys/combos.dtsi:49-50` |
| Its invocation | same file, line 53 |
| `ak_tap_time` 10 / `hold_key_event_delay` 11 | `config/layout/CONFIG.h:27-28` |
| `CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO=36` | `config/keyboards/chocofi/corne.conf:45` |

> [!note] Its only effect
>
> - Every key on layers 0–24 has at least one combo candidate
> - → every press is captured and held by the combo engine 📜

## ⏱️ What a press really does

### 🧱 Held by its longest live combo

| Hold | Keys |
|---|---|
| 11 ms | the 8 hack-only keys: X (LT4), C (LM4), F (LB4), RT0, LH2, LH1, LH0, RH0 |
| 16 ms | most keys |
| 18 ms | A, E, I, H |

- ✋ **Released early** by a key-up, or a press that shares none of its combos 🧪 `T-08-b`, `T-23-d3`
- 🐢 **Latency**
  - Typed alone, the hack adds 11 ms only on the 8 hack-only keys; the rest are held 16/18 ms anyway 🧪 `T-11-c/d`
  - In a roll under 11 ms, the first key waits to `t+11` on every position
    - Without the hack it leaves at the second key's press 🧪 `T-02-a` vs `T-02-b-nohack`

### ⌨️ The `&ak` keystroke

- 🔤 **Letter** at delivery D
- 📌 **AK layer ON** at D+10 (the queue tick)
- 🚪 **AK layer OFF** at D+110
- **Lone T:** press `t` → letter `t+16` · layer ON `t+26` · OFF `t+126` 🧪 `T-12-a`

> [!warning] The whole problem
>
> - A follower delivered between D and D+10 lands on the **base** layer
> - Every band below is about whether the follower reaches the keymap after D+10

## 🧨 Why rolls under 11 ms miss

- 🧨 **Gap ≤ 9 ms** → ❌
  - The follower shares the hack with the trigger → the trigger's candidate set is not emptied
  - Both wait for the trigger's hack rung at `t+11`
  - The trigger's letter is stamped **now** (`t+11`); the follower keeps its **old** timestamp
  - ZMK's quick-tap check (`require-prior-idle-ms = -1`) treats it as a quick tap → zero candidates → straight to the keymap, on **base**
  - 🧪 `T-02-a`, `T-23-a/b` · control `T-02-c`: disabling the check flips the follower to captured
- ✅ **Gap ≥ 11 ms** (pairs sharing no real combo)
  - The trigger is already delivered, or the follower's press flushes it
  - The follower is held ≥ 11 ms from its own press → reaches the keymap after the layer is ON
  - Margin = max(11, follower's combo) − 10 ≥ 1 ms 🧪 `T-04-d11`, `T-05`
  - A BLE-stamped hack-only follower can shrink that 1 ms to ≈ 0, still ✅ 🧮 (❓ open #3 in FACTS)
- ⏸ **Gap = exactly 10 ms** → predicted stall on the board (section ⏸ below)

### 🎬 M→T at 5 ms, hack ON → "mt" ❌

- Adapted would be "mn" (`l_akM` LM1 = `&bk N`) 🧪 `T-23-a`

| Board | Event |
|---|---|
| `t` | M↓ captured (typeQ, typeZ, hack) |
| `t+5` | T↓ captured; it shares only the hack with M |
| `t+11` | hack expires → M delivered → **m↓**; T released in the same burst with its old timestamp → quick-tap bypass → **base** `&ak T` (queued) |
| `t+21` | m↑ · `l_akM` ON · **t↓** (T's own keycode consumes `l_akM`) |
| `t+31` | t↑ · `l_akM` OFF · `l_akT` ON |
| `t+131` | `l_akT` OFF |

### 🔁 C→P at 6 ms: the hack reverses the outcome

| | Output | Why |
|---|---|---|
| 🧩 Hack ON | ❌ "cp" | C is held 11 ms; P shares the hack, leaves with C at `t+11`, bypassed onto base 🧪 `T-23-b` |
| 🚫 Hack OFF | ✅ "tp" | C has no combo → **c↓** at once; P waits 16 ms for its own combos → delivered at `t+22` on `l_akC` → `CP_to_TP` 🧪 `T-23-c` |

## 📊 The bands, per pair class

- **54 compiled AK pairs** across 23 AK layers; all same-hand, 42 of them left-left 📜
- Board cells; Δ = follower press − trigger press

| Class | Pairs | Hack ON | Hack OFF (= upstream v0.3+) |
|---|---|---|---|
| 🟩 **N** · follower has its own combo, shares none | 34 | ❌ ≤ 9 · ⏸ 10 · ✅ 11 → edge | ✅ every gap below the edge |
| 🟨 **H0** · follower is hack-only (X LT4, C LM4, F LB4, R thumb LH0) | 11 | ❌ ≤ 9 · ⏸ 10 · ✅ 11 → edge | ❌ ≤ 25 · ⚖️ 26 · ✅ ≥ 27 |
| 🟥 **L→G key** · share `magicCloseQuitCb` (S 16) | 1 | ❌ ≤ 14 ("lg") · ⏸ 15 · ✅ 16 ("ll") | identical |
| 🟥 **H→E key** · share `capsWord` (S 18) | 1 | ❌ ≤ 16 · ⏸ 17 · ✅ 18 | identical |
| 🟪 **M↔W** (`typeZ`) · **D↔V** (`tab`) | 4 | 🟪 Δ ≤ 15 → Z / Tab · ✅ 16 | same outcome |
| 👍 **R thumb** (R→LT4) · **E E** · **R R** | 3 | no Δ band (idle queue) | no Δ band |

- 🔮 Board bands are predicted; native misses 1 ms further (hack ON: N/H0 ❌ ≤ 10, S3 ❌ ≤ S−1, no ⏸ · hack OFF H0: ❌ ≤ 27) 🧪 `S-*`, `T-23`
- 🟥 **H→E is invisible in its own output**
  - E is typed either way; only the armed layer changes
  - The next key shows it: "heu" instead of "hey"
- 🟪 **M↔W and D↔V are 2-key combos themselves**
  - Only M→W was run 🧪 `S-M_LT3-*`; the other three are 🧮

### 🖐️ Why 6 pairs stay fragile

- The shared real combo contains the follower → its press does not empty the trigger's set
- Both leave at that combo's deadline (16/18) instead of 11 → the follower is bypassed onto base
- The hack changes none of the 6 outcomes 🧪 `T-23-d*/e5`, `S-H_RM2-d17-nohack`, `S-M_LT3-d15-nohack`
  - Only the 🟪 timing moves: M then W 5 ms apart fires Z at `t+16` with the hack, at the W press without 🧮

### 🚪 Window edge E_b

| Group | E_b hack ON | E_b hack OFF |
|---|---|---|
| Trigger and follower combos 16/16 or 18/18 (most N, L→G, all S2, H→E) | 110 | 110 |
| 18 ms triggers (A→RT2, E→RT1/RT3, hE→RT1/RT3/RB1) | 112 | 112 |
| Y→RM4 (16 / 18) | 108 | 108 |
| Triggers with no real combo (C→LT1, C→LB3, F→LB3, X→LM3) | 105 | 94 |
| 🟨 H0 followers | 115 | 126 |

- E_b itself is a ⚖️ cell on the board; ✅ up to E_b − 1, ❌ from E_b + 1 🔮
- Native last hit = E_b + 1 🧪 `T-12-b-d111/d112`

## ⏸ The exactly 10 ms cell

- 📜 **Why 10 is special**
  - The bypass condition is `last_tapped − 1 > follower_ts` → true for gaps ≤ 9, **false at 10** 📜 `combo.c:141-143`
  - The follower is re-captured inside the rung's timer handler, which just cancelled its own work item → its new deadline is refused → no timer 📜 `work.c:492-511, 966-968`
- ⏸ **So it stalls** until the next release, or the next press sharing none of its live candidates
  - A press up to 10 ms after the follower's own press joins the stall 📜 `combo.c:228` · 🧪 `RVB-strand-join` (gap 8)
  - Flush between `t+21` and ≈ `t+121` → adapts late; otherwise base
- 🔮 **Board-only prediction, not measured** (`T-24a`)
  - Native can't show it: its rung runs 1 ms late → 10 still bypasses → ❌ in every native log
  - Right-hand trigger → the rung runs on time → ⏸
  - Left-hand trigger → the rung inherits its BLE stamp's sub-ms phase → ❌ for an unmeasured fraction 🧮
  - 42 of 54 pairs are left-left: gaps arrive quantised to ~7.5 ms by BLE, so "10 ms" rarely occurs; a 9 ms roll may arrive as 7–8 (❌) or 14–16 (✅) 🧮
- 🟥 Same shape at S−1 for the shared-combo pairs: L→G at 15, H→E at 17

## ⚖️ The trade

> [!important] What the hack buys and costs
>
> - ❌ **Costs** the 34 🟩 N pairs every roll ≤ 9 ms, plus a ⏸ stall at 10
>   - Without it they never miss below the window edge
> - ✅ **Rescues** the 11 🟨 H0 pairs for gaps of 11–25 ms 🔮
>   - Without it they miss up to 25 ms (board; native 27) 🧪 `T-23-e3/e4`
> - ➖ **No change** for the 6 shared-combo pairs and the 3 band-less pairs

- 🌐 **Hack off = upstream ZMK v0.3+**
  - Upstream silently drops combos with ≥ 20 keys 📜 upstream `app/src/combo.c:100-101`
  - The hack-off numbers above are upstream's numbers
- 📏 **The invariant that matters:** `ak_tap_time (10) < max(hold_key_event_delay, follower's combo timeout)`
  - Margin at the band start: 1 ms for hack-only followers, 6 ms for 16 ms followers
  - With a hack timeout ≤ 10, only the hack-only followers would tie or miss at the band start; 16/18 ms followers keep ≥ 6 ms 🧮

## 🧬 Interactions with real combos

- 🕰️ **A fast 2-key combo waits for its deadline**
  - Typed under 11 ms, as the only real combo left → fires at its 16 ms deadline, not at completion
  - Cost: 16 − gap; M+W 5 ms apart → Z at `t+16` 🧪 `S-M_LT3-d5`, `T-09-a` vs `T-09-c`
- ⌫ **`bspc` / `del` always fire at `t+18`** (or at your next key event), hack or not
  - Never alone: `delWord` / `capsWord` (18 ms) stay alive 🧪 `RVB-bspc-d12`, `RVB-bspc-d5-nohack`
- 🟪 **S2 pairs:** same outcome, different timing
  - M then W 5 ms apart → Z at `t+16` with the hack, at the W press without 🧮

## ⛔ What the old explanation got wrong

| Never say | Truth |
|---|---|
| ~~"Key 2 is delayed 11 ms after its own press, so the layer is always ready"~~ | for gaps ≤ 9 it leaves in the same ms as key 1, on base 🧪 `T-02-a`, `T-23-a` |
| ~~"M then T 5 ms apart types MN"~~ | types "mt" 🧪 `T-23-a` |
| ~~"Without the hack both keys are released at once at the 16 ms timeout"~~ | a non-member key empties the set at once; the follower then waits for its own combos 🧪 `T-02-b`, `T-23-c` |
| ~~"Every key press is delayed 11 ms"~~ | most are held 16/18 ms anyway 🧪 `T-11-c/d` |
| ~~"The hack never interferes with real combos (11 < 16)"~~ | a 2-key combo typed under 11 ms fires at its 16 ms deadline 🧪 `T-09-a` |
| ~~"Two keys < 11 ms apart are released at once; doesn't matter, they wanted a combo"~~ | that band is the normal fast-roll failure: ≤ 9 ms (board) for 45 pairs, wider for 6 🧪 `T-02`, `T-04` · PAIRS |

> [!tip] Check out the timing proof
>
> [`Timing/`](Timing/README.md) holds the evidence behind every line here:
>
> - [`FACTS.md`](Timing/FACTS.md) → facts with log-line proofs, worked examples, must-not-say lists
> - [`MODEL.md`](Timing/MODEL.md) → the hack as a theorem, Δ tables hack ON / OFF
> - [`PAIRS.md`](Timing/PAIRS.md) → all 54 pairs, their class and band

---

_Firmware: fork `4211ad74` = upstream ZMK `6e03a0bb`, Zephyr 3.5, right half central. Proven from source and 181 native_posix test cases; re-run any case with `tests/timing/run.sh <case>` (see [`Timing/TESTS.md`](Timing/TESTS.md))._
