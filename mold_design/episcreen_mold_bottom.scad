// ============================================================
// EpiScreen Mold — BOTTOM PIECE
// ============================================================
include <episcreen_mold_parameters.scad>;

// Draft angle helper: given a radius at base_z, compute radius
// at height h above base_z (cavity expands outward going up for
// internal walls so electrode can be demolded).
function drafted_r(base_r, h) =
    base_r + h * tan(draft_angle);

// ============================================================
// Main bottom mold piece
// ============================================================
module bottom_mold() {
    difference() {
        // --- Outer shell ---
        bottom_shell();

        // --- Internal electrode cavity (bottom half: 0 to parting_z) ---
        translate([0, 0, base_plate_thick])
            electrode_cavity_bottom();

        // --- Bottom surface cavity bump (creates recess in electrode) ---
        // This is a protrusion in the mold that creates the
        // bottom surface cavity in the electrode. We subtract
        // nothing here; the bump is added as positive geometry.
        // Actually: the bottom cavity is a RECESS in the electrode
        // bottom, meaning the mold floor has a RAISED area except
        // where the cavity is. Let me reconsider:
        // The electrode has a 12mm dia, 1mm deep recess on its
        // bottom (skin-contact side). In the mold, the floor is
        // flat, and the 12mm circle is 1mm LOWER than the
        // surrounding floor — i.e., the surrounding annular ring
        // is raised 1mm. Actually no: the mold cavity floor IS
        // the electrode bottom. A 1mm deep recess in the electrode
        // bottom means the mold floor has a 1mm tall raised ring
        // around the 12mm area...
        //
        // Simpler: electrode bottom is at z=base_plate_thick.
        // The 12mm cavity is 1mm deep INTO the electrode bottom,
        // meaning the mold has a bump (protrusion into cavity)
        // that is the area OUTSIDE the 12mm circle, 1mm tall.
        // Wait — a cavity in the skin-contact side means that
        // side has a concave area. The mold creates this by having
        // a convex protrusion. So the mold floor inside 12mm dia
        // is 1mm LOWER than outside it. The cavity is cut by the
        // main electrode cavity cut; we need to ADD material as
        // a ring from 12mm to 24mm dia at 1mm height.

        // --- Alignment pin holes on top rim ---
        translate([0, 0, base_plate_thick + parting_z])
            alignment_pin_holes();

        // --- Microchannel guide holes ---
        microchannel_holes();
    }

    // --- Bottom surface cavity ring (raised annulus) ---
    // Creates the 1mm deep recess in electrode's skin-contact side
    translate([0, 0, base_plate_thick])
        bottom_surface_ring();

    // --- Spiral exposure platform ---
    translate([0, 0, base_plate_thick])
        spiral_platform();

    // --- Micro-texture concentric rings on bottom cavity floor ---
    translate([0, 0, base_plate_thick])
        bottom_texture();

    // --- FR-4 seat ledge ---
    translate([0, 0, base_plate_thick])
        fr4_seat();
}

// ============================================================
// Outer shell of bottom mold
// ============================================================
module bottom_shell() {
    // Base plate + walls up to parting line
    total_h = base_plate_thick + parting_z;

    // Filleted cylinder
    minkowski() {
        cylinder(r = mold_radius - fillet_r, h = total_h - fillet_r);
        sphere(r = fillet_r);
    }
}

// ============================================================
// Electrode cavity — bottom half (0 to parting_z)
// ============================================================
module electrode_cavity_bottom() {
    // Main cylindrical cavity with draft angle
    // At z=0 (bottom of electrode), radius = electrode_radius
    // At z=parting_z, radius = electrode_radius + parting_z*tan(draft)

    // Approximate drafted cylinder as a cone
    cylinder(
        r1 = electrode_radius,
        r2 = drafted_r(electrode_radius, parting_z),
        h = parting_z + 0.01
    );
}

