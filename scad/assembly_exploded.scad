// ============================================================
// EpiScreen Standard Electrode — Exploded Assembly View
// ============================================================
// Shows all layers separated vertically with assembly arrows.
// Component order (bottom to top):
//   1. Bottom mold piece (gray, transparent)
//   2. Copper spiral (copper)
//   3. Silicone body bottom (light blue, transparent)
//   4. FR-4 disk (green)
//   5. Emici halka / absorbent ring (white)
//   6. Reservoir ring void (yellow, transparent)
//   7. Microchannel wires (red)
//   8. Silicone body top (light blue, transparent)
//   9. Top mold piece (gray, transparent)
//
// Render: openscad --render -o assembly_exploded.png
//         --imgsize=2400,3200 --camera=0,0,80,55,0,0,200
//         assembly_exploded.scad
// ============================================================

include <params.scad>

// ── Explosion offsets (Z gap between components) ──────────
EXPLODE_GAP = 12;  // mm between each layer

// Component Z positions (exploded)
Z_BOT_MOLD  =   0;
Z_SPIRAL    =   Z_BOT_MOLD  + EP_BOT_H + WALL + EXPLODE_GAP;
Z_SIL_BOT   =   Z_SPIRAL    + 1        + EXPLODE_GAP;
Z_FR4       =   Z_SIL_BOT   + EP_FR4_Z + EP_FR4_T + EXPLODE_GAP;
Z_EMICI     =   Z_FR4       + EP_FR4_T + EXPLODE_GAP;
Z_RESERVOIR =   Z_EMICI     + 2        + EXPLODE_GAP;
Z_WIRES     =   Z_RESERVOIR + EP_RES_H + EXPLODE_GAP * 0.5;
Z_SIL_TOP   =   Z_WIRES     + 2        + EXPLODE_GAP;
Z_TOP_MOLD  =   Z_SIL_TOP   + (EP_H - EP_BOT_H) + EXPLODE_GAP;

// ── Colours ─────────────────────────────────────────────────
SILICONE_C  = [0.60, 0.80, 1.00, 0.55];
FR4_C       = [0.20, 0.60, 0.20, 1.00];
COPPER_C    = [0.85, 0.55, 0.20, 1.00];
MOLD_C      = [0.50, 0.50, 0.50, 0.30];
GRAPH_C     = [0.10, 0.10, 0.10, 0.85];
CHANNEL_C   = [1.00, 0.20, 0.20, 0.80];
RESERVOIR_C = [1.00, 1.00, 0.30, 0.40];
WHITE_C     = [1.00, 1.00, 1.00, 1.00];
ARROW_C     = [0.20, 0.20, 0.80, 1.00];  // blue arrows

// ════════════════════════════════════════════════════════════
// Exploded scene
// ════════════════════════════════════════════════════════════

// 1. Bottom mold (ghost/transparent)
translate([0, 0, Z_BOT_MOLD]) {
    color(MOLD_C)
        bottom_mold_ghost();
    assembly_arrow(Z_SPIRAL - Z_BOT_MOLD - EP_BOT_H - WALL - 1);
}

// 2. Copper spiral
translate([0, 0, Z_SPIRAL]) {
    color(COPPER_C)
        copper_spiral();
    assembly_arrow(Z_SIL_BOT - Z_SPIRAL - 1.5);
}

// 3. Silicone body — bottom half
translate([0, 0, Z_SIL_BOT]) {
    color(SILICONE_C)
        silicone_bottom_half();
    assembly_arrow(Z_FR4 - Z_SIL_BOT - EP_FR4_Z - 1);
}

// 4. FR-4 disk
translate([0, 0, Z_FR4]) {
    color(FR4_C)
        fr4_disk();
    assembly_arrow(Z_EMICI - Z_FR4 - EP_FR4_T - 1);
}

// 5. Emici halka (absorbent ring)
translate([0, 0, Z_EMICI]) {
    color(WHITE_C)
        emici_halka();
    assembly_arrow(Z_RESERVOIR - Z_EMICI - 2.5);
}

// 6. Reservoir ring (yellow transparent)
translate([0, 0, Z_RESERVOIR]) {
    color(RESERVOIR_C)
        reservoir_ring();
    // No arrow — wires overlay
}

// 7. Microchannel wires (3 red angled rods)
translate([0, 0, Z_WIRES]) {
    color(CHANNEL_C)
        microchannel_wires();
    assembly_arrow(Z_SIL_TOP - Z_WIRES - 2.5);
}

