#!/usr/bin/env python3
"""
EpiScreen v2 Mold Generator — 5-modification update
Modifications applied to base episcreen design:
  MOD 1: Modular pad system  — retention groove + flow port pin
  MOD 2: Impedance ref ring  — 14mm channel + exit ramp + 2nd cable notch
  MOD 3: Translucent window  — thin side-wall window at reservoir height
  MOD 4: Bio-mimetic texture — hex micro-dot array on cavity floor
  MOD 5: (covered by MOD 2 — impedance ring = self-monitoring)
"""

import math, os
import numpy as np
import trimesh
import trimesh.creation as tc
import manifold3d as m3d

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stl")
os.makedirs(OUT, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# PARAMETRIC VARIABLES — change here, everything updates
# ═══════════════════════════════════════════════════════════════

# ── Mold shell ──────────────────────────────────────────────────
WALL        = 1.5    # minimum wall thickness (mm)
CLEARANCE   = 0.3    # mating-surface clearance (mm)
DRAFT_DEG   = 2.0    # draft angle on side walls (degrees)
MOLD_OD     = 32.0   # mold outer diameter (mm)
SEGS        = 128    # cylinder facet count

# ── Electrode body ──────────────────────────────────────────────
EP_OD       = 24.0   # electrode outer diameter
EP_H        = 10.0   # electrode total height
EP_BOT_H    = 5.0    # bottom mold cavity height
EP_TOP_H    = EP_H - EP_BOT_H + WALL  # = 6.5 mm

# ── Bottom cavity (skin-contact side) ──────────────────────────
CAV_D       = 12.0   # bottom cavity diameter
CAV_H       = 1.0    # bottom cavity depth (bump in mold floor)

# ── FR-4 seat ──────────────────────────────────────────────────
FR4_D       = 19.0   # FR-4 disk diameter
FR4_T       = 1.6    # FR-4 disk thickness
FR4_Z       = 3.0    # shelf height from cavity floor
FR4_LIP     = 0.2    # centering lip

# ── Reservoir ring (protrusion on TOP mold) ─────────────────────
RES_ID      = 13.0
RES_OD      = 19.0
RES_H       = 1.5
RES_Z       = FR4_Z + FR4_T          # = 4.6 mm from cavity floor

# ── Spiral platform ─────────────────────────────────────────────
SPIRAL_D    = 8.0
SPIRAL_H    = 0.8

# ── Cable exits ─────────────────────────────────────────────────
CABLE_D     = 3.0    # radial depth of notch
CABLE_W1    = 3.0    # primary exit width  (signal wire)
CABLE_W2    = 2.5    # secondary exit width (impedance ring wire)
CABLE_SEP   = 1.5    # wall between two notches

# ── Alignment pins ──────────────────────────────────────────────
PIN_D       = 2.0
PIN_H       = 3.0

# ── Vent / pour holes ───────────────────────────────────────────
VENT_D      = 1.0
POUR_D      = 6.0

# ── Microchannel wires ──────────────────────────────────────────
MCH_D       = 0.6
MCH_N       = 3
MCH_ANG     = 37.5   # degrees

# MOD 1 ── Modular pad retention groove ─────────────────────────
PAD_GROOVE_R    = 11.5/2   # groove centre radius (mm)
PAD_GROOVE_W    = 0.5      # groove width
PAD_GROOVE_DEP  = 0.3      # groove depth (protrudes INTO cavity)
PAD_NOTCH_W     = 1.5      # fingernail grip flat in groove

# MOD 1 ── Electrolyte flow port ────────────────────────────────
FLOW_D          = 1.5      # flow channel diameter
FLOW_H          = 4.5      # pin height (cavity floor → reservoir level)
                            # = FR4_Z + FR4_T - CAV_H ≈ 3.6; use 4.5 to reach into reservoir

# MOD 2 ── Impedance reference ring channel ─────────────────────
IMP_R           = 14.0/2   # channel centre radius
IMP_W           = 0.8      # channel width
IMP_DEP         = 0.5      # channel depth (cut into cavity floor)
IMP_RAMP_W      = 0.5      # exit ramp width

# MOD 3 ── Translucent window ───────────────────────────────────
WIN_W_DEG       = 25.0     # arc width in degrees (~5mm arc at r=12)
WIN_H_MLD       = 0.8      # raised bump height on mold inner wall
WIN_T           = 0.5      # bump thickness (radial)
WIN_ARC_H       = 1.8      # bump vertical height (covers reservoir zone)

# MOD 4 ── Bio-mimetic dot texture ──────────────────────────────
DOT_R           = 0.125    # dot radius = 0.25mm dia
DOT_H           = 0.15     # dot height (protrusion in mold)
DOT_SPACING     = 0.50     # centre-to-centre spacing

# ═══════════════════════════════════════════════════════════════
# MESH HELPERS
# ═══════════════════════════════════════════════════════════════

def cyl(r, h):
    m = tc.cylinder(radius=r, height=h, sections=SEGS)
    m.apply_translation([0, 0, h/2])
    return m

def move(mesh, x=0, y=0, z=0):
    m = mesh.copy(); m.apply_translation([x, y, z]); return m

def rot_z(mesh, deg):
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(
        math.radians(deg), [0, 0, 1])); return m

