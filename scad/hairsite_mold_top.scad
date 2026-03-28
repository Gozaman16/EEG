// ============================================================
// HairSite Hair-Contact 24 mm EEG Electrode — TOP MOLD PIECE
// ============================================================

include <params.scad>

hairsite_top();

module hairsite_top() {
    difference() {
        // Outer lid
        cylinder(d = HS_MOLD_OD, h = HS_TOP_H, center = false);

        // Internal top-half cavity
        translate([0, 0, WALL])
            hs_top_cavity();

        // Pour hole
        translate([0, 0, HS_TOP_H - HS_POUR_D])
            cylinder(d = HS_POUR_D, h = HS_POUR_D + 0.1, center = false);

        // Vent holes (2×)
        for (a = [90, 270])
            rotate([0, 0, a])
                translate([(HS_MOLD_OD/2 - WALL - 2), 0, HS_TOP_H - 4])
                    cylinder(d = VENT_D, h = WALL + 4.1, center = false);

        // Reservoir fill port
        translate([EP_RES_OD/2 - 2, 0, HS_TOP_H - 6])
            cylinder(d = 2.0, h = WALL + 6.1, center = false);

        // Cable exit upper
        translate([HS_MOLD_OD/2 - EP_CABLE_D + 0.1, 0, WALL])
            cube([EP_CABLE_D + 0.2, EP_CABLE_W_TOP,
                  HS_TOP_H - WALL + 0.1], center = false);

        // Through-holes for pin tips to poke through top mold
        // (allows even longer pins if needed; also serves as guide)
        translate([0, 0, WALL])
            pin_tip_holes();
    }

    // Alignment pins (4×, male)
    for (i = [0 : PIN_R - 1])
        rotate([0, 0, i * 360 / PIN_R + 45])
            translate([(HS_MOLD_OD/2 - WALL - PIN_D/2 - 0.5), 0, 0])
                cylinder(d = PIN_D, h = PIN_H + WALL, center = false);
}

module hs_top_cavity() {
    top_cav_h = HS_H - HS_BOT_H;

    cylinder(d = HS_OD, h = top_cav_h + 0.1, center = false);

    // Reservoir ring inner hole
    translate([0, 0, -0.05])
        cylinder(d = EP_RES_ID - CLEARANCE,
                 h = EP_RES_H + 0.1, center = false);
}

module pin_tip_holes() {
    // Guide holes for pin tip protrusion through lid
    top_cav_h = HS_H - HS_BOT_H;
    pin_z     = HS_PIN_H - HS_BOT_H;  // height above parting plane

    if (pin_z > 0) {
        cylinder(d = HS_PIN_D + 0.2, h = top_cav_h + 0.1, center = false);
        for (i = [0 : 5])
            rotate([0, 0, i * 60])
                translate([HS_PIN_RAD, 0, 0])
                    cylinder(d = HS_PIN_D + 0.2, h = top_cav_h + 0.1, center = false);
    }
}
