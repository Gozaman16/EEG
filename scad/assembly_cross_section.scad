// ============================================================
// EpiScreen Standard Electrode — Cross-Section View
// ============================================================
// Shows a vertical cut through the centre of the assembled
// electrode revealing all internal layers and features.
//
// Cut plane: Y = 0 (shows the X-Z plane)
// Everything on Y < 0 is rendered; Y ≥ 0 is clipped.
//
// Render: openscad --render -o assembly_cross_section.png
//         --imgsize=2400,2800 --camera=30,0,5,90,0,0,120
//         assembly_cross_section.scad
// ============================================================

include <params.scad>

// ── Colours ─────────────────────────────────────────────────
SILICONE_C  = [0.60, 0.80, 1.00, 0.75];
FR4_C       = [0.20, 0.60, 0.20, 1.00];
COPPER_C    = [0.85, 0.55, 0.20, 1.00];
MOLD_C      = [0.55, 0.55, 0.60, 0.50];
GRAPH_C     = [0.10, 0.10, 0.10, 0.90];
CHANNEL_C   = [1.00, 0.20, 0.20, 0.90];
RESERVOIR_C = [1.00, 1.00, 0.30, 0.60];
WHITE_C     = [0.95, 0.95, 0.95, 1.00];
WIRE_C      = [0.80, 0.80, 0.85, 1.00];  // steel wire

// Clip half-space: only render Y < 0 portion
module half() {
    intersection() {
        children();
        translate([-(EP_MOLD_OD + 10), -(EP_MOLD_OD + 10), -5])
            cube([2*(EP_MOLD_OD + 10), EP_MOLD_OD + 10, EP_H + 30], center = false);
    }
}

// ════════════════════════════════════════════════════════════
// Main cross-section scene
// ════════════════════════════════════════════════════════════

// ── Bottom mold half ──────────────────────────────────────
color(MOLD_C)
    half()
        difference() {
            cylinder(d = EP_MOLD_OD, h = EP_BOT_H + WALL, center = false);
            translate([0, 0, WALL])
                cylinder(d = EP_OD, h = EP_BOT_H + 0.1, center = false);
            // Bottom cavity bump
            translate([0, 0, WALL - 0.05])
                cylinder(d = EP_BOT_CAV_D, h = EP_BOT_CAV_H + 0.05, center = false);
            // Spiral platform pocket
            translate([0, 0, WALL - 0.05])
                cylinder(d = EP_SPIRAL_D, h = EP_SPIRAL_H, center = false);
        }

// ── Top mold half ─────────────────────────────────────────
color(MOLD_C)
    translate([0, 0, EP_BOT_H + WALL])
        half()
            difference() {
                cylinder(d = EP_MOLD_OD, h = EP_TOP_H, center = false);
                translate([0, 0, WALL])
                    cylinder(d = EP_OD, h = EP_H - EP_BOT_H + 0.1, center = false);
                // Pour hole
                translate([0, 0, EP_TOP_H - EP_POUR_D - 0.1])
                    cylinder(d = EP_POUR_D, h = EP_POUR_D + 0.2, center = false);
            }

// ── Silicone electrode body ───────────────────────────────
color(SILICONE_C)
    half()
        difference() {
            union() {
                translate([0, 0, WALL])
                    cylinder(d = EP_OD, h = EP_H, center = false);
                // Skin contact surface (slightly raised)
                translate([0, 0, WALL - EP_BOT_CAV_H])
                    cylinder(d = EP_BOT_CAV_D, h = EP_BOT_CAV_H, center = false);
            }
            // FR-4 seat (void where FR-4 sits)
            translate([0, 0, WALL + EP_FR4_Z])
                cylinder(d = EP_FR4_D, h = EP_FR4_T + 0.1, center = false);
            // Reservoir ring void
            translate([0, 0, WALL + EP_FR4_Z + EP_FR4_T])
                difference() {
                    cylinder(d = EP_RES_OD, h = EP_RES_H + 0.1, center = false);
                    cylinder(d = EP_RES_ID, h = EP_RES_H + 0.2, center = false);
                }
            // Spiral platform pocket
            translate([0, 0, WALL])
                cylinder(d = EP_SPIRAL_D, h = EP_SPIRAL_H, center = false);
        }

