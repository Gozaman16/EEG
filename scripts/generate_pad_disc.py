#!/usr/bin/env python3
"""
EpiScreen Pad Disc Mold Generator
Two-part mold for casting the removable pad disc that snaps into
the EpiScreen v2 electrode bottom cavity.
"""

import math, os
import numpy as np
import trimesh
import trimesh.creation as tc
import manifold3d as m3d

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stl")
os.makedirs(OUT, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# PARAMETRIC VARIABLES
# ═══════════════════════════════════════════════════════════════

# ── Pad disc geometry ───────────────────────────────────────────
DISC_OD         = 11.8   # outer diameter (12mm cavity - 0.1mm per side)
DISC_T          = 2.5    # total thickness

# ── Retention lip (snaps into groove on electrode body) ─────────
LIP_W           = 0.5    # radial width of snap lip
LIP_H           = 0.3    # height of snap lip
LIP_Z           = 0.5    # distance from bottom surface to lip centre

# ── Fingernail grip ──────────────────────────────────────────────
GRIP_W          = 1.5    # arc-length of flat in lip

# ── Contact pad (top surface, faces into electrode) ─────────────
PAD_D           = 8.0    # contact pad diameter
PAD_H           = 0.3    # raised height (presses on copper spiral)

# ── Absorbent ring seat (annular groove on top surface) ─────────
ABS_ID          = 8.5    # inner diameter of cotton seat
ABS_OD          = 11.0   # outer diameter of cotton seat
ABS_DEP         = 1.0    # groove depth

# ── Electrolyte flow hole ────────────────────────────────────────
FLOW_D          = 1.5    # centre through-hole diameter

# ── Convex skin crown (bottom surface) ──────────────────────────
CROWN           = 0.3    # crown height over 12mm span

# ── Electrolyte distribution channels (bottom surface) ──────────
CH_W            = 0.3    # channel width
CH_DEP          = 0.2    # channel depth
CH_N            = 3      # number of channels (120° apart)

# ── Hex dot texture (skin-contact surface) ──────────────────────
DOT_R           = 0.125  # 0.25mm dia
DOT_H           = 0.15
DOT_SPACING     = 0.50

# ── Mold outer shell ────────────────────────────────────────────
MOLD_OD         = 18.0
BOT_H           = 5.0    # bottom mold total height
TOP_H           = 3.0    # top mold total height
WALL            = 1.5
SEGS            = 96

# ── Alignment pins ──────────────────────────────────────────────
PIN_D           = 1.5
PIN_H           = 2.0
PIN_R           = MOLD_OD/2 - WALL - PIN_D/2 - 0.3   # radial position

# ── Clearances ──────────────────────────────────────────────────
CL              = 0.05   # small Boolean overlap to avoid touching-surface issues

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
        math.radians(deg), [0, 0, 1]))
    return m

def box(w, d, h, x=0, y=0, z=0):
    m = trimesh.creation.box(extents=[w, d, h])
    m.apply_translation([x + w/2, y + d/2, z + h/2])
    return m

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
    o = cyl(r_out, h)
    i = cyl(r_in, h + 2*CL)
    r = sub(o, move(i, z=-CL))
    return move(r, x=x, y=y, z=z)

def clean_export(mesh, name):
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

def pin_positions(n=2):
    """Two alignment pins at 90° and 270°."""
    return [(PIN_R * math.cos(math.radians(a)),
             PIN_R * math.sin(math.radians(a)))
            for a in [90, 270]]

def hex_dot_texture(area_r, exclude_r=0, seed=42):
    """Hex-packed dot field for skin-contact surface of pad disc."""
    rng = np.random.default_rng(seed)
    sx = DOT_SPACING
    sy = DOT_SPACING * math.sqrt(3) / 2
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
            if r > area_r - DOT_R - 0.1:
                continue
            if r < exclude_r + DOT_R + 0.1:
                continue
            dots.append(move(cyl(DOT_R, DOT_H), x=x, y=y))
    if not dots:
        return None
    print(f"    texture: {len(dots)} dots")
    return trimesh.boolean.union(dots, engine="manifold")

# ═══════════════════════════════════════════════════════════════
# CONVEX FLOOR (approximate crown by sphere-cap subtraction)
# ═══════════════════════════════════════════════════════════════

