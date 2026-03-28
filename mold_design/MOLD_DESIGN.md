# EpiScreen Semi-Dry EEG Electrode Mold Design

## Overview

Two-part resin 3D-printable mold for silicone casting of a semi-dry EEG electrode.
Designed for SLA/DLP resin printing. Minimum feature size: 0.3mm.

## Files

| File | Description |
|------|-------------|
| `episcreen_mold_parameters.scad` | Shared parametric dimensions |
| `episcreen_mold_bottom.scad` | Bottom mold piece (OpenSCAD source) |
| `episcreen_mold_top.scad` | Top mold piece (OpenSCAD source) |
| `episcreen_mold_cross_section.scad` | Assembly cross-section view |
| `episcreen_mold_bottom.stl` | Bottom mold (printable STL) |
| `episcreen_mold_top.stl` | Top mold (printable STL) |

## Cross-Section Diagram

```
                    POUR HOLE (6mm)
                        │
            VENT ──►  ┌─┴─┐  ◄── VENT
                    ┌──┤   ├──┐
                    │  │   │  │ ◄── TOP MOLD LID (3.5mm thick)
     ───────────────┤  └───┘  ├───────────────
    │               │         │               │
    │  CABLE EXIT   │  CAVITY │  RESERVOIR    │
    │  CHANNEL ──►  │ (top    │  FILL PORT    │
    │  ┌──┐         │  half)  │  (2mm dia)    │
    │  │  │         │         │               │
    │  │  │    ┌────┴────┐    │               │  ◄── TOP MOLD
    │  │  │    │RESERVOIR│    │               │      PIECE
    │  │  │    │  RING   │    │               │
    │  │  │    │PROTRUSN │    │               │
    │  │  │    └────┬────┘    │               │
    │  │  │         │         │               │
    │  └──┘     ●   │   ●     │               │  ◄── ALIGNMENT
  ══╪══════════╪════╪════╪════╪═══════════════╪══    PINS (4x)
    │  ┌──┐    ○    │    ○    │               │  ◄── PIN HOLES
    │  │  │         │         │               │
    │  │  │    ┌────┴────┐    │               │
    │  │  │    │ FR-4    │    │               │  ◄── BOTTOM MOLD
    │  │  │    │ SEAT    │    │               │      PIECE
    │  │  │    │ LEDGE   │    │               │
    │  │  │    ├─────────┤    │               │
    │  └──┘    │  FR-4   │    │               │
    │          │  DISK   │    │               │
    │          └─────────┘    │               │
    │               │         │               │
    │          ┌────┴────┐    │               │
    │    ┌─────┤ BOTTOM  ├────┤               │
    │    │ANNUL│ CAVITY  │ANNL│               │
    │    │RING │  12mm   │RING│               │
    │    │     │┌───────┐│    │               │
    │    │     ││SPIRAL ││    │               │
    │    │     ││PLATFRM││    │               │
    │    └─────┤└───────┘├────┘               │
    │          │ TEXTURE │                    │
     ─────────────────────────────────────────
                    │
               BASE PLATE (5mm)

    ◄───────── 32mm outer diameter ──────────►
           ◄── 24mm electrode dia ──►
```

## Key Dimensions

| Parameter | Value |
|-----------|-------|
| Mold outer diameter | 32 mm |
| Electrode outer diameter | 24 mm |
| Electrode height | 10 mm |
| Base plate thickness | 5 mm |
| Parting line | 5 mm from cavity bottom |
| Wall thickness (min) | 1.5 mm |
| Mating surface clearance | 0.3 mm |
| Draft angle | 2.5° |
| Edge fillets | 0.2 mm |

## Assembly & Casting Instructions

1. **Print** both mold pieces in resin (SLA/DLP)
2. **Post-cure** and clean mold pieces
3. **Place copper spiral** on the spiral exposure platform (8mm dia)
4. **Insert steel wires** (0.5mm) through the 3 microchannel guide holes
5. **Place FR-4 disk** (19mm dia, 1.6mm thick) on the seat ledge
6. **Align and close** the mold using the 4 alignment pins
7. **Pour silicone** through the 6mm center pour hole
8. **Cure** silicone per manufacturer instructions
9. **Remove steel wires** to create microchannels
10. **Separate mold** halves and demold electrode
11. **Fill reservoir** through the 2mm fill port if needed

## Modifying Dimensions

All dimensions are parametrized in `episcreen_mold_parameters.scad`.
Edit values there and re-export STLs:

```bash
openscad -o episcreen_mold_bottom.stl episcreen_mold_bottom.scad
openscad -o episcreen_mold_top.stl episcreen_mold_top.scad
```
