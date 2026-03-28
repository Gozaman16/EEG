#!/usr/bin/env python3
"""
Cross-Section View — publication-quality 300 DPI PNG
Vertical cut through EpiScreen electrode centre revealing all
internal layers, dimensions, and material callouts.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mp
from matplotlib.patches import FancyArrowPatch, Arc, FancyBboxPatch
from matplotlib.lines import Line2D
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "renders")
os.makedirs(OUT, exist_ok=True)

C = {
    "silicone":   (0.55, 0.78, 0.96, 0.82),
    "silicone_e": (0.20, 0.50, 0.80, 1.0),
    "fr4":        (0.18, 0.58, 0.18, 1.0),
    "fr4_e":      (0.08, 0.38, 0.08, 1.0),
    "copper":     (0.85, 0.55, 0.20, 1.0),
    "copper_e":   (0.60, 0.32, 0.05, 1.0),
    "reservoir":  (0.98, 0.95, 0.10, 0.60),
    "reservoir_e":(0.72, 0.70, 0.00, 1.0),
    "graphene":   (0.10, 0.10, 0.12, 1.0),
    "mold":       (0.60, 0.62, 0.66, 0.55),
    "mold_dark":  (0.40, 0.42, 0.46, 0.75),
    "mold_e":     (0.28, 0.30, 0.34, 1.0),
    "channel":    (0.90, 0.12, 0.12, 1.0),
    "white":      (0.97, 0.97, 0.97, 1.0),
    "white_e":    (0.68, 0.68, 0.70, 1.0),
    "pin_steel":  (0.78, 0.80, 0.84, 1.0),
    "text":       (0.08, 0.08, 0.12, 1.0),
    "dim":        (0.42, 0.42, 0.48, 1.0),
    "bg":         (0.97, 0.97, 0.98, 1.0),
    "grid":       (0.86, 0.86, 0.89, 1.0),
    "accent":     (0.12, 0.32, 0.70, 1.0),
    "hatch_mold": (0.50, 0.52, 0.56, 0.40),
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size":   9,
    "figure.dpi":  300,
    "savefig.dpi": 300,
    "hatch.linewidth": 0.4,
})

# ── Electrode geometry (all mm) ───────────────────────────────────────────────
OD   = 24.0;  R  = OD / 2        # electrode outer radius
WALL = 1.5                        # mold wall thickness
MR   = 16.0                       # mold outer radius

# Layer Z positions (bottom of electrode = 0)
Z0_ELEC   = 0.0                   # electrode bottom (skin surface)
Z_SKIN_H  = 1.0                   # skin-contact recess height
Z_FR4     = 3.0                   # FR-4 bottom
FR4_T     = 1.6
Z_RES     = Z_FR4 + FR4_T         # reservoir bottom
RES_H     = 1.5
Z_TOP     = 10.0                  # electrode top

RES_ID    = 13.0; RES_OR = 9.5   # reservoir half-widths
RES_IR    = 6.5

# Spiral platform
SP_R      = 4.0;  SP_H = 0.8

# Mold geometry
Z_MOLD_B  = -WALL                 # mold body starts below electrode
Z_PART    = Z_TOP / 2             # parting line at 5 mm
Z_MOLD_T  = Z_TOP + WALL

# Microchannel wire
MCH_ANG   = 37.5                  # degrees from horizontal
MCH_D     = 0.25                  # half-diameter in drawing

CX = 0   # centre X of electrode

# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 13))
fig.patch.set_facecolor(C["bg"])
ax.set_facecolor(C["bg"])
ax.set_aspect('equal')
ax.axis('off')

ax.set_xlim(-48, 48)
ax.set_ylim(-14, 26)

# ── Title ─────────────────────────────────────────────────────────────────────
ax.text(0, 25.2, "EpiScreen Electrode — Cross-Section View (Y = 0 plane)",
        ha='center', va='top', fontsize=11, fontweight='bold', color=C["text"])
ax.text(0, 24.2, "Standard 24 mm electrode with all internal features • Assembled configuration",
        ha='center', va='top', fontsize=7.5, color=C["dim"])

# ═══════════════════════════════════════════════════════════════════════════════
# BOTTOM MOLD HALF  (z from -WALL to Z_PART)
# ═══════════════════════════════════════════════════════════════════════════════
bm_h = WALL + Z_PART

# Outer mold body (left half only — cross-section convention)
bm_outer_l = mp.Rectangle((-MR, Z_MOLD_B), MR - R, bm_h,
                            facecolor=C["mold"], edgecolor=C["mold_e"],
                            linewidth=0.9, hatch='////', zorder=3)
bm_outer_r = mp.Rectangle((R, Z_MOLD_B), MR - R, bm_h,
                            facecolor=C["mold"], edgecolor=C["mold_e"],
                            linewidth=0.9, hatch='////', zorder=3)
ax.add_patch(bm_outer_l)
ax.add_patch(bm_outer_r)

# Mold base plate (below electrode)
base = mp.Rectangle((-MR, Z_MOLD_B), MR*2, WALL,
                     facecolor=C["mold_dark"], edgecolor=C["mold_e"],
                     linewidth=0.9, zorder=3)
ax.add_patch(base)

# FR-4 shelf ring (protrusion inside mold at z=FR4_Z)
shelf_l = mp.Rectangle((-MR, Z_FR4 - 0.3), (MR - R - 2), 0.3,
                         facecolor=C["mold_dark"], edgecolor="none", zorder=5)
shelf_r = mp.Rectangle((R + 2, Z_FR4 - 0.3), (MR - R - 2), 0.3,
                         facecolor=C["mold_dark"], edgecolor="none", zorder=5)
ax.add_patch(shelf_l)
ax.add_patch(shelf_r)

# Spiral exposure platform (raised inside bottom cavity)
sp_plat = mp.Rectangle((-SP_R, Z_MOLD_B + WALL), SP_R*2, SP_H,
                         facecolor=C["mold_dark"], edgecolor="none", zorder=5)
ax.add_patch(sp_plat)

# Alignment pin holes (left side only in cross-section)
ph = mp.Rectangle((-MR + 1, Z_PART - 3), 2, 3.1,
                    facecolor=C["bg"], edgecolor=C["mold_e"],
                    linewidth=0.6, zorder=5)
ax.add_patch(ph)

# ═══════════════════════════════════════════════════════════════════════════════
# TOP MOLD HALF  (z from Z_PART to Z_MOLD_T)
# ═══════════════════════════════════════════════════════════════════════════════
tm_h = WALL + (Z_TOP - Z_PART)

tm_outer_l = mp.Rectangle((-MR, Z_PART), MR - R, tm_h,
                            facecolor=C["mold"], edgecolor=C["mold_e"],
                            linewidth=0.9, hatch='////', zorder=3)
tm_outer_r = mp.Rectangle((R, Z_PART), MR - R, tm_h,
                            facecolor=C["mold"], edgecolor=C["mold_e"],
                            linewidth=0.9, hatch='////', zorder=3)
ax.add_patch(tm_outer_l)
ax.add_patch(tm_outer_r)

# Top mold cap
cap = mp.Rectangle((-MR, Z_TOP), MR*2, WALL,
                    facecolor=C["mold_dark"], edgecolor=C["mold_e"],
                    linewidth=0.9, zorder=3)
ax.add_patch(cap)

# Pour hole (centre, top cap)
pour_cut = mp.Rectangle((-3, Z_TOP - 0.1), 6, WALL + 0.2,
                          facecolor=C["bg"], edgecolor="none", zorder=5)
ax.add_patch(pour_cut)
# Funnel hint
pour_funnel = mp.Polygon([[-3.5, Z_TOP + WALL + 0.1], [3.5, Z_TOP + WALL + 0.1],
                           [3, Z_TOP], [-3, Z_TOP]],
                          facecolor=C["bg"], edgecolor=C["dim"], lw=0.6, zorder=6)
ax.add_patch(pour_funnel)

# Vent holes (both sides, top mold)
for vx in [-11, 11]:
    vent = mp.Rectangle((vx - 0.5, Z_TOP - 0.1), 1, WALL + 0.2,
                          facecolor=C["bg"], edgecolor=C["mold_e"],
                          linewidth=0.5, zorder=5)
    ax.add_patch(vent)

# Reservoir ring protrusion on top mold bottom face
res_prot_l = mp.Rectangle((-RES_OR, Z_RES), RES_OR - RES_IR, RES_H,
                            facecolor=C["mold_dark"], edgecolor="none", zorder=5)
res_prot_r = mp.Rectangle((RES_IR, Z_RES), RES_OR - RES_IR, RES_H,
                            facecolor=C["mold_dark"], edgecolor="none", zorder=5)
ax.add_patch(res_prot_l)
ax.add_patch(res_prot_r)

# Alignment pins (male, on top mold)
pin_m = mp.Rectangle((-MR + 1, Z_PART - 3), 2, 3.1,
                       facecolor=C["pin_steel"], edgecolor=C["mold_e"],
                       linewidth=0.6, zorder=5)
ax.add_patch(pin_m)

# ═══════════════════════════════════════════════════════════════════════════════
# ELECTRODE SILICONE BODY
# ═══════════════════════════════════════════════════════════════════════════════
sil_body = mp.Rectangle((-R, Z0_ELEC), OD, Z_TOP,
                          facecolor=C["silicone"], edgecolor=C["silicone_e"],
                          linewidth=1.2, zorder=4)
ax.add_patch(sil_body)

# ── Skin-contact graphene surface (bottom) ────────────────────────────────────
skin_surface = mp.Rectangle((-6, -1.0), 12, 1.05,
                              facecolor=C["graphene"], edgecolor="none", zorder=6)
ax.add_patch(skin_surface)

# Micro-texture lines on skin surface
for tx in np.arange(-5.5, 5.5, 0.5):
    ax.plot([tx, tx], [-1.0, -0.7],
            color=(0.35, 0.35, 0.35), lw=0.35, zorder=7, alpha=0.7)

# Skin contact recess boundary
skin_edge = mp.Rectangle((-6, -1.0), 12, 1.0,
                           facecolor='none', edgecolor=C["graphene"],
                           linewidth=0.8, zorder=7)
ax.add_patch(skin_edge)

# ── Spiral exposure platform area ─────────────────────────────────────────────
spiral = mp.Rectangle((-SP_R, Z0_ELEC), SP_R*2, SP_H,
                        facecolor=C["copper"], edgecolor=C["copper_e"],
                        linewidth=0.7, zorder=6)
ax.add_patch(spiral)
# Spiral trace hint
for rs in np.arange(0.5, SP_R - 0.3, 0.6):
    arc = Arc((0, SP_H/2), rs*2, rs*2, angle=0, theta1=15, theta2=345,
               color=C["copper_e"], lw=0.35, zorder=7)
    ax.add_patch(arc)

# ── FR-4 disk ─────────────────────────────────────────────────────────────────
fr4 = mp.Rectangle((-9.5, Z_FR4), 19, FR4_T,
                    facecolor=C["fr4"], edgecolor=C["fr4_e"],
                    linewidth=0.9, zorder=6)
ax.add_patch(fr4)

# PCB traces on FR-4 (copper rings)
for rr in [2.2, 4.0, 5.8, 7.5, 8.8]:
    arc = Arc((0, Z_FR4 + FR4_T/2), rr*2, rr*2, angle=0, theta1=10, theta2=170,
               color=C["copper"], lw=0.55, zorder=7)
    ax.add_patch(arc)

# ── Reservoir ring void ────────────────────────────────────────────────────────
res_l = mp.Rectangle((-RES_OR, Z_RES), RES_OR - RES_IR, RES_H,
                      facecolor=C["reservoir"], edgecolor=C["reservoir_e"],
                      linewidth=0.7, linestyle='--', zorder=6)
res_r = mp.Rectangle((RES_IR, Z_RES), RES_OR - RES_IR, RES_H,
                      facecolor=C["reservoir"], edgecolor=C["reservoir_e"],
                      linewidth=0.7, linestyle='--', zorder=6)
ax.add_patch(res_l)
ax.add_patch(res_r)

# ── Emici halka (absorbent ring, white, sits in reservoir) ────────────────────
em_l = mp.Rectangle((-RES_OR + 0.3, Z_RES + 0.2), RES_OR - RES_IR - 0.6, RES_H - 0.4,
                     facecolor=C["white"], edgecolor=C["white_e"],
                     linewidth=0.6, zorder=7)
em_r = mp.Rectangle((RES_IR + 0.3, Z_RES + 0.2), RES_OR - RES_IR - 0.6, RES_H - 0.4,
                     facecolor=C["white"], edgecolor=C["white_e"],
                     linewidth=0.6, zorder=7)
ax.add_patch(em_l)
ax.add_patch(em_r)

# ── Microchannel wire (one shown, angled) ─────────────────────────────────────
ang_rad = np.radians(MCH_ANG)
wire_x0 = 6.5     # starts at inner reservoir edge
wire_z0 = Z_RES + RES_H/2
wire_len = 10
wire_x1 = wire_x0 + wire_len * np.cos(ang_rad)
wire_z1 = wire_z0 - wire_len * np.sin(ang_rad)

ax.plot([wire_x0, wire_x1], [wire_z0, wire_z1],
        color=C["channel"], lw=2.0, solid_capstyle='round', zorder=8)
ax.plot([wire_x0, wire_x1], [wire_z0, wire_z1],
        color='white', lw=0.7, solid_capstyle='round', zorder=9, alpha=0.6)

# Microchannel exit point (through mold wall)
ax.plot(wire_x1, wire_z1, 'o', color=C["channel"], ms=3.5, zorder=10)

# ── Cable exit notch (right side wall) ────────────────────────────────────────
cable = mp.Rectangle((R - 0.5, Z_FR4), 5, Z_TOP - Z_FR4,
                       facecolor=C["bg"], edgecolor=C["dim"],
                       linewidth=0.6, linestyle=':', zorder=8)
ax.add_patch(cable)
# Funnel shape at top
cable_top = mp.Polygon([(R - 0.5, Z_TOP), (R + 4.5, Z_TOP),
                         (R + 5.0, Z_TOP + 0.5), (R - 0.8, Z_TOP + 0.5)],
                        facecolor=C["bg"], edgecolor=C["dim"],
                        linewidth=0.5, zorder=8)
ax.add_patch(cable_top)

# ── Parting line ──────────────────────────────────────────────────────────────
ax.plot([-MR - 2, MR + 2], [Z_PART, Z_PART],
        color=C["accent"], lw=1.0, ls=(0, (8, 4)), zorder=10)
ax.text(MR + 2.5, Z_PART, "Parting line", ha='left', va='center',
        fontsize=7, color=C["accent"], fontstyle='italic')

# ═══════════════════════════════════════════════════════════════════════════════
# DIMENSION LINES (right side)
# ═══════════════════════════════════════════════════════════════════════════════
dim_x = MR + 6   # X position for dim lines

def dim_arrow(ax, x, y1, y2, label, label_side='right', offset=0):
    lx = x + offset
    ax.annotate("", xy=(lx, y2), xytext=(lx, y1),
                arrowprops=dict(arrowstyle="<->", color=C["accent"],
                                lw=0.85, mutation_scale=8))
    mid = (y1 + y2) / 2
    tx = lx + (1.2 if label_side == 'right' else -1.2)
    ax.text(tx, mid, label, ha='left' if label_side == 'right' else 'right',
            va='center', fontsize=7, color=C["accent"])
    # extension lines
    ax.plot([x - 1, lx + 0.5], [y1, y1], color=C["grid"], lw=0.5, ls='--', zorder=2)
    ax.plot([x - 1, lx + 0.5], [y2, y2], color=C["grid"], lw=0.5, ls='--', zorder=2)

dim_arrow(ax, R, Z0_ELEC, Z_TOP,   "10 mm\n(electrode\nheight)", offset=dim_x - R)
dim_arrow(ax, R, Z_FR4, Z_FR4 + FR4_T, "1.6", offset=dim_x - R + 8)
dim_arrow(ax, R, Z_RES, Z_RES + RES_H, "1.5", offset=dim_x - R + 8)

# Outer diameter
ax.annotate("", xy=(R, -8), xytext=(-R, -8),
            arrowprops=dict(arrowstyle="<->", color=C["accent"],
                            lw=0.85, mutation_scale=8))
ax.text(0, -8.8, "Ø 24 mm (electrode) / Ø 32 mm (mold)",
        ha='center', va='top', fontsize=7, color=C["accent"])
ax.plot([-R, -R], [-8, Z0_ELEC], color=C["grid"], lw=0.5, ls='--', zorder=2)
ax.plot([R, R],   [-8, Z0_ELEC], color=C["grid"], lw=0.5, ls='--', zorder=2)

# FR-4 seat Z
ax.annotate("", xy=(-MR - 5, Z_FR4), xytext=(-MR - 5, Z0_ELEC),
            arrowprops=dict(arrowstyle="<->", color=C["dim"],
                            lw=0.75, mutation_scale=7))
ax.text(-MR - 6, Z_FR4/2, "3 mm\nseat", ha='right', va='center',
        fontsize=6.5, color=C["dim"])
ax.plot([-MR - 5, -R], [Z_FR4, Z_FR4], color=C["grid"], lw=0.5, ls='--', zorder=2)

# Skin recess
ax.annotate("", xy=(-MR - 8, Z0_ELEC), xytext=(-MR - 8, -1.0),
            arrowprops=dict(arrowstyle="<->", color=C["dim"],
                            lw=0.75, mutation_scale=7))
ax.text(-MR - 9, -0.5, "1 mm", ha='right', va='center',
        fontsize=6.5, color=C["dim"])
ax.plot([-MR - 8, -6], [Z0_ELEC, Z0_ELEC], color=C["grid"], lw=0.5, ls='--', zorder=2)
ax.plot([-MR - 8, -6], [-1.0, -1.0],       color=C["grid"], lw=0.5, ls='--', zorder=2)

# Mold wall thickness
ax.annotate("", xy=(-MR, -11), xytext=(-R, -11),
            arrowprops=dict(arrowstyle="<->", color=C["mold_e"],
                            lw=0.75, mutation_scale=7))
ax.text((-MR - R)/2, -11.8, "4 mm wall", ha='center', va='top',
        fontsize=6.5, color=C["mold_e"])
ax.plot([-MR, -MR], [-11, Z_MOLD_B], color=C["grid"], lw=0.5, ls='--', zorder=2)
ax.plot([-R,  -R],  [-11, Z_MOLD_B], color=C["grid"], lw=0.5, ls='--', zorder=2)

# ═══════════════════════════════════════════════════════════════════════════════
# CALLOUT ANNOTATIONS (leader lines + labels, left side)
# ═══════════════════════════════════════════════════════════════════════════════
def callout(ax, xy, xytext, label, color=None):
    c = color or C["text"]
    ax.annotate(label,
                xy=xy, xytext=xytext,
                ha='right', va='center',
                fontsize=7, color=c,
                arrowprops=dict(arrowstyle="-|>",
                                color=c, lw=0.7,
                                mutation_scale=7),
                bbox=dict(boxstyle='round,pad=0.15',
                          facecolor=C["bg"], edgecolor='none', alpha=0.8))

callout(ax, xy=(-SP_R, SP_H/2),   xytext=(-37, 0.4),
        label="Copper spiral\n(exposed, 8 mm Ø)", color=C["copper_e"])

callout(ax, xy=(-6, -0.5),        xytext=(-38, -1.5),
        label="Graphene coating\n+ micro-texture skin surface", color=C["graphene"])

callout(ax, xy=(-9.5, Z_FR4 + FR4_T/2), xytext=(-42, Z_FR4 + FR4_T/2),
        label="FR-4 PCB disk\n19 mm Ø × 1.6 mm", color=C["fr4_e"])

callout(ax, xy=(-RES_OR, Z_RES + RES_H/2), xytext=(-42, Z_RES + RES_H/2),
        label="Reservoir ring\n(hydrogel channel)\nID 13 / OD 19 mm", color=C["reservoir_e"])

callout(ax, xy=(-RES_OR + 0.5, Z_RES + 0.5), xytext=(-42, Z_RES + RES_H + 1.5),
        label="Emici halka\n(absorbent ring)", color=C["white_e"])

callout(ax, xy=(wire_x1 - 1, wire_z1 + 0.5), xytext=(32, wire_z1 + 3),
        label="Microchannel wire\n(Ø 0.5 mm steel,\nremoved after cure)",
        color=C["channel"])

callout(ax, xy=(R + 0.3, Z_FR4 + (Z_TOP - Z_FR4)/2), xytext=(32, Z_FR4 + 1.5),
        label="Cable exit\nnotch\n(3 mm × 3 mm)", color=C["dim"])

callout(ax, xy=(0, Z_TOP + WALL/2), xytext=(12, Z_TOP + WALL + 1.5),
        label="Pour hole\n(Ø 6 mm)", color=C["mold_e"])

callout(ax, xy=(-11, Z_TOP + WALL/2), xytext=(-28, Z_TOP + WALL + 1.5),
        label="Vent holes\n(Ø 1 mm × 2)", color=C["mold_e"])

callout(ax, xy=(-MR + 2.5, Z_PART - 1.5), xytext=(-42, Z_PART - 2),
        label="Alignment pin\n(Ø 2 mm × 3 mm)", color=C["pin_steel"])

callout(ax, xy=(SP_R - 0.5, SP_H/2), xytext=(38, 0.8),
        label="Spiral platform\n(0.8 mm raised,\nprevents silicone\nunderfill)",
        color=C["mold_e"])

# ── Section cut marker (top) ───────────────────────────────────────────────────
for xx in [-22, 22]:
    ax.annotate("A", xy=(xx, 23.5), ha='center', va='center',
                fontsize=9, fontweight='bold', color=C["accent"],
                bbox=dict(boxstyle='circle,pad=0.2', facecolor='white',
                          edgecolor=C["accent"], lw=1.2))
ax.annotate("", xy=(20, 23.5), xytext=(-20, 23.5),
            arrowprops=dict(arrowstyle="-", color=C["accent"],
                            lw=1.5, linestyle='dashed'))
ax.text(0, 23.5, "  SECTION A–A  ",
        ha='center', va='center', fontsize=7.5,
        color=C["accent"], fontweight='bold',
        bbox=dict(facecolor=C["bg"], edgecolor='none', pad=2))

# ── Material hatch legend ─────────────────────────────────────────────────────
leg_x, leg_y = 24, -3
legend_items = [
    (C["mold"],      "////", C["mold_e"],     "Resin mold (SLA)"),
    (C["silicone"],  "",     C["silicone_e"], "Silicone electrode body"),
    (C["fr4"],       "",     C["fr4_e"],      "FR-4 PCB disk"),
    (C["copper"],    "",     C["copper_e"],   "Copper spiral trace"),
    (C["reservoir"], "",     C["reservoir_e"],"Reservoir channel"),
    (C["graphene"],  "",     "none",          "Graphene/skin surface"),
    (C["white"],     "",     C["white_e"],    "Emici halka (absorbent)"),
]
ax.text(leg_x, leg_y + 0.5, "Materials", ha='left', fontsize=8,
        fontweight='bold', color=C["text"])
for i, (fc, hatch, ec, lbl) in enumerate(legend_items):
    ry = leg_y - 1.5 - i * 2.2
    rect = mp.Rectangle((leg_x, ry), 3.0, 1.8,
                          facecolor=fc, edgecolor=ec if ec != "none" else "none",
                          linewidth=0.7, hatch=hatch, zorder=5)
    ax.add_patch(rect)
    ax.text(leg_x + 4, ry + 0.9, lbl, va='center', fontsize=7, color=C["text"])

# ── Footer ─────────────────────────────────────────────────────────────────────
ax.text(0, -13.5,
        "EpiScreen EEG Electrode System  •  ISEF 2026  "
        "•  Section cut through electrode centre  •  All dimensions in mm",
        ha='center', va='bottom', fontsize=6.5,
        color=C["dim"], style='italic')

plt.tight_layout(pad=0.3)
out_path = os.path.join(OUT, "assembly_cross_section.png")
fig.savefig(out_path, dpi=300, bbox_inches='tight',
            facecolor=C["bg"], edgecolor='none')
plt.close()
print(f"Saved: {out_path}")