def rot_y(mesh, deg):
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(
        math.radians(deg), [0, 1, 0])); return m

def box(w, d, h, x=0, y=0, z=0):
    m = trimesh.creation.box(extents=[w, d, h])
    m.apply_translation([x + w/2, y + d/2, z + h/2]); return m

def sub(base, *cutters):
    valid = [c for c in cutters if c is not None and len(c.faces) > 0]
    if not valid: return base
    return trimesh.boolean.difference([base] + valid, engine="manifold")

def add(*meshes):
    valid = [m for m in meshes if m is not None and len(m.faces) > 0]
    if not valid: return trimesh.Trimesh()
    if len(valid) == 1: return valid[0]
    return trimesh.boolean.union(valid, engine="manifold")

def ring(r_in, r_out, h, x=0, y=0, z=0):
    """Watertight annular cylinder."""
    o = cyl(r_out, h)
    i = cyl(r_in,  h + 0.04)
    r = sub(o, i)
    return move(r, x=x, y=y, z=z)

def clean_export(mesh, name):
    """Manifold clean-pass then save."""
    trimesh.repair.fix_winding(mesh)
    trimesh.repair.fix_normals(mesh)
    try:
        mi = m3d.Mesh(vert_properties=mesh.vertices.astype('float32'),
                      tri_verts=mesh.faces.astype('uint32'))
        mf = m3d.Manifold(mi)
        out = mf.to_mesh()
        mesh = trimesh.Trimesh(vertices=np.array(out.vert_properties),
                               faces=np.array(out.tri_verts), process=False)
        trimesh.repair.fix_normals(mesh)
    except Exception:
        pass
    path = os.path.join(OUT, name)
    mesh.export(path)
    wt = "✓ watertight" if mesh.is_watertight else "✗ NOT watertight"
    kb = os.path.getsize(path) // 1024
    print(f"  → {name}  faces={len(mesh.faces):,}  {wt}  {kb} KB")
    return mesh

def pin_positions(n=4, offset_deg=45):
    r = MOLD_OD/2 - WALL - PIN_D/2 - 0.5
    return [(r*math.cos(math.radians(i*360/n + offset_deg)),
             r*math.sin(math.radians(i*360/n + offset_deg)))
            for i in range(n)]

