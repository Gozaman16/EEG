// ═════════════════════════════════════════════════════════════
// EpiScreen / NeoGuard / HairSite — Shared Parameters
// Project: EpiScreen / NeoGuard / HairSite / ImpactGuard
// License: MIT
// ─────────────────────────────────────────────────────────────
// Changelog (funnel-integrated redesign):
//   • CLEARANCE 0.3 → 0.5 (Ecoflex 00-50 needs more room)
//   • DRAFT     2   → 4   (softer silicone needs more draft)
//   • Reservoir rings and spiral platforms removed — the funnel
//     IS the reservoir. Impedance ring sits on funnel inner wall.
//   • Cable exits are now fully enclosed through-tunnels in the
//     bottom mold only (top mold has no cable features).
//   • Concentric ring texture replaced by hexagonal pillar array.
//   • Alignment pins are now conical with generous clearance.
//   • Pry slots, flash trap, silicone interlock, refill port added.
// ═════════════════════════════════════════════════════════════

// ── Global print-quality settings ──────────────────────────
$fn        = 120;    // Cylinder facets (high quality)
FILLET     = 0.2;    // Edge fillet for printability (mm)
CLEARANCE  = 0.5;    // Mating-surface clearance — was 0.3; Ecoflex 00-50 needs more
WALL       = 1.5;    // Minimum wall thickness (mm)
DRAFT      = 4;      // Draft angle on vertical walls — was 2; softer silicone needs more

// ── Vent hole geometry ─────────────────────────────────────
VENT_D     = 1.0;    // Vent hole diameter (mm)

// ── Cable tunnel geometry (C-strategy for EP / HS) ─────────
CABLE_CH_W    = 1.5;                          // per-channel width (1 mm cable + 0.5 mm clearance)
CABLE_CH_H    = 1.8;                          // per-channel height
CABLE_DIV_W   = 2.0;                          // silicone divider between channels
CABLE_FLARE   = 1;                            // deg flare on outside opening (strain relief)

// ── Refill port (upper silicone) ───────────────────────────
REFILL_PORT_D = 2.0;                          // vertical through-hole in top mold

// ── Hexagonal pillar texture (skin contact) ────────────────
PILLAR_D      = 0.5;                          // pillar diameter
PILLAR_H      = 0.4;                          // pillar height
PILLAR_PITCH  = 1.0;                          // center-to-center (hex grid)

// ── Pry slots (at parting line, 4× per mold) ───────────────
PRY_SLOT_W    = 3.0;                          // width along parting line
PRY_SLOT_D    = 2.0;                          // radial depth

// ── Flash trap groove (bottom mold, top face) ──────────────
FLASH_GROOVE_W = 0.5;
FLASH_GROOVE_D = 0.5;

// ── Silicone interlock (lip + groove + key + service notch) ──
SIL_LIP_H        = 1.5;                       // raised lip height on top of lower silicone
SIL_LIP_W        = 1.5;                       // lip radial width
SIL_GROOVE_CLEAR = 0.1;                       // radial clearance lip↔groove
SIL_KEY_SIZE     = 2.0;                       // 2×2 mm anti-rotation key
SIL_KEY_ANGLE    = 90;                        // 12 o'clock
SIL_SERVICE_W    = 2.0;                       // service notch tab width
SIL_SERVICE_H    = 1.0;                       // tab height
SIL_SERVICE_ANGLE = 270;                      // 6 o'clock

// ═════════════════════════════════════════════════════════════
// EpiScreen standard electrode (24 mm adult)
// ═════════════════════════════════════════════════════════════
EP_OD         = 24.0;
EP_H          = 10.0;
EP_MOLD_OD    = EP_OD + 2*WALL + 4.0;         // = 32 mm mold OD
EP_BOT_H      = 5.0;
EP_TOP_H      = EP_H - EP_BOT_H + WALL;
EP_POUR_D     = 6.0;                          // silicone pour hole (upper)

// FR-4 seat — sits at top of lower silicone, accessible when opened
EP_FR4_D      = 19.0;
EP_FR4_T      = 1.6;
EP_FR4_Z      = EP_BOT_H - EP_FR4_T;          // = 3.4 mm (top face flush with top of lower silicone)
EP_FR4_LIP    = 0.2;                          // centering lip