// ── Graphene coating on skin surface ─────────────────────
color(GRAPH_C)
    half()
        difference() {
            translate([0, 0, WALL - EP_BOT_CAV_H - 0.25])
                cylinder(d = EP_BOT_CAV_D, h = 0.25, center = false);
            translate([0, 0, WALL - EP_BOT_CAV_H - 0.3])
                cylinder(d = EP_BOT_CAV_D - 1.5, h = 0.4, center = false);
        }

// ── Copper spiral ────────────────────────────────────────
color(COPPER_C)
    half()
        translate([0, 0, WALL + EP_FR4_Z - 0.4])
            cylinder(d = EP_SPIRAL_D, h = 0.4, center = false);

// ── FR-4 disk ────────────────────────────────────────────
color(FR4_C)
    half()
        translate([0, 0, WALL + EP_FR4_Z])
            cylinder(d = EP_FR4_D, h = EP_FR4_T, center = false);

// ── Reservoir ring (liquid) ───────────────────────────────
color(RESERVOIR_C)
    half()
        translate([0, 0, WALL + EP_FR4_Z + EP_FR4_T])
            difference() {
                cylinder(d = EP_RES_OD, h = EP_RES_H, center = false);
                cylinder(d = EP_RES_ID, h = EP_RES_H + 0.2, center = false);
            }

// ── Emici halka (absorbent ring) ──────────────────────────
color(WHITE_C)
    half()
        translate([0, 0, WALL + EP_FR4_Z + EP_FR4_T + 0.2])
            difference() {
                cylinder(d = EP_RES_OD - 0.5, h = EP_RES_H - 0.4, center = false);
                cylinder(d = EP_RES_ID + 0.5, h = EP_RES_H, center = false);
            }

// ── Microchannel wire (one visible in cross-section) ──────
color(WIRE_C)
    half()
        translate([EP_RES_ID/2, 0, WALL + EP_FR4_Z + EP_FR4_T + EP_RES_H/2])
            rotate([0, EP_MCH_ANG, 0])
                cylinder(d = 0.5, h = 12, center = false);

// ── Cable exit channel (section view) ────────────────────
color(MOLD_C)
    translate([EP_OD/2 - 0.5, -EP_CABLE_W_BOT/2, WALL + EP_FR4_Z])
        cube([EP_CABLE_D + 3, EP_CABLE_W_BOT/2, EP_H - EP_FR4_Z], center = false);

// ── Dimension leader lines (thin rods) ───────────────────
// Outer diameter arrow
color([0.2, 0.2, 0.2, 1]) {
    translate([-EP_OD/2 - 8, -0.2, WALL + EP_H/2])
        rotate([0, 90, 0])
            cylinder(d = 0.3, h = EP_OD + 16, center = false);
    // tick left
    translate([-EP_OD/2 - 8, -0.2, WALL + EP_H/2])
        cylinder(d = 0.3, h = 3, center = false);
    // tick right
    translate([EP_OD/2 + 8, -0.2, WALL + EP_H/2])
        cylinder(d = 0.3, h = 3, center = false);

    // Height arrow
    translate([EP_OD/2 + 10, -0.2, WALL])
        cylinder(d = 0.3, h = EP_H, center = false);
    translate([EP_OD/2 + 7, -0.2, WALL])
        rotate([0, 90, 0])
            cylinder(d = 0.3, h = 6, center = false);
    translate([EP_OD/2 + 7, -0.2, WALL + EP_H])
        rotate([0, 90, 0])
            cylinder(d = 0.3, h = 6, center = false);
}

// ── Alignment pin (one, in cross-section) ────────────────
color(MOLD_C)
    translate([EP_MOLD_OD/2 - WALL - PIN_D/2 - 0.5, -0.2,
               EP_BOT_H + WALL - PIN_H])
        cylinder(d = PIN_D, h = PIN_H * 2 + WALL, center = false);
