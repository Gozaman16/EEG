# EpiScreen EEG Electrode System

Semi-dry EEG electrode system with resin-printable silicone casting molds.
Designed for ISEF 2026.

## Components

| Component | File(s) | Description |
|-----------|---------|-------------|
| EpiScreen electrode mold | `stl/episcreen_mold_bottom.stl` / `_top.stl` | 24 mm standard electrode, 2-part mold |
| NeoGuard neonatal mold | `stl/neoguard_mold_bottom.stl` / `_top.stl` | 15 mm neonatal electrode, 2-part mold |
| HairSite hair-contact mold | `stl/hairsite_mold_bottom.stl` / `_top.stl` | 24 mm electrode + 7 penetrating pins |
| ImpactGuard helmet adapter | `stl/impactguard_helmet_adapter.stl` | Snap-fit mount for sports helmets |
| Adult headband mount | `stl/headband_mount_adult.stl` | 22 mm elastic band clip, 24 mm electrode |
| Neonatal headband mount | `stl/headband_mount_neonatal.stl` | 16 mm silicone band clip, 15 mm electrode |

## Assembly Renders (300 DPI, ISEF-ready)

| Render | File | Description |
|--------|------|-------------|
| Family photo | `renders/assembly_family.png` | All components side by side with scale bar & Turkish Lira coin reference |
| Exploded view | `renders/assembly_exploded.png` | All electrode layers separated vertically with assembly arrows |
| Cross-section | `renders/assembly_cross_section.png` | Internal features with full dimensioning and material callouts |

## Parametric Source (OpenSCAD)

All geometry is parametric via `scad/params.scad`. Edit dimensions there and
re-run `scripts/generate_stl.py` (uses `trimesh` + `manifold3d`) to regenerate STLs,
or open `.scad` files in OpenSCAD 2021+ for interactive editing.

```
scad/
  params.scad                 ← all dimensions in one place
  episcreen_mold_bottom.scad
  episcreen_mold_top.scad
  neoguard_mold_bottom.scad
  neoguard_mold_top.scad
  hairsite_mold_bottom.scad
  hairsite_mold_top.scad
  impactguard_helmet_adapter.scad
  headband_mount_adult.scad
  headband_mount_neonatal.scad
  assembly_family.scad
  assembly_exploded.scad
  assembly_cross_section.scad
```

## Regenerating outputs

```bash
# Install deps
pip install trimesh manifold3d numpy matplotlib pillow

# Generate all STL files
python3 scripts/generate_stl.py

# Render publication PNGs (300 DPI)
python3 scripts/render_family.py
python3 scripts/render_exploded.py
python3 scripts/render_cross_section.py
```

## Electrode Design Specs

### EpiScreen (24 mm)
- Outer diameter: 24 mm, total height: 10 mm
- FR-4 disk seat at 3 mm, reservoir ring ID/OD 13/19 mm × 1.5 mm
- 3× microchannel guide holes (Ø 0.6 mm, 37.5° angle)
- Spiral exposure platform: Ø 8 mm × 0.8 mm
- Cable exit: 3–4 mm wide funnel notch
- Mold: 32 mm OD, 4× Ø 2 mm alignment pins, 2× Ø 1 mm vent holes

### NeoGuard (15 mm)
- Outer diameter: 15 mm, total height: 8 mm
- FR-4 seat at 2.5 mm, reservoir ring ID/OD 8.5/12 mm × 1.2 mm
- Mold: 22 mm OD

### HairSite (24 mm + pins)
- Same body as EpiScreen, height 12 mm
- 7 penetrating pins: 1 centre + 6 on Ø 12 mm circle
- Pin diameter: 1.2 mm, length: 8 mm

## Print Settings (SLA/DLP)
- Layer height: 0.05 mm
- Resin: standard or flexible resin (depends on electrode flexibility needed)
- Supports: on mold exterior only — never inside cavity
- Minimum feature: 0.3 mm (microchannel holes, texture rings)
