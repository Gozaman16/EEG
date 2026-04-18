// ═════════════════════════════════════════════════════════════
// HairSite 24 mm Hair-Contact EEG Electrode — BOTTOM MOLD PIECE
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
// Same 24 mm body as EpiScreen plus 7 flexible penetration-pin
// cores (1 centre + 6 at 60° on 6 mm radius).  Pins protrude
// through the hair so the sensing tip can reach the scalp.

include <params.scad>

hairsite_bottom();

module hairsite_bottom() {
  mold_h = HS_BOT_H + WALL;
  difference() {
    // Outer body
    cylinder(d = HS_MOLD_OD, h = mold_h, center = false);

    // Main electrode cavity
    translate([0, 0, WALL - 0.01])
      cylinder(d = HS_OD + CLEARANCE, h = HS_BOT_H + 0.02, center = false);

    // Pillar texture on skin-contact floor.  HairSite special case:
    // exclude cylindrical zones around each of the 7 pin positions so
    // texture doesn't interfere with pin cores.
    translate([0, 0, WALL])
      difference() {
        hex_pillar_texture(EP_FUN_BOT_D/2 + 3.0, -PILLAR_H);
        pin_texture_exclusions();
      }

    // Alignment pin holes (4×)
    for (a = PIN_ANGLES)
      rotate([0, 0, a])
        translate([(HS_MOLD_OD/2 - WALL - HOLE_D/2 - 0.5), 0,
                   mold_h - HOLE_DEPTH])
          alignment_hole(HOLE_D, HOLE_DEPTH + 0.1);

    // Cable exit tunnels (C-strategy — same as EpiScreen)
    hs_cable_exit_bottom();

    // Pry slots at parting line
    pry_slots(HS_MOLD_OD, mold_h);

    // Flash trap
    flash_trap(HS_MOLD_OD, mold_h);

    // Silicone interlock voids in cavity ceiling
    translate([0, 0, mold_h - SIL_LIP_H])
      interlock_lower_voids(HS_OD);
  }

  // ── Positive features inside cavity ───────────────────────
  // Funnel protrusion (same size as EpiScreen)
  translate([0, 0, WALL - 0.01])
    funnel_void(EP_FUN_TOP_D, EP_FUN_BOT_D, EP_FUN_H);

  // Sensing tip
  translate([0, 0, WALL - EP_SENSE_PROTRUDE])
    cylinder(d = EP_SENSE_TIP_D, h = EP_FUN_H + EP_SENSE_PROTRUDE + 0.01);

  // Impedance ring recess — generously sized
  translate([0, 0, WALL])
    impedance_ring_void(EP_FUN_TOP_D, EP_FUN_BOT_D, EP_FUN_H,
                        EP_IMP_RING_Z_FRAC, EP_IMP_RING_W, EP_IMP_RING_T);

  // FR-4 seat shelf — top face flush with top of lower silicone
  translate([0, 0, WALL + HS_FR4_Z])
    difference() {
      cylinder(d = HS_FR4_D + 2*HS_FR4_LIP, h = HS_FR4_T + 0.01);
      translate([0, 0, -0.05])
        cylinder(d = HS_FR4_D + CLEARANCE, h = HS_FR4_T + 0.1);
    }

  // ── 7 penetration-pin cores (solid posts; silicone cures around) ──
  translate([0, 0, WALL])
    pin_array_cores();
}

// ─────────────────────────────────────────────────────────────
// 7 tapered pin cores (draft for release)
// ─────────────────────────────────────────────────────────────
module pin_array_cores() {
  d_base = HS_PIN_D;
  d_tip  = HS_PIN_D * 0.7;
  // Centre
  cylinder(d1 = d_base, d2 = d_tip, h = HS_PIN_H, center = false);
  // 6 outer pins
  for (i = [0 : 5])
    rotate([0, 0, i * 60])
      translate([HS_PIN_RAD, 0, 0])
        cylinder(d1 = d_base, d2 = d_tip, h = HS_PIN_H, center = false);
}

// ─────────────────────────────────────────────────────────────
// Texture exclusion zones — cylindrical voids around each pin so
// pillars don't interfere with the pins during silicone flow.
// ─────────────────────────────────────────────────────────────
module pin_texture_exclusions() {
  // Centre exclusion
  translate([0, 0, -PILLAR_H - 0.1])
    cylinder(r = HS_PIN_EXCL_R, h = PILLAR_H + 0.2);
  // 6 outer exclusions
  for (i = [0 : 5])
    rotate([0, 0, i * 60])
      translate([HS_PIN_RAD, 0, -PILLAR_H - 0.1])
        cylinder(r = HS_PIN_EXCL_R, h = PILLAR_H + 0.2);
}

// ─────────────────────────────────────────────────────────────
// Cable exit (C-strategy, same geometry as EpiScreen)
// ─────────────────────────────────────────────────────────────
module hs_cable_exit_bottom() {
  z_top_max = HS_BOT_H - 0.3;
  z_centre  = WALL + min(HS_FR4_Z + HS_FR4_T/2,
                         z_top_max - CABLE_CH_H/2);
  x_start   = HS_OD/2 - 0.2;
  rad_l     = (HS_MOLD_OD - HS_OD)/2 + 1.0;
  for (y_off = [+(CABLE_CH_W + CABLE_DIV_W)/2,
                -(CABLE_CH_W + CABLE_DIV_W)/2])
    translate([x_start, y_off, z_centre])
      rotate([0, 90, 0])
        cylinder(d1 = CABLE_CH_W,
                 d2 = CABLE_CH_W + 2*tan(CABLE_FLARE)*rad_l,
                 h  = rad_l + 0.5,
                 center = false, $fn = 4);
}
