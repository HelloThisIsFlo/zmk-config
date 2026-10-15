# 🖲️ Chocofi trackpad (TPS43)

An Azoteq **TPS43-201A** trackpad (43.3 × 40.3 mm, IQS572, I²C) built into the **right** half (central) of the Chocofi, in the **02 Massive** case.

## 📍 Status (15 Oct 2026)

- 🧪 **v3 spike built** (active in Fusion): pad aligned with the index column, over the socketed nano (see 🆕 v3 at a glance)
  - ⏳ **Waiting on Flo's test prints**: `TEST v3 Reach Mockup` (reach) and `TEST Pin Gauge` (pin height). No polishing before that feedback
- 🗄️ **v2** (Toucan2 style) is shelved: it doesn't fit the socketed nano (see 📌)
- ⏳ Not started: buying parts, firmware (blocked on the ZMK fork rebase)

## 📌 Hard constraints

- 📏 **Socketed nice!nano + battery underneath** (sockets aren't in the Fusion REF)
  - Pin tips stand **1.6–1.9 mm above the case rim**, already trimmed. 2 pins can lose ~0.2 more
  - User param **`nano_pin_above_rim` = 2.0**, the only pin knob (it includes any air gap)
  - The real nano board is ~flush with the rim. The stock controller cover doesn't fit either
- ⌨️ **KLP Lamé keycaps**, two heights above the PCB (user params)
  - **Home row (low) `keycap_height` = 10.42** → the touch-surface target
  - Top + bottom rows (high) `keycap_height_tall` = 13.7
  - Thumbs: not measured, modelled at `keycap_height`
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
- 📟 **Nano**: x 155.19–172.97, y 2.21–35.23. USB-C cut-out x 159.46–168.70 at the top end
  - Header pin rows at x ≈ 156.46 and 171.70, 12 pins each from y ≈ 3.5, 2.54 pitch
  - `REF Controller Right` (z 2.5–3.55) is the unsocketed stock REF. **`REF Nano v3` is the real build**: board top at the rim, pin envelope rim → rim + `nano_pin_above_rim`, mid-mount USB-C centred at rim − 0.525 (top ≈ rim + 1.1)
- 🔌 **Raised USB-C plug** (socketed nano): overmold 12.35 × 6.5 centred x 164.08, z rim − 0.525, from y 35.4. It pokes ~2.7 above the rim, so nothing may cover the top-wall notch beyond y ≈ 35.4
- ⌨️ **Keys** (17.5 × 16.5 keycaps)
  - Inner index column x 184.68: bottom y −6.39 · home 10.61 · top 27.61
  - Thumbs: inner (167.93, −29.78) 30° · middle (188.53, −26.57) 15° · outer (208.58, −23.98) 0°
- 🖲️ **TPS43 back**: components ≤ 0.9 mm (C2 tallest), in a band 6.8–20.3 mm from one 43.3 mm edge, y 5–31 of 40.3
  - Place that band off the nano, over open space, so the pad's flat back can sit right over the pins

## 🧩 Versions in Fusion

Each version is one timeline group. Suppress one, unsuppress another to switch (see [FUSION.md](../FUSION.md)).

| Group | State | Saved as | What |
|---|---|---|---|
| `Trackpad mod` (v1) | suppressed | milestone **M4 - v1 final** (v6) | Bolt-on wing beside the inner wall. Works, judged ugly |
| `Trackpad mod v2` | suppressed | v12, plain version ("v2 final" in the description) | Toucan2 style: pad at 30°, case bulge + one pod replacing the controller cover. Doesn't fit the sockets |
| `Trackpad mod v3` | **active** | v14, plain version ("M9 - v3 spike" in the description) | Index-aligned pad over the socketed nano, one flat-top pod. Spike, waiting on test prints |

- 🏷️ Only M0–M4 (v2–v6) are real milestones. Every later `saveMilestone` reads True for ~1 min, then the flag disappears (see [FUSION.md](../FUSION.md) → Milestones)
- 🧊 `keycap_height` users in v1/v2 are frozen (`wing_height` = 8.5 mm, `touch_height` = 8.5 mm − `bezel_step`, REF Keys v2 d242 = 5.5 mm, d246 = 5 mm), so each version rebuilds as saved
- 🔁 Switch check: all off → case 45.482 cm³ · v2 only → case 55.809 + pod 3.549 · v3 only → case 59.852 + pod 5.046

### v2 at a glance

- 🎯 Pad centre (142.3, −6.2), rotated 30° = the inner thumb key angle. Tile reaches 39.4 mm past the inner wall
- 🧭 Build path: reprinted right case with the bulge + one **Trackpad Pod** (replaces the stock cover)
  - The PCB drops in from above and the pad reaches over it → the part above the PCB must come off
- 🔩 One hidden M2×14 countersunk screw from below at S2 (stock countersink) into a pod insert. S1 standoff → M2 nut
- 🧱 Master sketch `Pad Frame` (offset constraints from the rounded pad outline); every v2 sketch projects from it
- 🎚️ Params: `pad_angle` 30° · `pad_x` 142.3 · `pad_y` −6.2 · `touch_height` = 8.5 mm − `bezel_step` (8.0, frozen) · `bezel_step` 0.5 · `bezel_width` 2.5 · `skin_thickness` 0.9 · `pad_clearance` 0.3 · `pad_thickness` 1.2 · `pad_preload` 0.1 · `lip_width` 1.15 · `ledge_width` 2

## 🆕 v3 at a glance (spike)

Renders: print folder → `trackpad-mod-v3/renders/` (01–04 = v2 vs v3 side by side, 06–07 = sections, 08–11 = TEST parts).

- 🎯 **Pad at 0°**, aligned with the index column, floating over the socketed nano, just above the inner thumb key
  - Centre (`v3_pad_x`, `v3_pad_y`) = (149.6, 5.9), long side along x → the back components sit outboard, off the nano
  - 1.9 mm from the index keycaps, 1.6 mm from the inner thumb keycap
- 📊 **vs v2**: 35.4 mm from the index home key (v2: 45.6) · pod reaches 30.1 mm past the inner wall (v2: 39.4) · 40.1 mm from the inner thumb key (v2: 34.8)
- 🧱 **Height stack** (from the rim, 6.6 above the PCB)

  | Layer | Top above the PCB | Param |
  |---|---|---|
  | Pin tips = pad back | 8.6 | `nano_pin_above_rim` 2.0 |
  | Pad | 9.8 | `pad_thickness` 1.2 |
  | Skin = **touch surface** | **10.7** (rim + 4.1) | `skin_thickness` 0.9 → `v3_touch_height` |

  - `v3_touch_vs_keycap` = **+0.28** above the Lamé home row. The tall index keys (13.7) stand **3.0 above** the pod, 1.9 mm away
  - Flush options: `nano_pin_above_rim` 1.7 (after the gauge), skin 0.6, or a measured thinner pad
- 🧢 **Trackpad Pod v3**: one flat-top part, 53.4 × 51.7 × 4.1 mm (x 120.65–174.05, y −17.05–34.61, z 6.6–10.7), 5.05 cm³
  - Printed **upside down, no supports**: every cut opens downward, so the only up-facing face is the top (checked)
  - Underside: pad pocket (pad + 0.3, up to the 0.9 skin), nano cavity (nano + 0.5, up to the pin envelope), 2 insert holes
  - Outline: `v3_frame` 2.5 around the pocket on the index/thumb sides, `v3_outboard` 7 on the far side (room for the screws), top edge `v3_pod_top_y` 34.61 (stock cover line, clear of the raised USB-C plug)
- 🧱 **Case v3** (59.85 cm³): bulge under the outboard part, rim-high, with a cavity for the pad's components (`v3_floor` 2)
  - Pad support at 8.6: a 2 mm ledge (`v3_ledge`) under the pad edges over the bulge + a rib on the stock inner wall + the nano pins
  - The TRRS opening is closed (bulge + `Case v3 - TRRS Fill`)
- 🔩 **Fixing**: 2 × M2 from below through the bulge (counterbore 4.5 up to z −0.4, so M2 × 10) into heat-set inserts in the pod's outboard frame, at (124.15, `v3_pad_y` ± `v3_screw_dy` 12). S1/S2 aren't used: S2 sits under the pad edge
- 🎚️ **Params** (v3-only = `v3_` prefix): `v3_pad_x` · `v3_pad_y` · `v3_frame` · `v3_outboard` · `v3_pod_top_y` · `v3_ledge` · `v3_nano_clearance` 0.5 · `v3_floor` · `v3_screw_dy` · `v3_touch_height` · `v3_touch_vs_keycap`. Shared: `nano_pin_above_rim`, `pad_*`, `skin_thickness`, `rim_height`, `comp_height`, screw/insert diameters, `keycap_height*`
  - Modelling limit: `v3_ledge − pad_clearance < pad_corner`, or the inward ledge offset collapses
- 🧱 **Master sketch** `v3 Pad Frame`: pad loop + offset rings (pocket +0.3, ledge rim +0.15, ledge −1.7) + component band + pod outline. Every v3 sketch projects from it

### 🧪 Test prints (for the stock case, own components)

- 🖐️ **`TEST v3 Reach Mockup`**: the pod's top at the real touch height (rim + 4.1)
  - Its plate rests on the stock inner-wall rim, the outboard block stands on the desk; a nano cavity clears the pins
  - A 0.3 mm groove marks the pad's edge
  - Print upside down, no supports, 2 walls, ~10 % infill (34.4 cm³ solid)
  - Remove the right nice!view if fitted
  - Test: reach to the pad's far corners with the thumb on the inner thumb key, and how the 3 mm step to the tall index keys feels
- 📏 **`TEST Pin Gauge`**: 5 separate bodies (2.2 / 2.0 / 1.8 / 1.6 / 1.4), number debossed in the top
  - L-shaped feet rest on the inner-wall + top-wall rims; two ribs hang over the pin rows at rim + the gauge value; everything else is relieved 3.5 deep (clears the USB-C receptacle)
  - Print each upside down (number on the bed), no supports
  - Use: marker on the pin tips → press the gauge at its top-left corner. Rocks or shows marker = pins too tall. **The smallest gauge that sits flat and clean = `nano_pin_above_rim`**

### ⚠️ Open after the spike

- 🧷 **The pad's index-side edge is unsupported**: the right pin row (x 171.70) sits just outside the pad (edge 171.25), so only the wall rib + the left pin row hold it
  - The pad could sag off the skin (air gap = weaker sensing)
  - Options: stick it to the skin (its 3M 468 adhesive), a foam strip on the nano, or a standoff at S2
- ⚡ Insulate the pad's back over the nano (Kapton): the pins touch it by design
- 🧱 Look: the 4.1 mm block on the rim and the 3 mm step to the tall index keys. Judge on the mockup before any styling (fillets, chamfers, raised bulge walls)
- 🖐️ Thumb reach to the pad's far corner (40.1 mm from the inner thumb key)

## ✅ Checks every version must pass

- Suppress the version's group → stock right case, **45.482 cm³**, then unsuppress, all healthy
- Interference clean between case, pod, pad, PCB, nano (board, pin envelope, USB-C), keycaps, switches (allowing for any intended preload)
- PCB drop-in path: the PCB lifted 0.05–10 mm never touches the case
- USB-C plug envelope (12.35 × 6.5 max overmold, raised with the socketed nano) + switch lever corridor: 0 overlap
- Param sweep: each user param ± a step rebuilds clean, every sketch fully constrained
- Pod print orientation: its only up-facing face is the top
- TEST parts against the **stock** case (timeline marker just before the version's first case feature): touching, 0 overlap
- v3 results (15 Oct): all of the above pass. 39 param variants clean. Gauges vs a 2.0 pin envelope: 2.2 and 2.0 clear, 1.8 / 1.6 / 1.4 hit the pins (as designed)
