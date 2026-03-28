// ============================================================
// EpiScreen Standard 24 mm EEG Electrode — BOTTOM MOLD PIECE
// ============================================================
// Mold cavity defines electrode shape. Silicone is poured in.
// Material: Resin (SLA/DLP), minimum feature size 0.3 mm.
// ============================================================

include <params.scad>

// Main entry point
episcreen_bottom();

module episcreen_bottom() {
    difference() {
        // ── Outer mold body ───────────────────────────────
        union() {
            cylinder(d = EP_MOLD_OD, h = EP_BOT_H + WALL, center = false);
        }

        // ── Internal electrode cavity (bottom half 0..5 mm) ──
        translate([0, 0, WALL])
            electrode_bottom_cavity();

        // ── Alignment pin holes (4×) on top rim ─────────────
        for (i = [0 : PIN_R - 1])
            rotate([0, 0, i * 360 / PIN_R + 45])
                translate([(EP_MOLD_OD/2 - WALL - PIN_D/2 - 0.5), 0,
                            EP_BOT_H + WALL - PIN_H])
                    cylinder(d = PIN_D + CLEARANCE, h = PIN_H + 0.1,
                             center = false);

        // ── Cable exit notch (side wall, full height of bottom piece) ─
        cable_exit_bottom();
    }
}

// ─────────────────────────────────────────────────────────────
// Bottom-half electrode cavity (positive space removed from mold)
// ─────────────────────────────────────────────────────────────
module electrode_bottom_cavity() {
    // Outer cylinder with draft angle
    draft_r = tan(DRAFT) * EP_BOT_H;
    cylinder(d1 = EP_OD + 2 * draft_r,   // wider at bottom
             d2 = EP_OD,
             h = EP_BOT_H + 0.1, center = false);

    // Bottom skin-contact concave bump (raised on mold = concave on electrode)
    // The mold has a shallow raised disc → electrode has recessed skin pocket
    translate([0, 0, -0.05])
        union() {
            // Raised platform creates electrode bottom recess
            cylinder(d = EP_BOT_CAV_D, h = EP_BOT_CAV_H + 0.05, center = false);
            // Concentric micro-texture rings on the platform surface
            skin_contact_texture(EP_BOT_CAV_D / 2, EP_BOT_CAV_H);
        }

    // Spiral exposure platform (raised in mold → copper sits here, not covered)
    translate([0, 0, -0.05])
        union() {
            // Smooth central post
            cylinder(d = EP_SPIRAL_D, h = EP_SPIRAL_H, center = false);
            // Light texture grooves around edge of platform
            for (r = [EP_SPIRAL_D/2 - 0.4, EP_SPIRAL_D/2 - 0.8])
                rotate_extrude()
                    translate([r, 0, 0])
                        square([0.15, EP_SPIRAL_H], center = false);
        }

    // FR-4 seat ledge — shelf at z = EP_FR4_Z (measured from cavity floor)
    // The shelf is created by leaving material; here we cut away above it
    // Approach: cut a wider cylinder above FR4_Z, keeping shelf ring
    translate([0, 0, EP_FR4_Z])
        cylinder(d = EP_FR4_D + EP_FR4_LIP * 2,
                 h = EP_BOT_H - EP_FR4_Z + 0.1, center = false);

    // Microchannel guide holes (3× at 120°, angled 37.5° downward)
    for (i = [0 : EP_MCH_N - 1])
        rotate([0, 0, i * 120 + 30])
            microchannel_hole();
}

// ─────────────────────────────────────────────────────────────
// Concentric skin-contact texture rings
// ─────────────────────────────────────────────────────────────
module skin_contact_texture(max_r, base_h) {
    for (r = [TEXTURE_STEP : TEXTURE_STEP : max_r - TEXTURE_STEP])
        rotate_extrude()
            translate([r, base_h, 0])
                square([TEXTURE_W, TEXTURE_DEPTH + 0.01], center = false);
}

// ─────────────────────────────────────────────────────────────
// Single microchannel guide hole (angled bore through mold wall)
// ─────────────────────────────────────────────────────────────
module microchannel_hole() {
    // Starts at outer edge of reservoir ring, goes down ~37.5° to bottom cavity
    start_r = EP_RES_OD / 2;
    start_z = EP_FR4_Z + EP_FR4_T + EP_RES_H / 2;  // mid-reservoir height
    length  = (EP_MOLD_OD / 2 - start_r + 4) / cos(EP_MCH_ANG);

    translate([start_r, 0, WALL + start_z])
        rotate([0, EP_MCH_ANG, 0])
            cylinder(d = EP_MCH_D, h = length, center = false);
}

// ─────────────────────────────────────────────────────────────
// Cable exit notch — funnel-shaped, FR-4 level to top
// ─────────────────────────────────────────────────────────────
module cable_exit_bottom() {
    // Position on +X side of mold
    translate([EP_MOLD_OD / 2 - EP_CABLE_D + 0.1, 0, WALL + EP_FR4_Z])
        hull() {
            translate([0, -EP_CABLE_W_BOT / 2, 0])
                cube([EP_CABLE_D + 0.2,
                      EP_CABLE_W_BOT,
                      (EP_BOT_H - EP_FR4_Z)], center = false);
            translate([0, -EP_CABLE_W_TOP / 2, 0])
                cube([EP_CABLE_D + 0.2,
                      EP_CABLE_W_TOP,
                      (EP_BOT_H - EP_FR4_Z)], center = false);
        }
}
