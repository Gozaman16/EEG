// ============================================================
// HairSite Mold — CROSS-SECTION ASSEMBLY VIEW
// Shows pin wells, capillary ridges, and how top/bottom mate
// ============================================================
include <hairsite_mold_parameters.scad>;

function drafted_r(base_r, h) =
    base_r + h * tan(draft_angle);

function pin_pos(i) =
    (i == 0) ? [0, 0] :
    [pin_ring_radius * cos((i-1) * 360 / pin_ring_count),
     pin_ring_radius * sin((i-1) * 360 / pin_ring_count)];

// ============================================================
// Bottom mold solid
// ============================================================
module bottom_solid() {
    difference() {
        union() {
            minkowski() {
                cylinder(r = mold_radius - fillet_r,
                         h = base_plate_thick + parting_z - fillet_r);
                sphere(r = fillet_r);
            }

            // Bottom surface ring
            translate([0, 0, base_plate_thick])
            difference() {
                cylinder(r = electrode_radius, h = bottom_cavity_depth);
                translate([0, 0, -0.01])
                    cylinder(r = bottom_cavity_r, h = bottom_cavity_depth + 0.02);
            }

            // Capillary web ridges
            translate([0, 0, base_plate_thick]) {
                for (i = [1 : pin_ring_count]) {
                    pos_o = pin_pos(i);
                    dx = pos_o[0]; dy = pos_o[1];
                    len = sqrt(dx*dx + dy*dy);
                    ang = atan2(dy, dx);
                    translate([0, 0, 0]) rotate([0, 0, ang])
                        translate([0, -web_ridge_width/2, 0])
                            cube([len, web_ridge_width, web_ridge_height]);
                }
                for (i = [1 : pin_ring_count]) {
                    next = (i < pin_ring_count) ? i + 1 : 1;
                    pa = pin_pos(i); pb = pin_pos(next);
                    dx = pb[0]-pa[0]; dy = pb[1]-pa[1];
                    len = sqrt(dx*dx + dy*dy);
                    ang = atan2(dy, dx);
                    translate([pa[0], pa[1], 0]) rotate([0, 0, ang])
                        translate([0, -web_ridge_width/2, 0])
                            cube([len, web_ridge_width, web_ridge_height]);
                }
            }

            // FR-4 seat
            wall_r = drafted_r(electrode_radius, fr4_seat_z);
            translate([0, 0, base_plate_thick + fr4_seat_z]) {
                difference() {
                    cylinder(r = wall_r, h = fr4_thickness);
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

        // Electrode cavity
        translate([0, 0, base_plate_thick])
            cylinder(r1 = electrode_radius,
                     r2 = drafted_r(electrode_radius, parting_z),
                     h = parting_z + 0.01);

        // Pin wells
        translate([0, 0, base_plate_thick])
        for (i = [0 : pin_total - 1]) {
            pos = pin_pos(i);
            translate([pos[0], pos[1], -pin_height])
                cylinder(d1 = pin_tip_dia, d2 = pin_base_dia, h = pin_height + 0.01);
            translate([pos[0], pos[1], -pin_height])
                sphere(r = pin_tip_r);
        }

        // Pin holes and microchannel holes
        translate([0, 0, base_plate_thick + parting_z])
        for (i = [0 : pin_count - 1]) {
            angle = i * 360 / pin_count;
            rotate([0, 0, angle])
                translate([pin_ring_r, 0, -pin_depth])
                    cylinder(d = pin_dia + clearance, h = pin_depth + 0.01);
        }
        for (i = [0 : microchannel_count - 1]) {
            angle = i * 360 / microchannel_count;
            rotate([0, 0, angle])
                translate([reservoir_od/2, 0, base_plate_thick + reservoir_z])
                    rotate([0, 90 - microchannel_angle, 0])
                        cylinder(d = microchannel_dia, h = 20);
        }
    }
}

// ============================================================
// Top mold solid
// ============================================================
module top_solid() {
    top_h = electrode_height - parting_z;
    lid_thick = wall_thickness + 2.0;
    total_h = top_h + lid_thick;

    difference() {
        minkowski() {
            cylinder(r = mold_radius - fillet_r, h = total_h - fillet_r);
            sphere(r = fillet_r);
        }
        r_b = drafted_r(electrode_radius, parting_z);
        r_t = drafted_r(electrode_radius, electrode_height);
        translate([0, 0, -0.01])
            cylinder(r1 = r_b, r2 = r_t, h = top_h + 0.01);
        translate([0, 0, top_h - 0.01])
            cylinder(d = pour_hole_dia, h = lid_thick + 1);
        vent_r = electrode_radius * 0.6;
        for (i = [0 : vent_count - 1]) {
            angle = 180 + i * 60;
            rotate([0, 0, angle])
                translate([vent_r, 0, top_h - 0.01])
                    cylinder(d = vent_hole_dia, h = lid_thick + 1);
        }
        cable_z = max(cable_start_z - parting_z, 0);
        cable_h = total_h - cable_z + 1;
        translate([0, 0, cable_z])
        hull() {
            translate([electrode_radius-1, -cable_width_bottom/2, 0])
                cube([mold_radius, cable_width_bottom, 0.01]);
            translate([electrode_radius-1, -cable_width_top/2, cable_h])
                cube([mold_radius, cable_width_top, 0.01]);
        }
        fill_r = (reservoir_id/2 + reservoir_od/2) / 2;
        ring_z = reservoir_z - parting_z;
        translate([0, fill_r, ring_z])
            cylinder(d = reservoir_port_dia, h = total_h + 1);
    }

    // Pins
    for (i = [0 : pin_count - 1]) {
        angle = i * 360 / pin_count;
        rotate([0, 0, angle])
            translate([pin_ring_r, 0, -pin_depth])
                cylinder(d = pin_dia, h = pin_depth);
    }

    // Reservoir ring
    ring_z = reservoir_z - parting_z;
    if (ring_z >= 0)
        translate([0, 0, ring_z])
        difference() {
            cylinder(r = reservoir_od/2, h = reservoir_height);
            translate([0, 0, -0.01])
                cylinder(r = reservoir_id/2, h = reservoir_height + 0.02);
        }
}

// ============================================================
// Reference: FR-4 disk
// ============================================================
module fr4_disk() {
    color("green", 0.8)
    translate([0, 0, base_plate_thick + fr4_seat_z])
        cylinder(r = fr4_seat_r, h = fr4_thickness);
}

// ============================================================
// Reference: silicone pins (what the electrode looks like)
// ============================================================
module silicone_pins_ref() {
    color("Plum", 0.6)
    translate([0, 0, base_plate_thick])
    for (i = [0 : pin_total - 1]) {
        pos = pin_pos(i);
        translate([pos[0], pos[1], -pin_height]) {
            cylinder(d1 = pin_tip_dia, d2 = pin_base_dia, h = pin_height);
            sphere(r = pin_tip_r);
        }
    }
}

// ============================================================
// Assembly cross-section
// ============================================================
module assembly() {
    difference() {
        union() {
            color("SteelBlue", 0.7)  bottom_solid();
            color("IndianRed", 0.7)
                translate([0, 0, base_plate_thick + parting_z + clearance])
                    top_solid();
            fr4_disk();
            silicone_pins_ref();
        }
        // Cut front half
        translate([0, -50, -10]) cube([100, 50, 100]);
    }
}

assembly();
