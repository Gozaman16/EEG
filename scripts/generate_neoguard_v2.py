#!/usr/bin/env python3
"""
NeoGuard v2 Mold Generator — 5-modification update (neonatal, scaled)
Base: NeoGuard neonatal electrode (∅15mm × 8mm)
Mods:
  MOD 1: Modular pad system  — retention groove (∅7.5mm) + flow port pin (∅1.2mm)
  MOD 2: Impedance ref ring  — 9mm channel + exit ramp + 2nd cable notch
  MOD 3: Translucent window  — 4mm wide arc bump at reservoir height
  MOD 4: Bio-mimetic texture — denser hex dot array (∅0.2mm, 0.4mm pitch)
Also generates neonatal pad disc mold (∅7.8mm × 2mm disc).
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

# ── Mold shell ──────────────────────────────────────────────────
WALL        = 1.5
CLEARANCE   = 0.3
DRAFT_DEG   = 2.0
MOLD_OD     = 22.0
SEGS        = 96

# ── NeoGuard electrode body ─────────────────────────────────────
NG_OD       = 15.0
NG_H        = 8.0
NG_BOT_H    = 4.0
NG_TOP_H    = NG_H - NG_BOT_H + WALL   # 5.5 mm

# ── Bottom cavity ───────────────────────────────────────────────
CAV_D       = 8.0    # pad cavity diameter
CAV_H       = 0.8    # bump depth on cavity floor

# ── FR-4 seat ──────────────────────────────────────────────────
FR4_D       = 12.0
FR4_T       = 1.0
FR4_Z       = 2.5    # shelf height from cavity floor

# ── Reservoir ──────────────────────────────────────────────────
RES_ID      = 8.5
RES_OD      = 12.0
RES_H       = 1.2

# ── Spiral platform ────────────────────────────────────────────
SPIRAL_D    = 5.0
SPIRAL_H    = 0.6

# ── Cable exits ────────────────────────────────────────────────
CABLE_D     = 2.5    # radial notch depth
CABLE_W1    = 2.5    # primary exit (signal wire)
CABLE_W2    = 2.0    # secondary exit (impedance ring wire)
CABLE_SEP   = 1.2    # wall between notches

# ── Alignment pins ─────────────────────────────────────────────
PIN_D       = 2.0
PIN_H       = 3.0

# ── Vent / pour ────────────────────────────────────────────────
VENT_D      = 1.0
POUR_D      = 4.0

# ── MOD 1: Pad retention groove ────────────────────────────────
PAD_GROOVE_R    = 7.5/2    # 3.75 mm
PAD_GROOVE_W    = 0.4
PAD_GROOVE_DEP  = 0.25
PAD_NOTCH_W     = 1.2      # fingernail grip width

# ── MOD 1: Electrolyte flow port ───────────────────────────────
FLOW_D          = 1.2
FLOW_H          = 4.0      # reaches from floor through FR-4 into reservoir

# ── MOD 2: Impedance reference ring ────────────────────────────
IMP_R           = 9.0/2    # 4.5 mm
IMP_W           = 0.6
IMP_DEP         = 0.4
IMP_RAMP_W      = 0.4

# ── MOD 3: Translucent window ──────────────────────────────────
# 4mm arc width at electrode inner wall (r = NG_OD/2 = 7.5mm)
WIN_W_DEG       = math.degrees(2 * math.asin(2.0 / (NG_OD/2)))  # ≈ 30.9°
WIN_T           = 0.5

# ── MOD 4: Denser bio-mimetic dot texture ──────────────────────
DOT_R           = 0.10     # 0.2 mm dia
DOT_H           = 0.12
DOT_SPACING     = 0.40

# ═══════════════════════════════════════════════════════════════
# NEONATAL PAD DISC MOLD PARAMETERS
# ═══════════════════════════════════════════════════════════════
NEO_DISC_OD     = 7.8
NEO_DISC_T      = 2.0
NEO_LIP_W       = 0.4
NEO_LIP_H       = 0.25
NEO_LIP_Z       = 0.4
NEO_GRIP_W      = 1.2
NEO_CROWN       = 0.25
NEO_PAD_D       = 5.0
NEO_PAD_H       = 0.25
NEO_ABS_ID      = 5.5
NEO_ABS_OD      = 7.0
NEO_ABS_DEP     = 0.8
NEO_CH_W        = 0.25
NEO_CH_DEP      = 0.15
NEO_CH_N        = 3
NEO_DISC_MOLD_OD = 14.0
NEO_DISC_BOT_H  = 4.0
NEO_DISC_TOP_H  = 2.5
NEO_DISC_PIN_D  = 1.0
NEO_DISC_PIN_R  = 14.0/2 - WALL - 0.5/2 - 0.3   # ≈ 4.7 mm

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

def rot_y(mesh, deg):
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(
        math.radians(deg), [0, 1, 0]))
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
    i = cyl(r_in, h + 0.04)
    r = sub(o, move(i, z=-0.02))
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

def pin_positions_ng(n=4, offset_deg=45):
    r = MOLD_OD/2 - WALL - PIN_D/2 - 0.5
    return [(r*math.cos(math.radians(i*360/n + offset_deg)),
             r*math.sin(math.radians(i*360/n + offset_deg)))
            for i in range(n)]

def pin_positions_disc():
    return [(NEO_DISC_PIN_R * math.cos(math.radians(a)),
             NEO_DISC_PIN_R * math.sin(math.radians(a)))
            for a in [90, 270]]

# ═══════════════════════════════════════════════════════════════
# MOD 4: Hex dot texture
# ═══════════════════════════════════════════════════════════════
def hex_dot_texture(area_r, exclude_r_in=0, exclude_r_out=0,
                    dot_r=DOT_R, dot_h=DOT_H, spacing=DOT_SPACING,
                    clear_spiral_r=0, clear_groove_r=0, clear_groove_w=0,
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
            x += rng.uniform(-0.06, 0.06)
            y += rng.uniform(-0.06, 0.06)
            r = math.sqrt(x*x + y*y)
            if r > area_r - dot_r - 0.1:
                continue
            if clear_spiral_r > 0 and r < clear_spiral_r + dot_r + 0.1:
                continue
            if exclude_r_in > 0:
                if exclude_r_in - dot_r < r < exclude_r_out + dot_r:
                    continue
            if clear_groove_r > 0:
                if (clear_groove_r - clear_groove_w/2 - dot_r
                        < r <
                        clear_groove_r + clear_groove_w/2 + dot_r):
                    continue
            dots.append(move(cyl(dot_r, dot_h), x=x, y=y))
    if not dots:
        return None
    print(f"    texture: {len(dots)} dots")
    return trimesh.boolean.union(dots, engine="manifold")

# ═══════════════════════════════════════════════════════════════
# [1/4] NEOGUARD v2 BOTTOM MOLD
# ═══════════════════════════════════════════════════════════════
print("\n[1/4] NeoGuard v2 — BOTTOM MOLD")

def neoguard_v2_bottom():
    body_h  = NG_BOT_H + WALL   # 5.5 mm
    floor_z = WALL               # 1.5 mm

    # ── Outer body ──────────────────────────────────────────────
    base = cyl(MOLD_OD/2, body_h)

    # ── Main cavity ─────────────────────────────────────────────
    draft_r = math.tan(math.radians(DRAFT_DEG)) * NG_BOT_H
    cavity  = move(cyl(NG_OD/2 + draft_r, NG_BOT_H + 0.05), z=floor_z)

    # ── Skin-contact bump ────────────────────────────────────────
    bump = move(cyl(CAV_D/2, CAV_H + 0.05), z=floor_z - 0.05)

    # ── Spiral platform ──────────────────────────────────────────
    plat = move(cyl(SPIRAL_D/2, SPIRAL_H), z=floor_z - 0.05)

    # ── FR-4 seat ledge ─────────────────────────────────────────
    fr4_cut = move(cyl(FR4_D/2 + 0.2, NG_BOT_H - FR4_Z + 0.1),
                   z=floor_z + FR4_Z)

    # ── Alignment pin holes ──────────────────────────────────────
    pin_holes = [move(cyl((PIN_D + CLEARANCE)/2, PIN_H + 0.1),
                      x=px, y=py, z=body_h - PIN_H)
                 for (px, py) in pin_positions_ng()]

    # ── MOD 2: Impedance ring channel ───────────────────────────
    imp_r_in  = IMP_R - IMP_W/2   # 4.2 mm
    imp_r_out = IMP_R + IMP_W/2   # 4.8 mm
    imp_ring  = ring(imp_r_in, imp_r_out, IMP_DEP + 0.05,
                     z=floor_z - IMP_DEP)

    # MOD 2: Wire exit ramp toward cable exit (+X)
    ramp_len = MOLD_OD/2 - imp_r_out - 0.5
    ramp = trimesh.creation.box(extents=[ramp_len, IMP_RAMP_W, IMP_DEP + 0.1])
    ramp.apply_translation([imp_r_out + ramp_len/2,
                             -IMP_RAMP_W/2,
                             floor_z - IMP_DEP/2 - 0.05])

    # ── Primary cable notch (signal wire) ───────────────────────
    total_w = CABLE_W1 + CABLE_SEP + CABLE_W2
    cable1 = box(CABLE_D + 0.2, CABLE_W1,
                 NG_BOT_H - FR4_Z,
                 x=MOLD_OD/2 - CABLE_D,
                 y=-total_w/2,
                 z=floor_z + FR4_Z)

    # ── MOD 2: Secondary cable notch (impedance ring wire) ───────
    cable2 = box(CABLE_D + 0.2, CABLE_W2,
                 NG_BOT_H - FR4_Z,
                 x=MOLD_OD/2 - CABLE_D,
                 y=-total_w/2 + CABLE_W1 + CABLE_SEP,
                 z=floor_z + FR4_Z)

    # ── Boolean: subtract all ────────────────────────────────────
    result = sub(base, cavity, bump, plat, fr4_cut,
                 imp_ring, ramp, cable1, cable2, *pin_holes)

    # ════════════════════════════════════════════════════════════
    # ADD positive features
    # ════════════════════════════════════════════════════════════

    # MOD 1: Pad retention groove ring
    ret_ring = ring(PAD_GROOVE_R - PAD_GROOVE_W/2,
                    PAD_GROOVE_R + PAD_GROOVE_W/2,
                    PAD_GROOVE_DEP,
                    z=floor_z)

    # MOD 1: Fingernail grip — cut flat in groove at 180° (−X side)
    grip_cut = box(PAD_GROOVE_W + 0.1, PAD_NOTCH_W,
                   PAD_GROOVE_DEP + 0.1,
                   x=-(PAD_GROOVE_R + PAD_GROOVE_W/2 + 0.05),
                   y=-PAD_NOTCH_W/2,
                   z=floor_z - 0.05)
    ret_ring = sub(ret_ring, grip_cut)
    result = add(result, ret_ring)

    # MOD 1: Electrolyte flow port pin
    flow_pin = move(cyl(FLOW_D/2, FLOW_H), z=floor_z)
    result = add(result, flow_pin)

    # MOD 3: Translucent window bump on inner cavity wall
    # Rectangular protrusion on −X side at reservoir height
    win_z         = floor_z + FR4_Z           # 4.0 mm
    win_top       = body_h - 0.3              # 5.2 mm
    win_arc_h     = win_top - win_z           # 1.2 mm
    arc_half_chord = (NG_OD/2) * math.sin(math.radians(WIN_W_DEG/2))
    win_bump = box(WIN_T, arc_half_chord * 2, win_arc_h,
                   x=-(NG_OD/2),
                   y=-arc_half_chord,
                   z=win_z)
    result = add(result, win_bump)

    # MOD 4: Bio-mimetic hex dot texture (denser, smaller dots)
    print("  Building hex dot texture field...")
    dots = hex_dot_texture(
        area_r        = CAV_D/2 - 0.1,
        exclude_r_in  = imp_r_in,
        exclude_r_out = imp_r_out,
        clear_spiral_r = SPIRAL_D/2,
        clear_groove_r = PAD_GROOVE_R,
        clear_groove_w = PAD_GROOVE_W,
    )
    if dots is not None:
        result = add(result, move(dots, z=floor_z - 0.10))

    return result

mesh = neoguard_v2_bottom()
clean_export(mesh, "neoguard_v2_mold_bottom.stl")

# ═══════════════════════════════════════════════════════════════
# [2/4] NEOGUARD v2 TOP MOLD
# ═══════════════════════════════════════════════════════════════
print("\n[2/4] NeoGuard v2 — TOP MOLD")

def neoguard_v2_top():
    body      = cyl(MOLD_OD/2, NG_TOP_H)
    top_cav_h = NG_H - NG_BOT_H   # 4.0 mm

    cavity    = move(cyl(NG_OD/2, top_cav_h + 0.1), z=WALL)
    res_inner = move(cyl(RES_ID/2 - CLEARANCE/2, RES_H + 0.1), z=WALL - 0.05)
    pour      = move(cyl(POUR_D/2, POUR_D + 0.1), z=NG_TOP_H - POUR_D)

    # Vent holes
    vents = []
    for a in [90, 270]:
        vx = (MOLD_OD/2 - WALL - 1.5) * math.cos(math.radians(a))
        vy = (MOLD_OD/2 - WALL - 1.5) * math.sin(math.radians(a))
        vents.append(move(cyl(VENT_D/2, WALL + 4), x=vx, y=vy, z=NG_TOP_H - 3))

    # Fill port centred, aligned with flow pin
    fill_port = move(cyl(FLOW_D/2, WALL + top_cav_h + 0.1), z=WALL - 0.05)

    # Cable notches (primary + secondary, matching bottom mold)
    total_w = CABLE_W1 + CABLE_SEP + CABLE_W2
    cable1 = box(CABLE_D + 0.2, CABLE_W1,
                 NG_TOP_H - WALL,
                 x=MOLD_OD/2 - CABLE_D,
                 y=-total_w/2,
                 z=WALL)
    cable2 = box(CABLE_D + 0.2, CABLE_W2,
                 NG_TOP_H - WALL,
                 x=MOLD_OD/2 - CABLE_D,
                 y=-total_w/2 + CABLE_W1 + CABLE_SEP,
                 z=WALL)

    pin_holes = [move(cyl((PIN_D + CLEARANCE)/2, PIN_H + 0.1),
                      x=px, y=py, z=-0.05)
                 for (px, py) in pin_positions_ng()]

    base = sub(body, cavity, res_inner, pour, fill_port,
               cable1, cable2, *vents, *pin_holes)

    # Alignment pins (male)
    pins = [move(cyl(PIN_D/2, PIN_H + WALL), x=px, y=py)
            for (px, py) in pin_positions_ng()]

    return add(base, *pins)

mesh = neoguard_v2_top()
clean_export(mesh, "neoguard_v2_mold_top.stl")

# ═══════════════════════════════════════════════════════════════
# [3/4] NEONATAL PAD DISC — BOTTOM MOLD
# ═══════════════════════════════════════════════════════════════
print("\n[3/4] Neonatal pad disc — BOTTOM MOLD")

def neo_pad_disc_bottom():
    body_h  = NEO_DISC_BOT_H
    floor_z = WALL

    base = cyl(NEO_DISC_MOLD_OD/2, body_h)

    # Main disc cavity
    cavity = move(cyl(NEO_DISC_OD/2 + 0.05, NEO_DISC_T + 0.05), z=floor_z - 0.05)

    # Convex floor (sphere-cap approximation)
    r_sphere = (NEO_DISC_OD/2)**2 / (2 * NEO_CROWN) + NEO_CROWN/2
    sphere = trimesh.creation.icosphere(subdivisions=4, radius=r_sphere)
    sphere_z = floor_z + NEO_CROWN - r_sphere
    sphere.apply_translation([0, 0, sphere_z])
    clip = move(cyl(NEO_DISC_OD/2 + 0.5, NEO_CROWN + 1.0), z=floor_z - 0.5)
    crown_cut = trimesh.boolean.intersection([sphere, clip], engine="manifold")

    # Centre flow hole through-pin
    flow_pin = move(cyl(FLOW_D/2, NEO_DISC_T + 0.1), z=floor_z - 0.05)

    # 3× radial electrolyte channels
    ch_cuts = []
    for i in range(NEO_CH_N):
        ch = box(NEO_DISC_OD/2 + 0.1, NEO_CH_W, NEO_CH_DEP + 0.05,
                 x=0, y=-NEO_CH_W/2, z=floor_z - NEO_CH_DEP - 0.05)
        ch_cuts.append(rot_z(ch, i * 120))

    # Retention lip groove in cavity wall
    lip_ring = ring(NEO_DISC_OD/2 + 0.05,
                    NEO_DISC_OD/2 + 0.05 + NEO_LIP_H + 0.05,
                    NEO_LIP_W + 0.05,
                    z=floor_z + NEO_LIP_Z - NEO_LIP_W/2)

    # Fingernail grip flat at +X (0°)
    grip_slot = box(NEO_LIP_H + 0.2, NEO_GRIP_W,
                    NEO_LIP_W + 0.1,
                    x=NEO_DISC_OD/2 - 0.05,
                    y=-NEO_GRIP_W/2,
                    z=floor_z + NEO_LIP_Z - NEO_LIP_W/2 - 0.05)

    # Alignment pin holes
    pin_holes = [move(cyl((NEO_DISC_PIN_D + 0.1)/2, NEO_DISC_PIN_D + 0.1),
                      x=px, y=py, z=body_h - NEO_DISC_PIN_D - 0.05)
                 for (px, py) in pin_positions_disc()]

    result = sub(base, cavity, crown_cut, flow_pin,
                 lip_ring, grip_slot, *ch_cuts, *pin_holes)

    # Hex dot texture on cavity floor (skin-contact surface)
    print("  Building hex dot texture...")
    dots = hex_dot_texture(
        area_r        = NEO_DISC_OD/2 - 0.15,
        exclude_r_in  = 0,
        exclude_r_out = 0,
        dot_r         = DOT_R,
        dot_h         = DOT_H,
        spacing       = DOT_SPACING,
        clear_spiral_r = FLOW_D/2 + 0.2,
    )
    if dots is not None:
        result = add(result, move(dots, z=floor_z - 0.10))

    return result

mesh = neo_pad_disc_bottom()
clean_export(mesh, "neoguard_pad_disc_mold_bottom.stl")

# ═══════════════════════════════════════════════════════════════
# [4/4] NEONATAL PAD DISC — TOP MOLD
# ═══════════════════════════════════════════════════════════════
print("\n[4/4] Neonatal pad disc — TOP MOLD")

def neo_pad_disc_top():
    body_h = NEO_DISC_TOP_H
    lid_h  = WALL

    base = cyl(NEO_DISC_MOLD_OD/2, body_h)

    # Disc cavity
    cavity = move(cyl(NEO_DISC_OD/2 + 0.05, NEO_DISC_T + 0.05), z=lid_h - 0.05)

    # Centre flow hole
    flow_pin = move(cyl(FLOW_D/2, body_h + 0.1), z=-0.05)

    # Alignment pin holes (female)
    pin_holes = [move(cyl((NEO_DISC_PIN_D + 0.1)/2, NEO_DISC_PIN_D + 0.2),
                      x=px, y=py, z=-0.05)
                 for (px, py) in pin_positions_disc()]

    # Vent hole
    vent = move(cyl(0.4, body_h + 0.1), x=NEO_DISC_OD/2 - 0.4, z=-0.05)

    result = sub(base, cavity, flow_pin, vent, *pin_holes)

    # Contact pad bump (∅5mm × 0.25mm) — protrudes into cavity
    contact_bump = move(cyl(NEO_PAD_D/2, NEO_PAD_H), z=lid_h - 0.05)
    result = add(result, contact_bump)

    # Absorbent ring seat protrusion (∅5.5–7mm, 0.8mm tall)
    abs_ring = ring(NEO_ABS_ID/2, NEO_ABS_OD/2, NEO_ABS_DEP, z=lid_h - 0.05)
    result = add(result, abs_ring)

    return result

mesh = neo_pad_disc_top()
clean_export(mesh, "neoguard_pad_disc_mold_top.stl")

print("""
╔══════════════════════════════════════════════════════════════╗
║      NeoGuard v2 — Scaled Modification Summary               ║
╠══════════════════════════════════════════════════════════════╣
║ NEOGUARD v2 BOTTOM MOLD  (∅22 mm × 5.5 mm)                  ║
║                                                               ║
║ MOD 1a │ Pad retention groove ring                           ║
║        │ ∅7.5 mm, 0.4 mm wide × 0.25 mm tall                 ║
║ MOD 1b │ Fingernail grip flat  1.2 mm at 180°               ║
║ MOD 1c │ Flow port pin  ∅1.2 mm × 4.0 mm                    ║
║ MOD 2a │ Impedance ring channel  ∅9.0 mm, 0.6×0.4 mm        ║
║ MOD 2b │ Wire exit ramp  0.4 mm                              ║
║ MOD 2c │ 2nd cable notch  2.0 mm (+ 1.2 mm wall)            ║
║ MOD 3  │ Window bump  4 mm arc (~30.9°), 0.5 mm thick        ║
║ MOD 4  │ Hex dot texture  ∅0.2 mm, 0.12 mm, 0.4 mm pitch    ║
╠══════════════════════════════════════════════════════════════╣
║ NEOGUARD v2 TOP MOLD  (∅22 mm × 5.5 mm)                     ║
║  Fill port ∅1.2 mm centred | 2nd cable notch 2.0 mm         ║
╠══════════════════════════════════════════════════════════════╣
║ NEONATAL PAD DISC BOTTOM MOLD  (∅14 mm × 4.0 mm)            ║
║  Disc ∅7.8 mm × 2.0 mm | Crown 0.25 mm | Flow pin ∅1.2 mm  ║
║  Lip groove 0.4×0.25 mm | Grip flat 1.2 mm                  ║
║  3× radial channels 0.25×0.15 mm | Hex dot texture          ║
╠══════════════════════════════════════════════════════════════╣
║ NEONATAL PAD DISC TOP MOLD  (∅14 mm × 2.5 mm)               ║
║  Contact bump ∅5 mm × 0.25 mm                               ║
║  Abs ring seat ∅5.5–7.0 mm × 0.8 mm                         ║
╚══════════════════════════════════════════════════════════════╝
""")