// ============================================================
// Bottom surface ring — creates 1mm recess in electrode bottom
// ============================================================
module bottom_surface_ring() {
    // Raised annular ring: from bottom_cavity_r to electrode_radius
    // height = bottom_cavity_depth (1mm)
    difference() {
        cylinder(r = electrode_radius, h = bottom_cavity_depth);
        translate([0, 0, -0.01])
            cylinder(r = bottom_cavity_r, h = bottom_cavity_depth + 0.02);
    }
}

// ============================================================
// Spiral exposure platform
// ============================================================
module spiral_platform() {
    // Raised 8mm dia platform in center of bottom cavity floor
    // Height 0.8mm (less than 1mm cavity depth)
    // With light texture grooves

    difference() {
        cylinder(r = spiral_platform_r, h = spiral_platform_height);

        // Radial texture grooves (concentric rings on top surface)
        for (r_pos = [1 : groove_spacing : spiral_platform_r - 0.3]) {
            translate([0, 0, spiral_platform_height - groove_depth])
                difference() {
                    cylinder(r = r_pos + 0.1, h = groove_depth + 0.01);
                    cylinder(r = r_pos - 0.1, h = groove_depth + 0.02);
                }
        }
    }
}

// ============================================================
// Bottom cavity micro-texture (concentric rings)
// ============================================================
module bottom_texture() {
    // Concentric rings on the floor of the bottom cavity
    // (the 12mm dia recessed area)
    // These are raised rings on the mold floor = grooves in electrode
    for (r_pos = [1 : texture_ring_spacing : bottom_cavity_r - 0.3]) {
        difference() {
            cylinder(r = r_pos + 0.1, h = texture_ring_depth);
            translate([0, 0, -0.01])
                cylinder(r = r_pos - 0.1, h = texture_ring_depth + 0.02);
        }
    }
}

// ============================================================
// FR-4 seat ledge
// ============================================================
module fr4_seat() {
    // An inward-facing shelf at z = fr4_seat_z
    // The FR-4 disk (19mm dia) rests on this ledge
    // Shelf is the annular step from electrode wall inward
    // With 0.2mm lip above to keep FR-4 centered

    seat_inner_r = fr4_seat_r;
    // The ledge is part of the wall — we add material inward
    // from the drafted cavity wall at that height

    wall_r_at_seat = drafted_r(electrode_radius, fr4_seat_z);
    ledge_width = wall_r_at_seat - seat_inner_r;

    // Only add the ledge if within bottom half
    if (fr4_seat_z < parting_z) {
        translate([0, 0, fr4_seat_z]) {
            // Ledge ring
            difference() {
                cylinder(r = wall_r_at_seat, h = fr4_thickness);
                translate([0, 0, -0.01])
                    cylinder(r = seat_inner_r, h = fr4_thickness + 0.02);
            }
            // Centering lip (0.2mm above ledge surface)
            translate([0, 0, 0]) {
                difference() {
                    cylinder(r = seat_inner_r + 0.3, h = fr4_lip);
                    translate([0, 0, -0.01])
                        cylinder(r = seat_inner_r, h = fr4_lip + 0.02);
                }
            }
        }
    }
}

// ============================================================
// Alignment pin HOLES in bottom piece (pins are on top piece)
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
// Microchannel guide holes
// ============================================================
module microchannel_holes() {
    // 3 holes at 120° spacing
    // Each goes from outer edge of reservoir ring down to
    // bottom cavity at ~37.5° from vertical

    reservoir_mid_r = (reservoir_id/2 + reservoir_od/2) / 2;

    for (i = [0 : microchannel_count - 1]) {
        angle = i * 360 / microchannel_count;

        // Start point: reservoir ring outer edge at reservoir_z height
        start_z = base_plate_thick + reservoir_z;
        // End point: bottom cavity floor
        end_z = base_plate_thick;

        // The hole goes from mold exterior through to cavity
        hole_length = 20; // long enough to go through

        rotate([0, 0, angle])
            translate([reservoir_od/2, 0, start_z])
                rotate([0, 90 - microchannel_angle, 0])
                    cylinder(d = microchannel_dia, h = hole_length, center = false);
    }
}

// ============================================================
// Render
// ============================================================
bottom_mold();
