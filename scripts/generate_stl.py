#!/usr/bin/env python3
"""
EpiScreen EEG Electrode Mold — STL Generator
Generates all mold and mounting STL files using trimesh primitives.
Mirrors the parametric design from the .scad files.
"""

import math
import numpy as np
import trimesh
import manifold3d as m3d
import trimesh.creation as tc
import os, sys

# ── output dir ────────────────────────────────────────────────
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stl")
os.makedirs(OUT, exist_ok=True)

# ── helpers ───────────────────────────────────────────────────
SEGS = 128   # cylinder facets

def cyl(r, h, center=False):
    m = tc.cylinder(radius=r, height=h, sections=SEGS)
    if not center:
        m.apply_translation([0, 0, h/2])
    return m

def annulus(r_in, r_out, h, center=False):
    outer = cyl(r_out, h, center)
    inner = cyl(r_in, h + 0.02, center)
    return trimesh.boolean.difference([outer, inner], engine="blender")

def move(mesh, x=0, y=0, z=0):
    m = mesh.copy()
    m.apply_translation([x, y, z])
    return m

def rot_z(mesh, deg):
    m = mesh.copy()
    angle = math.radians(deg)
    T = trimesh.transformations.rotation_matrix(angle, [0, 0, 1])
    m.apply_transform(T)
    return m

def rot_y(mesh, deg):
    m = mesh.copy()
    angle = math.radians(deg)
    T = trimesh.transformations.rotation_matrix(angle, [0, 1, 0])
    m.apply_transform(T)
    return m

def box(w, d, h, x=0, y=0, z=0):
    m = trimesh.creation.box(extents=[w, d, h])
    m.apply_translation([x + w/2, y + d/2, z + h/2])
    return m

def union(*meshes):
    valid = [m for m in meshes if m is not None and len(m.faces) > 0]
    if len(valid) == 0:
        return trimesh.Trimesh()
    if len(valid) == 1:
        return valid[0]
    return trimesh.boolean.union(valid, engine="manifold")

def subtract(base, *cutters):
    valid = [m for m in cutters if m is not None and len(m.faces) > 0]
    if not valid:
        return base
    return trimesh.boolean.difference([base] + valid, engine="manifold")

def clean(mesh):
    """
    Guarantee a single-shell, watertight, correctly-wound manifold.
    Strategy:
      1. Split into connected components; keep the largest by volume.
      2. Fix winding so all normals point outward.
      3. Run a self-union through manifold (identity boolean) to merge
         any co-planar duplicate faces and close T-junctions.
    """
    import manifold3d as m3d

    # Step 1 — largest component
    try:
        parts = mesh.split(only_watertight=False)
        if len(parts) > 1:
            mesh = max(parts, key=lambda m: abs(m.volume) if m.is_watertight else len(m.faces))
    except Exception:
        pass

    # Step 2 — fix normals
    trimesh.repair.fix_winding(mesh)
    trimesh.repair.fix_normals(mesh)

    # Step 3 — import into manifold (validates + merges duplicate verts, closes T-junctions)
    try:
        mesh_in = m3d.Mesh(vert_properties=mesh.vertices.astype('float32'),
                           tri_verts=mesh.faces.astype('uint32'))
        mf = m3d.Manifold(mesh_in)
        out = mf.to_mesh()
        mesh = trimesh.Trimesh(vertices=np.array(out.vert_properties),
                               faces=np.array(out.tri_verts), process=False)
        trimesh.repair.fix_normals(mesh)
    except Exception:
        pass   # fallback: use as-is

    return mesh

def save(mesh, name):
    mesh = clean(mesh)
    path = os.path.join(OUT, name)
    mesh.export(path)
    wt = "✓ watertight" if mesh.is_watertight else "✗ NOT watertight"
    print(f"  Saved: {path}  faces={len(mesh.faces)}  {wt}")

# ── Parameters ────────────────────────────────────────────────
WALL      = 1.5
CLEARANCE = 0.3
DRAFT     = 2.0        # degrees
PIN_D     = 2.0
PIN_H     = 3.0
PIN_R     = 4

# EpiScreen
EP_OD         = 24.0
EP_H          = 10.0
EP_MOLD_OD    = 32.0
EP_BOT_H      = 5.0
EP_TOP_H      = EP_H - EP_BOT_H + WALL   # 6.5
EP_BOT_CAV_D  = 12.0
EP_BOT_CAV_H  = 1.0
EP_FR4_D      = 19.0
EP_FR4_T      = 1.6
EP_FR4_Z      = 3.0
EP_FR4_LIP    = 0.2
EP_RES_ID     = 13.0
EP_RES_OD     = 19.0
EP_RES_H      = 1.5
EP_SPIRAL_D   = 8.0
EP_SPIRAL_H   = 0.8
EP_CABLE_W    = 3.0
EP_CABLE_D    = 3.0
EP_POUR_D     = 6.0
EP_MCH_D      = 0.6
EP_MCH_N      = 3
EP_MCH_ANG    = 37.5
VENT_D        = 1.0

