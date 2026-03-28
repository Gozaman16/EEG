#!/usr/bin/env python3
"""
EpiScreen EEG Electrode Mold — STL Generator
Generates all mold and mounting STL files using trimesh primitives.
Mirrors the parametric design from the .scad files.
"""

import math
import numpy as np
import trimesh
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

def save(mesh, name):
    path = os.path.join(OUT, name)
    mesh.export(path)
    print(f"  Saved: {path}  (faces={len(mesh.faces)})")

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
