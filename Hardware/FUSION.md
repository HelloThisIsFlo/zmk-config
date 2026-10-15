# 🧩 Fusion

How we work in Fusion, and what the API (via the Fusion MCP) gets wrong.

## 🌿 Versions = timeline groups (our "git")

Personal licence: no branches, no Configurations, max 10 editable documents.

| Git | Fusion |
|---|---|
| commit | save (a new version) |
| tag | **milestone**, checked after saving (see below) |
| branch you can switch | a **timeline group** per version → suppress one, unsuppress another |
| fork | Save As a copy (no merge back) |
| revert / reset | open an old version → **Promote** |

- 🧱 One file per thing that must fit together (case + mods + REF parts). Separate things get their own file and link the case
- 🏷️ A version group must not depend on another version's features, so each one switches cleanly on its own
- 🔤 Timeline item names in plain ASCII
- 🧪 Test prints = their own components (names start with `TEST`), exported to Bambu by Flo
  - Built inside the version's group, **before** its case features, so they can be checked against the stock case (see 🔍)

## 💾 Milestones

- ❌ **`doc.saveMilestone(name, desc)` doesn't stick** (since Oct 2026, this document)
  - It returns True and `isMilestone` reads True for ~1 min. Then the flag is gone and only a plain version remains (v12, v13, v14)
  - Only M0–M4 (v2–v6) survive. Suspected cause: a 5-milestone-per-file cap on the Personal plan (unconfirmed; no file in the project has more than 5)
  - Freeing a slot (unmarking an old milestone) is Flo's call. Marking a version by hand in the Data Panel is the other test
  - Fallback tag: put the milestone name at the start of the version description
- Verify **after ≥ 2 min**, from the cloud:
  ```python
  df = app.data.findFileById(doc.dataFile.id); df.refresh(None)
  [(v.versionNumber, v.isMilestone, v.milestone.name if v.milestone else None) for v in df.versions]
  ```

## 🪞 Mirrored right half

- `04 Right Half - Mirror` copies case, cover, PCB and controller into `... Right` components
- A mirrored occurrence's native coordinates are mirrored **and** z-flipped vs the assembly
  - Pick edges on `occ.bRepBodies` (proxies), then pass `edge.nativeObject` to the component's fillet/chamfer
- 📦 **STL export**: hide every other occurrence and export the root. Exporting the mirrored body alone gives an upside-down STL

## ✏️ Sketches

- Offset constraints (`createOffsetInput` + `addOffset2`, expression-driven, positive = outward) keep **sharp** corners
  - → build the base loop already rounded (lines + `addFillet` arcs + radial dims) and offset that, so arcs grow concentrically
- Expressions come back normalized with spaces → strip spaces before matching
- `addByThreePoints` may swap arc start/end → match endpoints by distance. `addByCenterStartSweep` is reliable
- Keep every sketch fully constrained. A master sketch that the others project from keeps parts from drifting apart
  - Put **every offset ring in the master**. An offset constraint on projected curves in a derived sketch breaks for good once the master moves
  - An inward offset deeper than the corner radius collapses the arcs (v3: `v3_ledge − pad_clearance < pad_corner`)
- Fixed geometry counts as constrained only with its endpoints fixed too (`line.startSketchPoint.isFixed = True`, same for the end)
- Sketch text: fix its box (`text.definition.rectangleLines`, endpoints included)
- Root sketches can drive extrudes in any component, the mirrored case included: `comp.features.extrudeFeatures` + `participantBodies`
- 🎯 Pick profiles by **bounding box**, not centroid. An L-shaped leftover profile can have its centroid inside the region you want to cut (it ate the pin gauges' feet once)

## 🧱 Features

- 3D fillets meeting stock fillets/chamfers fail (`ASM_BL_END_TOO_CMPLX`)
  - → draw the concave fillet as a tangent arc in a sketch and join the filler prism
- Chamfer/fillet with tangent chain = True spreads round the whole loop (it once re-chamfered the entire case bottom) → chain = False + explicit edges
- Convex-edge test: step off the edge along the other face's normal, then `body.pointContainment` → outside = convex

## 🔍 Checks

- 💥 **Interference**: `design.analyzeInterference` returned None → intersect `TemporaryBRepManager` copies instead
  - Coincident faces can fail → nudge one copy 0.001 cm and retry
- 📦 **Envelopes** (USB plug, finger corridor, pin tips): `tbm.createBox(OrientedBoundingBox3D)` and intersect with the bodies
- 🔁 **Param sweep**: set `userParameters.itemByName(n).expression`, check timeline health + `sketch.isFullyConstrained` + body count, restore. Then check the restore matches the baseline volumes (a feature can stay broken after the restore)
- 🧪 **Against the stock case**: `timeline.markerPosition` = index of the version's first case feature, check, `timeline.moveToEnd()`
- 🖨️ **Upside-down print check**: list the planar faces with normal +z. Anything other than the top = an overhang

## 📸 Renders

- Orthographic only (perspective via the API misbehaves). `viewExtents` ≈ visible height in cm, set **after** eye/target
- `vp.visualStyle = ShadedVisualStyle`, then `vp.saveAsImageFile(path, 2000, 1400)`
- Sections: `design.analyses.sectionAnalyses.createInput(root.yZConstructionPlane, 0)` + `inp.transform` (no timeline item), `isHatchShown = False`, view with a slight tilt (0.25 up) + `adsk.doEvents()`. Delete them afterwards
- New bodies get "Steel - Satin" → set matte appearances (`Plastic - Matte (Black)` = case/pod, `(White)` = keycaps). Low grazing views still show reflections on matte black; it isn't transparency

## ⚠️ MCP quirks

- An open dialog in Fusion makes every MCP call time out → check the Fusion window
- Non-ASCII in script strings gets garbled → ASCII names only
- Occurrence timeline items show as " Name:1" and can't be renamed
- Groups can't nest. Regroup: `group.deleteMe(False)` then `tl.timelineGroups.add(start, end)`. `isGroup` items report health state 5
- A **collapsed** group hides its items from `timeline.item(i)` → set `group.isCollapsed = False` before indexing, collapse again after
- A script that raises **rolls back everything it did**, so a failure leaves no half-built state
- `timelineObject.rollTo()` fails on a broken feature ("Associated feature is invalid") → set `timeline.markerPosition`. A feature created at the marker inside a group joins that group
