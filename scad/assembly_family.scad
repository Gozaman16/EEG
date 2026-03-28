// ============================================================
// EpiScreen System — "Family Photo" Assembly Diagram
// ============================================================
// Publication-quality layout for ISEF poster / paper.
//
// Layout:
//   TOP ROW:    EpiScreen (24mm) | NeoGuard (15mm) | HairSite (24mm+pins)
//               Scale bar + 1 Turkish Lira coin (23mm dia) reference
//   BOTTOM ROW: Headband Adult | Headband Neonatal | Helmet Adapter
//
// Render this file in OpenSCAD with View → Render (F6),
// then export as PNG (File → Export → Export as PNG).
// Resolution hint:  openscad --render -o assembly_family.png
//                   --imgsize=3600,2400 assembly_family.scad
// ============================================================

include <params.scad>

// ── Colour helpers ──────────────────────────────────────────
SILICONE_C  = [0.60, 0.80, 1.00, 0.65];  // light blue, semi-transparent
FR4_C       = [0.20, 0.60, 0.20, 1.00];  // PCB green
COPPER_C    = [0.85, 0.55, 0.20, 1.00];  // copper orange
MOLD_C      = [0.50, 0.50, 0.50, 0.35];  // gray, transparent
GRAPH_C     = [0.10, 0.10, 0.10, 0.85];  // near-black graphene
CHANNEL_C   = [1.00, 0.20, 0.20, 0.80];  // red microchannels
RESERVOIR_C = [1.00, 1.00, 0.30, 0.40];  // yellow reservoir
COIN_C      = [0.85, 0.75, 0.25, 1.00];  // Turkish Lira gold
BAND_C      = [0.30, 0.30, 0.35, 1.00];  // dark gray band
WHITE_C     = [1.00, 1.00, 1.00, 1.00];  // white ring

// ── Row spacing ─────────────────────────────────────────────
ROW_Y_TOP  =  50;   // Y position of top row electrodes
ROW_Y_BOT  = -50;   // Y position of bottom row mounts
COL_X      =  60;   // Column spacing

// ════════════════════════════════════════════════════════════
// Main scene
// ════════════════════════════════════════════════════════════

// TOP ROW — Electrodes
translate([-COL_X, ROW_Y_TOP, 0]) episcreen_electrode_model();
translate([0,       ROW_Y_TOP, 0]) neoguard_electrode_model();
translate([ COL_X, ROW_Y_TOP, 0]) hairsite_electrode_model();

// Scale bar (100 mm ruler below top row)
translate([-50, ROW_Y_TOP - 30, 0]) scale_bar(100);

// Turkish Lira coin next to NeoGuard
translate([30, ROW_Y_TOP - 20, 0]) turkish_lira_coin();

// BOTTOM ROW — Mounts
translate([-COL_X, ROW_Y_BOT, 0]) headband_adult_model();
translate([0,       ROW_Y_BOT, 0]) headband_neonatal_model();
translate([ COL_X, ROW_Y_BOT, 0]) helmet_adapter_model();

// Row labels (thin plates used as label bases — annotate in post)
translate([-COL_X, ROW_Y_TOP + 22, 0])
    label_plate("EpiScreen\n24 mm", 28);
translate([0,       ROW_Y_TOP + 18, 0])
    label_plate("NeoGuard\n15 mm", 20);
translate([ COL_X, ROW_Y_TOP + 22, 0])
    label_plate("HairSite\n24 mm+pins", 28);

translate([-COL_X, ROW_Y_BOT - 18, 0])
    label_plate("Adult Headband", 36);
translate([0,       ROW_Y_BOT - 15, 0])
    label_plate("Neonatal Headband", 30);
translate([ COL_X, ROW_Y_BOT - 18, 0])
    label_plate("Helmet Adapter", 36);


// ════════════════════════════════════════════════════════════
// Electrode models (simplified solid representations)
// ════════════════════════════════════════════════════════════

module episcreen_electrode_model() {
    // Silicone body
    color(SILICONE_C)
        cylinder(d = EP_OD, h = EP_H, center = false);
    // Bottom skin-contact recess hint
    color(GRAPH_C)
        translate([0, 0, -0.1])
            cylinder(d = EP_BOT_CAV_D, h = 0.3, center = false);
    // FR-4 disk (visible through semi-transparent silicone)
    color(FR4_C)
        translate([0, 0, EP_FR4_Z])
            cylinder(d = EP_FR4_D, h = EP_FR4_T, center = false);
    // Copper spiral (flat disc approximation)
    color(COPPER_C)
        translate([0, 0, EP_FR4_Z - 0.3])
            cylinder(d = EP_SPIRAL_D, h = 0.3, center = false);
    // Reservoir ring (yellow transparent)
    color(RESERVOIR_C)
        translate([0, 0, EP_FR4_Z + EP_FR4_T])
            difference() {
                cylinder(d = EP_RES_OD, h = EP_RES_H, center = false);
                cylinder(d = EP_RES_ID, h = EP_RES_H + 0.1, center = false);
            }
    // White emici halka in reservoir
    color(WHITE_C)
        translate([0, 0, EP_FR4_Z + EP_FR4_T + EP_RES_H/2 - 0.4])
            difference() {
                cylinder(d = EP_RES_OD - 1, h = 0.8, center = false);
                cylinder(d = EP_RES_ID + 1, h = 0.9, center = false);
            }
    // Microchannel wire indicators (3 red lines)
    color(CHANNEL_C)
        for (i = [0:2])
            rotate([0, 0, i*120+30])
                translate([EP_RES_ID/2, 0, 0])
                    rotate([0, EP_MCH_ANG, 0])
                        cylinder(d = EP_MCH_D + 0.1, h = 4, center = false);
}

