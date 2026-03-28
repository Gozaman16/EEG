// ============================================================
// EpiScreen Semi-Dry EEG Electrode Mold — Parametric Design
// Two-part resin 3D-printable mold for silicone casting
// ============================================================
// All dimensions in millimeters.
// Internal cavity dimensions define the ELECTRODE shape.
// ============================================================

// --- Electrode dimensions (cavity) ---
electrode_od        = 24.0;   // outer diameter
electrode_height    = 10.0;   // total height
electrode_radius    = electrode_od / 2;

// --- Bottom surface cavity (skin-contact) ---
bottom_cavity_dia   = 12.0;
bottom_cavity_depth = 1.0;
bottom_cavity_r     = bottom_cavity_dia / 2;

// --- Spiral exposure platform ---
spiral_platform_dia    = 8.0;
spiral_platform_height = 0.8;
spiral_platform_r      = spiral_platform_dia / 2;
groove_depth           = 0.1;   // texture grooves
groove_spacing         = 0.3;   // radial spacing of grooves

// --- FR-4 seat ring ---
fr4_seat_dia     = 19.0;
fr4_seat_r       = fr4_seat_dia / 2;
fr4_thickness    = 1.6;
fr4_seat_z       = 3.0;        // above bottom of cavity
fr4_lip          = 0.2;        // centering lip height

// --- Reservoir channel (ring void) ---
reservoir_id     = 13.0;
reservoir_od     = 19.0;
reservoir_height = 1.5;
reservoir_z      = fr4_seat_z + fr4_thickness; // directly above FR-4

// --- Microchannel guide holes ---
microchannel_dia     = 0.6;
microchannel_count   = 3;
microchannel_angle   = 37.5;   // degrees from vertical (between 30-45)

// --- Cable exit ---
cable_width_bottom = 3.0;
cable_width_top    = 4.0;
cable_depth        = 3.0;
cable_start_z      = fr4_seat_z; // from FR-4 level to top

// --- Mold construction ---
mold_od             = 32.0;
mold_radius         = mold_od / 2;
wall_thickness      = 1.5;     // minimum around all features
base_plate_thick    = 5.0;     // bottom mold base
clearance           = 0.3;     // between mating surfaces
draft_angle         = 2.5;     // degrees on internal vertical walls
fillet_r            = 0.2;     // edge fillets for printability
parting_z           = 5.0;     // parting line height (mid-electrode)

// --- Alignment pins ---
pin_dia             = 2.0;
pin_depth           = 3.0;
pin_count           = 4;
pin_ring_r          = (electrode_radius + mold_radius) / 2; // between cavity and outer wall

// --- Pour hole & vents ---
pour_hole_dia       = 6.0;
vent_hole_dia       = 1.0;
vent_count          = 2;

// --- Reservoir fill port ---
reservoir_port_dia  = 2.0;

// --- Micro-texture on bottom cavity ---
texture_ring_depth   = 0.15;
texture_ring_spacing = 0.5;

// --- Rendering quality ---
$fn = 120;  // smooth circles