# NeoGuard
NG_OD         = 15.0
NG_H          = 8.0
NG_MOLD_OD    = 22.0
NG_BOT_H      = 4.0
NG_TOP_H      = NG_H - NG_BOT_H + WALL
NG_FR4_D      = 12.0
NG_FR4_T      = 1.0
NG_FR4_Z      = 2.5
NG_BOT_CAV_D  = 8.0
NG_BOT_CAV_H  = 0.8
NG_RES_ID     = 8.5
NG_RES_OD     = 12.0
NG_RES_H      = 1.2
NG_SPIRAL_D   = 5.0
NG_SPIRAL_H   = 0.6
NG_POUR_D     = 4.0
NG_CABLE_W    = 2.5
NG_CABLE_D    = 2.5

# HairSite
HS_OD         = 24.0
HS_H          = 12.0
HS_MOLD_OD    = 32.0
HS_BOT_H      = 6.0
HS_TOP_H      = HS_H - HS_BOT_H + WALL
HS_PIN_D      = 1.2
HS_PIN_H      = 8.0
HS_PIN_RAD    = 6.0
HS_POUR_D     = 6.0

# ImpactGuard
IG_OD         = 38.0
IG_H          = 12.0
IG_ELEC_D     = 24.5
IG_ELEC_H     = 8.0
IG_MOUNT_W    = 50.0
IG_MOUNT_H    = 8.0
IG_SNAP_R     = 0.8

# Headband adult
HBA_CLIP_W    = 30.0
HBA_CLIP_H    = 12.0
HBA_ELEC_D    = 24.5
HBA_ELEC_H    = 6.0
HBA_BAND_W    = 22.0
HBA_BAND_T    = 2.5
HBA_SNAP_R    = 0.8

# Headband neonatal
HBN_CLIP_W    = 22.0
HBN_CLIP_H    = 9.0
HBN_ELEC_D    = 15.5
HBN_ELEC_H    = 5.0
HBN_BAND_W    = 16.0
HBN_BAND_T    = 2.0
HBN_SNAP_R    = 0.6

# ══════════════════════════════════════════════════════════════
# Helper: build alignment pin column positions
# ══════════════════════════════════════════════════════════════

def pin_positions(mold_od, n=4, offset_angle=45):
    r = mold_od/2 - WALL - PIN_D/2 - 0.5
    positions = []
    for i in range(n):
        ang = math.radians(i * 360/n + offset_angle)
        positions.append((r * math.cos(ang), r * math.sin(ang)))
    return positions

# ══════════════════════════════════════════════════════════════
# 1. EpiScreen bottom mold
# ══════════════════════════════════════════════════════════════
print("\n[1/8] EpiScreen bottom mold...")

def episcreen_bottom():
    body_h = EP_BOT_H + WALL
    base   = cyl(EP_MOLD_OD/2, body_h)

    # Main cavity (with simplified draft — cylinder close enough for mold)
    draft_r = math.tan(math.radians(DRAFT)) * EP_BOT_H
    cavity = move(cyl((EP_OD/2 + draft_r), EP_BOT_H + 0.05), z=WALL)

    # Bottom skin-contact bump (raised in mold = recess in electrode)
    bump  = move(cyl(EP_BOT_CAV_D/2, EP_BOT_CAV_H + 0.05), z=WALL - 0.05)

    # Spiral exposure platform
    plat  = move(cyl(EP_SPIRAL_D/2, EP_SPIRAL_H), z=WALL - 0.05)

    # FR-4 seat (ledge at EP_FR4_Z — cut wider above ledge)
    fr4_cut = move(cyl((EP_FR4_D/2 + EP_FR4_LIP), EP_BOT_H - EP_FR4_Z + 0.1),
                   z=WALL + EP_FR4_Z)

    # Microchannel holes (3×, angled)
    mch_cuts = []
    start_r = EP_RES_OD/2
    start_z = WALL + EP_FR4_Z + EP_FR4_T + EP_RES_H/2
    for i in range(EP_MCH_N):
        wire = cyl(EP_MCH_D/2, 20)
        wire = rot_y(wire, EP_MCH_ANG)
        wire = move(wire, x=start_r, z=start_z - 5)
        wire = rot_z(wire, i * 120 + 30)
        mch_cuts.append(wire)

    # Alignment pin holes (4×)
    pin_holes = []
    for (px, py) in pin_positions(EP_MOLD_OD):
        h = cyl((PIN_D + CLEARANCE)/2, PIN_H + 0.1)
        h = move(h, x=px, y=py, z=body_h - PIN_H)
        pin_holes.append(h)

    # Cable exit notch
    cable = box(EP_CABLE_D + 0.2, EP_CABLE_W, EP_BOT_H - EP_FR4_Z,
                x=EP_MOLD_OD/2 - EP_CABLE_D, y=-EP_CABLE_W/2, z=WALL + EP_FR4_Z)

    mesh = subtract(base, cavity, bump, plat, fr4_cut,
                    *mch_cuts, *pin_holes, cable)
    return mesh

save(episcreen_bottom(), "episcreen_mold_bottom.stl")

# ══════════════════════════════════════════════════════════════
# 2. EpiScreen top mold
# ══════════════════════════════════════════════════════════════
print("\n[2/8] EpiScreen top mold...")

