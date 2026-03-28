// ============================================================
// EpiScreen Mold — TOP PIECE (Lid)
// ============================================================
include <episcreen_mold_parameters.scad>;

// Draft angle helper
function drafted_r(base_r, h) =
    base_r + h * tan(draft_angle);

// ============================================================
// Main top mold piece
// ============================================================
module top_mold() {
    difference() {
        // --- Outer shell ---
        top_shell();

        // --- Internal electrode cavity (top half: parting_z to electrode_height) ---
        translate([0, 0, 0])
            electrode_cavity_top();

        // --- Pour hole ---
        pour_hole();

        // --- Vent holes ---
        vent_holes();

        // --- Cable exit channel ---
        cable_exit();

        // --- Reservoir fill port ---
        reservoir_fill_port();
    }

    // --- Alignment pins (protrude downward) ---
    alignment_pins();

    // --- Reservoir ring protrusion ---
    // Creates the ring-shaped void in the electrode
    reservoir_ring();
}

// ============================================================
// Outer shell of top mold
// ============================================================
module top_shell() {
    top_cavity_h = electrode_height - parting_z;
    // Wall above parting line + some lid thickness
    lid_thickness = wall_thickness + 2.0;  // solid top
    total_h = top_cavity_h + lid_thickness;

    minkowski() {
        cylinder(r = mold_radius - fillet_r, h = total_h - fillet_r);
        sphere(r = fillet_r);
    }
}

// ============================================================
// Electrode cavity — top half (parting_z to electrode_height)
// Cavity opens downward (the top piece flips onto the bottom)
// Convention: z=0 at parting line, cavity goes UP to top_cavity_h
// ============================================================
module electrode_cavity_top() {
    top_cavity_h = electrode_height - parting_z;

    // Drafted cylinder — radius at parting line is larger,
    // narrows going up (draft for demolding)
    // At z=0 (parting line), r = drafted_r(electrode_radius, parting_z)
    // At z=top_cavity_h, r = drafted_r(electrode_radius, electrode_height)
    r_bottom = drafted_r(electrode_radius, parting_z);
    r_top = drafted_r(electrode_radius, electrode_height);

    translate([0, 0, -0.01])
        cylinder(r1 = r_bottom, r2 = r_top, h = top_cavity_h + 0.01);
}

// ============================================================
// Reservoir ring protrusion
// Creates the ring-shaped void in the electrode silicone
// ============================================================
module reservoir_ring() {
    // Position relative to top mold: reservoir_z is measured from
    // electrode bottom. In top mold coordinates (z=0 at parting),
    // reservoir starts at reservoir_z - parting_z
    ring_z = reservoir_z - parting_z;

    // Only render if reservoir is in top half
    if (ring_z >= 0) {
        translate([0, 0, ring_z]) {
            difference() {
                cylinder(r = reservoir_od / 2, h = reservoir_height);
                translate([0, 0, -0.01])
                    cylinder(r = reservoir_id / 2, h = reservoir_height + 0.02);
            }
        }
    }
}

// ============================================================
// Pour hole (centered on top)
// ============================================================
module pour_hole() {
    top_cavity_h = electrode_height - parting_z;
    lid_thickness = wall_thickness + 2.0;
    total_h = top_cavity_h + lid_thickness;

    translate([0, 0, top_cavity_h - 0.01])
        cylinder(d = pour_hole_dia, h = lid_thickness + 1);
}

// ============================================================
// Vent holes (2 small holes at edges, opposite to pour hole)
// ============================================================
module vent_holes() {
    top_cavity_h = electrode_height - parting_z;
    lid_thickness = wall_thickness + 2.0;
    total_h = top_cavity_h + lid_thickness;

    vent_r_pos = electrode_radius * 0.6; // offset from center

    for (i = [0 : vent_count - 1]) {
        angle = 180 + i * 60; // opposite side from pour position
        rotate([0, 0, angle])
            translate([vent_r_pos, 0, top_cavity_h - 0.01])
                cylinder(d = vent_hole_dia, h = lid_thickness + 1);
    }
}

// ============================================================
// Cable exit channel
// ============================================================
module cable_exit() {
    // Notch on side wall from FR-4 level to top
    // In top mold coords: starts at cable_start_z - parting_z
    cable_z = cable_start_z - parting_z;
    top_cavity_h = electrode_height - parting_z;
    lid_thickness = wall_thickness + 2.0;

    // Funnel shape: wider at top (4mm), narrower at bottom (3mm)
    cable_h = top_cavity_h + lid_thickness - max(cable_z, 0) + 1;
    start_z = max(cable_z, 0);

    translate([0, 0, start_z]) {
        // Position at edge of cavity
        hull() {
            // Bottom of channel (narrower)
            translate([electrode_radius - 1, 0, 0])
                cube([mold_radius, cable_width_bottom, 0.01], center = false);
            // Move to the correct centering
            translate([electrode_radius - 1, -cable_width_bottom/2, 0])
                cube([mold_radius, cable_width_bottom, 0.01]);

            // Top of channel (wider)
            translate([electrode_radius - 1, -cable_width_top/2, cable_h])
                cube([mold_radius, cable_width_top, 0.01]);
        }
    }
}

// ============================================================
// Alignment pins (protrude from bottom face of top piece)
// ============================================================
module alignment_pins() {
    for (i = [0 : pin_count - 1]) {
        angle = i * 360 / pin_count;
        rotate([0, 0, angle])
            translate([pin_ring_r, 0, 0])
                // Pin extends below z=0 (into bottom piece holes)
                translate([0, 0, -pin_depth])
                    cylinder(d = pin_dia, h = pin_depth);
    }
}

// ============================================================
// Reservoir fill port
// ============================================================
module reservoir_fill_port() {
    top_cavity_h = electrode_height - parting_z;
    lid_thickness = wall_thickness + 2.0;

    // Position above reservoir ring midpoint
    fill_r_pos = (reservoir_id/2 + reservoir_od/2) / 2;

    ring_z = reservoir_z - parting_z;

    translate([0, fill_r_pos, ring_z])
        cylinder(d = reservoir_port_dia, h = top_cavity_h + lid_thickness + 1);
}

// ============================================================
// Render
// ============================================================
top_mold();
