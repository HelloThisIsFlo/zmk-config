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

## 💾 Milestones

- `doc.saveMilestone(name, desc)` can return True yet save only a **plain version**
- Always verify:
  ```python
  df = app.data.findFileById(doc.dataFile.id)
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

## 🧱 Features

- 3D fillets meeting stock fillets/chamfers fail (`ASM_BL_END_TOO_CMPLX`)
  - → draw the concave fillet as a tangent arc in a sketch and join the filler prism
- Chamfer/fillet with tangent chain = True spreads round the whole loop (it once re-chamfered the entire case bottom) → chain = False + explicit edges
- Convex-edge test: step off the edge along the other face's normal, then `body.pointContainment` → outside = convex

## 🔍 Checks

- 💥 **Interference**: `design.analyzeInterference` returned None → intersect `TemporaryBRepManager` copies instead
  - Coincident faces can fail → nudge one copy 0.001 cm and retry
- 📦 **Envelopes** (USB plug, finger corridor, pin tips): `tbm.createBox(OrientedBoundingBox3D)` and intersect with the bodies
- 🔁 **Param sweep**: set `userParameters.itemByName(n).expression`, check timeline health + `sketch.isFullyConstrained` + body count, restore

## 📸 Renders

- Orthographic only (perspective via the API misbehaves). `viewExtents` ≈ visible height in cm, set **after** eye/target
- `vp.visualStyle = ShadedVisualStyle`, then `vp.saveAsImageFile(path, 2000, 1400)`
- Sections: `design.analyses.sectionAnalyses.createInput(root.yZConstructionPlane, 0)` + `inp.transform` (no timeline item). Delete them afterwards

## ⚠️ MCP quirks

- An open dialog in Fusion makes every MCP call time out → check the Fusion window
- Non-ASCII in script strings gets garbled → ASCII names only
- Occurrence timeline items show as " Name:1" and can't be renamed
- Groups can't nest. Regroup: `group.deleteMe(False)` then `tl.timelineGroups.add(start, end)`. `isGroup` items report health state 5