def episcreen_top():
    body   = cyl(EP_MOLD_OD/2, EP_TOP_H)

    # Top-half cavity
    top_cav_h = EP_H - EP_BOT_H
    cavity = move(cyl(EP_OD/2, top_cav_h + 0.1), z=WALL)

    # Inner hole of reservoir ring (ring stays as solid protrusion on mold)
    res_inner = move(cyl(EP_RES_ID/2 - CLEARANCE/2, EP_RES_H + 0.1), z=WALL - 0.05)

    # Pour hole (top centre)
    pour = move(cyl(EP_POUR_D/2, EP_POUR_D + 0.1), z=EP_TOP_H - EP_POUR_D)

    # Vent holes (2×)
    vent_cuts = []
    for a in [90, 270]:
        v = cyl(VENT_D/2, WALL + 5)
        vx = (EP_MOLD_OD/2 - WALL - 2) * math.cos(math.radians(a))
        vy = (EP_MOLD_OD/2 - WALL - 2) * math.sin(math.radians(a))
        v = move(v, x=vx, y=vy, z=EP_TOP_H - 4)
        vent_cuts.append(v)

    # Reservoir fill port
    fill = move(cyl(1.0, WALL + 6.1), x=EP_RES_OD/2 - 2, z=EP_TOP_H - 6)

    # Cable exit
    cable = box(EP_CABLE_D + 0.2, EP_CABLE_W + 1,
                EP_TOP_H - WALL,
                x=EP_MOLD_OD/2 - EP_CABLE_D,
                y=-(EP_CABLE_W + 1)/2, z=WALL)

    base = subtract(body, cavity, res_inner, pour, fill, cable, *vent_cuts)

    # Alignment pins (4×, male — ADD to body before subtract)
    pins = []
    for (px, py) in pin_positions(EP_MOLD_OD):
        p = cyl(PIN_D/2, PIN_H + WALL)
        p = move(p, x=px, y=py, z=0)
        pins.append(p)

    mesh = union(base, *pins)
    return mesh

save(episcreen_top(), "episcreen_mold_top.stl")

# ══════════════════════════════════════════════════════════════
# 3. NeoGuard bottom mold
# ══════════════════════════════════════════════════════════════
print("\n[3/8] NeoGuard bottom mold...")

def neoguard_bottom():
    body_h = NG_BOT_H + WALL
    base   = cyl(NG_MOLD_OD/2, body_h)

    draft_r = math.tan(math.radians(DRAFT)) * NG_BOT_H
    cavity  = move(cyl((NG_OD/2 + draft_r), NG_BOT_H + 0.05), z=WALL)
    bump    = move(cyl(NG_BOT_CAV_D/2, NG_BOT_CAV_H + 0.05), z=WALL - 0.05)
    plat    = move(cyl(NG_SPIRAL_D/2, NG_SPIRAL_H), z=WALL - 0.05)
    fr4_cut = move(cyl(NG_FR4_D/2 + 0.2, NG_BOT_H - NG_FR4_Z + 0.1),
                   z=WALL + NG_FR4_Z)

    pin_holes = []
    for (px, py) in pin_positions(NG_MOLD_OD):
        h = cyl((PIN_D + CLEARANCE)/2, PIN_H + 0.1)
        h = move(h, x=px, y=py, z=body_h - PIN_H)
        pin_holes.append(h)

    cable = box(NG_CABLE_D + 0.2, NG_CABLE_W,
                NG_BOT_H - NG_FR4_Z,
                x=NG_MOLD_OD/2 - NG_CABLE_D, y=-NG_CABLE_W/2,
                z=WALL + NG_FR4_Z)

    return subtract(base, cavity, bump, plat, fr4_cut, cable, *pin_holes)

save(neoguard_bottom(), "neoguard_mold_bottom.stl")

# ══════════════════════════════════════════════════════════════
# 4. NeoGuard top mold
# ══════════════════════════════════════════════════════════════
print("\n[4/8] NeoGuard top mold...")

def neoguard_top():
    body     = cyl(NG_MOLD_OD/2, NG_TOP_H)
    top_cav_h = NG_H - NG_BOT_H
    cavity   = move(cyl(NG_OD/2, top_cav_h + 0.1), z=WALL)
    res_inner = move(cyl(NG_RES_ID/2 - CLEARANCE/2, NG_RES_H + 0.1), z=WALL - 0.05)
    pour     = move(cyl(NG_POUR_D/2, NG_POUR_D + 0.1), z=NG_TOP_H - NG_POUR_D)
    fill     = move(cyl(1.0, WALL + 5), x=NG_RES_OD/2 - 1.5, z=NG_TOP_H - 5)
    cable    = box(NG_CABLE_D + 0.2, NG_CABLE_W + 1, NG_TOP_H - WALL,
                   x=NG_MOLD_OD/2 - NG_CABLE_D, y=-(NG_CABLE_W+1)/2, z=WALL)

    vent_cuts = []
    for a in [90, 270]:
        v = cyl(VENT_D/2, WALL + 4)
        vx = (NG_MOLD_OD/2 - WALL - 1.5) * math.cos(math.radians(a))
        vy = (NG_MOLD_OD/2 - WALL - 1.5) * math.sin(math.radians(a))
        v = move(v, x=vx, y=vy, z=NG_TOP_H - 3)
        vent_cuts.append(v)

    base = subtract(body, cavity, res_inner, pour, fill, cable, *vent_cuts)

    pins = []
    for (px, py) in pin_positions(NG_MOLD_OD):
        p = cyl(PIN_D/2, PIN_H + WALL)
        p = move(p, x=px, y=py, z=0)
        pins.append(p)

    return union(base, *pins)

save(neoguard_top(), "neoguard_mold_top.stl")

# ══════════════════════════════════════════════════════════════
# 5. HairSite bottom mold
# ══════════════════════════════════════════════════════════════
print("\n[5/8] HairSite bottom mold...")

