// ============================================================
// NeoGuard Neonatal 15 mm EEG Electrode — BOTTOM MOLD PIECE
// ============================================================
// Scaled-down design for neonatal patients.
// Same structural logic as EpiScreen but smaller and gentler.
// ============================================================

include <params.scad>

neoguard_bottom();

module neoguard_bottom() {
    difference() {
        // Outer mold body
        cylinder(d = NG_MOLD_OD, h = NG_BOT_H + WALL, center = false);

        // Internal electrode cavity (bottom half)
        translate([0, 0, WALL])
            ng_bottom_cavity();

        // Alignment pin holes (4×)
        for (i = [0 : PIN_R - 1])
            rotate([0, 0, i * 360 / PIN_R + 45])
                translate([(NG_MOLD_OD/2 - WALL - PIN_D/2 - 0.4), 0,
                            NG_BOT_H + WALL - PIN_H])
                    cylinder(d = PIN_D + CLEARANCE, h = PIN_H + 0.1, center = false);

        // Cable exit
        translate([NG_MOLD_OD/2 - NG_CABLE_D + 0.1, 0, WALL + NG_FR4_Z])
            cube([NG_CABLE_D + 0.2, NG_CABLE_W_BOT,
                  NG_BOT_H - NG_FR4_Z + 0.1], center = false);
    }
}

module ng_bottom_cavity() {
    draft_r = tan(DRAFT) * NG_BOT_H;

    // Main cavity with draft
    cylinder(d1 = NG_OD + 2 * draft_r,
             d2 = NG_OD,
             h = NG_BOT_H + 0.1, center = false);

    // Skin-contact cavity bump
    translate([0, 0, -0.05])
        cylinder(d = NG_BOT_CAV_D, h = NG_BOT_CAV_H + 0.05, center = false);

    // Micro-texture on skin-contact surface
    for (r = [TEXTURE_STEP : TEXTURE_STEP : NG_BOT_CAV_D/2 - TEXTURE_STEP])
        rotate_extrude()
            translate([r, NG_BOT_CAV_H, 0])
                square([TEXTURE_W, TEXTURE_DEPTH + 0.01], center = false);

    // Spiral exposure platform
    translate([0, 0, -0.05])
        cylinder(d = NG_SPIRAL_D, h = NG_SPIRAL_H, center = false);

    // FR-4 seat shelf
    translate([0, 0, NG_FR4_Z])
        cylinder(d = NG_FR4_D + 0.4,
                 h = NG_BOT_H - NG_FR4_Z + 0.1, center = false);
}
