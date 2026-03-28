// ============================================================
// EpiScreen EEG Electrode Mold — Shared Parameters
// Project: EpiScreen / NeoGuard / HairSite / ImpactGuard
// Author:  Generated for ISEF submission
// Date:    2026-03-28
// License: MIT
// ============================================================

// ── Global print-quality settings ──────────────────────────
$fn = 120;           // Cylinder facets (high quality)
FILLET  = 0.2;       // Edge fillet for printability (mm)
CLEARANCE = 0.3;     // Mating-surface clearance (mm)
WALL    = 1.5;       // Minimum wall thickness (mm)
DRAFT   = 2;         // Draft angle on vertical walls (deg)

// ── Alignment pin/hole geometry ────────────────────────────
PIN_D   = 2.0;       // Alignment pin diameter (mm)
PIN_H   = 3.0;       // Alignment pin height (mm)
PIN_R   = 4;         // Number of alignment pins

// ── Vent hole geometry ──────────────────────────────────────
VENT_D  = 1.0;       // Vent hole diameter (mm)

// ── EpiScreen standard electrode (24 mm) ───────────────────
EP_OD       = 24.0;  // Electrode outer diameter
EP_H        = 10.0;  // Electrode total height
EP_BOT_CAV_D = 12.0; // Bottom skin-contact cavity diameter
EP_BOT_CAV_H = 1.0;  // Bottom skin-contact cavity depth
EP_MOLD_OD  = EP_OD + 2*WALL + 4.0;  // = 32 mm mold OD
EP_BOT_H    = 5.0;   // Bottom mold piece height
EP_TOP_H    = EP_H - EP_BOT_H + WALL; // Top mold piece height
EP_POUR_D   = 6.0;   // Silicone pour hole diameter

// FR-4 seat
EP_FR4_D    = 19.0;  // FR-4 disk diameter
EP_FR4_T    = 1.6;   // FR-4 disk thickness
EP_FR4_Z    = 3.0;   // Shelf height above cavity bottom
EP_FR4_LIP  = 0.2;   // Centering lip width

// Reservoir ring (protrusion on top mold)
EP_RES_ID   = 13.0;  // Reservoir inner diameter
EP_RES_OD   = 19.0;  // Reservoir outer diameter
EP_RES_H    = 1.5;   // Reservoir channel height

// Spiral platform
EP_SPIRAL_D = 8.0;   // Spiral platform diameter
EP_SPIRAL_H = 0.8;   // Spiral platform height

// Cable exit notch
EP_CABLE_W_BOT = 3.0; // Cable notch width at bottom
EP_CABLE_W_TOP = 4.0; // Cable notch width at top (funnel)
EP_CABLE_D  = 3.0;   // Cable notch depth

// Microchannel wires
EP_MCH_D    = 0.6;   // Microchannel hole diameter
EP_MCH_N    = 3;     // Number of microchannel holes
EP_MCH_ANG  = 37.5;  // Microchannel angle (degrees)

// ── NeoGuard neonatal electrode (15 mm) ────────────────────
NG_OD       = 15.0;
NG_H        = 8.0;
NG_BOT_CAV_D = 8.0;
NG_BOT_CAV_H = 0.8;
NG_MOLD_OD  = NG_OD + 2*WALL + 4.0; // ~22 mm
NG_BOT_H    = 4.0;
NG_TOP_H    = NG_H - NG_BOT_H + WALL;
NG_POUR_D   = 4.0;
NG_FR4_D    = 12.0;
NG_FR4_T    = 1.0;
NG_FR4_Z    = 2.5;
NG_RES_ID   = 8.5;
NG_RES_OD   = 12.0;
NG_RES_H    = 1.2;
NG_SPIRAL_D = 5.0;
NG_SPIRAL_H = 0.6;
NG_CABLE_W_BOT = 2.5;
NG_CABLE_W_TOP = 3.5;
NG_CABLE_D  = 2.5;

// ── HairSite electrode (24 mm + 7 penetration pins) ────────
HS_OD       = 24.0;  // Same outer body as EpiScreen
HS_H        = 12.0;  // Taller to accommodate pins
HS_MOLD_OD  = HS_OD + 2*WALL + 4.0; // 32 mm
HS_BOT_H    = 6.0;
HS_TOP_H    = HS_H - HS_BOT_H + WALL;
HS_POUR_D   = 6.0;

// Pin array (7 pins: 1 center + 6 at 60-deg spacing)
HS_PIN_D    = 1.2;   // Pin hole diameter in mold
HS_PIN_H    = 8.0;   // Pin post height in mold
HS_PIN_RAD  = 6.0;   // Radius of outer 6 pins
HS_PIN_N    = 7;     // Total pins

// ── ImpactGuard helmet adapter ──────────────────────────────
IG_OD       = 38.0;  // Adapter outer diameter
IG_H        = 12.0;  // Total height
IG_ELEC_D   = 24.5;  // Electrode socket (electrode OD + clearance)
IG_ELEC_H   = 8.0;   // Electrode insertion depth
IG_SNAP_R   = 0.8;   // Snap-fit ring radius
IG_MOUNT_W  = 50.0;  // Mounting plate width
IG_MOUNT_H  = 8.0;   // Mounting plate height

// ── Headband mount — adult (24 mm electrode) ───────────────
HBA_BAND_W  = 22.0;  // Band width
HBA_BAND_T  = 2.5;   // Band thickness
HBA_ELEC_D  = 24.5;  // Electrode socket
HBA_ELEC_H  = 6.0;   // Electrode retention depth
HBA_CLIP_H  = 12.0;  // Clip block height
HBA_CLIP_W  = 30.0;  // Clip block width
HBA_SNAP_R  = 0.8;   // Snap ring radius

// ── Headband mount — neonatal (15 mm electrode) ────────────
HBN_BAND_W  = 16.0;
HBN_BAND_T  = 2.0;
HBN_ELEC_D  = 15.5;
HBN_ELEC_H  = 5.0;
HBN_CLIP_H  = 9.0;
HBN_CLIP_W  = 22.0;
HBN_SNAP_R  = 0.6;

// ── Concentric micro-texture on skin-contact surface ───────
TEXTURE_STEP  = 0.5;  // Ring spacing (mm)
TEXTURE_DEPTH = 0.15; // Ring depth (mm)
TEXTURE_W     = 0.2;  // Ring width (mm)