def hairsite_bottom():
    body_h = HS_BOT_H + WALL
    base   = cyl(HS_MOLD_OD/2, body_h)

    draft_r = math.tan(math.radians(DRAFT)) * HS_BOT_H
    cavity  = move(cyl((HS_OD/2 + draft_r), HS_BOT_H + 0.05), z=WALL)
    bump    = move(cyl(EP_BOT_CAV_D/2, EP_BOT_CAV_H + 0.05), z=WALL - 0.05)
    fr4_cut = move(cyl(EP_FR4_D/2 + EP_FR4_LIP, HS_BOT_H - EP_FR4_Z + 0.1),
                   z=WALL + EP_FR4_Z)

    pin_holes = []
    for (px, py) in pin_positions(HS_MOLD_OD):
        h = cyl((PIN_D + CLEARANCE)/2, PIN_H + 0.1)
        h = move(h, x=px, y=py, z=body_h - PIN_H)
        pin_holes.append(h)

    cable = box(EP_CABLE_D + 0.2, EP_CABLE_W, HS_BOT_H - EP_FR4_Z,
                x=HS_MOLD_OD/2 - EP_CABLE_D, y=-EP_CABLE_W/2,
                z=WALL + EP_FR4_Z)

    cut_mesh = subtract(base, cavity, bump, fr4_cut, cable, *pin_holes)

    # Add 7 pin cores (solid posts — stay in mold body)
    pin_posts = []
    # centre
    pin_posts.append(move(cyl(HS_PIN_D/2, HS_PIN_H), z=WALL))
    for i in range(6):
        ang = math.radians(i * 60)
        px  = HS_PIN_RAD * math.cos(ang)
        py  = HS_PIN_RAD * math.sin(ang)
        pin_posts.append(move(cyl(HS_PIN_D/2, HS_PIN_H), x=px, y=py, z=WALL))

    return union(cut_mesh, *pin_posts)

save(hairsite_bottom(), "hairsite_mold_bottom.stl")

# ══════════════════════════════════════════════════════════════
# 6. HairSite top mold
# ══════════════════════════════════════════════════════════════
print("\n[6/8] HairSite top mold...")

def hairsite_top():
    body      = cyl(HS_MOLD_OD/2, HS_TOP_H)
    top_cav_h = HS_H - HS_BOT_H
    cavity    = move(cyl(HS_OD/2, top_cav_h + 0.1), z=WALL)
    res_inner = move(cyl(EP_RES_ID/2 - CLEARANCE/2, EP_RES_H + 0.1), z=WALL - 0.05)
    pour      = move(cyl(HS_POUR_D/2, HS_POUR_D + 0.1), z=HS_TOP_H - HS_POUR_D)
    fill      = move(cyl(1.0, WALL + 6.1), x=EP_RES_OD/2 - 2, z=HS_TOP_H - 6)
    cable     = box(EP_CABLE_D + 0.2, EP_CABLE_W + 1, HS_TOP_H - WALL,
                    x=HS_MOLD_OD/2 - EP_CABLE_D, y=-(EP_CABLE_W+1)/2, z=WALL)

    vent_cuts = []
    for a in [90, 270]:
        v = cyl(VENT_D/2, WALL + 5)
        vx = (HS_MOLD_OD/2 - WALL - 2) * math.cos(math.radians(a))
        vy = (HS_MOLD_OD/2 - WALL - 2) * math.sin(math.radians(a))
        v = move(v, x=vx, y=vy, z=HS_TOP_H - 4)
        vent_cuts.append(v)

    # Through-holes for pin tips
    pin_tip_cuts = [move(cyl(HS_PIN_D/2 + 0.1, top_cav_h + 0.1), z=WALL)]
    for i in range(6):
        ang = math.radians(i * 60)
        px  = HS_PIN_RAD * math.cos(ang)
        py  = HS_PIN_RAD * math.sin(ang)
        pin_tip_cuts.append(move(cyl(HS_PIN_D/2 + 0.1, top_cav_h + 0.1),
                                  x=px, y=py, z=WALL))

    base = subtract(body, cavity, res_inner, pour, fill, cable,
                    *vent_cuts, *pin_tip_cuts)

    pins = []
    for (px, py) in pin_positions(HS_MOLD_OD):
        p = cyl(PIN_D/2, PIN_H + WALL)
        p = move(p, x=px, y=py, z=0)
        pins.append(p)

    return union(base, *pins)

save(hairsite_top(), "hairsite_mold_top.stl")

# ══════════════════════════════════════════════════════════════
# 7. ImpactGuard helmet adapter
# ══════════════════════════════════════════════════════════════
print("\n[7/8] ImpactGuard helmet adapter...")