module neoguard_electrode_model() {
    color(SILICONE_C)
        cylinder(d = NG_OD, h = NG_H, center = false);
    color(GRAPH_C)
        translate([0, 0, -0.1])
            cylinder(d = NG_BOT_CAV_D, h = 0.3, center = false);
    color(FR4_C)
        translate([0, 0, NG_FR4_Z])
            cylinder(d = NG_FR4_D, h = NG_FR4_T, center = false);
    color(COPPER_C)
        translate([0, 0, NG_FR4_Z - 0.3])
            cylinder(d = NG_SPIRAL_D, h = 0.3, center = false);
    color(RESERVOIR_C)
        translate([0, 0, NG_FR4_Z + NG_FR4_T])
            difference() {
                cylinder(d = NG_RES_OD, h = NG_RES_H, center = false);
                cylinder(d = NG_RES_ID, h = NG_RES_H + 0.1, center = false);
            }
}

module hairsite_electrode_model() {
    // Body
    color(SILICONE_C)
        cylinder(d = HS_OD, h = HS_H, center = false);
    color(FR4_C)
        translate([0, 0, EP_FR4_Z])
            cylinder(d = EP_FR4_D, h = EP_FR4_T, center = false);
    color(COPPER_C)
        translate([0, 0, EP_FR4_Z - 0.3])
            cylinder(d = EP_SPIRAL_D, h = 0.3, center = false);
    // 7 penetrating pins (graphene-coated, dark)
    color(GRAPH_C) {
        cylinder(d = HS_PIN_D + 0.2, h = HS_PIN_H + 2, center = false);
        for (i = [0:5])
            rotate([0, 0, i*60])
                translate([HS_PIN_RAD, 0, 0])
                    cylinder(d = HS_PIN_D + 0.2, h = HS_PIN_H + 2, center = false);
    }
}


// ════════════════════════════════════════════════════════════
// Mount models (simplified)
// ════════════════════════════════════════════════════════════

module headband_adult_model() {
    color(BAND_C) {
        translate([-HBA_CLIP_W/2, -HBA_CLIP_W/2, 0])
            cube([HBA_CLIP_W, HBA_CLIP_W, HBA_CLIP_H]);
        // Band stub (show attachment)
        for (side = [-1, 1])
            translate([side * HBA_CLIP_W/2 + (side > 0 ? 0 : -20),
                       -HBA_BAND_W/2, 2])
                cube([20, HBA_BAND_W, HBA_BAND_T]);
    }
    // Electrode inserted (lighter)
    translate([0, 0, HBA_CLIP_H])
        color(SILICONE_C)
            cylinder(d = EP_OD, h = 6, center = false);
}

module headband_neonatal_model() {
    color(BAND_C) {
        translate([-HBN_CLIP_W/2, -HBN_CLIP_W/2, 0])
            cube([HBN_CLIP_W, HBN_CLIP_W, HBN_CLIP_H]);
        for (side = [-1, 1])
            translate([side * HBN_CLIP_W/2 + (side > 0 ? 0 : -15),
                       -HBN_BAND_W/2, 1])
                cube([15, HBN_BAND_W, HBN_BAND_T]);
    }
    translate([0, 0, HBN_CLIP_H])
        color(SILICONE_C)
            cylinder(d = NG_OD, h = 5, center = false);
}

module helmet_adapter_model() {
    color(BAND_C) {
        cylinder(d = IG_OD, h = IG_H, center = false);
        // Flange
        translate([-IG_MOUNT_W/2, -IG_MOUNT_W/2, 0])
            cube([IG_MOUNT_W, IG_MOUNT_W, IG_MOUNT_H]);
    }
    // Electrode in socket
    translate([0, 0, IG_H])
        color(SILICONE_C)
            cylinder(d = EP_OD, h = 5, center = false);
}


// ════════════════════════════════════════════════════════════
// Scale bar and coin reference
// ════════════════════════════════════════════════════════════

module scale_bar(len) {
    // 100 mm ruler with 10 mm tick marks
    color([0.2, 0.2, 0.2, 1])
        cube([len, 2, 1], center = false);
    for (x = [0 : 10 : len])
        color([0.2, 0.2, 0.2, 1])
            translate([x, 0, 1])
                cube([0.5, (x % 50 == 0 ? 4 : 2.5), 1], center = false);
}

module turkish_lira_coin() {
    // 23 mm diameter, 2.3 mm thick (1 Turkish Lira dimensions)
    color(COIN_C) {
        cylinder(d = 23, h = 2.3, center = false);
        // Simple edge ring detail
        difference() {
            cylinder(d = 23, h = 2.3, center = false);
            cylinder(d = 21.5, h = 2.4, center = false);
        }
        // Central relief (simplified)
        translate([0, 0, 2.3])
            cylinder(d = 10, h = 0.15, center = false);
    }
}

module label_plate(txt, w) {
    // Thin base plate used as anchor for text labels
    // (OpenSCAD cannot render text to STL meaningfully;
    //  labels are added in the poster layout software)
    color([0.9, 0.9, 0.9, 0.5])
        translate([-w/2, -2, 0])
            cube([w, 4, 0.3], center = false);
}
