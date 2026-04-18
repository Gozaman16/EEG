# EEG Electrode Mold Design — EpiScreen / NeoGuard / HairSite

Two-part SLA-resin 3D-printable molds for casting semi-dry EEG electrodes
in Ecoflex 00-50 silicone. Three variants share a common architecture.

| Variant     | Target use          | Electrode OD | Pins                                    |
|-------------|---------------------|--------------|-----------------------------------------|
| EpiScreen   | Adult               | 24 mm        | —                                       |
| NeoGuard    | Neonatal            | 15 mm        | —                                       |
| HairSite    | Adult, through hair | 24 mm        | 7 (1 centre + 6 on 6 mm radius)         |

All mold SCAD sources live in `scad/`. This directory (`mold_design/`)
contains symlinks to those sources plus rendered STL / PNG assets for
non-mold parts (headband, impactguard, band guide).

## Files

| File | Description |
|------|-------------|
| `../scad/params.scad`                 | Shared parameters + utility modules |
| `../scad/episcreen_mold_bottom.scad`  | EpiScreen bottom mold |
| `../scad/episcreen_mold_top.scad`     | EpiScreen top mold |
| `../scad/neoguard_mold_bottom.scad`   | NeoGuard bottom mold |
| `../scad/neoguard_mold_top.scad`      | NeoGuard top mold |
| `../scad/hairsite_mold_bottom.scad`   | HairSite bottom mold |
| `../scad/hairsite_mold_top.scad`      | HairSite top mold |

## Architecture

Each electrode is cast from **two silicone pours**, separated by a
barrier coat. The result is a **LOWER** silicone piece and an **UPPER**
silicone piece that mechanically interlock but are **separable for
service** (FR-4 swap, cleaning, inspection).

Key design decisions:

- **Funnel IS the reservoir.** A truncated-cone void inside the lower
  silicone holds the electrolyte. No separate reservoir ring.
- **Impedance ring** sits on the inner funnel wall, wetted
  automatically by electrolyte.
- **Lower silicone** owns FR-4, cables, funnel, sensing tip, impedance
  ring. **Upper silicone** is a thin lid with a refill port.
- **When opened, FR-4 stays with the lower half** and is accessible
  from above.

## Cross-Section Diagram

```
 ┌──────────────────────────┐
 │   UPPER SILICONE (lid)   │  ← refill port through this
 ├──────────────────────────┤  ← openable interlock interface
 │        FR-4 card         │  ← sits in recess on lower silicone's upper face
 ├──────────────────────────┤
 │                          │
 │      LOWER SILICONE      │
 │                          │
 │     ╲             ╱      │  ← funnel walls
 │      ╲   ▓▓▓▓▓   ╱       │  ← electrolyte (fills funnel = reservoir)
 │       ╲▓▓▓▓▓▓▓▓▓╱        │
 │        ╲▓▓▓▓▓▓▓╱         │
 │         ╲ ███ ╱          │  ← sensing tip (protrudes 0.1 mm)
 └──────────┴───┴───────────┘
           SKIN
```

## Parameter Table

| Parameter              | EpiScreen | NeoGuard | HairSite  | Notes |
|------------------------|-----------|----------|-----------|-------|
| Electrode OD (mm)      | 24.0      | 15.0     | 24.0      | `*_OD` |
| Electrode height (mm)  | 10.0      | 8.0      | 12.0      | `*_H` |
| Mold OD (mm)           | 32.0      | ~22.0    | 32.0      | = OD + 2·WALL + 4 |
| Bottom mold height     | 5.0       | 4.0      | 6.0       | `*_BOT_H` |
| Top mold height        | 6.5       | 5.5      | 7.5       | `*_TOP_H` |
| Pour hole Ø            | 6.0       | 4.0      | 6.0       | |
| FR-4 Ø × thickness     | 19×1.6    | 12×1.0   | 19×1.6    | flush with top of lower silicone |
| Funnel top Ø (FR-4)    | 10.0      | 6.0      | 10.0      | `*_FUN_TOP_D` |
| Funnel bottom Ø (skin) | 18.0      | 11.0     | 18.0      | `*_FUN_BOT_D` |
| Funnel height          | 3.0       | 2.5      | 3.0       | `*_FUN_H` |
| Sensing tip Ø          | 3.0       | 2.0      | 3.0       | `*_SENSE_TIP_D` |
| Sensing tip protrude   | 0.1       | 0.1      | 0.1       | past funnel bottom rim |
| Impedance ring width   | 1.5       | 1.0      | 1.5       | on inner funnel wall |
| Impedance ring thick   | 0.3       | 0.25     | 0.3       | generous — no "powdered sugar" tolerances |
| Cable strategy         | C (2ch)   | B (2×Ø)  | C (2ch)   | see below |
| Cable channel W × H    | 1.5 × 1.8 | Ø 1.5    | 1.5 × 1.8 | 1 mm cable + 0.5 mm clearance |
| Channel divider W      | 2.0       | —        | 2.0       | silicone divider (C only) |
| Alignment pins (count) | 4         | 3        | 4         | |
| Pin base × tip × h     | 2.5/2.0/2.5 | 2.0/1.5/2.0 | 2.5/2.0/2.5 | conical, self-releasing |
| Hole Ø / depth         | 2.3 / 2.8 | 1.8 / 2.3 | 2.3 / 2.8 | 0.3 mm clearances |
| Pin angles (deg)       | 45,135,225,315 | 90,210,330 | 45,135,225,315 | avoid cable/vent/port |
| Refill port Ø          | 2.0       | 2.0      | 2.0       | over funnel centre |

