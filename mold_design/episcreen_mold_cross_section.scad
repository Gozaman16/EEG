// ============================================================
// EpiScreen Mold — CROSS-SECTION ASSEMBLY VIEW
// Shows how top and bottom pieces fit together
// with FR-4 disk and spiral platform visible
// ============================================================
include <episcreen_mold_parameters.scad>;

function drafted_r(base_r, h) =
    base_r + h * tan(draft_angle);

// ============================================================
// Bottom mold (simplified for cross-section)
// ============================================================
module bottom_mold_solid() {
    difference() {
        // Outer shell
        minkowski() {
            cylinder(r = mold_radius - fillet_r, h = base_plate_thick + parting_z - fillet_r);
            sphere(r = fillet_r);
        }

        // Electrode cavity
        translate([0, 0, base_plate_thick])
            cylinder(r1 = electrode_radius, r2 = drafted_r(electrode_radius, parting_z),
                     h = parting_z + 0.01);

        // Pin holes
        translate([0, 0, base_plate_thick + parting_z])
        for (i = [0 : pin_count - 1]) {
            angle = i * 360 / pin_count;
            rotate([0, 0, angle])
                translate([pin_ring_r, 0, -pin_depth])
                    cylinder(d = pin_dia + clearance, h = pin_depth + 0.01);
        }

        // Microchannel holes
        reservoir_mid_r = (reservoir_id/2 + reservoir_od/2) / 2;
        for (i = [0 : microchannel_count - 1]) {
            angle = i * 360 / microchannel_count;
            rotate([0, 0, angle])
                translate([reservoir_od/2, 0, base_plate_thick + reservoir_z])
                    rotate([0, 90 - microchannel_angle, 0])
                        cylinder(d = microchannel_dia, h = 20);
        }
    }

    // Bottom surface ring
    translate([0, 0, base_plate_thick])
    difference() {
        cylinder(r = electrode_radius, h = bottom_cavity_depth);
        translate([0, 0, -0.01])
            cylinder(r = bottom_cavity_r, h = bottom_cavity_depth + 0.02);
    }

    // Spiral platform
    translate([0, 0, base_plate_thick])
        cylinder(r = spiral_platform_r, h = spiral_platform_height);

    // FR-4 seat
    translate([0, 0, base_plate_thick + fr4_seat_z]) {
        difference() {
            cylinder(r = drafted_r(electrode_radius, fr4_seat_z), h = fr4_thickness);
            translate([0, 0, -0.01])
                cylinder(r = fr4_seat_r, h = fr4_thickness + 0.02);
        }
        difference() {
            cylinder(r = fr4_seat_r + 0.3, h = fr4_lip);
            translate([0, 0, -0.01])
                cylinder(r = fr4_seat_r, h = fr4_lip + 0.02);
        }
    }
}

// ============================================================
// Top mold (simplified for cross-section)
// ============================================================
module top_mold_solid() {
    top_h = electrode_height - parting_z;
    lid_thick = wall_thickness + 2.0;
    total_h = top_h + lid_thick;

    difference() {
        // Outer shell
        minkowski() {
            cylinder(r = mold_radius - fillet_r, h = total_h - fillet_r);
            sphere(r = fillet_r);
        }

        // Electrode cavity
        r_bottom = drafted_r(electrode_radius, parting_z);
        r_top = drafted_r(electrode_radius, electrode_height);
        translate([0, 0, -0.01])
            cylinder(r1 = r_bottom, r2 = r_top, h = top_h + 0.01);

        // Pour hole
        translate([0, 0, top_h - 0.01])
            cylinder(d = pour_hole_dia, h = lid_thick + 1);

        // Vent holes
        vent_r_pos = electrode_radius * 0.6;
        for (i = [0 : vent_count - 1]) {
            angle = 180 + i * 60;
            rotate([0, 0, angle])
                translate([vent_r_pos, 0, top_h - 0.01])
                    cylinder(d = vent_hole_dia, h = lid_thick + 1);
        }

        // Cable exit
        cable_z = max(cable_start_z - parting_z, 0);
        cable_h = total_h - cable_z + 1;
        translate([0, 0, cable_z])
        hull() {
            translate([electrode_radius - 1, -cable_width_bottom/2, 0])
                cube([mold_radius, cable_width_bottom, 0.01]);
            translate([electrode_radius - 1, -cable_width_top/2, cable_h])
                cube([mold_radius, cable_width_top, 0.01]);
        }

        // Reservoir fill port
        fill_r_pos = (reservoir_id/2 + reservoir_od/2) / 2;
        ring_z = reservoir_z - parting_z;
        translate([0, fill_r_pos, ring_z])
            cylinder(d = reservoir_port_dia, h = total_h + 1);
    }

    // Alignment pins
    for (i = [0 : pin_count - 1]) {
        angle = i * 360 / pin_count;
        rotate([0, 0, angle])
            translate([pin_ring_r, 0, -pin_depth])
                cylinder(d = pin_dia, h = pin_depth);
    }

    // Reservoir ring protrusion
    ring_z = reservoir_z - parting_z;
    if (ring_z >= 0) {
        translate([0, 0, ring_z])
        difference() {
            cylinder(r = reservoir_od / 2, h = reservoir_height);
            translate([0, 0, -0.01])
                cylinder(r = reservoir_id / 2, h = reservoir_height + 0.02);
        }
    }
}

// ============================================================
// FR-4 disk (shown for reference in assembly)
// ============================================================
module fr4_disk() {
    color("green", 0.8)
    translate([0, 0, base_plate_thick + fr4_seat_z])
        cylinder(r = fr4_seat_r, h = fr4_thickness);
}

// ============================================================
// Copper spiral (shown for reference)
// ============================================================
module copper_spiral() {
    color("orange", 0.8)
    translate([0, 0, base_plate_thick])
        cylinder(r = spiral_platform_r - 0.5, h = 0.1);
}

// ============================================================
// Assembly with cross-section cut
// ============================================================
module assembly_cross_section() {
    // Cut plane: remove front half to show cross-section
    difference() {
        union() {
            // Bottom mold (blue)
            color("SteelBlue", 0.7)
                bottom_mold_solid();

            // Top mold, positioned on top of bottom mold (red/orange)
            color("IndianRed", 0.7)
            translate([0, 0, base_plate_thick + parting_z + clearance])
                top_mold_solid();

            // FR-4 disk
            fr4_disk();

            // Copper spiral
            copper_spiral();
        }

        // Cross-section cut — remove front half
        translate([0, -50, -10])
            cube([100, 50, 100]);
    }
}

assembly_cross_section();
