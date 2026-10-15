# 📜 Trackpad log

> Decisions on the Chocofi TPS43 trackpad mod. Newest first. Current state: [TRACKPAD.md](TRACKPAD.md).

---

## 2026-10-15 -- v3 spike: index-aligned pad over the socketed nano

**Context**: v2 doesn't fit the socketed nano and felt far. Spike v3 as its own timeline group, then stop for print feedback.

**Decision**:
- Pad at 0° over the nano, centre (149.6, 5.9), touch at rim + pins + pad + skin = **10.7** (+0.28 over the Lamé home row)
- One flat-top **Trackpad Pod v3**, printed upside down without supports. The case grows a rim-high bulge with a cavity for the pad's components
- The pad rests on a 2 mm case ledge, a rib on the stock inner wall, and the nano pins
- **Fixing**: 2 × M2 from below through the bulge into pod inserts, on a 7 mm outboard frame. S2 sits under the pad edge, and S1 would need a lobe toward the thumb keys
- `keycap_height` = 10.42 + `keycap_height_tall` = 13.7; its v1/v2 users frozen to literals
- The TRRS opening is closed (wireless build)

**Not chosen** (agent's call during the spike, open for review):
- Screwing the pod at S1: needs a pod lobe toward the thumb cluster, close to the "ear" look Flo disliked in v2

**Rejected**: a pin gauge as one stepped bridge, since it lifts at the first contact (Flo's catch) → 5 separate gauges

**Found**:
- The pad's index-side edge has no support: the right pin row sits 0.45 outside it. Needs adhesive, foam or a standoff at S2
- The tall Lamé index keys stand 3.0 above the pod, 1.9 mm away
- `saveMilestone` flags no longer stick (v12 "v2 final", v13, v14 "M9 - v3 spike" all lost theirs within ~1 min). Only M0–M4 are milestones. Cause unknown (5-milestone cap on Personal?)

**Verified**:
- Interference (pins, USB-C, keys, PCB) clean
- Raised USB-C plug + switch corridor clear; PCB drop-in clear
- 39 param variants clean
- Pod has one up-facing face
- TEST parts sit on the stock case; gauges behave go/no-go
- v2-only still rebuilds to 55.809 / 3.549

**Outcome**: (after the reach + pin test prints)

---

## 2026-10-15 -- v2 review: printability + socketed nano → v3 experiment

**Context**: Flo loved v2's look. Two problems surfaced in review.
- 🖨️ The pod printed right side up needs support under the whole part and under the 0.9 mm skin (sag → air gap → weak sensing)
- 📏 The real nano is socketed with a battery underneath. Its pin tips stand 1.6–1.9 above the rim, so v2's pad (back at 5.9 above the PCB) and pod (underside 6.6) both clash
- ✋ v2's pad also felt a bit far for the hand

**Decision**:
- Pod = flat top, printed **upside down, no supports**. The bed texture is the touch surface for now; ironing can come back later
- One param `nano_pin_above_rim` = 2.0. No separate clearance param
- Everything is measured from the case rim
- Try **v3** as a new timeline group: pad at 0°, over the nano, flush with the Lamé home-row keys (≈10.42 above the PCB). Tall Lamé keys make a higher pad OK

**Rejected**:
- Sliding v2 7 mm off the nano: the pad gets even further away (52.6 mm from the index home key) and needs a separate raised controller cap
- Raising v2 over the pins: as tall as v3 but further away

**Corrected**: the first pin measurement (3 mm) was a mismeasure. PCB-based readings disagree (6.52–6.9 to the rim) because heat-set inserts bulged the case

---

## 2026-10-15 -- v2: Toucan2-style pod (milestone "v2 final")

**Context**: v1 worked but looked like a box bolted on. Target: beekeeb's Toucan2. Pad between the index column and the inner thumb key, angled like the thumb key, with the case bulging to hold it.

**Decision**: reprinted right case with the bulge + one **Trackpad Pod** replacing the stock controller cover
- Pad at 30° (the inner thumb key's angle), centre (142.3, −6.2)
- The pod sits on the stock rim (6.6) all round. The case's R1 top fillet turns the seam into a shadow line
- One hidden M2 screw from below through the stock S2 countersink. The lip in a case groove locates it
- Pad face up on a case ledge, chips on the outboard half over a 12 mm hollow

**Why the mix**: the PCB drops in from above and the pad reaches over it → the deck must come off. The pad hangs ~40 mm past the stock wall → the case must grow walls and a floor.

**Look rounds** (vs Toucan2 photos 4, 6, 12):
1. Deck flush at 8.5 → no tile hierarchy
2. Raised bezel ring (+0.5), cover stepped down → sharp inside junction
3. R3 junction fillers on case + pod → the corner wrap read as an "ear"
4. Cover stops at the stock cover edge with an R6 corner, case rim visible → integrated

**Found**: the power switch is at the **top edge beside USB-C**, not in the inner-wall notch. That notch is the unused TRRS opening, reused as the wire pass

**Verified**: 20 param variants, interference, PCB drop-in, USB-C + switch envelopes (0 overlap, identical to stock), suppress = 45.482 cm³

---

## 2026-10-15 -- v1: bolt-on wing (M1–M4)

**Decision**: a printed wing bolted to the case's inner wall, beside the thumb cluster, standing on the desk
- Pad from below into a pocket under a 0.9 mm ironed skin, held by a screwed back cover with a presser ring
- Case mod: 2 M2 insert holes + a wire slot. All in one group → suppress = stock case

**Outcome**: works, but Flo judged it "absolutely ugly" (tall white brick). Kept, suppressed

---

## 2026-10-14 -- Case, hand and overlay

**Decision**:
- **02 original Massive case** (the printed one, M2 heat-set inserts). 03 M3 remix dropped: the PCB only has M2 holes
- **Right half** (central): simplest firmware, no split input forwarding. Costs battery on the busier half
- **Overlay = an ironed printed skin** (~0.9 mm) over the TPS43-201A. Flo preferred ironed over bed side by finger test
  - Fallbacks: matte PET film (a DIY 201B), then 1 mm acrylic/PC/glass

---

## 2026-10-14 -- Pins verified

**Decision**: SDA/SCL on **D8/D9** (`&i2c1`), RDY on **P1.02**, NRST on **P1.07**, VDD on VCC

**Verified** on the beekeeb `power-switch` PCB (the wireless kit Flo owns): D8, D9, D10, D16 pads have no tracks or vias. The wired main-branch PCB agrees

**Rejected**: D0 (routed to the TRRS data pad)
