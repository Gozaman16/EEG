// ============================================================
// Headband Guide Clip — Prevents elastic band rolling/twisting
// Print 2 per headband setup. Slides onto the elastic band
// and sits against the head to keep band flat and stable.
// ============================================================

// --- Parametric band dimensions ---
band_width          = 25;        // elastic band width (match adult mount)
band_thickness      = 3;         // elastic band thickness + clearance

// --- Clip body ---
clip_w              = 30;        // total width
clip_h              = 10;        // height (along head surface)
clip_d              = 5;         // depth/thickness of clip

// --- Band slot through clip ---
slot_w              = band_width; // matches band width
slot_h              = band_thickness; // matches band thickness

// --- Smooth edges ---
fillet_r            = 0.3;

$fn                 = 60;

// ============================================================
// Main clip body with band slot
// ============================================================
module band_guide_clip() {
    difference() {
        // Rounded rectangular body
        minkowski() {
            translate([-clip_w/2 + fillet_r, -clip_h/2 + fillet_r, 0])
                cube([clip_w - 2*fillet_r, clip_h - 2*fillet_r,
                      clip_d - fillet_r]);
            sphere(r = fillet_r);
        }

        // Band slot — horizontal through-slot for elastic band
        translate([-slot_w/2, -clip_h/2 - 1, (clip_d - slot_h) / 2])
            cube([slot_w, clip_h + 2, slot_h]);

        // Slight inner curve on skin-facing surface
        // so clip sits flush on rounded head
        translate([0, 0, -80 + fillet_r])
            sphere(r = 80, $fn = 120);
    }
}

band_guide_clip();
