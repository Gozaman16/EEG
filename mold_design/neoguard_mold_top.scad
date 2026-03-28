// ============================================================
// NeoGuard Neonatal Mold — TOP PIECE (Lid)
// ============================================================
include <neoguard_mold_parameters.scad>;

function drafted_r(base_r, h) =
    base_r + h * tan(draft_angle);

// ============================================================
// Main top mold piece
// ============================================================
module top_mold() {
    difference() {
        top_shell();

        // Electrode cavity (top half)
        electrode_cavity_top();

        // Pour hole
        pour_hole();

        // Vent holes
        vent_holes();

        // Cable exit channel
        cable_exit();

        // Reservoir fill port
        reservoir_fill_port();
    }

    // Alignment pins (protrude downward)
    alignment_pins();

    // Reservoir ring protrusion
    reservoir_ring();
}

// ============================================================
// Outer shell
// ============================================================
module top_shell() {
    top_cavity_h = electrode_height - parting_z;
    lid_thickness = wall_thickness + 2.0;
    total_h = top_cavity_h + lid_thickness;

    minkowski() {
        cylinder(r = mold_radius - fillet_r, h = total_h - fillet_r);
        sphere(r = fillet_r);
    }
}

// ============================================================
// Electrode cavity — top half
// ============================================================
module electrode_cavity_top() {
    top_cavity_h = electrode_height - parting_z;
    r_bottom = drafted_r(electrode_radius, parting_z);
    r_top = drafted_r(electrode_radius, electrode_height);

    translate([0, 0, -0.01])
        cylinder(r1 = r_bottom, r2 = r_top, h = top_cavity_h + 0.01);
}

// ============================================================
// Reservoir ring protrusion
// ============================================================
module reservoir_ring() {
    ring_z = reservoir_z - parting_z;

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
// Pour hole
// ============================================================
module pour_hole() {
    top_cavity_h = electrode_height - parting_z;
    lid_thickness = wall_thickness + 2.0;

    translate([0, 0, top_cavity_h - 0.01])
        cylinder(d = pour_hole_dia, h = lid_thickness + 1);
}

// ============================================================
// Vent holes
// ============================================================
module vent_holes() {
    top_cavity_h = electrode_height - parting_z;
    lid_thickness = wall_thickness + 2.0;
    vent_r_pos = electrode_radius * 0.6;

    for (i = [0 : vent_count - 1]) {
        angle = 180 + i * 60;
        rotate([0, 0, angle])
            translate([vent_r_pos, 0, top_cavity_h - 0.01])
                cylinder(d = vent_hole_dia, h = lid_thickness + 1);
    }
}

// ============================================================
// Cable exit channel
// ============================================================
module cable_exit() {
    cable_z = max(cable_start_z - parting_z, 0);
    top_cavity_h = electrode_height - parting_z;
    lid_thickness = wall_thickness + 2.0;
    cable_h = top_cavity_h + lid_thickness - cable_z + 1;

    translate([0, 0, cable_z]) {
        hull() {
            translate([electrode_radius - 1, -cable_width_bottom/2, 0])
                cube([mold_radius, cable_width_bottom, 0.01]);
            translate([electrode_radius - 1, -cable_width_top/2, cable_h])
                cube([mold_radius, cable_width_top, 0.01]);
        }
    }
}

// ============================================================
// Alignment pins
// ============================================================
module alignment_pins() {
    for (i = [0 : pin_count - 1]) {
        angle = i * 360 / pin_count;
        rotate([0, 0, angle])
            translate([pin_ring_r, 0, -pin_depth])
                cylinder(d = pin_dia, h = pin_depth);
    }
}

// ============================================================
// Reservoir fill port
// ============================================================
module reservoir_fill_port() {
    top_cavity_h = electrode_height - parting_z;
    lid_thickness = wall_thickness + 2.0;
    fill_r_pos = (reservoir_id/2 + reservoir_od/2) / 2;
    ring_z = reservoir_z - parting_z;

    translate([0, fill_r_pos, ring_z])
        cylinder(d = reservoir_port_dia, h = top_cavity_h + lid_thickness + 1);
}

// ============================================================
// Render
// ============================================================
top_mold();