def impactguard():
    body  = cyl(IG_OD/2, IG_H)
    flange = box(IG_MOUNT_W, IG_MOUNT_W, IG_MOUNT_H,
                 x=-IG_MOUNT_W/2, y=-IG_MOUNT_W/2, z=0)
    solid = union(body, flange)

    # Electrode socket
    sock  = move(cyl(IG_ELEC_D/2, IG_ELEC_H + 0.1), z=IG_H - IG_ELEC_H)
    # Snap ring groove approximated as thin annular cylinder
    snap_r_big = IG_ELEC_D/2 + IG_SNAP_R
    snap_r_sml = IG_ELEC_D/2 - IG_SNAP_R
    snap = move(
        trimesh.creation.annulus(r_min=snap_r_sml, r_max=snap_r_big,
                                  height=IG_SNAP_R * 2, sections=SEGS),
        z=IG_H - IG_ELEC_H/2 - IG_SNAP_R
    ) if hasattr(trimesh.creation, 'annulus') else cyl(0.1, 0.1)  # fallback

    # Lead-in chamfer
    chamfer = trimesh.creation.cone(radius=IG_ELEC_D/2 + 1,
                                     height=1.6, sections=SEGS)
    chamfer.apply_translation([0, 0, IG_H - 1.5])

    # M3 bolt holes
    corner_r = IG_MOUNT_W/2 - 4
    bolt_holes = []
    for a in [45, 135, 225, 315]:
        bx = corner_r * math.cos(math.radians(a))
        by = corner_r * math.sin(math.radians(a))
        bolt_holes.append(move(cyl(1.7, IG_MOUNT_H + 0.2), x=bx, y=by, z=-0.1))

    # Cable exit slot
    cable = box(EP_CABLE_D + 2, EP_CABLE_W, IG_H + 0.1,
                x=IG_OD/2 - EP_CABLE_D, y=-EP_CABLE_W/2, z=0)

    return subtract(solid, sock, chamfer, cable, *bolt_holes)

save(impactguard(), "impactguard_helmet_adapter.stl")

# ══════════════════════════════════════════════════════════════
# 8a. Headband mount — adult
# ══════════════════════════════════════════════════════════════
print("\n[8a/8] Headband mount adult...")

def headband_adult():
    clip = box(HBA_CLIP_W, HBA_CLIP_W, HBA_CLIP_H,
               x=-HBA_CLIP_W/2, y=-HBA_CLIP_W/2, z=0)
    # Velcro ears
    ear_l = box(10, HBA_BAND_W, 3, x=-HBA_CLIP_W/2 - 10, y=-HBA_BAND_W/2, z=1)
    ear_r = box(10, HBA_BAND_W, 3, x= HBA_CLIP_W/2,       y=-HBA_BAND_W/2, z=1)
    solid = union(clip, ear_l, ear_r)

    # Electrode socket
    sock = move(cyl(HBA_ELEC_D/2, HBA_ELEC_H + 0.1),
                z=HBA_CLIP_H - HBA_ELEC_H)
    # Lead-in chamfer
    chamfer = trimesh.creation.cone(radius=HBA_ELEC_D/2 + 1,
                                     height=1.5, sections=SEGS)
    chamfer.apply_translation([0, 0, HBA_CLIP_H - 1.5])
    # Band slot
    band = box(HBA_CLIP_W + 0.2, HBA_BAND_W, HBA_BAND_T + 0.5,
               x=-HBA_CLIP_W/2 - 0.1, y=-HBA_BAND_W/2,
               z=HBA_CLIP_H - HBA_ELEC_H - HBA_BAND_T - 1)
    # Cable exit
    cable = box(EP_CABLE_D + 1, EP_CABLE_W, HBA_ELEC_H + 0.1,
                x=HBA_ELEC_D/2 - 2, y=-EP_CABLE_W/2,
                z=HBA_CLIP_H - HBA_ELEC_H)

    return subtract(solid, sock, chamfer, band, cable)

save(headband_adult(), "headband_mount_adult.stl")

# ══════════════════════════════════════════════════════════════
# 8b. Headband mount — neonatal
# ══════════════════════════════════════════════════════════════
print("\n[8b/8] Headband mount neonatal...")

def headband_neonatal():
    clip = box(HBN_CLIP_W, HBN_CLIP_W, HBN_CLIP_H,
               x=-HBN_CLIP_W/2, y=-HBN_CLIP_W/2, z=0)
    ear_l = box(7, HBN_BAND_W, 2.5, x=-HBN_CLIP_W/2 - 7, y=-HBN_BAND_W/2, z=0.5)
    ear_r = box(7, HBN_BAND_W, 2.5, x= HBN_CLIP_W/2,      y=-HBN_BAND_W/2, z=0.5)
    solid = union(clip, ear_l, ear_r)

    sock = move(cyl(HBN_ELEC_D/2, HBN_ELEC_H + 0.1),
                z=HBN_CLIP_H - HBN_ELEC_H)
    chamfer = trimesh.creation.cone(radius=HBN_ELEC_D/2 + 0.75,
                                     height=1.2, sections=SEGS)
    chamfer.apply_translation([0, 0, HBN_CLIP_H - 1.2])
    band = box(HBN_CLIP_W + 0.2, HBN_BAND_W, HBN_BAND_T + 0.5,
               x=-HBN_CLIP_W/2 - 0.1, y=-HBN_BAND_W/2,
               z=HBN_CLIP_H - HBN_ELEC_H - HBN_BAND_T - 0.5)
    cable = box(EP_CABLE_D + 0.5, EP_CABLE_W, HBN_ELEC_H + 0.1,
                x=HBN_ELEC_D/2 - 1.5, y=-EP_CABLE_W/2,
                z=HBN_CLIP_H - HBN_ELEC_H)

    return subtract(solid, sock, chamfer, band, cable)

save(headband_neonatal(), "headband_mount_neonatal.stl")

print("\n✓  All STL files generated in:", OUT)

