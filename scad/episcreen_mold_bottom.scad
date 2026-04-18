// ═════════════════════════════════════════════════════════════
// EpiScreen 24 mm EEG Electrode — BOTTOM MOLD PIECE
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

episcreen_bottom();

// ─────────────────────────────────────────────────────────────
// Bottom mold — owns funnel, sensing tip, impedance ring, FR-4 seat,
// cable tunnels, pillar texture, alignment holes, flash trap, pry
// slots, and silicone interlock voids in the cavity ceiling.
// ─────────────────────────────────────────────────────────────
module episcreen_bottom() {
  mold_h = EP_BOT_H + WALL;
  difference() {
    union() {
      // Outer body
      cylinder(d = EP_MOLD_OD, h = mold_h, center = false);
    }

    // Main electrode cavity (subtract a flat cylinder from wall to top face)
    translate([0, 0, WALL - 0.01])
      cylinder(d = EP_OD + CLEARANCE, h = EP_BOT_H + 0.02, center = false);

    // Pillar texture: holes in the mold floor → raised pillars on silicone skin side
    translate([0, 0, WALL])
      hex_pillar_texture(EP_FUN_BOT_D/2 + 3.0, -PILLAR_H);

    // Alignment pin holes (4×, avoid cable notch at 0°)
    for (a = PIN_ANGLES)
      rotate([0, 0, a])
        translate([(EP_MOLD_OD/2 - WALL - HOLE_D/2 - 0.5), 0,
                   mold_h - HOLE_DEPTH])
          alignment_hole(HOLE_D, HOLE_DEPTH + 0.1);

    // Cable exit tunnels (C-strategy — two channels, 2 mm divider)
    cable_exit_bottom();

    // Pry slots at parting line
    pry_slots(EP_MOLD_OD, mold_h);

    // Flash trap groove on the top face
    flash_trap(EP_MOLD_OD, mold_h);

    // Silicone interlock voids in cavity ceiling: perimeter lip, key,
    // service notch.  Produces matching raised features on the upper
    // face of the lower silicone.
    translate([0, 0, mold_h - SIL_LIP_H])
      interlock_lower_voids(EP_OD);
  }

  // ── Positive features inside the cavity ───────────────────
  // Funnel protrusion (skin side narrow on skin = wide at cavity floor)
  translate([0, 0, WALL - 0.01])
    funnel_void(EP_FUN_TOP_D, EP_FUN_BOT_D, EP_FUN_H);

  // Sensing tip — smaller cylinder centred inside funnel, protrudes
  // 0.1 mm below the funnel bottom rim (creates a raised sensing seat
  // in the silicone that pokes past the funnel opening).
  translate([0, 0, WALL - EP_SENSE_PROTRUDE])
    cylinder(d = EP_SENSE_TIP_D, h = EP_FUN_H + EP_SENSE_PROTRUDE + 0.01);

  // Impedance ring recess: annular void on inner funnel wall.
  // NOTE: sized generously — was too tight in previous generation.
  translate([0, 0, WALL])
    impedance_ring_void(EP_FUN_TOP_D, EP_FUN_BOT_D, EP_FUN_H,
                        EP_IMP_RING_Z_FRAC, EP_IMP_RING_W, EP_IMP_RING_T);

  // FR-4 seat shelf — square/circular shelf the FR-4 rests on so its
  // top face is flush with the top of the lower silicone.  Silicone
  // fills around, not over, the FR-4.
  translate([0, 0, WALL + EP_FR4_Z])
    difference() {
      cylinder(d = EP_FR4_D + 2*EP_FR4_LIP, h = EP_FR4_T + 0.01);
      translate([0, 0, -0.05])
        cylinder(d = EP_FR4_D + CLEARANCE, h = EP_FR4_T + 0.1);
    }
}

// ─────────────────────────────────────────────────────────────
// Cable exit (C-strategy): single notch on +X side, two parallel
// rectangular through-tunnels separated by a 2 mm divider.  Each
// tunnel is 1.5 mm (Y) × 1.8 mm (Z), runs radially from cavity to
// outside, Z-centred at FR-4 level.  Top of tunnel ≤ EP_BOT_H - 0.3
// to stay below the parting line.  Small 1° flare on the outside.
// ─────────────────────────────────────────────────────────────
module cable_exit_bottom() {
  z_top_max = EP_BOT_H - 0.3;                 // must stay below parting line
  z_centre  = WALL + min(EP_FR4_Z + EP_FR4_T/2,
                         z_top_max - CABLE_CH_H/2);
  x_start   = EP_OD/2 - 0.2;
  for (y_off = [+(CABLE_CH_W + CABLE_DIV_W)/2,
                -(CABLE_CH_W + CABLE_DIV_W)/2])
    translate([x_start, y_off, z_centre])
      rotate([0, 90, 0])
        // slight flare from inside to outside
        cylinder(d1 = CABLE_CH_W,
                 d2 = CABLE_CH_W + 2*tan(CABLE_FLARE)*EP_CABLE_RAD_L,
                 h  = EP_CABLE_RAD_L + 0.5,
                 center = false, $fn = 4);    // square-ish profile via $fn=4
}