// Funnel (replaces reservoir ring + spiral platform)
EP_FUN_TOP_D     = 10.0;                      // FR-4 side (narrow)
EP_FUN_BOT_D     = 18.0;                      // skin side (wide)
EP_FUN_H         = 3.0;
EP_FUN_WALL      = 1.2;

// Sensing tip — disk protruding 0.1 mm past funnel bottom rim
EP_SENSE_TIP_D    = 3.0;
EP_SENSE_PROTRUDE = 0.1;

// Impedance ring — INNER funnel wall, GENEROUSLY sized
EP_IMP_RING_Z_FRAC = 0.5;                     // 0 = FR-4 side, 1 = skin side
EP_IMP_RING_W      = 1.5;                     // width along funnel wall (NOT cramped)
EP_IMP_RING_T      = 0.3;                     // radial protrusion into electrolyte

// Cable exit (C-strategy — single notch, two channels, divider)
EP_CABLE_TOTAL_W = CABLE_CH_W*2 + CABLE_DIV_W;    // = 5.0 mm
EP_CABLE_RAD_L   = (EP_MOLD_OD - EP_OD)/2 + 1.0;  // full wall + 1 mm overhang

// Alignment pins (conical, 4×, avoid cable notch at 0°)
PIN_D_BASE    = 2.5;
PIN_D_TIP     = 2.0;
PIN_H         = 2.5;
HOLE_D        = 2.3;                          // 0.3 mm radial clearance at tip
HOLE_DEPTH    = 2.8;                          // 0.3 mm axial clearance
PIN_R         = 4;                            // number of pins
PIN_ANGLES    = [45, 135, 225, 315];

// ═════════════════════════════════════════════════════════════
// NeoGuard neonatal electrode (15 mm)
// ═════════════════════════════════════════════════════════════
NG_OD         = 15.0;
NG_H          = 8.0;
NG_MOLD_OD    = NG_OD + 2*WALL + 4.0;         // ~22 mm
NG_BOT_H      = 4.0;
NG_TOP_H      = NG_H - NG_BOT_H + WALL;
NG_POUR_D     = 4.0;

// FR-4
NG_FR4_D      = 12.0;
NG_FR4_T      = 1.0;
NG_FR4_Z      = NG_BOT_H - NG_FR4_T;          // = 3.0 mm
NG_FR4_LIP    = 0.2;

// Funnel (scaled)
NG_FUN_TOP_D     = 6.0;
NG_FUN_BOT_D     = 11.0;
NG_FUN_H         = 2.5;
NG_FUN_WALL      = 1.0;

NG_SENSE_TIP_D    = 2.0;
NG_SENSE_PROTRUDE = 0.1;

NG_IMP_RING_Z_FRAC = 0.5;
NG_IMP_RING_W      = 1.0;
NG_IMP_RING_T      = 0.25;

// Cable exit (B-strategy — two opposite round holes)
NG_CABLE_HOLE_D = 1.5;                        // 1 mm cable + 0.5 mm clearance
NG_CABLE_RAD_L  = (NG_MOLD_OD - NG_OD)/2 + 1.0;

// Alignment pins (scaled, 3× — 22 mm OD can't comfortably fit 4)
NG_PIN_D_BASE = 2.0;
NG_PIN_D_TIP  = 1.5;
NG_PIN_H      = 2.0;
NG_HOLE_D     = 1.8;
NG_HOLE_DEPTH = 2.3;
NG_PIN_R      = 3;
NG_PIN_ANGLES = [90, 210, 330];               // avoid cable exits at 0° and 180°

// ═════════════════════════════════════════════════════════════
// HairSite electrode (24 mm + 7 penetration pins)
// Uses EP_ funnel dimensions (same 24 mm body) and EP_ pin params.
// ═════════════════════════════════════════════════════════════
HS_OD         = 24.0;
HS_H          = 12.0;                         // taller to accommodate pins
HS_MOLD_OD    = HS_OD + 2*WALL + 4.0;         // 32 mm
HS_BOT_H      = 6.0;
HS_TOP_H      = HS_H - HS_BOT_H + WALL;
HS_POUR_D     = 6.0;

HS_FR4_D      = EP_FR4_D;
HS_FR4_T      = EP_FR4_T;
HS_FR4_Z      = HS_BOT_H - HS_FR4_T;          // top face flush with top of lower silicone
HS_FR4_LIP    = EP_FR4_LIP;

