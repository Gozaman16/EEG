// ═════════════════════════════════════════════════════════════
// HairSite 24 mm Hair-Contact EEG Electrode — TOP MOLD PIECE
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

hairsite_top();

module hairsite_top() {
  mold_h = HS_TOP_H;
  difference() {
    cylinder(d = HS_MOLD_OD, h = mold_h, center = false);

    // Upper silicone cavity
    translate([0, 0, -0.01])
      cylinder(d = HS_OD + CLEARANCE, h = mold_h - WALL + 0.02, center = false);

    // Silicone pour hole
    translate([0, 0, mold_h - HS_POUR_D])
      cylinder(d = HS_POUR_D, h = HS_POUR_D + 0.1, center = false);

    // Vent holes
    for (a = [90, 270])
      rotate([0, 0, a])
        translate([(HS_MOLD_OD/2 - WALL - 2), 0, mold_h - 4])
          cylinder(d = VENT_D, h = WALL + 4.1, center = false);

    // Refill port
    translate([0, 0, -0.05])
      cylinder(d = REFILL_PORT_D, h = mold_h + 0.1, center = false);

    // Pin-tip clearance holes (penetration pins are tall — lid needs
    // guide holes so pin tips can poke through if HS_PIN_H > HS_BOT_H).
    pin_tip_holes();

    // Pry slots at parting line
    pry_slots(HS_MOLD_OD, mold_h);
  }

  // Alignment pins (4×, conical, male)
  for (a = PIN_ANGLES)
    rotate([0, 0, a])
      translate([(HS_MOLD_OD/2 - WALL - PIN_D_BASE/2 - 0.5), 0,
                 -PIN_H + 0.01])
        alignment_pin_male(PIN_D_BASE, PIN_D_TIP, PIN_H);

  // Silicone interlock protrusions
  translate([0, 0, 0])
    interlock_upper_protrusions(HS_OD);
}

// ─────────────────────────────────────────────────────────────
// Guide holes through the top lid for long penetration pins.
// ─────────────────────────────────────────────────────────────
module pin_tip_holes() {
  pin_z = HS_PIN_H - HS_BOT_H;                // height above parting plane
  if (pin_z > 0) {
    translate([0, 0, -0.05])
      cylinder(d = HS_PIN_D + CLEARANCE, h = HS_TOP_H + 0.1, center = false);
    for (i = [0 : 5])
      rotate([0, 0, i * 60])
        translate([HS_PIN_RAD, 0, -0.05])
          cylinder(d = HS_PIN_D + CLEARANCE, h = HS_TOP_H + 0.1, center = false);
  }
}