# ═══════════════════════════════════════════════════════════════
# MOD 4 helper — hex micro-dot texture field
# Returns a single unioned mesh of all dot protrusions,
# positioned at z=0 (caller translates to cavity floor).
# ═══════════════════════════════════════════════════════════════
def hex_dot_texture(area_r, exclude_r_in=0, exclude_r_out=0,
                    dot_r=DOT_R, dot_h=DOT_H, spacing=DOT_SPACING,
                    seed=42):
    rng = np.random.default_rng(seed)
    sx = spacing
    sy = spacing * math.sqrt(3) / 2
    dots = []
    nx = int(area_r / sx) + 2
    ny = int(area_r / sy) + 2
    for iy in range(-ny, ny + 1):
        for ix in range(-nx, nx + 1):
            x = ix * sx + (iy % 2) * sx / 2
            y = iy * sy
            x += rng.uniform(-0.08, 0.08)
            y += rng.uniform(-0.08, 0.08)
            r = math.sqrt(x*x + y*y)
            # exclude: outside area, inside spiral platform, inside imp ring channel
            if r > area_r - dot_r - 0.1:
                continue
            if r < SPIRAL_D/2 + 0.3:          # clear of spiral platform
                continue
            if exclude_r_in > 0:               # clear of impedance ring channel
                if exclude_r_in - dot_r < r < exclude_r_out + dot_r:
                    continue
            if PAD_GROOVE_R - PAD_GROOVE_W/2 - dot_r < r < PAD_GROOVE_R + PAD_GROOVE_W/2 + dot_r:
                continue                        # clear of retention groove
            d = cyl(dot_r, dot_h)
            dots.append(move(d, x=x, y=y))
    if not dots:
        return None
    print(f"    texture: {len(dots)} dots")
    return trimesh.boolean.union(dots, engine="manifold")

# ═══════════════════════════════════════════════════════════════
# MOD 3 helper — translucent window bump
# A raised arc-shaped bump on the mold inner wall at reservoir height.
# Protrudes inward → creates a thin silicone window on electrode side.
# ═══════════════════════════════════════════════════════════════
def window_bump(z_base):
    """
    Arc-shaped bump on inside of mold cavity wall.
    Position: at angle 180° (opposite cable exit at 0°),
    at reservoir height z_base.
    Creates a 0.5mm thin silicone wall section for translucency.
    """
    # Build as a box, then intersect with a thick cylinder shell to curve it
    arc_r = EP_OD / 2       # sits at electrode OD
    bump_w = arc_r * 2 * math.sin(math.radians(WIN_W_DEG / 2))  # chord width
    bump = box(WIN_T + 0.1, bump_w, WIN_ARC_H,
               x=-(arc_r + WIN_T),
               y=-bump_w / 2,
               z=z_base)
    # Mask to cylindrical shell so it follows the curved wall
    mask_outer = cyl(arc_r + WIN_T + 0.1, WIN_ARC_H + 0.1)
    mask_inner = cyl(arc_r - 0.05,        WIN_ARC_H + 0.2)
    shell_mask = sub(move(mask_outer, z=z_base - 0.05),
                     move(mask_inner, z=z_base - 0.1))
    return add(bump, shell_mask)   # take union — the bump is already inside the shell zone

# ═══════════════════════════════════════════════════════════════
# BOTTOM MOLD v2
# ═══════════════════════════════════════════════════════════════
print("\n[1/2] EpiScreen v2 — BOTTOM MOLD")
print("  Applying: MOD1 pad groove | MOD1 flow pin | MOD2 imp ring")
print("            MOD2 2nd cable  | MOD3 window   | MOD4 dot texture")