// Penetration pin array (1 centre + 6 at 60° on 6 mm radius)
HS_PIN_D      = 1.2;                          // penetration pin diameter in mold
HS_PIN_H      = 8.0;                          // post height
HS_PIN_RAD    = 6.0;                          // radius of outer 6 pins
HS_PIN_N      = 7;
HS_PIN_EXCL_R = 0.5;                          // texture exclusion radius around each pin

// ═════════════════════════════════════════════════════════════
// ImpactGuard helmet adapter (unchanged — not part of this redesign)
// ═════════════════════════════════════════════════════════════
IG_OD         = 38.0;
IG_H          = 12.0;
IG_ELEC_D     = 24.5;
IG_ELEC_H     = 8.0;
IG_SNAP_R     = 0.8;
IG_MOUNT_W    = 50.0;
IG_MOUNT_H    = 8.0;

// ═════════════════════════════════════════════════════════════
// Headband mounts (unchanged — not part of this redesign)
// ═════════════════════════════════════════════════════════════
HBA_BAND_W    = 22.0;
HBA_BAND_T    = 2.5;
HBA_ELEC_D    = 24.5;
HBA_ELEC_H    = 6.0;
HBA_CLIP_H    = 12.0;
HBA_CLIP_W    = 30.0;
HBA_SNAP_R    = 0.8;

HBN_BAND_W    = 16.0;
HBN_BAND_T    = 2.0;
HBN_ELEC_D    = 15.5;
HBN_ELEC_H    = 5.0;
HBN_CLIP_H    = 9.0;
HBN_CLIP_W    = 22.0;
HBN_SNAP_R    = 0.6;

// ═════════════════════════════════════════════════════════════
// SHARED MODULES
// ═════════════════════════════════════════════════════════════

// ── Alignment pin / hole primitives (conical for self-release) ──
module alignment_pin_male(d_base, d_tip, h) {
  cylinder(d1 = d_base, d2 = d_tip, h = h, center = false);
}

module alignment_hole(d, depth) {
  cylinder(d = d, h = depth, center = false);
}

// ── Pry slots: 4× V-profile notches at the parting line ──
// Rotated cube gives a 45°-tipped diamond; carved by difference()
// so the point of the "V" bites into the parting line.
module pry_slots(mold_od, mold_h, slot_w = PRY_SLOT_W, slot_d = PRY_SLOT_D) {
  for (a = [45, 135, 225, 315])
    rotate([0, 0, a])
      translate([mold_od/2 - slot_d + 0.1, 0, mold_h/2])
        rotate([0, 45, 0])
          cube([slot_w, slot_w, slot_w], center = true);
}

// ── Flash trap: shallow annular groove on bottom mold's top face ──
module flash_trap(mold_od, top_z) {
  outer_d = mold_od - 2*WALL + 0.5;
  inner_d = outer_d - 2*FLASH_GROOVE_W;
  translate([0, 0, top_z - FLASH_GROOVE_D])
    difference() {
      cylinder(d = outer_d, h = FLASH_GROOVE_D + 0.02);
      translate([0, 0, -0.01])
        cylinder(d = inner_d, h = FLASH_GROOVE_D + 0.04);
    }
}

// ── Hexagonal pillar texture (replaces concentric ring texture) ──
// Positive features on mold floor → raised pillars on silicone skin side.
module hex_pillar_texture(area_r, base_h) {
  pitch = PILLAR_PITCH;
  row_h = pitch * 0.866;                      // sqrt(3)/2
  n_rows = ceil(2 * area_r / row_h) + 2;
  n_cols = ceil(2 * area_r / pitch) + 2;
  for (i = [-n_rows/2 : n_rows/2]) {
    y     = i * row_h;
    x_off = (i % 2 == 0) ? 0 : pitch/2;
    for (j = [-n_cols/2 : n_cols/2]) {
      x = j * pitch + x_off;
      if (sqrt(x*x + y*y) < area_r - PILLAR_D/2)
        translate([x, y, base_h])
          cylinder(d = PILLAR_D, h = PILLAR_H, center = false);
    }
  }
}