# ══════════════════════════════════════════════════════════════
# V2 MODIFICATIONS — EpiScreen Modular Pad + Impedance Ring
# ══════════════════════════════════════════════════════════════
#
# New features vs v1:
#   Bottom mold:
#     – Retention groove ring   (11.5 mm dia, 0.5 mm wide, 0.3 mm deep protrusion)
#     – Impedance ref ring slot (14.0 mm dia, 0.8 mm wide, 0.5 mm deep groove)
#     – Second cable exit       (2 mm wide, offset from primary)
#     – Micro-dot texture       (replaces concentric rings)
#   Top mold: unchanged from v1
#   New: pad disc mold          (open-face, 12 mm dia × 2 mm disc)
# ══════════════════════════════════════════════════════════════

# ── helper: watertight ring mesh via manifold ─────────────────
def ring_mesh(r_inner, r_outer, h, x=0, y=0, z=0):
    """Annular cylinder (ring) guaranteed watertight via manifold subtraction."""
    outer = cyl(r_outer, h)
    inner = cyl(r_inner, h + 0.04)   # slight oversize so faces don't coincide
    ring  = subtract(outer, inner)
    return move(ring, x=x, y=y, z=z)

# ── helper: micro-dot texture field ──────────────────────────
def micro_dot_field(cavity_r, base_z, dot_r=0.12, dot_h=0.15, spacing=0.50,
                    seed=42):
    """
    Hex-packed grid of small cylinder protrusions on the mold floor.
    These protrude INTO the cavity → create dimples in the electrode surface.
    Dot diameter 0.24 mm, depth 0.15 mm — at SLA resolution limit.
    NOTE: if printer resolution is ≥0.05 mm layer / ≤0.10 mm XY, these
    will print. Otherwise press P400 sandpaper onto mold floor before use.
    """
    rng = np.random.default_rng(seed)
    sqrt3 = math.sqrt(3)
    x_step = spacing
    y_step = spacing * sqrt3 / 2

    dot_meshes = []
    for iy in range(-int(cavity_r / y_step) - 2,
                     int(cavity_r / y_step) + 3):
        for ix in range(-int(cavity_r / x_step) - 2,
                         int(cavity_r / x_step) + 3):
            x = ix * x_step + (iy % 2) * (x_step / 2)
            y = iy * y_step
            # small jitter for bio-inspired irregular look
            x += rng.uniform(-0.10, 0.10)
            y += rng.uniform(-0.10, 0.10)
            # keep inside the cavity circle with margin
            if math.sqrt(x*x + y*y) > cavity_r - dot_r - 0.2:
                continue
            d = cyl(dot_r, dot_h + 0.02)
            d = move(d, x=x, y=y, z=base_z)
            dot_meshes.append(d)

    if not dot_meshes:
        return None
    # union all dots into one mesh → single subtraction operation
    return trimesh.boolean.union(dot_meshes, engine="manifold")


# ══════════════════════════════════════════════════════════════
# V2 — EpiScreen bottom mold
# ══════════════════════════════════════════════════════════════
print("\n[V2-1/3] EpiScreen v2 bottom mold...")

def episcreen_v2_bottom():
    body_h = EP_BOT_H + WALL
    base   = cyl(EP_MOLD_OD/2, body_h)

    # Main cavity (with draft)
    draft_r = math.tan(math.radians(DRAFT)) * EP_BOT_H
    cavity  = move(cyl(EP_OD/2 + draft_r, EP_BOT_H + 0.05), z=WALL)

    # Spiral exposure platform
    plat = move(cyl(EP_SPIRAL_D/2, EP_SPIRAL_H), z=WALL - 0.05)

    # FR-4 shelf cut (wider above shelf level)
    fr4_cut = move(cyl(EP_FR4_D/2 + EP_FR4_LIP, EP_BOT_H - EP_FR4_Z + 0.1),
                   z=WALL + EP_FR4_Z)

    # Microchannel guide holes
    mch_cuts = []
    start_r = EP_RES_OD / 2
    start_z = WALL + EP_FR4_Z + EP_FR4_T + EP_RES_H / 2
    for i in range(EP_MCH_N):
        wire = cyl(EP_MCH_D / 2, 20)
        wire = rot_y(wire, EP_MCH_ANG)
        wire = move(wire, x=start_r, z=start_z - 5)
        wire = rot_z(wire, i * 120 + 30)
        mch_cuts.append(wire)

    # Alignment pin holes (4×)
    pin_holes = []
    for (px, py) in pin_positions(EP_MOLD_OD):
        h = cyl((PIN_D + CLEARANCE) / 2, PIN_H + 0.1)
        h = move(h, x=px, y=py, z=body_h - PIN_H)
        pin_holes.append(h)

    # Primary cable exit notch (3 mm wide)
    cable_1 = box(EP_CABLE_D + 0.2, EP_CABLE_W,
                  EP_BOT_H - EP_FR4_Z,
                  x=EP_MOLD_OD/2 - EP_CABLE_D,
                  y=-EP_CABLE_W/2,
                  z=WALL + EP_FR4_Z)

    # Secondary cable exit (2 mm wide, for impedance ring wire)
    cable_2 = box(EP_CABLE_D + 0.2, 2.0,
                  EP_BOT_H - EP_FR4_Z,
                  x=EP_MOLD_OD/2 - EP_CABLE_D,
                  y=EP_CABLE_W/2 + 0.5,          # offset from primary, +Y side
                  z=WALL + EP_FR4_Z)

    # ── V2 NEW: Impedance reference ring groove ───────────────
    # Annular groove at 14 mm dia (r=7), 0.8 mm wide, 0.5 mm deep
    # Cut INTO the cavity floor → wire ring sits here during casting
    imp_ring_r_in  = 14.0/2 - 0.8/2    # 6.6 mm
    imp_ring_r_out = 14.0/2 + 0.8/2    # 7.4 mm
    imp_ring = ring_mesh(imp_ring_r_in, imp_ring_r_out,
                         0.5 + 0.05,
                         z=WALL - 0.5)  # starts 0.5 mm below cavity floor

    # ── V2 NEW: Micro-dot texture field on cavity floor ───────
    # Protrudes UP into cavity from floor → dimples in electrode skin surface
    texture = micro_dot_field(cavity_r=EP_BOT_CAV_D/2 - 0.3,
                               base_z=WALL,
                               dot_r=0.12, dot_h=0.15, spacing=0.50)

    # ── Subtract everything from body ─────────────────────────
    cuts = [cavity, plat, fr4_cut, imp_ring, cable_1, cable_2,
            *mch_cuts, *pin_holes]
    body_cut = subtract(base, *cuts)

    # ── V2 NEW: Retention groove ring ─────────────────────────
    # PROTRUSION on cavity floor at 11.5 mm dia → groove on electrode face
    # Silicone fills around it → electrode gets an annular groove
    # Pad disc lip (0.3 mm tall) snaps into this groove
    ret_ring = ring_mesh(r_inner=11.5/2 - 0.5/2,   # 5.5 mm
                          r_outer=11.5/2 + 0.5/2,   # 6.0 mm
                          h=0.3,
                          z=WALL)   # sits on cavity floor, protrudes into cavity

    result = union(body_cut, ret_ring)

    # ── Add texture protrusions (union after body is built) ───
    if texture is not None:
        result = union(result, move(texture, z=0))

    return result

