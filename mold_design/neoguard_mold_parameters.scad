// ============================================================
// NeoGuard Neonatal Semi-Dry EEG Electrode Mold — Parameters
// Scaled-down version of EpiScreen for newborn skull
// ============================================================
// All dimensions in millimeters.
// Comments show [STANDARD] value where changed from adult version.
// ============================================================

// --- Electrode dimensions (cavity) ---
electrode_od        = 15.0;   // [STANDARD: 24.0] outer diameter
electrode_height    = 7.0;    // [STANDARD: 10.0] total height
electrode_radius    = electrode_od / 2;

// --- Bottom surface cavity (skin-contact) ---
bottom_cavity_dia   = 8.0;    // [STANDARD: 12.0]
bottom_cavity_depth = 0.7;    // [STANDARD: 1.0]
bottom_cavity_r     = bottom_cavity_dia / 2;

// --- Spiral exposure platform ---
spiral_platform_dia    = 5.0;  // [STANDARD: 8.0]
spiral_platform_height = 0.5;  // [STANDARD: 0.8]
spiral_platform_r      = spiral_platform_dia / 2;
groove_depth           = 0.1;  // texture grooves
groove_spacing         = 0.3;  // radial spacing

// --- FR-4 seat ring ---
fr4_seat_dia     = 12.0;      // [STANDARD: 19.0]
fr4_seat_r       = fr4_seat_dia / 2;
fr4_thickness    = 1.0;       // [STANDARD: 1.6] thinner for neonatal
fr4_seat_z       = 2.0;       // [STANDARD: 3.0] above bottom of cavity
fr4_lip          = 0.2;       // centering lip height (unchanged)

// --- Reservoir channel (ring void) ---
reservoir_id     = 8.0;       // [STANDARD: 13.0]
reservoir_od     = 12.0;      // [STANDARD: 19.0]
reservoir_height = 1.0;       // [STANDARD: 1.5]
reservoir_z      = fr4_seat_z + fr4_thickness; // directly above FR-4

// --- Microchannel guide holes ---
microchannel_dia     = 0.5;   // [STANDARD: 0.6] same wire, tighter hole
microchannel_count   = 4;     // [STANDARD: 3] more channels for distribution
microchannel_angle   = 37.5;  // degrees from vertical

// --- Cable exit ---
cable_width_bottom = 2.5;     // [STANDARD: 3.0] thinner neonatal cable
cable_width_top    = 3.5;     // [STANDARD: 4.0]
cable_depth        = 2.5;     // [STANDARD: 3.0]
cable_start_z      = fr4_seat_z;

// --- Mold construction ---
mold_od             = 22.0;   // [STANDARD: 32.0]
mold_radius         = mold_od / 2;
wall_thickness      = 1.5;    // minimum (unchanged)
base_plate_thick    = 4.0;    // [STANDARD: 5.0]
clearance           = 0.3;    // mating surface clearance (unchanged)
draft_angle         = 2.5;    // degrees (unchanged)
fillet_r            = 0.3;    // [STANDARD: 0.2] extra smooth for neonatal
parting_z           = 3.5;    // parting line at mid-electrode height

// --- Alignment pins (smaller for neonatal mold) ---
pin_dia             = 1.5;    // [STANDARD: 2.0]
pin_depth           = 2.5;    // [STANDARD: 3.0]
pin_count           = 4;      // unchanged
pin_ring_r          = (electrode_radius + mold_radius) / 2;

// --- Pour hole & vents ---
pour_hole_dia       = 5.0;    // [STANDARD: 6.0]
vent_hole_dia       = 0.8;    // [STANDARD: 1.0]
vent_count          = 2;

// --- Reservoir fill port ---
reservoir_port_dia  = 1.5;    // [STANDARD: 2.0]

// --- Micro-texture on bottom cavity ---
texture_ring_depth   = 0.10;  // [STANDARD: 0.15] gentler for neonatal skin
texture_ring_spacing = 0.5;   // unchanged

// --- Neonatal-specific: soft gasket rim ---
gasket_rim_height = 0.3;      // creates silicone gasket on electrode edge
gasket_rim_width  = 0.5;      // width of gasket ring

// --- Rendering quality ---
$fn = 120;
