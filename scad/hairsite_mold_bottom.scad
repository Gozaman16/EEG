// ============================================================
// HairSite Hair-Contact 24 mm EEG Electrode — BOTTOM MOLD
// ============================================================
// Like EpiScreen but with 7 flexible penetrating pin cores:
//   – 1 centre pin
//   – 6 pins at 60° spacing on 6 mm radius
// Pins are formed by solid posts in the mold; silicone cures
// around them creating hollow channels that guide through hair.
// ============================================================

include <params.scad>

hairsite_bottom();

module hairsite_bottom() {
    difference() {
        // Outer body (same OD as EpiScreen)
        cylinder(d = HS_MOLD_OD, h = HS_BOT_H + WALL, center = false);

        // Internal cavity
        translate([0, 0, WALL])
            hs_bottom_cavity();

        // Alignment pin holes (4×)
        for (i = [0 : PIN_R - 1])
            rotate([0, 0, i * 360 / PIN_R + 45])
                translate([(HS_MOLD_OD/2 - WALL - PIN_D/2 - 0.5), 0,
                            HS_BOT_H + WALL - PIN_H])
                    cylinder(d = PIN_D + CLEARANCE, h = PIN_H + 0.1, center = false);

        // Cable exit
        translate([HS_MOLD_OD/2 - EP_CABLE_D + 0.1, 0, WALL + EP_FR4_Z])
            cube([EP_CABLE_D + 0.2, EP_CABLE_W_BOT,
                  HS_BOT_H - EP_FR4_Z + 0.1], center = false);
    }

    // ── Pin array cores (positive features — stay in mold body) ──
    // These remain INSIDE the cavity as solid posts; silicone forms
    // around them. Posts are tapered (draft) for demolding.
    translate([0, 0, WALL])
        pin_array_cores();
}

module hs_bottom_cavity() {
    draft_r = tan(DRAFT) * HS_BOT_H;

    // Main cavity
    cylinder(d1 = HS_OD + 2 * draft_r,
             d2 = HS_OD,
             h = HS_BOT_H + 0.1, center = false);

    // Bottom cavity bump (skin contact)
    translate([0, 0, -0.05])
        cylinder(d = EP_BOT_CAV_D, h = EP_BOT_CAV_H + 0.05, center = false);

    // FR-4 shelf
    translate([0, 0, EP_FR4_Z])
        cylinder(d = EP_FR4_D + EP_FR4_LIP * 2,
                 h = HS_BOT_H - EP_FR4_Z + 0.1, center = false);
}

// ─────────────────────────────────────────────────────────────
// 7 tapered pin cores (solid; create hollow pin pockets in silicone)
// ─────────────────────────────────────────────────────────────
module pin_array_cores() {
    // Tip diameter slightly smaller (draft) for easy release
    pin_d_base = HS_PIN_D;
    pin_d_tip  = HS_PIN_D * 0.7;

    // Centre pin
    cylinder(d1 = pin_d_base, d2 = pin_d_tip,
             h = HS_PIN_H, center = false);

    // 6 outer pins
    for (i = [0 : 5])
        rotate([0, 0, i * 60])
            translate([HS_PIN_RAD, 0, 0])
                cylinder(d1 = pin_d_base, d2 = pin_d_tip,
                         h = HS_PIN_H, center = false);
}
