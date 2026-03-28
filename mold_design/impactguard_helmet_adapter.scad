// ============================================================
// ImpactGuard Helmet Mount Adapter
// Holds standard 24mm EEG electrode inside boxing headgear
// Direct-print functional part (not a mold)
// ============================================================

// --- Base plate ---
base_w          = 35;       // width (X)
base_d          = 35;       // depth (Y)
base_t          = 2;        // thickness
curve_radius    = 90;       // radius of curvature (head shape)

// --- Electrode seat ---
seat_dia        = 24.5;     // 24mm electrode + 0.5mm clearance
seat_r          = seat_dia / 2;
seat_depth      = 5;        // how deep the electrode sits
skin_hole_dia   = 14;       // hole for pad to protrude through
skin_hole_r     = skin_hole_dia / 2;

// --- Retention clips ---
clip_count      = 3;
clip_width      = 1.0;
clip_height     = 3.0;
clip_thickness  = 0.8;      // wall thickness of clip
clip_overhang   = 0.6;      // how far clip tip extends inward

// --- Cable exit channel ---
cable_ch_width  = 4.0;
cable_ch_depth  = 2.5;      // depth of groove in base

// --- Mounting holes (sewing / zip-tie) ---
mount_hole_dia  = 2.0;
mount_hole_inset = 4.0;     // distance from edge to hole center

// --- Velcro-compatible surface ---
bump_size       = 0.5;      // bump diameter
bump_height     = 0.4;      // bump protrusion
bump_spacing    = 1.0;      // center-to-center

// --- Sweat drainage channels ---
drain_count     = 3;
drain_width     = 1.0;
drain_depth     = 0.5;
// Channels radiate outward from seat edge, offset from clips

// --- Print settings ---
fillet          = 0.3;
$fn             = 80;

// ============================================================
// Curved base plate
// The helmet-side surface is convex (matches head curvature),
// the skin-side surface follows the same curve.
// We intersect a flat slab with a sphere to get curvature.
// ============================================================
module curved_base() {
    // Create a curved plate by intersecting a box with a sphere
    // The sphere center is above the plate so the bottom surface
    // is concave (fits over convex head/helmet padding)
    intersection() {
        translate([-base_w/2, -base_d/2, 0])
            cube([base_w, base_d, base_t + 5]);

        // Sphere creates curvature — center above so bottom is concave
        translate([0, 0, -curve_radius + base_t])
            sphere(r = curve_radius);
    }
}

// ============================================================
// Electrode seat — circular recess for the 24mm electrode
// The electrode drops in pad-side-out (toward skin)
// ============================================================
module electrode_seat() {
    // Cylindrical recess cut into the skin side of the base
    translate([0, 0, -seat_depth + base_t])
        cylinder(r = seat_r, h = seat_depth + 0.01);
}

// ============================================================
// Skin contact hole — 14mm opening so electrode pad protrudes
// through the base plate to contact the athlete's skin
// ============================================================
module skin_hole() {
    translate([0, 0, -1])
        cylinder(r = skin_hole_r, h = base_t + seat_depth + 2);
}

// ============================================================
// Retention clips — 3 flexible tabs on seat inner wall
// These flex inward to grip the electrode rim, keeping it
// seated during impacts. Flex outward to release.
// ============================================================
module retention_clips() {
    for (i = [0 : clip_count - 1]) {
        angle = i * 360 / clip_count + 30; // offset from cable exit
        rotate([0, 0, angle])
            translate([seat_r - clip_thickness, -clip_width/2,
                       base_t - seat_depth]) {
                // Clip body — thin wall rising from seat floor
                cube([clip_thickness, clip_width, clip_height]);
                // Overhang tip — hooks inward to grip electrode edge
                translate([-clip_overhang, 0, clip_height - 0.8])
                    cube([clip_overhang + 0.01, clip_width, 0.8]);
            }
    }
}