Global:

| Global parameter | Value | Was  | Why |
|------------------|-------|------|-----|
| `CLEARANCE`      | 0.5   | 0.3  | Ecoflex 00-50 needs more |
| `DRAFT`          | 4°    | 2°   | Softer silicone needs more draft |
| Pillar Ø / h / pitch | 0.5 / 0.4 / 1.0 | — | hex pillar array (Y pattern) replaces concentric rings |

## Full Casting Procedure

1. **Barrier coat:** apply 2–3 thin coats clear acrylic spray to both
   mold halves (15 min between coats). This prevents SLA resin from
   inhibiting platinum-cure silicone. **Do NOT use vaseline** — it
   also inhibits the silicone.
2. **FR-4 + cables:** place FR-4 in the FR-4 recess in the bottom
   mold; thread cables through the cable tunnels; solder/attach to
   pads.
3. **Lower pour:** pour lower silicone (Ecoflex 00-50) into bottom
   mold. Cure **4 h @ 25 °C** or **1 h @ 45 °C**.
4. **Silicone-silicone separator:** apply **one thin coat** of clear
   acrylic spray on the top face of the cured lower silicone.
5. **Close and upper pour:** close top mold onto bottom mold. Pour
   upper silicone through the pour hole. Cure.
6. **Demold:** open molds via pry slots. Demold the electrode. Upper
   and lower silicone halves are separable at their interlock
   interface.

## SLA Post-Processing (per printed mold)

1. IPA wash 2× (5 min each)
2. UV post-cure 2 h + 60 °C
3. Air dry 24 h
4. Clear acrylic spray 2–3 thin coats, 15 min between each (barrier
   against silicone cure inhibition)

### Print orientation

- **Bottom mold:** natural orientation, cavity up.
- **Top mold:** *FLIPPED* — pins pointing up. Conical pins are
  self-supporting in this orientation. Printing with pins pointing
  down will fail (unsupported overhang).

## Rendering STLs

```bash
for f in scad/episcreen_mold_bottom.scad scad/episcreen_mold_top.scad \
         scad/neoguard_mold_bottom.scad  scad/neoguard_mold_top.scad \
         scad/hairsite_mold_bottom.scad  scad/hairsite_mold_top.scad; do
  out="${f%.scad}.stl"
  openscad -o "$out" "$f" || echo "FAILED: $f"
done

# Preview PNGs
for f in scad/*_mold_*.scad; do
  base="${f%.scad}"
  openscad --imgsize=800,800 --autocenter --viewall \
           -o "${base}_view.png" "$f"
done
```

Check manifold integrity with `admesh --no-check <file>.stl` or
MeshLab.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Silicone sticks to mold | Acrylic barrier coat incomplete / missed | Re-spray 2–3 coats, verify full coverage including cavity floor and funnel protrusion |
| Upper and lower silicone fuse together | Between-layer acrylic spray skipped or too heavy | Apply exactly **one thin** coat after lower silicone cures; let it flash off ~15 min before upper pour |
| Cables break or crush | Tunnel height < 1.8 mm or cable > 1 mm | Verify `CABLE_CH_H` ≥ 1.8 mm; insulated cable Ø ≤ 1 mm |
| Mold halves won't separate | Draft too low / clearance too tight | Check `DRAFT = 4`, `CLEARANCE = 0.5`; pry via V-notches at 45° / 135° / 225° / 315° |
| FR-4 drops out of lower silicone | Seat shelf too small or lip missing | Verify FR-4 Ø clearance = 0.5 mm; `EP_FR4_LIP` = 0.2 mm |
| Impedance ring doesn't contact electrolyte | Ring recess too shallow | Increase `EP_IMP_RING_T` or `EP_IMP_RING_W` — err generous |
| Cavity flash on skin side | Flash trap overflowing | Pour slightly less; trap captures small excess only |
| Upper silicone rotates on lower | Anti-rotation key not engaging | Inspect square socket for flash; verify `SIL_KEY_SIZE = 2.0` and clearance = 0.1 mm |

## Modifying Dimensions

All dimensions are parametrized in `../scad/params.scad`. Edit values
there and re-export STLs with the commands above. Follow the coding
style already in the file: uppercase names, 2-space indent inside
modules, section dividers with Unicode box characters, `EP_` /
`NG_` / `HS_` prefixes for variant-specific values.

**Generosity mandate:** when in doubt between two values, pick the
one with more clearance. Physical silicone tolerances, cable routing
realities, and SLA resolution limits all eat margin — generous
dimensions recover it.
