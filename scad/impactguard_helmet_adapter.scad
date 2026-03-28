// ============================================================
// ImpactGuard Helmet Adapter
// ============================================================
// Snap-fit adapter that mounts a 24 mm EpiScreen electrode
// into a standard sports/clinical helmet.
//
// Features:
//   – Circular socket for electrode (snap-in retention)
//   – Flat mounting plate with 4× M3 bolt holes for helmet
//   – Strain-relief cable guide on side
//   – Low-profile design to minimise protrusion
// ============================================================

include <params.scad>

impactguard_adapter();

module impactguard_adapter() {
    difference() {
        union() {
            // ── Main adapter body (circular) ─────────────────
            cylinder(d = IG_OD, h = IG_H, center = false);

            // ── Rectangular mounting flange ───────────────────
            translate([-IG_MOUNT_W/2, -IG_MOUNT_W/2, 0])
                cube([IG_MOUNT_W, IG_MOUNT_W, IG_MOUNT_H], center = false);
        }

        // ── Electrode socket (top portion) ───────────────────
        translate([0, 0, IG_H - IG_ELEC_H])
            electrode_socket();

        // ── Cable exit slot (side) ────────────────────────────
        translate([IG_OD/2 - EP_CABLE_D, -EP_CABLE_W_BOT/2, IG_H - IG_ELEC_H])
            cube([EP_CABLE_D + 2, EP_CABLE_W_BOT, IG_H + 0.1], center = false);

        // ── M3 mounting bolt holes (4× in corners) ────────────
        corner_r = IG_MOUNT_W/2 - 4;
        for (a = [45, 135, 225, 315])
            rotate([0, 0, a])
                translate([corner_r, 0, -0.1])
                    cylinder(d = 3.4, h = IG_MOUNT_H + 0.2, center = false);

        // ── M3 countersink on bottom face ─────────────────────
        for (a = [45, 135, 225, 315])
            rotate([0, 0, a])
                translate([corner_r, 0, -0.1])
                    cylinder(d1 = 6.5, d2 = 3.4, h = 2.5, center = false);
    }
}

// ─────────────────────────────────────────────────────────────
// Electrode socket with snap-fit retention ring
// ─────────────────────────────────────────────────────────────
module electrode_socket() {
    // Straight bore
    cylinder(d = IG_ELEC_D, h = IG_ELEC_H + 0.1, center = false);

    // Snap ring groove (electrode pops in and locks)
    translate([0, 0, IG_ELEC_H / 2])
        rotate_extrude()
            translate([IG_ELEC_D/2 - IG_SNAP_R, 0, 0])
                circle(r = IG_SNAP_R);

    // Lead-in chamfer at opening
    translate([0, 0, IG_ELEC_H - 1.5])
        cylinder(d1 = IG_ELEC_D, d2 = IG_ELEC_D + 2,
                 h = 1.6, center = false);
}
