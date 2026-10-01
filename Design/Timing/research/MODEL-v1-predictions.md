# 🧭 MODEL — unified behavioural model of Flo's AK timing (single source of truth for the page)

> Firmware = ZMK fork `4211ad74` = upstream `6e03a0bb` (2024-09-12, pre-v0.1) + tooling only; Zephyr `v3.5.0+zmk-fixes`; right half central.
> Paths: `combo.c` = `zmk/app/src/combo.c`, `bq` = `zmk/app/src/behavior_queue.c`, `sk` = `zmk/app/src/behaviors/behavior_sticky_key.c`, `ht` = `zmk/app/src/behaviors/behavior_hold_tap.c`, `work.c` = Zephyr `kernel/work.c` (container volume), `cfg/` = `zmk-config/config`.
> Legend: **PROVEN** = read in the source that built the board (or observed in a native_posix run). **INFERRED** = follows from PROVEN facts by tracing, not yet executed. **TEST** = settled only by a test (see CLAIMS.md T-xx).
> All times are engine time = integer-ms timestamps on the central. Board timers fire `deadline + δ`, δ ∈ (0.03, 1.05] ms; native_posix fires at `deadline + 1` exactly.

---

## 🎯 Ten things the page must get right

- 🧱 **Every press on layers 0–24 is held by the combo engine for the LONGEST candidate combo containing it**: 11 ms (hack-only positions LT4 RT0 LM4 LB4 LH0-2 RH0), 16 ms (most letters), 18 ms (RM1–RM4). Not a flat 11. PROVEN (`combo.c:472-481` only flushes when 0 candidates remain; observed by A2/G).
- ⏱️ **`&ak` = kp↓ at delivery D, then one 10 ms queue tick: kp↑, AK layer ON, 100 ms sticky armed** → layer visible to keys delivered after D+10, gone at D+110 if nothing consumed it. PROVEN (`bq:27-49`, `cfg/adaptive_keys/macros.dtsi:25-39`, `sk:167-189`).
- 🧨 **Two `&ak` keys pressed ≤ 9 ms apart (board) both leave the engine at key 1 + 11 ms, back-to-back, key 2 on the BASE layer → no adaptation.** Mechanism = quick-tap bypass: `require-prior-idle-ms` defaults to −1, key 1's macro keycode is stamped *now*, key 2 is re-raised with its old timestamp → `is_quick_tap` true → 0 candidates → bubbles. PROVEN mechanism (`combo.c:141-143,153,496-502`, `bq:34-35`), reach INFERRED → **T-02**.
- 🪤 **At exactly Δ = 10 ms (board) key 2 is stranded**: re-captured inside the timer handler after `cleanup()` self-cancelled the work item → `k_work_schedule` refused (CANCELING) → no timer → delivered at the next press/release. PROVEN (`work.c:492-511, 966-968`; observed by A2 with `&kp` keys). Δ ≤ 10 on native_posix is all bypass (handler runs 1 ms later there).
- ✅ **For 11 ≤ Δ ≤ ~105 ms every compiled AK pair adapts**: key 1 delivered at `min(Δ, max(11,k1))`, key 2 at `Δ + max(11, k2)`, layer on 10 ms after key 1 → margin ≥ 1 ms. INFERRED from PROVEN rules → **T-04/T-05/T-06**.
- 🔁 **Without the hack, only the 12 pairs whose follower sits on a hack-only position miss (for Δ ≤ k1+9); every follower that is in a real combo already waited 16–18 ms and adapted for ALL Δ.** The hack therefore rescues 12 pairs for 11 ≤ Δ ≤ k1+10 and breaks all 23 pairs for Δ ≤ 10. INFERRED → **T-23**.
- 🕰️ **A completed 2-key combo does not fire at completion while the hack is alive**: it fires at its own 16/18 ms deadline or at the next press/release. If its second key lands at 11 ≤ Δ < 16 and no longer sibling survives, it fires at Δ. PROVEN (`combo.c:448-452`, observed A2 S7).
- 🧵 **One thread, one FIFO**: kscan, split events, combo/hold-tap/sticky timers and the behaviour queue all run on the system workqueue (prio −1, cooperative); "races" are ordering questions. Every macro key (`&ak`, `&bk`, morphs) is serialised through ONE queue: `moAndBuffer`'s release parks it for **260 ms**, so any letter typed in that window is emitted at thumb-release + 260. PROVEN (`bq:45-48,61-63`, `cfg/mods/macros.dtsi:19-22`).
- 🎯 **Timestamps never move**: a buffered/captured key is delivered with its original timestamp; hold-tap terms, sticky windows and combo deadlines count from it. Only behaviour-queue steps (`&ak`'s `&kp`, `&aksl`) are stamped at execution. PROVEN (`combo.c:267,280,284`, `ht:619`, `bq:35`).
- 🖐️ **Transport**: same half adds 4–6 ms (debounce, both keys → gap survives ±1 ms); a left key adds 0.5–9 ms BLE (7.5 ms anchor) before it is stamped on the right → L→R gaps shrink (can invert), R→L stretch, L→L quantise to 7.5 ms. All 23 compiled AK pairs are same-hand. PROVEN parameters, INFERRED distribution (hardware-only).

---

## (a) 🚚 Pipeline: finger → HID report, with every delay

```mermaid
sequenceDiagram
    autonumber
    box transparent 🅻 Left half (peripheral, nRF52840)
        participant LS as 🔘 Left switch
        participant LD as 🧮 kscan + debounce (L)
        participant LB as 📡 BLE split link
    end
    box transparent 🅡 Right half (central) — one system workqueue, prio −1
        participant RS as 🔘 Right switch
        participant RD as 🧮 kscan + debounce (R)
        participant EV as 📣 Event manager
        participant HT as ✋ Hold-tap listener
        participant CE as 🧩 Combo engine
        participant KM as 🗺️ Keymap
        participant BQ as ⏳ Behaviour queue
        participant SK as 📌 Sticky layer (aksl)
        participant HID as 📤 HID / endpoints
    end

    LS->>LD: contact
    Note over LD: +4.0–6.0 ms (5 samples on a 1 ms grid) [P]
    LD->>LB: bitmap notify (no timestamp on the wire)
    Note over LB: +0.5–9 ms to next 7.5 ms anchor,<br/>+7.5 ms per missed event [I]
    LB->>EV: position event, timestamp = k_uptime_get() at BT receipt (central.c:259-263)
    RS->>RD: contact
    Note over RD: +4.0–6.0 ms [P]
    RD->>EV: position event, timestamp = k_uptime_get() at raise (physical_layouts.c:178-182)

    EV->>HT: listener order: activity → hold_tap → combo → tap_dance → keymap (zmk.map)
    Note over HT: undecided hold-tap? capture until decided (≤ term − delivery delay)
    HT->>CE: bubble
    Note over CE: hold = LONGEST candidate timeout: 11 / 16 / 18 ms on layers 0–24 (0 on utility layers)<br/>early exit: any release, or a press that empties the set
    CE->>KM: ZMK_EVENT_RELEASE (elem 0) / ZMK_EVENT_RAISE (others), ORIGINAL timestamp
    Note over KM: layer resolved NOW (live bitmask), binding invoked synchronously
    KM->>BQ: &ak: enqueue kp↓(wait 10), kp↑, aksl↓, aksl↑
    BQ->>HID: kp↓ (synchronous if queue idle, timestamp = now)
    Note over HID: one report per keycode; BLE HOG send is async (hog.c)
    Note over BQ: +10 ms (K_MSEC(10); +1 tick)
    BQ->>HID: kp↑
    BQ->>SK: aksl↓ → &mo layer ON (visible to the NEXT dispatched key)
    SK->>SK: aksl↑ → release_at = now + 100
    Note over SK: OFF at first keycode's UP after arming, or at +100 ms, or pinned by a held modifier
```

- **Where the numbers come from (PROVEN):** debounce `debounce-press-ms 5`, scan 1 ms (`zmk,kscan-gpio-matrix.yaml` defaults, nothing overridden); BLE `CONFIG_ZMK_SPLIT_BLE_PREF_INT=6` (7.5 ms), latency 30, cancelled on TX (`ull_conn.c:253-255`); combo hold `combo.c:145-161, 472-481`; queue tick `bq:45-48`; sticky `sk:181-187, 281, 303-308`.
- **Same-thread guarantee (PROVEN):** all of the above except the BLE radio and HOG TX run on `k_sys_work_q` (`CONFIG_SYSTEM_WORKQUEUE_PRIORITY=-1`); a handler is never preempted by another handler. Timers are late by the length of whatever handler is running (`k_msleep(10)` in `ht:220-222` is the only sleeper).
- **Clock (PROVEN):** `k_uptime_get()` = floor ms of a 32768 Hz RTC; `K_MSEC(n)` fires `n` ms + 1 tick (30.5 µs) after the schedule call, so board timer deliveries land at `deadline + δ`, δ ∈ (0.03, 1.05] ms depending on the sub-ms phase of the schedule. native_posix: tick = 1 ms → exactly `deadline + 1`.

---

## (b) 🧩 Combo engine as a state machine (exact rules)

```mermaid
stateDiagram-v2
    direction LR
    state "🟢 Idle<br/>buffer empty, candidates empty" as Idle
    state "🟡 Collecting<br/>buffer[1..n], ≥1 candidate, timer armed for MIN deadline" as Coll
    state "🟠 Complete-pending<br/>candidates[0] fully pressed, ≥2 candidates alive" as Pend
    state "🔴 Stranded<br/>buffer ≥1, ≥1 candidate, NO live timer" as Dead

    [*] --> Idle
    Idle --> Idle : PRESS with 0 candidates on current layer → bubble (not captured)
    Idle --> Idle : PRESS re-raised & is_quick_tap (last_tapped−1 > ts) → bubble
    Idle --> Coll : PRESS with ≥1 candidate → capture, deadlines = ts + timeout, arm MIN
    Idle --> Dead : PRESS re-raised INSIDE the timer handler after cleanup() → schedule refused (CANCELING)
    Coll --> Coll : PRESS sharing a candidate, MIN unchanged → capture
    Coll --> Dead : PRESS sharing a candidate, MIN moved LATER → schedule refused (DELAYED), phantom deadline
    Coll --> Pend : PRESS completes candidates[0] with ≥2 alive → capture, mark only
    Coll --> Idle : PRESS completes the ONLY candidate → activate combo (ts = first key), flush rest
    Coll --> Idle : PRESS sharing no candidate → capture, cleanup: elem0 RELEASE, others RAISE (fresh set, own ts)
    Coll --> Coll : TIMER rung, candidates remain → drop expired, re-arm next MIN (allowed: RUNNING only)
    Coll --> Idle : TIMER last rung → cleanup → flush; re-raised keys: bypass, or Stranded
    Pend --> Pend : PRESS completes a longer candidate → overwrite slot
    Pend --> Idle : TIMER last rung / any RELEASE → activate slot combo, flush rest
    Dead --> Idle : any RELEASE, or a PRESS that empties the set → cleanup flushes everything
    Coll --> Idle : RELEASE of any position → cleanup → flush; if >1 flushed, dupe RELEASE re-raised
    Idle --> Idle : RELEASE of a fired-combo key → swallowed; behaviour released on the FIRST key up
```

### Rules (all PROVEN unless marked)

- **R1 Capture.** First key of a set: candidates = combos on that position active on `zmk_keymap_highest_layer_active()` and not `is_quick_tap`; each `timeout_at = ts + timeout_ms` (`combo.c:145-161`). Captured iff ≥1 candidate (`:424-437`). Layer and prior-idle are checked ONLY here, never for later keys (`:429-431`).
- **R2 Filter.** Later key: drop candidates with `timeout_at <= ts` (strict `>` keeps, `:228` → window is half-open: 2nd key at exactly `ts1 + T` is OUT), then keep only candidates containing the new position (`:163-195`). A key sharing nothing is still captured, then `cleanup()` flushes all (`:439-441`).
- **R3 Deadlines belong to key 1.** All `timeout_at` are anchored to the first key's timestamp; a re-raised key starts a fresh set anchored to ITS original timestamp (`:155`, `:284`).
- **R4 Timer ladder.** One delayable armed for the MIN deadline (`:407-420`); on expiry only candidates with `timeout_at <= deadline` drop; `cleanup()` only when 0 remain (`:477-479`) → a key held alone leaves at its LONGEST candidate's deadline.
- **R5 Flush.** `cleanup()` = cancel timer, clear candidates, activate `fully_pressed_combo` if any, then `release_pressed_keys()` (`:397-405`): element 0 → `ZMK_EVENT_RELEASE` (resumes at tap_dance → keymap, **skips hold-tap**), elements ≥1 → `ZMK_EVENT_RAISE` from listener 0 (hold-tap, combo again), synchronously, in press order, each with its ORIGINAL timestamp (`:273-289`).
- **R6 Release.** ANY position release calls `cleanup()` first (`:457`) → flushes the whole buffer; if >1 key flushed, a dupe release is re-raised so the keymap sees `A↓ B↓ A↑` in order (`:461-468`); the re-raised B is immediately re-flushed by the dupe's own `cleanup()` → B's timers never apply. Releases of fired-combo keys are swallowed; behaviour released on the FIRST key up (no `slow-release` anywhere in Flo's config) (`:363-395`).
- **R7 Combo fire.** Only `candidates[0]` (shortest, earliest-defined) is tested for completion (`:435, 443, 449`). With ≥2 candidates alive a complete combo only marks `fully_pressed_combo` and fires at the ladder end or next event (`:448-452`). Press carries the FIRST key's timestamp and the combo's virtual position (`:349, 291-299`).
- **R8 Quick-tap bypass (the AK-critical one).** `is_quick_tap = (last_tapped_timestamp + require_prior_idle_ms) > ts` with compiled `require_prior_idle_ms = -1` (`:141-143`, binding default, `devicetree_generated.h`). `last_tapped_timestamp` = timestamp of the last non-modifier keycode DOWN (`:496-502`). A keycode produced by the behaviour queue (`&ak`, `&bk`, any macro) is stamped `k_uptime_get()` at execution (`bq:34-35`); a raw `&kp` bound directly in the keymap keeps the position timestamp. Hence a re-raised key with `ts <= now − 2` after a macro key was just delivered gets **zero candidates and bubbles straight to the keymap**.
- **R9 Stranding (CANCELING trap).** `cleanup()` calls `k_work_cancel_delayable` (`:398`); when that runs INSIDE `combo_timeout_handler` the item is RUNNING → Zephyr sets `K_WORK_CANCELING` (`work.c:503-507`); `k_work_schedule` then refuses (`work.c:967`, returns 0) and `combo.c:417-418` records a phantom `timeout_task_timeout_at`. Any key re-captured during that handler invocation has no timer until the next press/release. Observed (A2 S1/S4b/S9/S10).
- **R10 Late-deadline stall.** While the timer is DELAYED, `k_work_schedule` is a no-op, so if a 2nd key filters out the shortest candidate the later MIN is never armed; the old timer fires, `:473` early-returns without re-arming → stall until the next event. Example on Flo's board: RM1 then RM3 at +12 ms then RM2 → `delWord` fires only on the first release. Observed by none; **T-10**.
- **R11 No poison timer (A1 refuted).** After a timer-driven empty flush `update_timeout_task()` computes `LONG_MAX` (= 2147483647 on ARM) ≠ `LLONG_MAX` and calls `k_work_schedule(~24.8 days)` — but the item is CANCELING, so the call is refused; only `timeout_task_timeout_at = 2147483647` is recorded (0 on native_posix), which no real deadline can equal. The next first key schedules normally (item idle after `work.c:681-684`). No board-only divergence here.
- **R12 Limits.** 28 compiled combos: 22 × 16 ms, 5 × 18 ms, 1 × 11 ms hack (36 keys, layers 0–24), none at 30 ms (`zephyr.dts`). `MAX_PRESSED_COMBOS=20`, `MAX_COMBOS_PER_KEY=30`, `MAX_KEYS_PER_COMBO=36`; buffer guard uses 30 (`:263`, harmless typo).

### Per-position candidate landscape on layers 0–24 (PROVEN from `zephyr.dts`)

| Positions | Real combos (max ms) | Solo delivery |
|---|---|---|
| LT4 X · RT0 / · LM4 C · LB4 F · LH2 · LH1 · LH0 · RH0 | none | **11** |
| LT3 LT2 LT1 LT0 · RT1–RT4 · LM3–LM0 · RM0 · LB3–LB0 · RB0–RB4 · RH1 RH2 | one to three × 16 | **16** |
| RM1 A · RM2 E · RM3 I · RM4 H | 16 + delWord/capsWord 18 | **18** |
| any position on `l_nav/l_num/l_numsym/l_nav_linwin` | hack absent; `*Trans` combos on LM1–LM3, bspc/del on RM1–RM3 | **0 or 16/18** |

---

## (c) ⌨️ The `&ak` keystroke path, exact offsets

Physical press P on the right half, key at position with longest candidate `k` (0 → hack-only). `T = P + 4…6` (debounce) is the timestamp. Queue idle.

| Instant (engine time) | What happens | Where |
|---|---|---|
| `T` | position event raised; hold-tap bubbles; combo captures (candidates: real combos + hack) | `combo.c:424-437` |
| `T + 11` | hack rung: candidates drop; if none remain (hack-only key) → `cleanup()` → **delivered** | `:472-481` |
| `T + max(11,k)` = **D** | key delivered to keymap with timestamp `T`; layer resolved now; `&ak L X` runs; `kp X↓` synchronous → HID report; queue schedules 10 ms | `keymap.c:651-682`, `bq:27-49` |
| `D + 10` (+δ) | queue tick: `kp X↑` (HID), `aksl L↓` → `&mo L` → **layer L ON**, `aksl L↑` → `release_at = D+10+100` | `bq:45-48`, `sk:160-163, 181-187` |
| `D + 110` (+δ) | sticky timer → `&mo L↑` → layer OFF (if no keycode consumed it) | `sk:124-131, 342-354` |
| physical release | `&ak` release phase is empty (no `macro_pause_for_release`) → nothing; holding never repeats | `behavior_macro.c:114-137` |

- **Visibility to the next key (PROVEN):** the layer bit is written synchronously at `D+10`; any position event whose keymap resolution runs after that instant resolves on L. A key flushed in the SAME `release_pressed_keys()` burst as key 1 resolves BEFORE `D+10` → base layer. A key delivered at exactly `D+10` is a same-tick ordering question (**T-04** records native's order; board = sub-ms coin flip).
- **Consumption (PROVEN, `sk:268-310`):** the first keycode DOWN after arming stops the 100 ms timer and pins the layer until that keycode's UP (after HID processed it); modifiers count (no `ignore-modifiers`), so a held/sticky Shift pins the AK layer until Shift up (≤ 1500 ms for `skms`). A `&bk` follower therefore keeps the layer on for 10 more ms after its delivery; an `&ak` follower's `kp↑` releases the old layer and its `aksl↓` (same tick) turns the new one on → gapless chaining.
- **Position-0 collision (PROVEN, `bq:54` never sets `.position`, `sk:85-92, 147-151`):** every `aksl` lives at position 0; a new `aksl↓` releases any still-armed unconsumed `aksl`. Moot in practice (the follower's own `kp↓` always consumed it first) but it is why logs show `position 0`.
- **Window seen from the next key-down:** with follower delivery `D_B = Δ + max(11,k2)` and layer alive on `[D_A+10, D_A+110]`, adaptation needs `Δ ≥ 11` (see (d)) and `Δ ≤ D_A + 110 − max(11,k2)` ≈ **105–110 ms between key-downs**, not 100.
- **native_posix offsets:** every timer +1 → delivery `T + max(11,k) + 1`, layer on `D + 11`, off `D + 112`.
- **R thumb (`blt_akR`, tap = `ak_R_macro` wait 0 / tap 0 wrapping `&ak`) — INFERRED, T-14:** the tap runs OUTSIDE the queue work, so `&ak`'s first `zmk_behavior_queue_add` re-enters `behavior_queue_process_next` (`bq:61-63`): `kp R↓`, then the outer loop drains `kp R↑`, `aksl↓`, `aksl↑` immediately → **0 ms tap, layer ON at the decision instant**, so a key captured by the thumb hold-tap is re-raised onto an already-active `l_akR`.

---

## (d) 🧪 The hack as a theorem

### Statement

Let A be a key bound to `&ak` (all 22 alphas + the R thumb tap), B any key, both on a layer in `l_alpha_aks`, sharing no real combo, apparent gap Δ (integer ms, B's timestamp − A's), `k1`/`k2` = longest real-combo timeout containing A/B (0 if none), `dA = max(11, k1)`, behaviour queue idle when A is delivered. Board timing.

- **Hack ON**
  - `Δ ≤ 9` → **MISS**. B shares only the hack with A, so both wait for the hack rung at `T_A + 11`; A is released first, its `&ak` emits `kp A` stamped `T_A+11`; B is re-raised with `T_B ≤ T_A+9` → `is_quick_tap` true → bubbles → resolved on the base layer at `T_A+11` (layer arrives at `T_A+21`). HID: `A↓ @11, A↑ @21, B↓ @21, B↑ @31`, both base letters.
  - `Δ = 10` → **STALL**. `is_quick_tap` false → B re-captured inside the timer handler → schedule refused (R9) → delivered at the next position event E. Adapted iff `E ≥ T_A+21` and the layer is still alive (E ≤ ~`T_A+121`); a release before `T_A+21` → MISS.
  - `11 ≤ Δ < dA` (only when `k1 > 11`) → **HIT**. B's press empties A's set → A delivered at Δ, layer at Δ+10; B re-raised, fresh set (hack + own combos), timer accepted (not inside the handler) → B at `Δ + max(11,k2)`. Margin `max(11,k2) − 10 ≥ 1`.
  - `dA ≤ Δ ≤ dA + 110 − max(11,k2)` → **HIT**. A delivered at dA by the ladder, layer at dA+10; B fresh at Δ → `Δ + max(11,k2) ≥ dA + 11`.
  - beyond → **MISS** (window closed).
- **Hack OFF**
  - `k2 > 0` → **HIT for every Δ ≥ 0** (B waits ≥ 16 ms for its own combos; A is delivered at min(Δ, k1) or immediately if `k1 = 0`; layer arrives ≥ 6 ms before B).
  - `k2 = 0`: A delivered at `min(Δ, k1)` (0 if `k1 = 0`), B delivered at Δ with no delay → **MISS for Δ ≤ k1 + 9, TIE at Δ = k1 + 10, HIT for Δ ≥ k1 + 11**.
- **Preconditions / caveats**
  - Queue idle at A's delivery. If a previous macro key was emitted < 10 ms before (3-key rolls, or inside `moAndBuffer`'s 260 ms park), A's keycode is enqueued, `last_tapped` is stale, and the Δ ≤ 9 case becomes STALL instead of MISS (still base layer if the flush comes before the layer).
  - The Δ boundary is `T_B ≤ now_flush − 2`. Board: `now_flush = T_A + 11` in ~95 % of cases (`T_A + 12` when the schedule phase f > 0.95) → bypass for Δ ≤ 9 (rarely ≤ 10). native_posix: `now_flush = T_A + 12` → bypass for Δ ≤ 10; Δ = 11 is a key-first case and HITs.
  - A = hold-tap (R thumb, linger keys) follows the hold-tap capture path instead (c).
  - Nominal 1 ms margin at Δ = 11 with `k2 = 0` can be eaten by sub-ms phase (layer via a K_MSEC(10) from A's timer-driven delivery vs B's own K_MSEC(11)); estimated ≈ 0.05 % of Δ = 11 events → INFERRED, unmeasurable on native.
- **Failure region summary:** with the hack, all 23 pairs fail for Δ ≤ 9 and stall at Δ = 10; without it, 12 pairs (followers on LT4/LM4/LB4/LH0) fail for Δ ≤ k1+9 (typically ≤ 25) and 11 pairs never fail. The hack also adds 11 ms of latency to the 8 hack-only positions and 0 ms to everything else.

### Predicted outcomes, 2-key adaptive sequence, apparent Δ = 0…45 (same hand)

Legend: ✅ HIT · ❌ MISS · ⏸ STALL (delivered at next press/release) · ⚖️ TIE (sub-ms coin flip on the board, deterministic on native).

| Δ (ms) | Hack ON, any k1/k2 | OFF, k2 ∈ {16,18,30}, any k1 | OFF, k2 = 0, k1 = 0 | OFF, k2 = 0, k1 = 16 | OFF, k2 = 0, k1 = 18 | OFF, k2 = 0, k1 = 30 |
|---|---|---|---|---|---|---|
| 0–9 | ❌ (bypass; native: 0–10) | ✅ | ❌ | ❌ | ❌ | ❌ |
| 10 | ⏸ (native: ❌) | ✅ | ⚖️ | ❌ | ❌ | ❌ |
| 11–25 | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| 26 | ✅ | ✅ | ✅ | ⚖️ | ❌ | ❌ |
| 27 | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| 28 | ✅ | ✅ | ✅ | ✅ | ⚖️ | ❌ |
| 29–39 | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| 40 | ✅ | ✅ | ✅ | ✅ | ✅ | ⚖️ |
| 41–45 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- Delivery times behind the ✅ cells (hack ON): `D_A = min(Δ, dA)` for Δ ≥ 11, `D_B = Δ + max(11,k2)`, layer on `D_A + 10`. Examples: L(16)→G(0) at Δ=13: L@13, layer@23, G@24. M(16)→T(16) at Δ=20: M@16, layer@26, T@36. C(0)→P(16) at Δ=11: C@11, layer@21, P@27.
- `k1 = 18` behaves like 16 with +2 everywhere; `k1 = k2 = 30` exists only if a two-hand combo were compiled (none is today).
- Upper window edge (not in the table): ✅ turns ❌ at `Δ > dA + 110 − max(11,k2)` → 105 (C→P), 110 (M→T, L→G).

### Cross-hand mapping (read the table at the *apparent* Δ)

| Physical pair | Apparent Δ seen by the engine | Effect on the table |
|---|---|---|
| R→R, L→L same anchor | physical ± 1 (debounce phase, floor) | as printed |
| L→R | physical − d, d ∈ [0.5, 9] (median ≈ 4.5; +7.5 tail) | a 12–19 ms roll can land in 0–10 → ❌/⏸; d > physical inverts order (B becomes key 1 → letters swap) |
| R→L | physical + d | pushed out of the failure band, toward the 105–110 window edge |
| L→L across anchors | quantised to k × 7.5 ± 1 | 9 ms physical → 7–8 (❌) or 14–16 (✅) |

- No compiled AK pair is cross-hand (all 23 layers' followers are on the trigger's hand, D §10), so this only touches generic bigram latency and the (uncompiled) 30 ms tier. INFERRED distribution; hardware-only (**T-24**).

---

## (e) 🎛️ Linger keys, Callum mods, combo tiers — what actually happens

### Linger keys (`LK` = hold-tap, tap-preferred, 100 ms; PROVEN `ht:297-311, 619-620, 636, 742`)

- Position event is held by combo first (16 ms for RT1/RT2/RT4/RM0, 11 for RT0/RB0 morphs); the hold-tap is created at delivery **with the original timestamp**, so the term timer is `(T + 100) − now` — the combo delay is NOT added.
- Decision: own key-up with `ts_up ≤ T + 100` → TAP; `ts_up ≥ T + 101` → HOLD (forced by `:636` even if the timer hasn't run); timer at `T + 100 + δ` → HOLD. Exactly 100 ms is a sub-ms coin flip on the board, TAP on native.
- Other keys pressed while undecided are **captured, never decide** (tap-preferred). TAP path: `tap↓`, captured keys delivered, `tap↑` (`:555-557, 640-642`); with `&bk` as tap the follower's HID down lands after `tap↑` at the next 10 ms tick. HOLD path: linger binding at 100, captured keys delivered right after.
- A linger key pressed ≤ 9 ms after an `&ak` alpha is **force-decided TAP at delivery** (`ht:142-149` with `require-prior-idle-ms = -1`, same skew as R8): it can never linger. INFERRED → **T-16**.

### Callum mods (PROVEN `cfg/mods/behaviors.dtsi`, `cfg/mods/macros.dtsi`, `ht:333-347, 444-464, 522-526`)

- `htls` (LH1, hold-preferred 90): held alone → `moAndBuffer↓` at `T + 90` (+δ; the 11 ms hack delay does not extend it) → `l_mod` ON; any other key DOWN while undecided → HOLD immediately (also for keys that were buffered with it and flushed together); released before 90 with no other key → TAP = `skms LSHIFT` (sticky 1500 ms, no ignore-modifiers).
- `moAndBuffer` release: `wait 130` → `&none` tap → `&mo l_mod↑` at **release + 130** (layer OFF), then the queue waits another 130 → **behaviour queue parked until release + 260**: every `&ak`/`&bk`/morph delivered in `(release, release+260)` is emitted at release + 260, in order. INFERRED timeline from PROVEN queue rules → **T-18**.
- `htm` (l_mod home row, tap-preferred 130, hold-while-undecided + linger): the modifier is DOWN from the key press (HID report immediately). Tap (< 130, no other key): `skm MOD↓` (count 2) then hold release (count 1) → mod stays until the next non-modifier key's UP or 1500 ms; other mods stack (`ignore-modifiers`). Hold ≥ 130 or key-up after a captured key: captured keys delivered with the mod down. The page's "bare skm tap" model is wrong; the mod is never absent between press and consumption.
- Page "late" scenario (thumb 0–120, Shift-tap at 100, next key at 260): `l_mod` off at 250; RM1 at 260 resolves on alpha → `&ak A`, still under the sticky Shift → **"A" shifted**, and its HID down is deferred by the park to 380 (≈ 100 ms late). Not lowercase "a".

### Combo tiers (PROVEN `zephyr.dts`, `cfg/CONFIG.h:9-11`)

- Live tiers: **16 ms** (22 combos) and **18 ms** (5). **30 ms has zero consumers** (`pronouns/combos.dtsi`, `h_digraphs/combos.dtsi` are `//` in `corne.keymap:86-87`).
- Acceptance is `floor(t2) − floor(t1) ≤ T − 1` (`combo.c:228`); the timer fires at `t1 + T + δ`.
- A 2-key combo whose second key arrives at Δ < 11 fires at its **own deadline** (16/18) or at the first release; at 11 ≤ Δ < T it fires at Δ iff it is the only surviving candidate (space, entr, typeExcl…), otherwise (bspc under delWord/capsWord) at the longest sibling's deadline. 3-key combos typed out of order (RM1, RM3, RM2) stall until a release (R10).
- Left-hand 16 ms combos are exposed to the 7.5 ms anchor grid (physical 8–15 ms gaps → in or out by phase); 18 ms is grid-safe. INFERRED.

---

## (f) 🔀 What differs on upstream ZMK today (v0.3.0 / main 2026-09; PROVEN by F)

- **The 36-key hack is silently dropped**: `combos[]` is built by `LISTIFY(20, …)` (lengths 0–19); `combo_init` logs `Have 27 combos!`; hack-only keys go back to 0 ms delay and the Δ ≤ k1+9 misses for the 12 hack-only-follower pairs return. Two `#warning`s for the deprecated Kconfigs, build succeeds.
- Combo semantics otherwise identical (capture/bubble, RELEASE-then-RAISE, first-key timestamp, deadline = ts1 + min timeout, shortest-first winner, R9/R10 quirks included). Storage is bitmasks; per-key limit unlimited; `layers = <-1>` would be UB (Flo never uses it).
- Behaviour queue and macro timing identical (`&ak` 10 ms hop, dequeue-time stamps). Macro release-param fix `1bac680c` is a no-op for Flo's shapes.
- Hold-tap logic unchanged; sticky key matches (position, behaviour, param) instead of position only — unreachable difference for `aksl`.
- Left-hand timestamp is taken on the workqueue (HEAD) instead of the BT RX callback (fork): sub-ms.
- Test board is `native_sim//zmk_test_mock` on Zephyr 4.1 (`native_sim.keymap`).
- Page wording that holds: "ZMK main from 2024-09 (pre-v0.1) through v0.3.x and current main, except the 36-key consistency hack, which is dropped from v0.3.0 on."

---

## (g) 🔍 Confidence

### PROVEN by reading the code that runs (or by an executed native_posix run)
- Listener order (map file), event-manager RELEASE/RAISE semantics, original timestamps preserved.
- Combo rules R1–R7, R12; R9 (CANCELING trap: `work.c` + observed by A2); R11 (no poison, `work.c:967` refuses while CANCELING).
- `&ak`/`&bk`/`aksl`/`moAndBuffer`/`htls`/`htm`/`LK` wiring and their step lists; queue tick = `k_work_schedule(K_MSEC(wait))` after the item; queued items stamped `now` and `position 0`.
- Sticky consumption/release rules incl. modifiers counting; hold-tap term from original timestamp; decision → tap↓, captured, tap↑ order; hold-preferred interrupt = HOLD.
- Constants, compiled combo set, per-position max timeouts, tick rates, debounce defaults, BLE link parameters, native_posix +1 ms.
- Lone-key delivery = longest candidate (observed G/A2); combo completed under the hack fires at its own deadline (observed A2 S7); stranded second key with `&kp` key 1 (observed A2 S1).

### INFERRED (mechanism proven, outcome not yet executed)
- Quick-tap bypass reach on Flo's layout (Δ ≤ 9 board / ≤ 10 native) and therefore the MISS verdict for the docs' M→T@5 and page's C→P@6 examples. → T-02, T-04, T-23
- STALL at Δ = 10 with `&ak` key 1. → T-04 (board-only band; native shows bypass)
- Hack-off table (12 pairs miss ≤ k1+9, others always hit). → T-23
- 260 ms queue park after the action thumb; late-scenario shifted letter. → T-18
- R thumb 0 ms tap + immediate layer; captured key adapted. → T-13/T-14
- Linger/hold-tap forced TAP after an `&ak` within 9 ms. → T-16
- Late-deadline stall for 3-key combos typed out of order (R10). → T-10
- BLE latency distribution and L→L quantisation. → T-24 (hardware only)
- Sub-ms phase eating the 1 ms margin at Δ = 11 (≈ 0.05 %). Not testable on native.

### Refuted / corrected reader claims
- A1 Defect 1 (board-only poisoned timer, B delayed until A's release at Δ = 40): refuted — schedule refused while CANCELING; B gets a real timer at Δ + 11. Its C6 test would pass identically on both targets.
- B §4.4 "queue parked 130 ms": the layer drops at +130, the queue is parked until +260 (D correct).
- D T7b "R thumb then held key → not adapted": with the nested-sync 0 ms tap the layer is on before the captured key is re-raised → adapted (B correct). → T-13
- E's artifact simulator Case B (`d2 = Δ + max(k2,11)` for Δ < 11): key 2 bypasses (Δ ≤ 9) or stalls (Δ = 10); its own combos are irrelevant there.
- B's OQ-1 (listener order inferred from CMake): settled PROVEN by A1/A2 from `zmk.map`.

### Needs a decision, not a test
- Whether page timelines are "engine time" (recommended: everything above) or end-to-end (add 4–6 ms debounce, BLE for the left hand).
- Whether to show uncompiled examples (th/sh/gh linger combos, I'm/I'll two-hand combos, the 30 ms tier).
