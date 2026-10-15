# 📜 Trackpad log

> Decisions on the Chocofi TPS43 trackpad mod. Newest first. Current state: [TRACKPAD.md](TRACKPAD.md).

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