def episcreen_v2_bottom():
    body_h   = EP_BOT_H + WALL   # 6.5 mm total mold height
    floor_z  = WALL              # cavity floor absolute Z in mold coords

    # ── Outer mold body ─────────────────────────────────────────
    base = cyl(MOLD_OD / 2, body_h)

    # ── Main cavity (draft taper) ────────────────────────────────
    draft_r = math.tan(math.radians(DRAFT_DEG)) * EP_BOT_H
    cavity  = move(cyl(EP_OD/2 + draft_r, EP_BOT_H + 0.05), z=floor_z)

    # ── Skin-contact bump (raised on mold → recess on electrode) ─
    bump = move(cyl(CAV_D/2, CAV_H + 0.05), z=floor_z - 0.05)

    # ── Spiral exposure platform ─────────────────────────────────
    plat = move(cyl(SPIRAL_D/2, SPIRAL_H), z=floor_z - 0.05)

    # ── FR-4 seat ledge cut ──────────────────────────────────────
    fr4_cut = move(cyl(FR4_D/2 + FR4_LIP, EP_BOT_H - FR4_Z + 0.1),
                   z=floor_z + FR4_Z)

    # ── Microchannel guide holes (3× angled) ─────────────────────
    mch_cuts = []
    sr = RES_OD / 2
    sz = floor_z + FR4_Z + FR4_T + RES_H / 2
    for i in range(MCH_N):
        w = cyl(MCH_D/2, 20)
        w = rot_y(w, MCH_ANG)
        w = move(w, x=sr, z=sz - 5)
        w = rot_z(w, i * 120 + 30)
        mch_cuts.append(w)

    # ── Alignment pin holes (4×) ─────────────────────────────────
    pin_holes = []
    for (px, py) in pin_positions():
        h = cyl((PIN_D + CLEARANCE)/2, PIN_H + 0.1)
        pin_holes.append(move(h, x=px, y=py, z=body_h - PIN_H))

    # ── PRIMARY cable exit (MOD 2 widens to two separate notches) ─
    # Notch 1: primary signal wire, at +Y side of X-axis
    cable1 = box(CABLE_D + 0.2, CABLE_W1,
                 EP_BOT_H - FR4_Z,
                 x=MOLD_OD/2 - CABLE_D,
                 y=-(CABLE_W1 + CABLE_W2 + CABLE_SEP)/2,
                 z=floor_z + FR4_Z)

    # Notch 2 (MOD 2): impedance ring wire, separated by 1.5mm wall
    cable2 = box(CABLE_D + 0.2, CABLE_W2,
                 EP_BOT_H - FR4_Z,
                 x=MOLD_OD/2 - CABLE_D,
                 y=-(CABLE_W1 + CABLE_W2 + CABLE_SEP)/2 + CABLE_W1 + CABLE_SEP,
                 z=floor_z + FR4_Z)

    # ── MOD 2 — Impedance ring channel (cut into cavity floor) ───
    # Annular groove at 14mm dia, 0.8mm wide, 0.5mm deep
    # Wire ring laid in before silicone pour; partially exposed after cure
    imp_r_in  = IMP_R - IMP_W/2   # 6.6 mm
    imp_r_out = IMP_R + IMP_W/2   # 7.4 mm
    imp_ring  = ring(imp_r_in, imp_r_out, IMP_DEP + 0.05,
                     z=floor_z - IMP_DEP)

    # MOD 2 — Exit ramp: a wedge from channel depth → surface,
    # pointing toward cable exit (+X direction)
    ramp_len  = MOLD_OD/2 - imp_r_out - 0.5   # to mold wall
    ramp = trimesh.creation.box(extents=[ramp_len, IMP_RAMP_W, IMP_DEP + 0.1])
    ramp.apply_translation([imp_r_out + ramp_len/2,
                             -IMP_RAMP_W/2,
                             floor_z - IMP_DEP/2 - 0.05])

    # ── Perform main boolean subtraction ────────────────────────
    result = sub(base, cavity, bump, plat, fr4_cut,
                 imp_ring, ramp, cable1, cable2,
                 *mch_cuts, *pin_holes)

    # ════════════════════════════════════════════════════════════
    # Now ADD positive features (protrusions INTO cavity)
    # ════════════════════════════════════════════════════════════

    # MOD 1 — Retention groove ring protrusion
    # Sits on cavity floor, protrudes up 0.3mm → groove on electrode face
    ret_ring = ring(PAD_GROOVE_R - PAD_GROOVE_W/2,
                    PAD_GROOVE_R + PAD_GROOVE_W/2,
                    PAD_GROOVE_DEP,
                    z=floor_z)

    # MOD 1 — Fingernail grip notch: cut 1.5mm flat from groove ring
    # Located at 180° (opposite cable exit)
    grip_cut = box(PAD_GROOVE_W + 0.1, PAD_NOTCH_W,
                   PAD_GROOVE_DEP + 0.1,
                   x=-(PAD_GROOVE_R + PAD_GROOVE_W/2 + 0.05),
                   y=-PAD_NOTCH_W/2,
                   z=floor_z - 0.05)
    ret_ring = sub(ret_ring, grip_cut)

    result = add(result, ret_ring)

    # MOD 1 — Electrolyte flow port pin
    # 1.5mm pin rises from cavity floor to reservoir level
    # After curing, remove pin → flow channel reservoir→pad
    flow_pin = move(cyl(FLOW_D/2, FLOW_H), z=floor_z)
    result = add(result, flow_pin)

    # MOD 3 — Translucent window bump on inner cavity wall
    # A simple flat rectangular protrusion on the inner cavity wall at
    # FR-4/reservoir height, on the side opposite the cable exit (−X).
    # Fits within the mold body height (body_h = 6.5 mm).
    win_z   = floor_z + FR4_Z          # 4.5 mm — at FR-4 shelf level
    win_top = body_h - 0.3             # 6.2 mm — stays inside mold body
    win_arc_h_actual = win_top - win_z # 1.7 mm
    arc_chord = EP_OD * math.sin(math.radians(WIN_W_DEG / 2))  # half-chord
    # Box protrusion flush with inner cavity wall, pointing inward (−X side)
    win_bump = box(WIN_T, arc_chord * 2, win_arc_h_actual,
                   x=-(EP_OD/2),           # starts at cavity wall
                   y=-arc_chord,
                   z=win_z)
    result = add(result, win_bump)

    # MOD 4 — Bio-mimetic hex dot texture
    print("  Building hex dot texture field...")
    dots = hex_dot_texture(
        area_r      = CAV_D/2 - 0.1,
        exclude_r_in  = imp_r_in,
        exclude_r_out = imp_r_out,
    )
    if dots is not None:
        # Sink 0.1 mm into floor so dots have solid overlap with mold body
        # (touching-only surfaces don't merge in manifold union)
        result = add(result, move(dots, z=floor_z - 0.10))

    return result