// ============================================================
// Cable exit channel — groove from seat edge to base plate
// edge for routing the electrode cable out
// ============================================================
module cable_exit_channel() {
    // Cut a groove from seat edge to plate edge along +X axis
    translate([seat_r - 1, -cable_ch_width/2, base_t - cable_ch_depth])
        cube([base_w/2 - seat_r + 2, cable_ch_width, cable_ch_depth + 0.01]);
}

// ============================================================
// Mounting holes — 4 holes at corners for sewing or zip-ties
// to attach adapter to helmet interior padding
// ============================================================
module mounting_holes() {
    positions = [
        [ base_w/2 - mount_hole_inset,  base_d/2 - mount_hole_inset],
        [-base_w/2 + mount_hole_inset,  base_d/2 - mount_hole_inset],
        [ base_w/2 - mount_hole_inset, -base_d/2 + mount_hole_inset],
        [-base_w/2 + mount_hole_inset, -base_d/2 + mount_hole_inset]
    ];
    for (p = positions) {
        translate([p[0], p[1], -1])
            cylinder(d = mount_hole_dia, h = base_t + seat_depth + 2);
    }
}

// ============================================================
// Velcro-compatible surface — grid of small bumps on the
// helmet-facing (top/convex) surface for hook-and-loop grip.
// The bumps interlock with hook-side velcro on the helmet.
// ============================================================
module velcro_surface() {
    // Grid of bumps on the top surface of the base plate
    for (x = [-base_w/2 + 2 : bump_spacing : base_w/2 - 2]) {
        for (y = [-base_d/2 + 2 : bump_spacing : base_d/2 - 2]) {
            // Only place bumps outside the seat area and
            // outside mounting hole zones
            dist = sqrt(x*x + y*y);
            if (dist > seat_r + 1.5 &&
                abs(abs(x) - (base_w/2 - mount_hole_inset)) > 2 ||
                abs(abs(y) - (base_d/2 - mount_hole_inset)) > 2) {
                // Find the surface Z at this XY position on the curve
                z_at_point = base_t - (curve_radius -
                    sqrt(max(0, curve_radius*curve_radius - x*x - y*y)));
                if (dist > seat_r + 1) {
                    translate([x, y, base_t])
                        cylinder(d = bump_size, h = bump_height, $fn = 8);
                }
            }
        }
    }
}

// ============================================================
// Sweat drainage channels — shallow grooves radiating from
// the electrode seat to the base plate edges, preventing
// sweat from pooling around the electrode during activity
// ============================================================
module sweat_channels() {
    for (i = [0 : drain_count - 1]) {
        // Offset from retention clips by 60 degrees
        angle = i * 360 / drain_count + 90;
        rotate([0, 0, angle])
            translate([seat_r - 0.5, -drain_width/2,
                       base_t - drain_depth - 0.01])
                cube([base_w/2 - seat_r + 2, drain_width,
                      drain_depth + 0.01]);
    }
}

// ============================================================
// Seat wall — cylindrical wall around the electrode seat
// This wall extends above the base plate to create the recess
// ============================================================
module seat_wall() {
    wall_t = 1.5; // seat wall thickness
    difference() {
        cylinder(r = seat_r + wall_t, h = seat_depth);
        translate([0, 0, -0.01])
            cylinder(r = seat_r, h = seat_depth + 0.02);
    }
}

// ============================================================
// Full assembly
// ============================================================
module helmet_adapter() {
    difference() {
        union() {
            // Curved base plate
            curved_base();

            // Seat wall rising from base plate (helmet side)
            translate([0, 0, base_t])
                seat_wall();

            // Retention clips inside seat
            retention_clips();

            // Velcro bumps on top surface
            velcro_surface();
        }

        // Cut the electrode seat recess
        // (hollow out the inside of the seat wall)
        // Already hollow from seat_wall difference

        // Skin contact hole through base plate
        skin_hole();

        // Cable exit channel
        cable_exit_channel();

        // Mounting holes
        mounting_holes();

        // Sweat drainage channels
        sweat_channels();
    }
}

// ============================================================
// Render
// ============================================================
helmet_adapter();
