// ============================================================
// EpiScreen Standard 24 mm EEG Electrode — TOP MOLD PIECE
// ============================================================
// Lid that clamps onto bottom piece. Has:
//   – Reservoir ring protrusion (creates ring void in silicone)
//   – Pour hole + 2 vent holes
//   – 4 alignment pins (male, match bottom female holes)
//   – Cable exit upper portion
//   – Reservoir fill port
// ============================================================

include <params.scad>

episcreen_top();

module episcreen_top() {
    difference() {
        // ── Outer lid body ────────────────────────────────
        cylinder(d = EP_MOLD_OD, h = EP_TOP_H, center = false);

        // ── Internal cavity (top half of electrode, 5..10 mm) ──
        translate([0, 0, WALL])
            electrode_top_cavity();

        // ── Silicone pour hole (center, top) ────────────────
        translate([0, 0, EP_TOP_H - EP_POUR_D])
            cylinder(d = EP_POUR_D, h = EP_POUR_D + 0.1, center = false);

        // ── Vent holes (2×, opposite sides near edge) ───────
        for (a = [90, 270])
            rotate([0, 0, a])
                translate([(EP_MOLD_OD/2 - WALL - 2), 0, EP_TOP_H - 4])
                    cylinder(d = VENT_D, h = WALL + 4.1, center = false);

        // ── Reservoir fill port ──────────────────────────────
        // 2 mm hole through top wall above reservoir ring
        translate([EP_RES_OD/2 - 2, 0, EP_TOP_H - 6])
            cylinder(d = 2.0, h = WALL + 6.1, center = false);

        // ── Cable exit notch (upper) ─────────────────────────
        cable_exit_top();
    }

    // ── Alignment pins (4×, male, project downward) ─────────
    for (i = [0 : PIN_R - 1])
        rotate([0, 0, i * 360 / PIN_R + 45])
            translate([(EP_MOLD_OD/2 - WALL - PIN_D/2 - 0.5), 0, 0])
                cylinder(d = PIN_D, h = PIN_H + WALL, center = false);
}

// ─────────────────────────────────────────────────────────────
// Top-half electrode cavity (5 mm to 10 mm of electrode height)
// ─────────────────────────────────────────────────────────────
module electrode_top_cavity() {
    top_cav_h = EP_H - EP_BOT_H;   // = 5 mm

    // Outer cylinder with matching draft
    draft_r = tan(DRAFT) * EP_BOT_H;
    cylinder(d = EP_OD,
             d2 = EP_OD,
             h = top_cav_h + 0.1, center = false);

    // ── Reservoir ring PROTRUSION removed from solid here ───
    // In the top mold, material is left as a ring (not subtracted)
    // so we cut out only the annular region OUTSIDE the ring protrusion
    // Strategy: cut the full cylinder, then leave the ring as solid
    // (ring will remain after this subtraction as positive feature)
    // The ring occupies: r from EP_RES_ID/2 to EP_RES_OD/2, z 0..EP_RES_H
    // We cut everything EXCEPT that ring:
    //   – inner hole
    translate([0, 0, -0.05])
        cylinder(d = EP_RES_ID - CLEARANCE, h = EP_RES_H + 0.1, center = false);
}

// ─────────────────────────────────────────────────────────────
// Cable exit notch — upper portion (FR-4 level to top of mold)
// ─────────────────────────────────────────────────────────────
module cable_exit_top() {
    translate([EP_MOLD_OD / 2 - EP_CABLE_D + 0.1, 0, 0])
        hull() {
            translate([0, -EP_CABLE_W_BOT / 2, WALL])
                cube([EP_CABLE_D + 0.2, EP_CABLE_W_BOT,
                      EP_TOP_H - WALL], center = false);
            translate([0, -EP_CABLE_W_TOP / 2, WALL])
                cube([EP_CABLE_D + 0.2, EP_CABLE_W_TOP,
                      EP_TOP_H - WALL], center = false);
        }
}