// ── Funnel void: truncated cone, narrow (top/FR-4 side) → wide (skin side) ──
// Parameterized so each variant can call with its own dimensions.
module funnel_void(top_d, bot_d, h) {
  // Inverted cone positioned with skin side at z = 0 (bottom of cavity).
  cylinder(d1 = bot_d, d2 = top_d, h = h, center = false);
}

// ── Sensing tip void: narrow cylinder through funnel centre ──
module sensing_tip_void(tip_d, fun_h, protrude) {
  translate([0, 0, -protrude - 0.05])
    cylinder(d = tip_d, h = fun_h + protrude + 0.1, center = false);
}

// ── Impedance ring void: annular recess on inner funnel wall ──
// Generously sized — "previous designs were so tight powdered sugar
// wouldn't fit."  Every clearance gets a ≥ 0.3 mm buffer.
module impedance_ring_void(top_d, bot_d, fun_h, z_frac, w, t) {
  z     = fun_h * (1 - z_frac);               // measured from skin side up
  r_at_z = (bot_d/2) * (1 - z_frac) + (top_d/2) * z_frac;
  translate([0, 0, z - w/2])
    difference() {
      cylinder(r = r_at_z + t, h = w);
      translate([0, 0, -0.05])
        cylinder(r = r_at_z, h = w + 0.1);
    }
}

// ── Silicone interlock (lower mold side): voids in cavity ceiling ──
// Produces raised features on the top of the lower silicone: perimeter
// lip, anti-rotation key, service-notch tab.  Called in top-face local
// coordinates (z = 0 at the silicone's top face, +z = up into mold).
module interlock_lower_voids(electrode_od) {
  outer_r = electrode_od/2;
  inner_r = outer_r - SIL_LIP_W;

  // 1. Perimeter lip void
  difference() {
    cylinder(r = outer_r, h = SIL_LIP_H + 0.05);
    translate([0, 0, -0.05])
      cylinder(r = inner_r, h = SIL_LIP_H + 0.2);
  }

  // 2. Anti-rotation key void — 2×2 mm square
  rotate([0, 0, SIL_KEY_ANGLE])
    translate([outer_r - SIL_LIP_W - SIL_KEY_SIZE/2 - 0.5, 0, 0])
      cube([SIL_KEY_SIZE, SIL_KEY_SIZE, SIL_LIP_H + 0.05], center = true);

  // 3. Service notch tab void — small rectangular bump
  rotate([0, 0, SIL_SERVICE_ANGLE])
    translate([outer_r - SIL_LIP_W/2, 0, SIL_SERVICE_H/2])
      cube([SIL_LIP_W + 0.5, SIL_SERVICE_W, SIL_SERVICE_H + 0.05], center = true);
}

// ── Silicone interlock (upper mold side): protrusions extend DOWN
// into what will become upper silicone, producing a matching groove +
// socket + service gap.  Called in bottom-face local coordinates
// (z = 0 at upper silicone's bottom face, +z = down into silicone).
// All clearances include SIL_GROOVE_CLEAR.
module interlock_upper_protrusions(electrode_od) {
  outer_r = electrode_od/2;
  inner_r = outer_r - SIL_LIP_W;
  clr     = SIL_GROOVE_CLEAR;

  // 1. Perimeter groove protrusion (slightly wider + deeper than lip)
  difference() {
    cylinder(r = outer_r + clr, h = SIL_LIP_H + clr);
    translate([0, 0, -0.05])
      cylinder(r = inner_r - clr, h = SIL_LIP_H + clr + 0.1);
  }

  // 2. Anti-rotation socket — 0.1 mm larger square
  rotate([0, 0, SIL_KEY_ANGLE])
    translate([outer_r - SIL_LIP_W - SIL_KEY_SIZE/2 - 0.5, 0,
               (SIL_LIP_H + clr)/2])
      cube([SIL_KEY_SIZE + 2*clr,
            SIL_KEY_SIZE + 2*clr,
            SIL_LIP_H + clr + 0.05], center = true);

  // 3. Service-notch complementary gap
  rotate([0, 0, SIL_SERVICE_ANGLE])
    translate([outer_r - SIL_LIP_W/2, 0, (SIL_SERVICE_H + clr)/2])
      cube([SIL_LIP_W + 0.5 + 2*clr,
            SIL_SERVICE_W + 2*clr,
            SIL_SERVICE_H + clr + 0.05], center = true);
}
