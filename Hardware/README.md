# 🛠️ Hardware

The physical side of the keyboards: cases, mods, CAD. Firmware and bindings live in `config/` and `Design/`.

## 🗺️ Map

| Doc | What's in it |
|---|---|
| [Chocofi/TRACKPAD.md](Chocofi/TRACKPAD.md) | 🖲️ TPS43 trackpad mod: status, hard constraints, measurements, model facts, versions |
| [Chocofi/TRACKPAD_LOG.md](Chocofi/TRACKPAD_LOG.md) | 📜 Trackpad decisions, newest first |
| [FUSION.md](FUSION.md) | 🧩 Fusion working conventions + API/MCP gotchas |
| [scripts/](scripts/) | 🐍 `stlcheck.py` (STL size/volume), `pad_placement.py` (pad position study) |

## 📍 Where things live

- 🖥️ **Fusion**: Default Project → `Chocofi` → `Chocofi Massive Case`, the single source of truth for the case and every mod
- 🖨️ **Print files**: Synology Drive → `99 Working Files/3D Printing/Keyboard/Chocofi/Cases/02 Massive Chocofi - PR814712/`
  - `trackpad-mod/` = v1, `trackpad-mod-v2/` = v2. Each has STLs, renders and a README (print + assembly)
- 📓 **Project tracker**: Notion → AI Conducting → "🖲️ Chocofi Trackpad Wing (TPS43)" (status, next action, shopping)
- 🔌 **PCB source**: [beekeeb/chocofi](https://github.com/beekeeb/chocofi), branch `power-switch` (the wireless kit PCB)

## 🧭 Doc rules

- `*.md` = current truth, rewritten as things change. `*_LOG.md` = append-only, newest first
- 📏 Measure physical heights **from the case rim**, never from the PCB (see TRACKPAD.md → Measurements)