save(episcreen_v2_bottom(), "episcreen_v2_mold_bottom.stl")


# ══════════════════════════════════════════════════════════════
# V2 — EpiScreen top mold (unchanged from v1 — re-export)
# ══════════════════════════════════════════════════════════════
print("\n[V2-2/3] EpiScreen v2 top mold (copy of v1)...")

def episcreen_v2_top():
    """Top mold unchanged. Re-exported as v2 name for matching pair."""
    body   = cyl(EP_MOLD_OD/2, EP_TOP_H)
    top_cav_h = EP_H - EP_BOT_H
    cavity = move(cyl(EP_OD/2, top_cav_h + 0.1), z=WALL)
    res_inner = move(cyl(EP_RES_ID/2 - CLEARANCE/2, EP_RES_H + 0.1),
                     z=WALL - 0.05)
    pour   = move(cyl(EP_POUR_D/2, EP_POUR_D + 0.1),
                  z=EP_TOP_H - EP_POUR_D)
    fill   = move(cyl(1.0, WALL + 6.1),
                  x=EP_RES_OD/2 - 2, z=EP_TOP_H - 6)
    cable_1 = box(EP_CABLE_D + 0.2, EP_CABLE_W + 1, EP_TOP_H - WALL,
                  x=EP_MOLD_OD/2 - EP_CABLE_D,
                  y=-(EP_CABLE_W+1)/2, z=WALL)
    # Second cable exit slot mirrored into top
    cable_2 = box(EP_CABLE_D + 0.2, 2.0, EP_TOP_H - WALL,
                  x=EP_MOLD_OD/2 - EP_CABLE_D,
                  y=EP_CABLE_W/2 + 0.5, z=WALL)

    vent_cuts = []
    for a in [90, 270]:
        v  = cyl(VENT_D/2, WALL + 5)
        vx = (EP_MOLD_OD/2 - WALL - 2) * math.cos(math.radians(a))
        vy = (EP_MOLD_OD/2 - WALL - 2) * math.sin(math.radians(a))
        v  = move(v, x=vx, y=vy, z=EP_TOP_H - 4)
        vent_cuts.append(v)

    base = subtract(body, cavity, res_inner, pour, fill,
                    cable_1, cable_2, *vent_cuts)

    pins = []
    for (px, py) in pin_positions(EP_MOLD_OD):
        p = cyl(PIN_D/2, PIN_H + WALL)
        p = move(p, x=px, y=py, z=0)
        pins.append(p)

    return union(base, *pins)

save(episcreen_v2_top(), "episcreen_v2_mold_top.stl")


