// ============================================================
// Adult Headband Mount — for 24 mm EpiScreen electrode
// ============================================================
// Forehead / temporal band clip. The electrode snaps into the
// clip block which slides or clips onto a standard 22 mm wide
// elastic or silicone headband.
//
// Features:
//   – Electrode socket with snap ring (24.5 mm bore)
//   – Band channel (22 mm wide, 2.5 mm thick) below socket
//   – Strain-relief cable exit at top
//   – Optional velcro tab ears (flat, 3 mm thick)
// ============================================================

include <params.scad>

headband_adult();

module headband_adult() {
    difference() {
        union() {
            // ── Clip block ────────────────────────────────────
            translate([-HBA_CLIP_W/2, -HBA_CLIP_W/2, 0])
                cube([HBA_CLIP_W, HBA_CLIP_W, HBA_CLIP_H], center = false);

            // ── Velcro tab ears (lateral, flat) ──────────────
            for (side = [-1, 1])
                translate([side * (HBA_CLIP_W/2), -HBA_BAND_W/2, 1])
                    cube([side * 10, HBA_BAND_W, 3], center = false);
        }

        // ── Electrode socket (centred, from top) ─────────────
        translate([0, 0, HBA_CLIP_H - HBA_ELEC_H])
            electrode_socket_adult();

        // ── Band channel (horizontal slot through block) ──────
        translate([-HBA_CLIP_W/2 - 0.1, -HBA_BAND_W/2,
                    HBA_CLIP_H - HBA_ELEC_H - HBA_BAND_T - 1])
            cube([HBA_CLIP_W + 0.2, HBA_BAND_W,
                  HBA_BAND_T + 0.5], center = false);

        // ── Cable exit (top, off-centre) ──────────────────────
        translate([HBA_ELEC_D/2 - 2, -EP_CABLE_W_BOT/2,
                    HBA_CLIP_H - HBA_ELEC_H])
            cube([EP_CABLE_D + 1, EP_CABLE_W_BOT, HBA_ELEC_H + 0.1],
                 center = false);
    }
}

module electrode_socket_adult() {
    // Main bore
    cylinder(d = HBA_ELEC_D, h = HBA_ELEC_H + 0.1, center = false);

    // Snap ring
    translate([0, 0, HBA_ELEC_H / 3])
        rotate_extrude()
            translate([HBA_ELEC_D/2 - HBA_SNAP_R, 0, 0])
                circle(r = HBA_SNAP_R);

    // Lead-in chamfer
    translate([0, 0, HBA_ELEC_H - 1.5])
        cylinder(d1 = HBA_ELEC_D, d2 = HBA_ELEC_D + 2,
                 h = 1.6, center = false);
}
