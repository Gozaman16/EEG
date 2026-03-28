// ============================================================
// NeoGuard Neonatal 15 mm EEG Electrode — TOP MOLD PIECE
// ============================================================

include <params.scad>

neoguard_top();

module neoguard_top() {
    difference() {
        // Outer lid
        cylinder(d = NG_MOLD_OD, h = NG_TOP_H, center = false);

        // Internal top-half cavity
        translate([0, 0, WALL])
            ng_top_cavity();

        // Pour hole
        translate([0, 0, NG_TOP_H - NG_POUR_D])
            cylinder(d = NG_POUR_D, h = NG_POUR_D + 0.1, center = false);

        // Vent holes (2×)
        for (a = [90, 270])
            rotate([0, 0, a])
                translate([(NG_MOLD_OD/2 - WALL - 2), 0, NG_TOP_H - 3])
                    cylinder(d = VENT_D, h = WALL + 3.1, center = false);

        // Reservoir fill port
        translate([NG_RES_OD/2 - 1.5, 0, NG_TOP_H - 5])
            cylinder(d = 2.0, h = WALL + 5.1, center = false);

        // Cable exit (upper)
        translate([NG_MOLD_OD/2 - NG_CABLE_D + 0.1, 0, WALL])
            cube([NG_CABLE_D + 0.2, NG_CABLE_W_TOP,
                  NG_TOP_H - WALL + 0.1], center = false);
    }

    // Alignment pins (4×, male)
    for (i = [0 : PIN_R - 1])
        rotate([0, 0, i * 360 / PIN_R + 45])
            translate([(NG_MOLD_OD/2 - WALL - PIN_D/2 - 0.4), 0, 0])
                cylinder(d = PIN_D, h = PIN_H + WALL, center = false);
}

module ng_top_cavity() {
    top_cav_h = NG_H - NG_BOT_H;

    // Main cylinder
    cylinder(d = NG_OD, h = top_cav_h + 0.1, center = false);

    // Inner hole of reservoir ring (leave ring as solid protrusion)
    translate([0, 0, -0.05])
        cylinder(d = NG_RES_ID - CLEARANCE,
                 h = NG_RES_H + 0.1, center = false);
}