// 8. Silicone body — top half
translate([0, 0, Z_SIL_TOP]) {
    color(SILICONE_C)
        silicone_top_half();
    assembly_arrow(Z_TOP_MOLD - Z_SIL_TOP - (EP_H - EP_BOT_H) - 1);
}

// 9. Top mold (ghost/transparent)
translate([0, 0, Z_TOP_MOLD])
    color(MOLD_C)
        top_mold_ghost();


// ════════════════════════════════════════════════════════════
// Component modules
// ════════════════════════════════════════════════════════════

module bottom_mold_ghost() {
    // Simplified bottom mold solid (full block minus cavity hint)
    difference() {
        cylinder(d = EP_MOLD_OD, h = EP_BOT_H + WALL, center = false);
        translate([0, 0, WALL - 0.1])
            cylinder(d = EP_OD - 1, h = EP_BOT_H + 0.2, center = false);
    }
}

module top_mold_ghost() {
    difference() {
        cylinder(d = EP_MOLD_OD, h = EP_TOP_H, center = false);
        translate([0, 0, WALL - 0.1])
            cylinder(d = EP_OD - 1, h = EP_TOP_H, center = false);
        // Pour hole
        translate([0, 0, EP_TOP_H - EP_POUR_D])
            cylinder(d = EP_POUR_D, h = EP_POUR_D + 0.1, center = false);
    }
    // Alignment pins
    for (i = [0:3])
        rotate([0, 0, i*90+45])
            translate([EP_MOLD_OD/2 - WALL - PIN_D/2 - 0.5, 0, 0])
                cylinder(d = PIN_D, h = PIN_H + WALL, center = false);
}

module copper_spiral() {
    // Flat disc representing the copper spiral PCB trace
    cylinder(d = EP_SPIRAL_D, h = 0.4, center = false);
    // Simple spiral grooves (decorative)
    for (r = [1 : 1 : EP_SPIRAL_D/2 - 0.5])
        rotate_extrude()
            translate([r, 0.35, 0])
                square([0.2, 0.08], center = false);
}

module fr4_disk() {
    cylinder(d = EP_FR4_D, h = EP_FR4_T, center = false);
    // PCB trace hint (concentric rings in copper)
    color(COPPER_C)
        for (r = [2 : 2 : EP_FR4_D/2 - 1])
            rotate_extrude()
                translate([r, EP_FR4_T, 0])
                    square([0.3, 0.12], center = false);
}

module emici_halka() {
    // Absorbent ring that sits in reservoir channel
    difference() {
        cylinder(d = EP_RES_OD - 0.4, h = EP_RES_H - 0.1, center = false);
        cylinder(d = EP_RES_ID + 0.4, h = EP_RES_H, center = false);
    }
}

module reservoir_ring() {
    // The void in the silicone — shown as transparent ring
    difference() {
        cylinder(d = EP_RES_OD, h = EP_RES_H, center = false);
        cylinder(d = EP_RES_ID, h = EP_RES_H + 0.2, center = false);
    }
}

module microchannel_wires() {
    // 3 angled steel wires (shown in place before removal)
    wire_length = 14;
    for (i = [0:2])
        rotate([0, 0, i*120+30])
            translate([EP_RES_ID/2 + 1, 0, 0])
                rotate([0, EP_MCH_ANG, 0])
                    cylinder(d = 0.5 + 0.1, h = wire_length, center = false);
}

module silicone_bottom_half() {
    difference() {
        cylinder(d = EP_OD, h = EP_BOT_H, center = false);
        // Hollow out to show interior
        translate([0, 0, -0.1])
            cylinder(d = EP_OD - 3, h = EP_BOT_H - 1.5, center = false);
    }
}

module silicone_top_half() {
    h = EP_H - EP_BOT_H;
    difference() {
        cylinder(d = EP_OD, h = h, center = false);
        translate([0, 0, -0.1])
            cylinder(d = EP_OD - 3, h = h - 1.5, center = false);
    }
}

// ─────────────────────────────────────────────────────────────
// Upward assembly arrow (placed at top of current component)
// ─────────────────────────────────────────────────────────────
module assembly_arrow(height) {
    if (height > 2) {
        color(ARROW_C) {
            // Shaft
            translate([EP_OD/2 + 6, 0, 0])
                cylinder(d = 0.8, h = height - 3, center = false);
            // Arrowhead
            translate([EP_OD/2 + 6, 0, height - 3])
                cylinder(d1 = 2.5, d2 = 0, h = 3, center = false);
        }
    }
}