def convex_floor_cut(cavity_r, crown, z_base):
    """
    Returns a cutter that, when subtracted from a flat floor,
    produces a slightly convex surface (crown height over cavity_r span).
    Uses a large-radius sphere cap approximation via a subtracted cylinder
    with a spherical endcap.
    r_sphere = (cavity_r^2 + crown^2) / (2 * crown)
    """
    r_sphere = (cavity_r**2 + crown**2) / (2 * crown)
    # Sphere placed so its top sits at z_base + crown, giving crown at centre
    sphere_z = z_base + crown - r_sphere
    sphere = trimesh.creation.icosphere(subdivisions=4, radius=r_sphere)
    sphere.apply_translation([0, 0, sphere_z])
    # Clamp to only the region inside cavity_r and below z_base + crown + 0.5
    clip = cyl(cavity_r + 0.5, crown + 1.0)
    clip_moved = move(clip, z=z_base - 0.5)
    return trimesh.boolean.intersection([sphere, clip_moved], engine="manifold")

# ═══════════════════════════════════════════════════════════════
# BOTTOM MOLD
# Cavity faces DOWN (skin side). Floor = WALL from bottom.
# The pad disc sits with skin-contact face DOWN in this cavity.
# ═══════════════════════════════════════════════════════════════
print("\n[1/2] Pad disc — BOTTOM MOLD")

def pad_disc_bottom():
    body_h  = BOT_H
    floor_z = WALL   # cavity floor absolute Z

    # ── Mold outer body ──────────────────────────────────────────
    base = cyl(MOLD_OD/2, body_h)

    # ── Main disc cavity ─────────────────────────────────────────
    # Diameter = DISC_OD + small clearance
    cavity = move(cyl(DISC_OD/2 + 0.05, DISC_T + CL), z=floor_z - CL)

    # ── Convex floor (creates convex skin surface on disc) ───────
    # Subtract a sphere cap from the flat floor
    crown_cut = convex_floor_cut(DISC_OD/2, CROWN, floor_z)

    # ── Electrolyte distribution channels in floor ───────────────
    # 3× radial grooves from centre to disc edge, 120° apart
    ch_cuts = []
    ch_len = DISC_OD/2 + 0.1
    for i in range(CH_N):
        ch = box(ch_len, CH_W, CH_DEP + CL,
                 x=0, y=-CH_W/2, z=floor_z - CH_DEP - CL)
        ch_cuts.append(rot_z(ch, i * 120))

    # ── Centre flow hole pin ──────────────────────────────────────
    # Through-pin: rises from floor through full cavity depth
    flow_pin = move(cyl(FLOW_D/2, DISC_T + 2*CL), z=floor_z - CL)

    # ── Retention lip groove in cavity wall ──────────────────────
    # At LIP_Z from floor, width LIP_W, depth LIP_H into the cavity wall
    # The groove IN the mold creates the LIP protrusion ON the disc
    lip_ring = ring(DISC_OD/2 + 0.05,
                    DISC_OD/2 + 0.05 + LIP_H + CL,
                    LIP_W + CL,
                    z=floor_z + LIP_Z - LIP_W/2)

    # ── Fingernail grip flat (removes LIP from 1.5mm section at 0°) ─
    # Located at +X (0°), 1.5mm wide
    grip_slot = box(LIP_H + 0.2, GRIP_W,
                    LIP_W + 2*CL,
                    x=DISC_OD/2 - CL,
                    y=-GRIP_W/2,
                    z=floor_z + LIP_Z - LIP_W/2 - CL)

    # ── Alignment pin holes ──────────────────────────────────────
    pin_holes = [move(cyl((PIN_D + 0.1)/2, PIN_H + CL),
                      x=px, y=py, z=body_h - PIN_H - CL)
                 for (px, py) in pin_positions()]

    # ── Boolean: subtract everything ────────────────────────────
    result = sub(base, cavity, crown_cut, flow_pin,
                 lip_ring, grip_slot, *ch_cuts, *pin_holes)

    # ── ADD hex dot texture protrusions on cavity floor ──────────
    print("  Building hex dot texture (skin-contact surface)...")
    dots = hex_dot_texture(area_r=DISC_OD/2 - 0.2,
                           exclude_r=FLOW_D/2 + 0.2)
    if dots is not None:
        result = add(result, move(dots, z=floor_z - 0.10))

    return result

mesh_bot = pad_disc_bottom()
clean_export(mesh_bot, "pad_disc_mold_bottom.stl")


