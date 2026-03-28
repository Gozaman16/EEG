// ============================================================
// HairSite Mold — BOTTOM PIECE
// Hair-penetrating pin variant of EpiScreen
// ============================================================
// Key difference from standard EpiScreen bottom:
//   - No raised spiral platform (flush for conductive coating)
//   - 7 blind holes (wells) that create silicone pins on the
//     finished electrode for penetrating through hair
//   - Capillary web ridges connecting pin wells for electrolyte
//     wicking from microchannels to pin tips
//   - Micro-texture between pins (not under pins)
// ============================================================
include <hairsite_mold_parameters.scad>;

function drafted_r(base_r, h) =
    base_r + h * tan(draft_angle);

// ============================================================
// Pin well positions — hexagonal pattern
// Returns [x, y] for pin index i
// ============================================================
function pin_pos(i) =
    (i == 0) ? [0, 0] :  // center pin
    [pin_ring_radius * cos((i-1) * 360 / pin_ring_count),
     pin_ring_radius * sin((i-1) * 360 / pin_ring_count)];

// ============================================================
// Main bottom mold piece
// ============================================================
module bottom_mold() {
    difference() {
        union() {
            // --- Outer shell ---
            bottom_shell();

            // --- Bottom surface ring (raised annulus) ---
            // Creates the recess zone around the pin area
            translate([0, 0, base_plate_thick])
                bottom_surface_ring();

            // --- Micro-texture concentric rings between pins ---
            translate([0, 0, base_plate_thick])
                bottom_texture_between_pins();

            // --- Capillary web ridges connecting pin wells ---
            translate([0, 0, base_plate_thick])
                capillary_web_ridges();

            // --- FR-4 seat ledge ---
            translate([0, 0, base_plate_thick])
                fr4_seat();
        }

        // --- Internal electrode cavity (bottom half) ---
        translate([0, 0, base_plate_thick])
            electrode_cavity_bottom();

        // --- Pin wells (blind holes for creating silicone pins) ---
        translate([0, 0, base_plate_thick])
            pin_wells();

        // --- Alignment pin holes on top rim ---
        translate([0, 0, base_plate_thick + parting_z])
            alignment_pin_holes();

        // --- Microchannel guide holes ---
        microchannel_holes();
    }
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
// Bottom surface ring — raised annulus outside bottom cavity
// ============================================================
module bottom_surface_ring() {
    difference() {
        cylinder(r = electrode_radius, h = bottom_cavity_depth);
        translate([0, 0, -0.01])
            cylinder(r = bottom_cavity_r, h = bottom_cavity_depth + 0.02);
    }
}

// ============================================================
// Pin wells — 7 blind holes (negative of the silicone pins)
//
// Each well is a tapered cylinder with hemispherical bottom:
//   - Opens at the mold cavity floor (electrode bottom surface)
//   - 2.0mm dia at top (mold surface), 1.5mm at bottom
//   - 3.0mm deep into the base plate
//   - Hemispherical concavity at bottom (rounded pin tip)
//
// Silicone fills these during casting, creating tapered pins
// with rounded tips on the finished electrode.
// ============================================================
module pin_wells() {
    for (i = [0 : pin_total - 1]) {
        pos = pin_pos(i);
        translate([pos[0], pos[1], 0]) {
            // Tapered well: wider at top (mold surface), narrower at bottom
            // Goes downward INTO the base plate (negative z direction)
            translate([0, 0, -pin_height])
                cylinder(d1 = pin_tip_dia, d2 = pin_base_dia, h = pin_height + 0.01);

            // Hemispherical concavity at well bottom (creates dome tip on pin)
            translate([0, 0, -pin_height])
                sphere(r = pin_tip_r);
        }
    }
}

// ============================================================
// Capillary web ridges
//
// Thin raised ridges on the mold floor connecting adjacent
// pin wells. These create shallow silicone channels between
// pins on the finished electrode. The channels wick
// electrolyte from microchannels to pin tips via capillary
// action, maintaining consistent skin contact impedance.
//
// Topology: center pin connects to all 6 outer pins (6 spokes)
// + outer pins connect to their neighbors (6 ring segments)
// = 12 total ridges
// ============================================================
module capillary_web_ridges() {
    // Spokes: center to each outer pin
    for (i = [1 : pin_ring_count]) {
        pos_outer = pin_pos(i);
        ridge_between([0, 0], pos_outer);
    }

    // Ring segments: each outer pin to its neighbor
    for (i = [1 : pin_ring_count]) {
        next = (i < pin_ring_count) ? i + 1 : 1;
        pos_a = pin_pos(i);
        pos_b = pin_pos(next);
        ridge_between(pos_a, pos_b);
    }
}

// Single ridge between two points on the mold floor
module ridge_between(p1, p2) {
    dx = p2[0] - p1[0];
    dy = p2[1] - p1[1];
    length = sqrt(dx*dx + dy*dy);
    angle = atan2(dy, dx);

    translate([p1[0], p1[1], 0])
        rotate([0, 0, angle])
            translate([0, -web_ridge_width/2, 0])
                cube([length, web_ridge_width, web_ridge_height]);
}

// ============================================================
// Bottom cavity micro-texture (concentric rings BETWEEN pins)
// Applied to the bottom cavity floor area, but the pin wells
// cut through them, so texture only remains between pins.
// ============================================================
module bottom_texture_between_pins() {
    for (r_pos = [1 : texture_ring_spacing : bottom_cavity_r - 0.3]) {
        difference() {
            cylinder(r = r_pos + 0.1, h = texture_ring_depth);
            translate([0, 0, -0.01])
                cylinder(r = r_pos - 0.1, h = texture_ring_depth + 0.02);
        }
    }
}

// ============================================================
// FR-4 seat ledge (identical to standard)
// ============================================================
module fr4_seat() {
    wall_r_at_seat = drafted_r(electrode_radius, fr4_seat_z);

    if (fr4_seat_z < parting_z) {
        translate([0, 0, fr4_seat_z]) {
            difference() {
                cylinder(r = wall_r_at_seat, h = fr4_thickness);
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
}

// ============================================================
// Alignment pin holes (identical to standard)
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
// Microchannel guide holes (identical to standard)
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