# ══════════════════════════════════════════════════════════════
# V2 — Pad Disc Mold  (open-face, single piece)
# ══════════════════════════════════════════════════════════════
#
# The disc is cast skin-contact-side DOWN (on the mold floor).
# The mold floor defines the disc's skin-contact bottom surface.
# The open top is poured level → becomes the disc top (contact-pad side).
#
# Disc geometry when used (from bottom to top):
#   Bottom (skin):  flat, micro-textured, Ø12 mm
#   Edge:           0.5 mm wide × 0.3 mm tall retaining lip
#   Centre hole:    Ø1.5 mm through-hole for electrolyte flow
#   Top (contact):  8 mm Ø raised contact pad, 0.3 mm above edges
#
# Mold cavity (floor = disc bottom / skin side):
#   • Cavity inner Ø = 12.0 mm, depth at edges = 2.0 mm
#   • Centre floor recess: Ø8 mm, 0.3 mm deeper → disc centre is
#     2.3 mm thick → top surface 0.3 mm higher than edges (raised pad)
#   • Centre pin Ø1.5 mm (through-hole former), height ≥ 2.5 mm
#   • Micro-dot texture on floor (creates texture on disc skin surface)
#   • Annular groove in side wall at rim: 0.5 mm wide × 0.3 mm deep
#     → creates retaining lip on disc edge
#   • Notch in side wall: 1 mm wide × 0.5 mm deep (fingernail grip)
#
# TRANSLUCENT SILICONE NOTE:
#   Use clear / translucent silicone (e.g. Smooth-On Ecoflex 00-20 Clear
#   or Dragon Skin 10 NV) so that reservoir fill level is visible through
#   the body. Pigment addition is optional (light blue tint recommended
#   for branding). The pad disc itself should be clear.
# ══════════════════════════════════════════════════════════════
print("\n[V2-3/3] Pad disc mold...")

# Disc parameters
PAD_DISC_D    = 12.0   # disc outer diameter
PAD_DISC_H    = 2.0    # disc thickness at edge
PAD_PAD_D     = 8.0    # contact pad diameter
PAD_PAD_RISE  = 0.3    # contact pad height above disc edge
PAD_LIP_W     = 0.5    # retaining lip width
PAD_LIP_H     = 0.3    # retaining lip height
PAD_HOLE_D    = 1.5    # electrolyte flow through-hole
PAD_NOTCH_W   = 1.0    # fingernail notch width
PAD_NOTCH_D   = 0.5    # fingernail notch depth

MOLD_WALL_SM  = 2.0    # mold outer wall thickness (small mold)
PAD_MOLD_OD   = PAD_DISC_D + 2 * MOLD_WALL_SM   # 16 mm
PAD_MOLD_H    = PAD_DISC_H + PAD_PAD_RISE + MOLD_WALL_SM  # 4.8 mm

def pad_disc_mold():
    # ── Outer body ────────────────────────────────────────────
    body = cyl(PAD_MOLD_OD/2, PAD_MOLD_H)

    # ── Main cavity (edge-thickness depth, full disc diameter) ─
    # The mold floor is at z = MOLD_WALL_SM (bottom wall)
    cav_depth_edge   = PAD_DISC_H            # 2.0 mm at edges
    cav_depth_centre = PAD_DISC_H + PAD_PAD_RISE  # 2.3 mm at centre

    floor_z = MOLD_WALL_SM                   # bottom of cavity
    rim_z   = floor_z + cav_depth_edge       # where you pour to (rim)

    # Edge cavity (full disc diameter, edge depth)
    edge_cav = move(cyl(PAD_DISC_D/2, cav_depth_edge + 0.02),
                    z=floor_z - 0.01)

    # Centre recess (extra 0.3 mm deeper, 8 mm dia)
    # → disc gets 0.3 mm more silicone at centre → raised contact pad
    centre_recess = move(cyl(PAD_PAD_D/2, PAD_PAD_RISE + 0.02),
                         z=floor_z - PAD_PAD_RISE - 0.01)

    # ── Centre pin (through-hole former) ─────────────────────
    # Extends from the deepest floor point to above the pour surface
    pin_bot_z = floor_z - PAD_PAD_RISE
    pin_height = cav_depth_centre + 0.5      # sticks 0.5 mm above pour
    pin = move(cyl(PAD_HOLE_D/2, pin_height + 0.02), z=pin_bot_z - 0.01)

    # ── Lip groove in cavity side wall ────────────────────────
    # Cut an annular groove into the inner wall at rim height
    # → when silicone cures and is demolded, the lip stays on disc
    # Groove: inner wall at r = PAD_DISC_D/2, groove goes outward 0.5 mm
    lip_groove_r_in  = PAD_DISC_D/2                  # flush with cavity wall
    lip_groove_r_out = PAD_DISC_D/2 + PAD_LIP_W      # 0.5 mm into mold wall
    lip_groove = ring_mesh(r_inner=lip_groove_r_in,
                            r_outer=lip_groove_r_out,
                            h=PAD_LIP_H + 0.02,
                            z=rim_z - PAD_LIP_H)

    # ── Fingernail notch in side wall ─────────────────────────
    # Rectangular slot through the outer wall at one point on circumference
    notch = box(MOLD_WALL_SM + 0.2,          # radial depth (through wall)
                PAD_NOTCH_W,                  # angular width
                cav_depth_edge,               # full cavity height
                x=PAD_DISC_D/2 - 0.1,        # starts just inside cavity wall
                y=-PAD_NOTCH_W/2,
                z=floor_z)

    # ── Micro-dot texture on cavity floor (skin-contact side) ─
    texture = micro_dot_field(cavity_r=PAD_DISC_D/2 - 0.3,
                               base_z=floor_z,
                               dot_r=0.12, dot_h=0.15, spacing=0.45)

    # ── Boolean operations ────────────────────────────────────
    result = subtract(body, edge_cav, centre_recess, pin,
                      lip_groove, notch)

    # Texture protrusions (union, pointing into cavity)
    if texture is not None:
        result = union(result, move(texture, z=0))

    return result

save(pad_disc_mold(), "pad_disc_mold.stl")

print("\n✓  V2 STL files generated in:", OUT)
