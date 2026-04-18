// ═════════════════════════════════════════════════════════════
// NeoGuard 15 mm Neonatal EEG Electrode — BOTTOM MOLD PIECE
// ─────────────────────────────────────────────────────────────
// SLA PRINT:
//   Bottom mold: natural orientation (cavity up)
//   Top mold:    FLIPPED (pins up — self-supporting)
// POST-PROCESS:
//   1. IPA wash 2× (5 min each)
//   2. UV post-cure 2 h + 60 °C
//   3. Air dry 24 h
//   4. Clear acrylic spray 2–3 thin coats, 15 min between
//      (barrier against silicone cure inhibition)
// CAST:
//   Silicone: Ecoflex 00-50 (platinum-cure, Shore 00-50)
//   Sequential pour: bottom first (4 h @ 25 °C or 1 h @ 45 °C)
//   Between silicone layers: 1 thin coat acrylic spray, 15 min
//   NEVER use vaseline — inhibits platinum cure
// ═════════════════════════════════════════════════════════════

include <params.scad>

neoguard_bottom();

module neoguard_bottom() {
  mold_h = NG_BOT_H + WALL;
  difference() {
    // Outer body
    cylinder(d = NG_MOLD_OD, h = mold_h, center = false);

    // Main electrode cavity
    translate([0, 0, WALL - 0.01])
      cylinder(d = NG_OD + CLEARANCE, h = NG_BOT_H + 0.02, center = false);

    // Pillar texture on the skin-contact floor
    translate([0, 0, WALL])
      hex_pillar_texture(NG_FUN_BOT_D/2 + 1.5, -PILLAR_H);

    // Alignment pin holes (3×, avoid cable exits at 0° and 180°)
    for (a = NG_PIN_ANGLES)
      rotate([0, 0, a])
        translate([(NG_MOLD_OD/2 - WALL - NG_HOLE_D/2 - 0.5), 0,
                   mold_h - NG_HOLE_DEPTH])
          alignment_hole(NG_HOLE_D, NG_HOLE_DEPTH + 0.1);

    // Cable exit tunnels (B-strategy — two opposite round through-holes)
    ng_cable_exit_bottom();

    // Pry slots at parting line
    pry_slots(NG_MOLD_OD, mold_h);

    // Flash trap
    flash_trap(NG_MOLD_OD, mold_h);

    // Silicone interlock voids (perimeter lip, anti-rotation key,
    // service notch tab) in the cavity ceiling
    translate([0, 0, mold_h - SIL_LIP_H])
      interlock_lower_voids(NG_OD);
  }

  // ── Positive features inside cavity ───────────────────────
  // Funnel protrusion
  translate([0, 0, WALL - 0.01])
    funnel_void(NG_FUN_TOP_D, NG_FUN_BOT_D, NG_FUN_H);

  // Sensing tip
  translate([0, 0, WALL - NG_SENSE_PROTRUDE])
    cylinder(d = NG_SENSE_TIP_D, h = NG_FUN_H + NG_SENSE_PROTRUDE + 0.01);

  // Impedance ring recess — NOTE: sized generously (≥0.3 mm buffer)
  translate([0, 0, WALL])
    impedance_ring_void(NG_FUN_TOP_D, NG_FUN_BOT_D, NG_FUN_H,
                        NG_IMP_RING_Z_FRAC, NG_IMP_RING_W, NG_IMP_RING_T);

  // FR-4 seat shelf — FR-4 top face flush with top of lower silicone
  translate([0, 0, WALL + NG_FR4_Z])
    difference() {
      cylinder(d = NG_FR4_D + 2*NG_FR4_LIP, h = NG_FR4_T + 0.01);
      translate([0, 0, -0.05])
        cylinder(d = NG_FR4_D + CLEARANCE, h = NG_FR4_T + 0.1);
    }
}

// ─────────────────────────────────────────────────────────────
// Cable exit (B-strategy): two independent circular through-tunnels
// at 0° and 180°, each 1.5 mm diameter, running radially from cavity
// to outside, Z-centred at FR-4 level.  Top of tunnel ≤ NG_BOT_H-0.3.
// Separate holes — mechanical balance on the 15 mm body.
// ─────────────────────────────────────────────────────────────
module ng_cable_exit_bottom() {
  z_top_max = NG_BOT_H - 0.3;
  z_centre  = WALL + min(NG_FR4_Z + NG_FR4_T/2,
                         z_top_max - NG_CABLE_HOLE_D/2);
  x_start   = NG_OD/2 - 0.2;
  for (a = [0, 180])
    rotate([0, 0, a])
      translate([x_start, 0, z_centre])
        rotate([0, 90, 0])
          cylinder(d = NG_CABLE_HOLE_D, h = NG_CABLE_RAD_L + 0.5,
                   center = false);
}
