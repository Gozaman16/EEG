// ============================================================
// HairSite Semi-Dry EEG Electrode Mold — Parameters
// Hair-penetrating pin variant of standard EpiScreen
// ============================================================
// Base dimensions identical to EpiScreen.
// Added: pin array parameters for hair-site bottom surface.
// ============================================================

// --- Electrode dimensions (same as EpiScreen) ---
electrode_od        = 24.0;
electrode_height    = 10.0;
electrode_radius    = electrode_od / 2;

// --- Bottom surface cavity (skin-contact) ---
bottom_cavity_dia   = 12.0;
bottom_cavity_depth = 1.0;
bottom_cavity_r     = bottom_cavity_dia / 2;

// --- Spiral exposure platform ---
// For hair-site: platform is FLUSH with pin well bases
// so conductive coating bridges spiral to pin bases.
spiral_platform_dia    = 8.0;
spiral_platform_height = 0.0;  // [EPISCREEN: 0.8] flush for coating continuity
spiral_platform_r      = spiral_platform_dia / 2;
groove_depth           = 0.1;
groove_spacing         = 0.3;

// --- FR-4 seat ring (identical) ---
fr4_seat_dia     = 19.0;
fr4_seat_r       = fr4_seat_dia / 2;
fr4_thickness    = 1.6;
fr4_seat_z       = 3.0;
fr4_lip          = 0.2;

// --- Reservoir channel (identical) ---
reservoir_id     = 13.0;
reservoir_od     = 19.0;
reservoir_height = 1.5;
reservoir_z      = fr4_seat_z + fr4_thickness;

// --- Microchannel guide holes (identical) ---
microchannel_dia     = 0.6;
microchannel_count   = 3;
microchannel_angle   = 37.5;

// --- Cable exit (identical) ---
cable_width_bottom = 3.0;
cable_width_top    = 4.0;
cable_depth        = 3.0;
cable_start_z      = fr4_seat_z;

// --- Mold construction (identical) ---
mold_od             = 32.0;
mold_radius         = mold_od / 2;
wall_thickness      = 1.5;
base_plate_thick    = 5.0;
clearance           = 0.3;
draft_angle         = 2.5;
fillet_r            = 0.2;
parting_z           = 5.0;

// --- Alignment pins (identical) ---
pin_dia             = 2.0;
pin_depth           = 3.0;
pin_count           = 4;
pin_ring_r          = (electrode_radius + mold_radius) / 2;

// --- Pour hole & vents (identical) ---
pour_hole_dia       = 6.0;
vent_hole_dia       = 1.0;
vent_count          = 2;

// --- Reservoir fill port (identical) ---
reservoir_port_dia  = 2.0;

// --- Micro-texture (identical — applied between pins) ---
texture_ring_depth   = 0.15;
texture_ring_spacing = 0.5;

// ============================================================
// PIN ARRAY PARAMETERS (hair-site specific)
// ============================================================
// These create BLIND HOLES (wells) in the bottom mold.
// Silicone fills the wells → pins on the finished electrode.

// --- Pin geometry ---
pin_height          = 3.0;    // pin length (= well depth in mold)
pin_base_dia        = 2.0;    // diameter at base (widest, at mold surface)
pin_tip_dia         = 1.5;    // diameter at tip (narrowest, at well bottom)
pin_tip_r           = pin_tip_dia / 2;  // hemispherical dome radius

// --- Pin arrangement: hexagonal, 1 center + 6 ring ---
pin_center_count    = 1;      // center pin
pin_ring_count      = 6;      // pins on outer ring
pin_total           = pin_center_count + pin_ring_count;
pin_ring_radius     = 7.0;    // radius of outer pin circle from center

// --- Capillary web ridges ---
// Thin raised ridges on the mold cavity floor connecting
// adjacent pin wells. Creates silicone channels between pins
// that wick electrolyte from microchannels to pin tips.
web_ridge_height    = 0.3;    // ridge height on mold floor
web_ridge_width     = 0.6;    // ridge width

// --- Rendering quality ---
$fn = 120;