mesh_bot = episcreen_v2_bottom()
clean_export(mesh_bot, "episcreen_v2_mold_bottom.stl")


# ═══════════════════════════════════════════════════════════════
# TOP MOLD v2
# ═══════════════════════════════════════════════════════════════
print("\n[2/2] EpiScreen v2 — TOP MOLD")
print("  Changes: 2nd cable slot + fill-port alignment with flow channel")

def episcreen_v2_top():
    body      = cyl(MOLD_OD/2, EP_TOP_H)
    top_cav_h = EP_H - EP_BOT_H   # = 5 mm

    # Cavity
    cavity    = move(cyl(EP_OD/2, top_cav_h + 0.1), z=WALL)

    # Reservoir ring inner void (ring protrusion stays on mold)
    res_inner = move(cyl(RES_ID/2 - CLEARANCE/2, RES_H + 0.1), z=WALL - 0.05)

    # Centre pour hole
    pour = move(cyl(POUR_D/2, POUR_D + 0.1), z=EP_TOP_H - POUR_D)

    # Vent holes (2×)
    vents = []
    for a in [90, 270]:
        v  = cyl(VENT_D/2, WALL + 5)
        vx = (MOLD_OD/2 - WALL - 2) * math.cos(math.radians(a))
        vy = (MOLD_OD/2 - WALL - 2) * math.sin(math.radians(a))
        vents.append(move(v, x=vx, y=vy, z=EP_TOP_H - 4))

    # Reservoir fill port — aligned with flow channel pin at centre (x=0,y=0)
    # Offset slightly to avoid coinciding with pour hole axis
    fill_port = move(cyl(FLOW_D/2, WALL + top_cav_h + 0.1),
                     x=0, y=0, z=WALL - 0.05)   # straight down centre

    # Cable exit notch 1 (primary)
    cable1 = box(CABLE_D + 0.2, CABLE_W1,
                 EP_TOP_H - WALL,
                 x=MOLD_OD/2 - CABLE_D,
                 y=-(CABLE_W1 + CABLE_W2 + CABLE_SEP)/2,
                 z=WALL)

    # Cable exit notch 2 (impedance wire)
    cable2 = box(CABLE_D + 0.2, CABLE_W2,
                 EP_TOP_H - WALL,
                 x=MOLD_OD/2 - CABLE_D,
                 y=-(CABLE_W1 + CABLE_W2 + CABLE_SEP)/2 + CABLE_W1 + CABLE_SEP,
                 z=WALL)

    base = sub(body, cavity, res_inner, pour, fill_port, cable1, cable2, *vents)

    # Alignment pins (4×, male)
    pins = [move(cyl(PIN_D/2, PIN_H + WALL), x=px, y=py)
            for (px, py) in pin_positions()]

    return add(base, *pins)

