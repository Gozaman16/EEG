// ═════════════════════════════════════════════════════════════
// NeoGuard 15 mm Neonatal EEG Electrode — TOP MOLD PIECE
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

neoguard_top();

module neoguard_top() {
  mold_h = NG_TOP_H;
  difference() {
    // Outer lid body
    cylinder(d = NG_MOLD_OD, h = mold_h, center = false);

    // Upper silicone cavity
    translate([0, 0, -0.01])
      cylinder(d = NG_OD + CLEARANCE, h = mold_h - WALL + 0.02, center = false);

    // Silicone pour hole (centre)
    translate([0, 0, mold_h - NG_POUR_D])
      cylinder(d = NG_POUR_D, h = NG_POUR_D + 0.1, center = false);

    // Vent holes (2×)
    for (a = [90, 270])
      rotate([0, 0, a])
        translate([(NG_MOLD_OD/2 - WALL - 2), 0, mold_h - 3])
          cylinder(d = VENT_D, h = WALL + 3.1, center = false);

    // Refill port — 2 mm through-hole over funnel centre
    translate([0, 0, -0.05])
      cylinder(d = REFILL_PORT_D, h = mold_h + 0.1, center = false);

    // Pry slots at parting line
    pry_slots(NG_MOLD_OD, mold_h);
  }

  // Alignment pins (3×, conical, male)
  for (a = NG_PIN_ANGLES)
    rotate([0, 0, a])
      translate([(NG_MOLD_OD/2 - WALL - NG_PIN_D_BASE/2 - 0.5), 0,
                 -NG_PIN_H + 0.01])
        alignment_pin_male(NG_PIN_D_BASE, NG_PIN_D_TIP, NG_PIN_H);

  // Silicone interlock protrusions (groove, key socket, service gap)
  translate([0, 0, 0])
    interlock_upper_protrusions(NG_OD);
}
