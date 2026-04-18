// ═════════════════════════════════════════════════════════════
// EpiScreen 24 mm EEG Electrode — TOP MOLD PIECE
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
// Top mold is a thin lid that caps the upper silicone (FR-4 stays
// with the lower silicone).  Has refill port over funnel centre,
// silicone interlock protrusions, alignment pins, pry slots, pour
// hole, vents.  NO cable exit features (all cable routing is in
// the bottom mold).

include <params.scad>

episcreen_top();

module episcreen_top() {
  mold_h = EP_TOP_H;
  difference() {
    // Outer lid body
    cylinder(d = EP_MOLD_OD, h = mold_h, center = false);

    // Upper silicone cavity (thin — just the lid's worth)
    translate([0, 0, -0.01])
      cylinder(d = EP_OD + CLEARANCE, h = mold_h - WALL + 0.02, center = false);

    // Silicone pour hole (centre)
    translate([0, 0, mold_h - EP_POUR_D])
      cylinder(d = EP_POUR_D, h = EP_POUR_D + 0.1, center = false);

    // Vent holes (2×, opposite sides)
    for (a = [90, 270])
      rotate([0, 0, a])
        translate([(EP_MOLD_OD/2 - WALL - 2), 0, mold_h - 4])
          cylinder(d = VENT_D, h = WALL + 4.1, center = false);

    // Refill port — 2 mm vertical through-hole over funnel centre
    translate([0, 0, -0.05])
      cylinder(d = REFILL_PORT_D, h = mold_h + 0.1, center = false);

    // Pry slots at parting line
    pry_slots(EP_MOLD_OD, mold_h);
  }

  // ── Alignment pins (male, conical, project down into bottom mold) ──
  for (a = PIN_ANGLES)
    rotate([0, 0, a])
      translate([(EP_MOLD_OD/2 - WALL - PIN_D_BASE/2 - 0.5), 0, -PIN_H + 0.01])
        alignment_pin_male(PIN_D_BASE, PIN_D_TIP, PIN_H);

  // ── Silicone interlock protrusions (lip-matching groove, key socket,
  //    service-notch gap) — all on the downward-facing inner surface.
  // Mold inner top face is at z = mold_h - WALL looking up from below,
  // but protrusions extend DOWN into the upper silicone cavity.  We
  // place them at the bottom of the cavity (z = 0) pointing upward in
  // mold coordinates; after the mold is flipped during casting this
  // corresponds to features on the bottom face of the upper silicone.
  translate([0, 0, 0])
    interlock_upper_protrusions(EP_OD);
}
