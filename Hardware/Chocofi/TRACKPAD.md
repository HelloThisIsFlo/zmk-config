# 🖲️ Chocofi trackpad (TPS43)

An Azoteq **TPS43-201A** trackpad (43.3 × 40.3 mm, IQS572, I²C) built into the **right** half (central) of the Chocofi, in the **02 Massive** case.

## 📍 Status (15 Oct 2026)

- ✅ **v2 final** (Toucan2 style) designed, checked and exported
  - ❌ Doesn't fit the real keyboard: the nano is socketed and sits higher than in the model (see 📌)
- 🧪 **Next: v3 experiment**: pad aligned with the index column, floating over the nano (see 🔜)
- ⏳ Not started: buying parts, printing, firmware (blocked on the ZMK fork rebase)

## 📌 Hard constraints

- 📏 **Socketed nice!nano + battery underneath** (sockets aren't in the Fusion REF)
  - Pin tips stand **1.6–1.9 mm above the case rim**, already trimmed. 2 pins can lose ~0.2 more
  - User param **`nano_pin_above_rim` = 2.0**, the only pin knob (it includes any air gap)
  - The real nano board is ~flush with the rim. The stock controller cover doesn't fit either
- ⌨️ **KLP Lamé keycaps**, two heights above the PCB
  - **Home row (low) ≈ 10.42** → the touch-surface target
  - Top + bottom rows (high) ≈ 13.7
- 🔌 **USB-C + power switch** reach out through the stock **top-wall notch** (x 157.06–171.06). It must stay open
  - MSK12C01 slide switch at model (164.4, 33.1), right under the nano's USB-C end
  - Its lever points +y into the notch (y 34.5–36.0, z 0–1.4)
- 📡 **Wireless build**: the TRRS jack isn't fitted
  - The inner-wall notch (y −18.68 to −4.68) is the unused TRRS opening. v2 uses it as the wire pass. Close it later
- 🖨️ **Pod printing**: flat top, printed **upside down, no supports**
  - The bed texture is the touch surface. ⏳ Temporary: ironing may come back as a glued-on skin or a smooth sheet
  - Plain PLA/PETG. ❌ No carbon-fibre or metal fill (blocks capacitive sensing)
- 📺 The right nice!view can go (the pad covers it)

## 📏 Measurements (Flo, 15 Oct)

| What | Value | Note |
|---|---|---|
| Case height (desk → rim) | 15.98–16.13 | Model 16.0 ✅ |
| PCB → rim | 6.52–6.9 | Model 6.6. Varies where heat-set inserts bulged the plastic → **don't reference the PCB** |
| Rim → nano pin tips | 1.6–1.9 (one at 1.0) | Design value 2.0 |
| PCB → Lamé home-row top | ≈ 10.42 | PCB-referenced, so ±0.3 |
| PCB → Lamé top/bottom-row top | ≈ 13.7 | Same |

- 🔩 Any screw post that runs down to the PCB stops **~0.5 mm short**, so the PCB height can't push the pod off the rim

## 🔌 Wiring

| TPS43 | nice!nano | Why |
|---|---|---|
| VDD | VCC (3.3 V) | ZMK cuts it in sleep. The pad resets on wake; the drivers handle it |
| GND | GND | |
| SDA + SCL | **D8 + D9** on `&i2c1` | The nice!view uses SPI0, the same nRF52 block as I²C0 |
| RDY | **P1.02** (extra nano pad) | No Chocofi pad there |
| NRST | **P1.07** (extra nano pad) | Same |

- 🧷 FFC pinout (datasheet v1.06): 1 RDY · 2 NRST · 3 GND · 4 VDDHI · 5 SCL · 6 SDA. Some older pages swap SDA/NRST → check continuity
- 🟡 Avoid D0 (routed to the TRRS data pad). Spare: D10/D16 (NFC pins, `CONFIG_NFCT_PINS_AS_GPIOS=y`), P1.01
- 🔬 Verified on the beekeeb `power-switch` PCB: D8, D9, D10, D16 pads have no copper at all. The wired main-branch PCB agrees
- 🧠 **Firmware blocker**: the `../zmk` fork predates ZMK pointing support → rebase onto upstream (keep the combo + AK patches). Drivers: `AYM1607/zmk-driver-azoteq-iqs5xx`, `essenceotd/zmk_driver_azoteq`

## 📐 Model facts (Fusion, right half, mm, z = 0 = PCB top)

- 🔁 **KiCad → model**: x = 342.588 − kicad_x, y = 89.01 − kicad_y. The right half shows the KiCad **B side** up
- 🧱 **Case**: rim 6.6 · floor bottom −9.4 · inner wall face x 150.77 · top wall inner face y 35.61 · stock cover z 6.7–8.7
- 🔩 **PCB holes**: S1 (157.17, −17.42) and S2 (171.27, −7.89) = stock cover standoffs, M2 countersunk from below
  - Others: (175.58, −21.35), (193.62, 19.16), (218.64, −15.13), (247.59, 5.19), (247.59, 22.21)
- 📟 **Nano**: x 155.19–172.97, y 2.21–35.23 (model z 2.5–3.55, no sockets). USB-C cut-out x 159.46–168.70 at the top end
  - Header pin rows at x ≈ 156.46 and 171.70, 12 pins each from y ≈ 3.5, 2.54 pitch
- ⌨️ **Keys** (17.5 × 16.5 keycaps)
  - Inner index column x 184.68: bottom y −6.39 · home 10.61 · top 27.61
  - Thumbs: inner (167.93, −29.78) 30° · middle (188.53, −26.57) 15° · outer (208.58, −23.98) 0°
- 🖲️ **TPS43 back**: components ≤ 0.9 mm (C2 tallest), in a band 6.8–20.3 mm from one 43.3 mm edge, y 5–31 of 40.3
  - Place that band off the nano, over open space, so the pad's flat back can sit right over the pins

## 🧩 Versions in Fusion

Each version is one timeline group. Suppress one, unsuppress another to switch (see [FUSION.md](../FUSION.md)).

| Group | State | What |
|---|---|---|
| `Trackpad mod` (v1) | suppressed | Bolt-on wing beside the inner wall. Works, judged ugly |
| `Trackpad mod v2` | **active**, milestone **v2 final** | Toucan2 style: pad at 30°, case bulge + one pod replacing the controller cover. Doesn't fit the sockets |
| `Trackpad mod v3` | planned | Index-aligned pad over the nano |

### v2 at a glance

- 🎯 Pad centre (142.3, −6.2), rotated 30° = the inner thumb key angle. Tile reaches 39.4 mm past the inner wall
- 🧭 Build path: reprinted right case with the bulge + one **Trackpad Pod** (replaces the stock cover)
  - The PCB drops in from above and the pad reaches over it → the part above the PCB must come off
- 🔩 One hidden M2×14 countersunk screw from below at S2 (stock countersink) into a pod insert. S1 standoff → M2 nut
- 🧱 Master sketch `Pad Frame` (offset constraints from the rounded pad outline); every v2 sketch projects from it
- 🎚️ Params: `pad_angle` 30° · `pad_x` 142.3 · `pad_y` −6.2 · `touch_height` = `keycap_height − bezel_step` (8.0) · `bezel_step` 0.5 · `bezel_width` 2.5 · `skin_thickness` 0.9 · `pad_clearance` 0.3 · `pad_thickness` 1.2 · `pad_preload` 0.1 · `lip_width` 1.15 · `ledge_width` 2

## 🔜 v3 plan (experiment)

- 🎯 Pad at **0°** (aligned with the index column), floating over the nano, just above the inner thumb key
- 📐 Long side along x (keeps the pad's components off the nano)
  - Centre ≈ (149.6, 5.9) · tile x 125.1–174.0, y −17.0–28.9
  - 1.9 mm from the index keycaps, 1.6 mm from the inner thumb keycap
- 📊 vs v2: **35.4 mm** from the index home key (v2: 45.6) · **25.6 mm** past the inner wall (v2: 39.4) · 40.1 mm from the inner thumb key (v2: 34.8)
- 🧱 Height stack (above the PCB): pins 6.6 + 2.0 = 8.6 → + pad 1.2 → + skin 0.9 → **touch 10.7** (Lamé home row 10.42)
  - Flush options: `nano_pin_above_rim` 1.7, or skin 0.6, or a measured thinner pad
- 🧢 One flat-top pod covering pad + nano → one upside-down print. Wires are short (pad over the nano)
- 🧪 Test prints (own components, Flo exports to Bambu)
  - `TEST v3 Reach Mockup`: v3 shape at the real touch height, rests on the current case rim, feet to the desk
  - `TEST Pin Gauge`: separate go/no-go bridges (2.2 / 2.0 / 1.8 / 1.6 / 1.4). The smallest one that sits flat on the rim wins
- ⚠️ Risks to check: block-on-top look (raise the bulge walls to meet it), a ~4 mm wall beside the inner index keys, thumb reach

## ✅ Checks every version must pass

- Suppress the version's group → stock right case, **45.482 cm³**, then unsuppress, all healthy
- Interference clean between case, pod, pad, PCB, nano, keycaps, switches (allowing for any intended preload)
- PCB drop-in path: the PCB lifted 0.05–10 mm never touches the case
- USB-C plug envelope (12.35 × 6.5 max overmold) + switch lever corridor: 0 overlap
- Param sweep: each user param ± a step rebuilds clean, every sketch fully constrained
