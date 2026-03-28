// ============================================================
// ImpactGuard Cable Routing Clip
// C-shaped clip to secure EEG cable inside boxing helmet
// Print 4-5 of these along the cable route
// ============================================================

// --- Clip dimensions ---
cable_id        = 5.0;      // inner diameter (fits standard mic cable)
clip_wall       = 1.5;      // wall thickness around cable
clip_od         = cable_id + 2 * clip_wall;  // outer diameter
clip_width      = 8.0;      // width/length of clip along cable axis
gap_width       = 3.0;      // opening gap for cable snap-in

// --- Mounting tab ---
tab_length      = 10.0;     // extends from clip body
tab_width       = 8.0;      // same as clip width
tab_thick       = 1.5;      // tab thickness
tab_hole_dia    = 2.0;      // sewing hole diameter

// --- Print settings ---
$fn             = 60;

// ============================================================
// C-shaped clip body
// A cylinder with a gap cut for cable insertion.
// Cable snaps in through the 3mm gap and is held by the
// surrounding C-shape.
// ============================================================
module clip_body() {
    difference() {
        // Outer cylinder
        cylinder(d = clip_od, h = clip_width);

        // Inner bore — cable sits here
        translate([0, 0, -0.01])
            cylinder(d = cable_id, h = clip_width + 0.02);

        // Gap opening — cable snaps in through here
        // Gap is on the +Y side (away from mounting tab)
        translate([-gap_width/2, 0, -0.01])
            cube([gap_width, clip_od, clip_width + 0.02]);
    }
}

// ============================================================
// Clip entry guides — small chamfers at the gap opening to
// help the cable slide in during installation
// ============================================================
module entry_guides() {
    // Small angled surfaces at the gap edges
    guide_len = 1.0;
    for (side = [-1, 1]) {
        translate([side * gap_width/2, clip_od/2 - 0.5, 0]) {
            rotate([0, 0, side * 20])
                translate([-0.3, -0.5, 0])
                    cube([0.6, 1.5, clip_width]);
        }
    }
}

// ============================================================
// Flat mounting tab — extends from the clip body for
// attachment to helmet padding via sewing or zip-tie.
// The hole allows a needle/thread or thin zip-tie to pass
// through for secure mounting.
// ============================================================
module mounting_tab() {
    // Tab extends from the bottom of the clip (-Y direction,
    // opposite the gap opening)
    translate([-tab_width/2, -clip_od/2 - tab_length + 1, 0]) {
        difference() {
            // Flat tab
            cube([tab_width, tab_length, tab_thick]);

            // Sewing hole centered on tab
            translate([tab_width/2, tab_length/2, -0.01])
                cylinder(d = tab_hole_dia, h = tab_thick + 0.02);
        }
    }
}

// ============================================================
// Transition fillet — smooth connection between clip and tab
// Prevents stress concentration at the joint
// ============================================================
module clip_tab_bridge() {
    // Small triangular support between clip body and tab
    translate([-tab_width/2, -clip_od/2, 0]) {
        hull() {
            cube([tab_width, 0.01, clip_width]);
            translate([0, 0, 0])
                cube([tab_width, 1, tab_thick]);
        }
    }
}

// ============================================================
// Full cable clip assembly
// ============================================================
module cable_clip() {
    difference() {
        union() {
            clip_body();
            mounting_tab();
            clip_tab_bridge();
        }

        // Re-cut the entry guide chamfers from the gap
        entry_guides();
    }
}

// ============================================================
// Render — single clip
// (For printing, arrange 4-5 on build plate in slicer)
// ============================================================
cable_clip();
