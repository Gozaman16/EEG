// ============================================================
// EpiScreen Adult Headband Mount — Forehead EEG Electrode
// Adjustable elastic headband mounting for 24mm electrode
// ============================================================

// --- Head curvature (parametric — adjust for different sizes) ---
head_radius         = 85;        // forehead radius of curvature (mm)
                                 // Typical adult range: 75-95mm

// --- Central forehead piece ---
plate_w             = 40;        // width (along headband axis)
plate_h             = 30;        // height (vertical on forehead)
plate_t             = 2.5;       // wall thickness

// --- Electrode pocket ---
pocket_dia          = 24.5;      // 24mm electrode + 0.5mm clearance
pocket_r            = pocket_dia / 2;
pocket_depth        = 6;
skin_hole_dia       = 18;        // opening for electrode pad
skin_hole_r         = skin_hole_dia / 2;

// --- Retention clips ---
clip_count          = 3;
clip_width          = 1.0;
clip_height         = 3.0;
clip_thickness      = 0.8;
clip_overhang       = 0.6;

// --- Cable exit ---
cable_groove_w      = 4.0;
cable_groove_d      = 3.0;       // depth of groove

// --- Band slots ---
band_width          = 25;        // elastic band width
band_slot_h         = 3;         // slot height (band thickness + clearance)
band_slot_inset     = 2;         // distance from plate edge to slot

// --- Pressure distribution ribs ---
rib_length          = 15;
rib_width           = 1.0;
rib_height          = 0.5;
rib_offset          = pocket_r + 3;  // distance from center

// --- Misc ---
fillet_r            = 0.3;
$fn                 = 80;

// ============================================================
// Curved plate — matches forehead curvature
// Outer surface concave (toward head), electrode side convex
// ============================================================
module curved_plate() {
    intersection() {
        // Bounding box
        translate([-plate_w/2, -plate_h/2, 0])
            cube([plate_w, plate_h, plate_t + 10]);

        // Sphere for curvature — center behind plate
        translate([0, 0, -head_radius + plate_t])
            sphere(r = head_radius);
    }
}

// ============================================================
// Pocket wall — cylindrical wall for electrode recess
// Rises from the outer (non-skin) side of the plate
// ============================================================
module pocket_wall() {
    wall_t = 1.8;
    translate([0, 0, plate_t]) {
        difference() {
            cylinder(r = pocket_r + wall_t, h = pocket_depth);
            translate([0, 0, -0.01])
                cylinder(r = pocket_r, h = pocket_depth + 0.02);
        }
    }
}

// ============================================================
// Skin-side hole — electrode pad protrudes through this
// ============================================================
module skin_hole() {
    translate([0, 0, -5])
        cylinder(r = skin_hole_r, h = plate_t + 12);
}

// ============================================================
// Retention clips — snap-fit inside pocket wall
// ============================================================
module retention_clips() {
    for (i = [0 : clip_count - 1]) {
        angle = i * 360 / clip_count + 30;  // offset from cable exit
        rotate([0, 0, angle])
            translate([pocket_r - clip_thickness, -clip_width/2,
                       plate_t]) {
                // Clip body
                cube([clip_thickness, clip_width, clip_height]);
                // Overhang tip
                translate([-clip_overhang, 0, clip_height - 0.8])
                    cube([clip_overhang + 0.01, clip_width, 0.8]);
            }
    }
}

// ============================================================
// Cable exit groove — exits to left side (-X direction)
// ============================================================
module cable_exit_groove() {
    translate([-plate_w/2 - 1, -cable_groove_w/2, plate_t - cable_groove_d])
        cube([plate_w/2 + 1 - pocket_r + 2, cable_groove_w,
              cable_groove_d + pocket_depth + 1]);
}

// ============================================================
// Band threading slots — left and right sides of plate
// Elastic band threads through these slots
// ============================================================
module band_slots() {
    for (side = [-1, 1]) {
        // Slot position: near left/right edge, vertically centered
        translate([side * (plate_w/2 - band_slot_inset - band_width/2),
                   0, 0]) {
            // Horizontal slot through the plate + pocket wall area
            translate([-band_width/2, -plate_h/2 - 1, plate_t - 0.5])
                cube([band_width, plate_h + 2, band_slot_h]);
        }
    }
}

// ============================================================
// Pressure distribution ribs — prevent rocking on forehead
// Small ridges on the skin-facing surface flanking the pocket
// ============================================================
module pressure_ribs() {
    for (side = [-1, 1]) {
        translate([side * rib_offset, -rib_length/2, -rib_height])
            cube([rib_width, rib_length, rib_height + 0.01]);
    }
}

// ============================================================
// Full assembly
// ============================================================
module adult_headband_mount() {
    difference() {
        union() {
            curved_plate();
            pocket_wall();
            retention_clips();
            pressure_ribs();
        }

        skin_hole();
        cable_exit_groove();
        band_slots();
    }
}

adult_headband_mount();
