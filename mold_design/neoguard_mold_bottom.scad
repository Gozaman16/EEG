// ============================================================
// NeoGuard Neonatal Mold — BOTTOM PIECE
// ============================================================
include <neoguard_mold_parameters.scad>;

function drafted_r(base_r, h) =
    base_r + h * tan(draft_angle);

// ============================================================
// Main bottom mold piece
// ============================================================
module bottom_mold() {
    difference() {
        bottom_shell();

        // Electrode cavity (bottom half)
        translate([0, 0, base_plate_thick])
            electrode_cavity_bottom();

        // Gasket rim groove — annular channel around bottom
        // edge of cavity to create soft silicone gasket
        translate([0, 0, base_plate_thick])
            gasket_rim_groove();

        // Alignment pin holes on top rim
        translate([0, 0, base_plate_thick + parting_z])
            alignment_pin_holes();

        // Microchannel guide holes
        microchannel_holes();
    }

    // Bottom surface ring (raised annulus for skin-contact recess)
    translate([0, 0, base_plate_thick])
        bottom_surface_ring();

    // Spiral exposure platform
    translate([0, 0, base_plate_thick])
        spiral_platform();

    // Micro-texture concentric rings
    translate([0, 0, base_plate_thick])
        bottom_texture();

    // FR-4 seat ledge
    translate([0, 0, base_plate_thick])
        fr4_seat();
}

// ============================================================
// Outer shell
// ============================================================
module bottom_shell() {
    total_h = base_plate_thick + parting_z;
    minkowski() {
        cylinder(r = mold_radius - fillet_r, h = total_h - fillet_r);
        sphere(r = fillet_r);
    }
}

// ============================================================
// Electrode cavity — bottom half (0 to parting_z)
// ============================================================
module electrode_cavity_bottom() {
    cylinder(
        r1 = electrode_radius,
        r2 = drafted_r(electrode_radius, parting_z),
        h = parting_z + 0.01
    );
}

// ============================================================
// Gasket rim groove — creates soft silicone gasket on electrode
// Annular channel at the very bottom edge of the cavity
// ============================================================
module gasket_rim_groove() {
    // This is a groove cut INTO the mold floor at the outer
    // edge of the electrode, creating a raised rim on the
    // finished silicone electrode
    translate([0, 0, -gasket_rim_height]) {
        difference() {
            cylinder(r = electrode_radius, h = gasket_rim_height + 0.01);
            translate([0, 0, -0.01])
                cylinder(r = electrode_radius - gasket_rim_width,
                         h = gasket_rim_height + 0.03);
        }
    }
}

// ============================================================
// Bottom surface ring — creates recess in electrode bottom
// ============================================================
module bottom_surface_ring() {
    difference() {
        cylinder(r = electrode_radius - gasket_rim_width, h = bottom_cavity_depth);
        translate([0, 0, -0.01])
            cylinder(r = bottom_cavity_r, h = bottom_cavity_depth + 0.02);
    }
}

// ============================================================
// Spiral exposure platform
// ============================================================
module spiral_platform() {
    difference() {
        cylinder(r = spiral_platform_r, h = spiral_platform_height);
        // Texture grooves on top
        for (r_pos = [0.8 : groove_spacing : spiral_platform_r - 0.2]) {
            translate([0, 0, spiral_platform_height - groove_depth])
                difference() {
                    cylinder(r = r_pos + 0.08, h = groove_depth + 0.01);
                    cylinder(r = r_pos - 0.08, h = groove_depth + 0.02);
                }
        }
    }
}

// ============================================================
// Bottom cavity micro-texture (concentric rings — gentler)
// ============================================================
module bottom_texture() {
    for (r_pos = [0.8 : texture_ring_spacing : bottom_cavity_r - 0.3]) {
        difference() {
            cylinder(r = r_pos + 0.08, h = texture_ring_depth);
            translate([0, 0, -0.01])
                cylinder(r = r_pos - 0.08, h = texture_ring_depth + 0.02);
        }
    }
}

// ============================================================
// FR-4 seat ledge
// ============================================================
module fr4_seat() {
    wall_r_at_seat = drafted_r(electrode_radius, fr4_seat_z);

    if (fr4_seat_z < parting_z) {
        translate([0, 0, fr4_seat_z]) {
            // Ledge ring
            difference() {
                cylinder(r = wall_r_at_seat, h = fr4_thickness);
                translate([0, 0, -0.01])
                    cylinder(r = fr4_seat_r, h = fr4_thickness + 0.02);
            }
            // Centering lip
            difference() {
                cylinder(r = fr4_seat_r + 0.3, h = fr4_lip);
                translate([0, 0, -0.01])
                    cylinder(r = fr4_seat_r, h = fr4_lip + 0.02);
            }
        }
    }
}

// ============================================================
// Alignment pin holes
// ============================================================
module alignment_pin_holes() {
    for (i = [0 : pin_count - 1]) {
        angle = i * 360 / pin_count;
        rotate([0, 0, angle])
            translate([pin_ring_r, 0, -pin_depth])
                cylinder(d = pin_dia + clearance, h = pin_depth + 0.01);
    }
}

// ============================================================
// Microchannel guide holes (4 at 90° spacing)
// ============================================================
module microchannel_holes() {
    for (i = [0 : microchannel_count - 1]) {
        angle = i * 360 / microchannel_count;
        start_z = base_plate_thick + reservoir_z;
        hole_length = 20;

        rotate([0, 0, angle])
            translate([reservoir_od/2, 0, start_z])
                rotate([0, 90 - microchannel_angle, 0])
                    cylinder(d = microchannel_dia, h = hole_length);
    }
}

// ============================================================
// Render
// ============================================================
bottom_mold();
