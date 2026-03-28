// ============================================================
// NeoGuard Neonatal Headband Mount — Forehead EEG Electrode
// For 15mm neonatal electrode on newborn skull
// ============================================================

// --- Head curvature (parametric — adjust for gestational age) ---
head_radius         = 55;        // newborn forehead curvature (mm)
                                 // Preterm: ~45mm, Term: ~55mm, Large: ~65mm

// --- Central forehead piece (smaller, thinner) ---
plate_w             = 25;        // width
plate_h             = 20;        // height
plate_t             = 2.0;       // thickness
min_wall            = 1.5;       // ultra-lightweight minimum wall

// --- Electrode pocket ---
pocket_dia          = 15.5;      // 15mm electrode + 0.5mm clearance
pocket_r            = pocket_dia / 2;
pocket_depth        = 4;         // shallower than adult
skin_hole_dia       = 10;        // opening for electrode pad
skin_hole_r         = skin_hole_dia / 2;

// --- Retention clips (2 only — smaller electrode) ---
clip_count          = 2;
clip_width          = 0.8;       // narrower
clip_height         = 2.5;       // shorter
clip_thickness      = 0.6;
clip_overhang       = 0.5;

// --- Cable exit ---
cable_groove_w      = 3.0;       // thinner neonatal cable
cable_groove_d      = 2.0;

// --- Band slots (narrow neonatal elastic) ---
band_width          = 15;        // narrow elastic for small head
band_slot_h         = 2.5;
band_slot_inset     = 1.5;

// --- Tape backup tab ---
// Flat area on top of the mount for medical tape attachment
// In case elastic band alone isn't sufficient for neonatal use
tape_tab_w          = 10;
tape_tab_d          = 8;
tape_tab_t          = 1.0;       // thin tab

// --- Extra-smooth edges for neonatal skin ---
fillet_r            = 0.5;       // larger fillets than adult (0.3)

$fn                 = 80;

// ============================================================
// Curved plate — tighter curvature for newborn skull
// ============================================================
module curved_plate() {
    intersection() {
        translate([-plate_w/2, -plate_h/2, 0])
            cube([plate_w, plate_h, plate_t + 10]);

        translate([0, 0, -head_radius + plate_t])
            sphere(r = head_radius);
    }
}

// ============================================================
// Pocket wall — thinner for lightweight design
// ============================================================
module pocket_wall() {
    wall_t = min_wall;
    translate([0, 0, plate_t]) {
        difference() {
            cylinder(r = pocket_r + wall_t, h = pocket_depth);
            translate([0, 0, -0.01])
                cylinder(r = pocket_r, h = pocket_depth + 0.02);
        }
    }
}

// ============================================================
// Skin-side hole
// ============================================================
module skin_hole() {
    translate([0, 0, -5])
        cylinder(r = skin_hole_r, h = plate_t + 12);
}

// ============================================================
// Retention clips — 2 clips for smaller electrode
// Positioned at 180° (left and right of pocket)
// ============================================================
module retention_clips() {
    for (i = [0 : clip_count - 1]) {
        angle = i * 360 / clip_count + 90;  // top and bottom
        rotate([0, 0, angle])
            translate([pocket_r - clip_thickness, -clip_width/2,
                       plate_t]) {
                cube([clip_thickness, clip_width, clip_height]);
                translate([-clip_overhang, 0, clip_height - 0.6])
                    cube([clip_overhang + 0.01, clip_width, 0.6]);
            }
    }
}

// ============================================================
// Cable exit groove — exits left
// ============================================================
module cable_exit_groove() {
    translate([-plate_w/2 - 1, -cable_groove_w/2, plate_t - cable_groove_d])
        cube([plate_w/2 + 1 - pocket_r + 2, cable_groove_w,
              cable_groove_d + pocket_depth + 1]);
}

// ============================================================
// Band slots — narrow neonatal elastic
// ============================================================
module band_slots() {
    for (side = [-1, 1]) {
        translate([side * (plate_w/2 - band_slot_inset - band_width/2),
                   0, 0]) {
            translate([-band_width/2, -plate_h/2 - 1, plate_t - 0.3])
                cube([band_width, plate_h + 2, band_slot_h]);
        }
    }
}

// ============================================================
// Tape backup tab — flat area on top for medical tape
// Provides secondary fixation for neonatal use where elastic
// band alone may not be sufficient or comfortable
// ============================================================
module tape_tab() {
    translate([-tape_tab_w/2, plate_h/2 - 1, plate_t]) {
        // Flat tab extending upward from top edge
        cube([tape_tab_w, tape_tab_d, tape_tab_t]);
    }
}

// ============================================================
// Edge rounding — apply extra fillets to all outer edges
// Critical for neonatal skin safety
// ============================================================
module rounded_body(body_module) {
    minkowski() {
        children();
        sphere(r = fillet_r/2, $fn = 16);
    }
}

// ============================================================
// Full assembly
// ============================================================
module neonatal_headband_mount() {
    difference() {
        union() {
            curved_plate();
            pocket_wall();
            retention_clips();
            tape_tab();
        }

        skin_hole();
        cable_exit_groove();
        band_slots();
    }
}

neonatal_headband_mount();
