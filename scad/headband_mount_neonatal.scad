// ============================================================
// Neonatal Headband Mount — for 15 mm NeoGuard electrode
// ============================================================
// Ultra-low-profile design for neonatal/infant use.
// Very gentle clamping force; designed for thin silicone bands.
//
// Features:
//   – Electrode socket (15.5 mm bore) with soft snap ring
//   – Band channel (16 mm wide, 2 mm thick)
//   – Minimal protrusion (9 mm clip height)
// ============================================================

include <params.scad>

headband_neonatal();

module headband_neonatal() {
    difference() {
        union() {
            // Clip block
            translate([-HBN_CLIP_W/2, -HBN_CLIP_W/2, 0])
                cube([HBN_CLIP_W, HBN_CLIP_W, HBN_CLIP_H], center = false);

            // Velcro ears (smaller)
            for (side = [-1, 1])
                translate([side * (HBN_CLIP_W/2), -HBN_BAND_W/2, 0.5])
                    cube([side * 7, HBN_BAND_W, 2.5], center = false);
        }

        // Electrode socket
        translate([0, 0, HBN_CLIP_H - HBN_ELEC_H])
            electrode_socket_neo();

        // Band channel
        translate([-HBN_CLIP_W/2 - 0.1, -HBN_BAND_W/2,
                    HBN_CLIP_H - HBN_ELEC_H - HBN_BAND_T - 0.5])
            cube([HBN_CLIP_W + 0.2, HBN_BAND_W,
                  HBN_BAND_T + 0.5], center = false);

        // Cable exit
        translate([HBN_ELEC_D/2 - 1.5, -EP_CABLE_W_BOT/2,
                    HBN_CLIP_H - HBN_ELEC_H])
            cube([EP_CABLE_D + 0.5, EP_CABLE_W_BOT,
                  HBN_ELEC_H + 0.1], center = false);
    }
}

module electrode_socket_neo() {
    cylinder(d = HBN_ELEC_D, h = HBN_ELEC_H + 0.1, center = false);

    // Snap ring (shallower = easier for neonatal use)
    translate([0, 0, HBN_ELEC_H / 3])
        rotate_extrude()
            translate([HBN_ELEC_D/2 - HBN_SNAP_R, 0, 0])
                circle(r = HBN_SNAP_R);

    // Lead-in chamfer
    translate([0, 0, HBN_ELEC_H - 1.2])
        cylinder(d1 = HBN_ELEC_D, d2 = HBN_ELEC_D + 1.5,
                 h = 1.3, center = false);
}