# ═══════════════════════════════════════════════════════════════
# TOP MOLD (LID)
# The lid underside creates the top surface of the pad disc
# (the surface that faces INTO the electrode body).
# Features: contact pad bump, absorbent ring protrusion, vent hole.
# ═══════════════════════════════════════════════════════════════
print("\n[2/2] Pad disc — TOP MOLD")

def pad_disc_top():
    body_h  = TOP_H
    lid_h   = WALL   # solid lid above disc cavity

    # ── Mold outer body ──────────────────────────────────────────
    base = cyl(MOLD_OD/2, body_h)

    # ── Disc cavity (must match bottom mold) ─────────────────────
    # Cavity depth = DISC_T; the lid sits on the parting plane
    cavity = move(cyl(DISC_OD/2 + 0.05, DISC_T + CL), z=lid_h - CL)

    # ── Centre flow hole through-pin ─────────────────────────────
    flow_pin = move(cyl(FLOW_D/2, DISC_T + body_h), z=-CL)

    # ── Alignment pin holes (female, receive bottom mold pins) ───
    pin_holes = [move(cyl((PIN_D + 0.1)/2, PIN_H + 0.2),
                      x=px, y=py, z=-CL)
                 for (px, py) in pin_positions()]

    # ── Vent hole (0.8mm, lets air escape during pour) ───────────
    vent = move(cyl(0.4, body_h + 0.1), x=DISC_OD/2 - 0.5, z=-CL)

    # ── Boolean: subtract voids ──────────────────────────────────
    result = sub(base, cavity, flow_pin, vent, *pin_holes)

    # ════════════════════════════════════════════════════════════
    # ADD positive features on lid underside
    # (these protrude DOWN into the cavity → create recesses on disc top)
    # ════════════════════════════════════════════════════════════

    # Contact pad bump: Ø8mm, 0.3mm tall — creates raised contact pad on disc
    contact_bump = move(cyl(PAD_D/2, PAD_H), z=lid_h - CL)
    result = add(result, contact_bump)

    # Absorbent ring seat protrusion: annular ring 8.5–11mm, 1.0mm tall
    # Creates the groove in the disc where the cotton ring sits
    abs_ring = ring(ABS_ID/2, ABS_OD/2, ABS_DEP, z=lid_h - CL)
    result = add(result, abs_ring)

    return result

mesh_top = pad_disc_top()
clean_export(mesh_top, "pad_disc_mold_top.stl")

print("""
╔══════════════════════════════════════════════════════════════╗
║            Pad Disc Mold — Feature Summary                   ║
╠══════════════════════════════════════════════════════════════╣
║ BOTTOM MOLD (skin-contact side)                              ║
║  Cavity    │ ∅11.8 mm × 2.5 mm deep                         ║
║  Crown     │ 0.3 mm convex floor → convex skin surface       ║
║  Flow pin  │ ∅1.5 mm through-pin → centre flow hole          ║
║  Lip groove│ 0.5 mm wide × 0.3 mm deep at 0.5 mm from floor  ║
║            │ → snap-fit retention lip on disc edge           ║
║  Grip flat │ 1.5 mm break in lip groove at 0°                ║
║            │ → fingernail notch for disc removal             ║
║  Channels  │ 3× radial, 0.3 × 0.2 mm, 120° spacing          ║
║            │ → electrolyte distribution by capillary action  ║
║  Texture   │ Hex dot field ∅0.25 mm, 0.15 mm, 0.5 mm pitch  ║
║            │ → gecko adhesion on skin-contact surface        ║
╠══════════════════════════════════════════════════════════════╣
║ TOP MOLD (electrode-facing side)                             ║
║  Contact   │ ∅8 mm × 0.3 mm bump → raised contact pad        ║
║  bump      │   presses on copper spiral in electrode body    ║
║  Abs ring  │ Ring ∅8.5–11 mm, 1.0 mm tall protrusion         ║
║  protrusion│   → annular groove where cotton ring sits        ║
║  Flow pin  │ ∅1.5 mm pin (aligns with bottom, makes hole)    ║
║  Vent      │ ∅0.8 mm vent hole                               ║
║  Pins      │ 2× ∅1.5 mm alignment pins at 90°/270°           ║
╠══════════════════════════════════════════════════════════════╣
║ MOLD OUTER DIMENSIONS                                        ║
║  Bottom    │ ∅18 mm × 5 mm                                   ║
║  Top       │ ∅18 mm × 3 mm                                   ║
╚══════════════════════════════════════════════════════════════╝
""")