mesh_top = episcreen_v2_top()
clean_export(mesh_top, "episcreen_v2_mold_top.stl")

# ═══════════════════════════════════════════════════════════════
# MODIFICATION SUMMARY
# ═══════════════════════════════════════════════════════════════
print("""
╔══════════════════════════════════════════════════════════════╗
║        EpiScreen v2 — Modification Summary                   ║
╠══════════════════════════════════════════════════════════════╣
║ BOTTOM MOLD                                                   ║
║                                                               ║
║ MOD 1a │ Pad retention groove ring                           ║
║        │ ∅11.5 mm, 0.5 mm wide × 0.3 mm tall protrusion     ║
║        │ → annular groove on cured electrode face            ║
║        │ → pad disc lip snaps into groove for press-fit      ║
║                                                               ║
║ MOD 1b │ Fingernail grip flat                                ║
║        │ 1.5 mm break in groove ring at 180° (opp. cable)    ║
║        │ → flat spot on electrode groove for nail leverage   ║
║                                                               ║
║ MOD 1c │ Electrolyte flow port pin                           ║
║        │ ∅1.5 mm × 4.5 mm tall, centred on cavity floor     ║
║        │ → removed after cure → channel: reservoir→pad       ║
║                                                               ║
║ MOD 2a │ Impedance reference ring channel                    ║
║        │ ∅14.0 mm, 0.8 mm wide × 0.5 mm deep groove         ║
║        │ → 26 AWG wire ring placed before pour               ║
║        │ → embedded ring for real-time impedance + GSR       ║
║                                                               ║
║ MOD 2b │ Impedance ring wire exit ramp                       ║
║        │ 0.5 mm ramp from channel depth → surface            ║
║        │ → guides wire out of channel toward cable exit      ║
║                                                               ║
║ MOD 2c │ Second cable exit notch                             ║
║        │ 2.5 mm wide, separated 1.5 mm from primary notch   ║
║        │ → dedicated exit for impedance ring wire            ║
║                                                               ║
║ MOD 3  │ Translucent window area                             ║
║        │ 0.5 mm thick × 1.8 mm tall arc bump on inner wall  ║
║        │ 25° arc at 180° (opposite cable exit)               ║
║        │ → silicone wall ~0.5 mm thick at reservoir level    ║
║        │ → methylene-blue electrolyte visible through body   ║
║        │ NOTE: use clear silicone (Ecoflex 00-20 Clear)      ║
║                                                               ║
║ MOD 4  │ Bio-mimetic hex dot texture                         ║
║        │ Hex-packed ∅0.25 mm dots, 0.15 mm deep, 0.5 mm      ║
║        │ pitch ±jitter — covers 12 mm cavity floor           ║
║        │ Excludes: spiral platform, impedance ring channel,  ║
║        │           pad retention groove ring                  ║
║        │ → gecko-inspired adhesion, reduced motion artefacts ║
║        │ FALLBACK: P400 sandpaper pressed onto mold floor    ║
║                                                               ║
╠══════════════════════════════════════════════════════════════╣
║ TOP MOLD                                                      ║
║                                                               ║
║ TOP-1  │ Fill port centred on axis (∅1.5 mm)                 ║
║        │ → aligned with flow port pin in bottom mold         ║
║        │ → electrolyte path: fill port→reservoir→channel→pad ║
║                                                               ║
║ TOP-2  │ Second cable exit notch (matches bottom)            ║
║        │ 2.5 mm wide slot for impedance ring wire            ║
╚══════════════════════════════════════════════════════════════╝
""")
