#!/usr/bin/env python3
"""
Cross-section diagram for the EpiScreen pad disc:
  Panel A — Pad disc alone (all features labeled)
  Panel B — Pad disc inserted in electrode body (assembly section)
"""

import math, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Arc
from matplotlib.lines import Line2D

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "renders")
os.makedirs(OUT, exist_ok=True)

# ── Colours ────────────────────────────────────────────────────
C_DISC      = "#C8E6C9"   # pale green — silicone pad disc
C_DISC_E    = "#2E7D32"   # dark green edge
C_ELECTRODE = "#B3E5FC"   # pale blue — main electrode body
C_ELEC_E    = "#01579B"
C_COPPER    = "#FF8F00"   # copper spiral
C_COTTON    = "#FFF9C4"   # cotton ring
C_COTTON_E  = "#F9A825"
C_ELECTRO   = "#80DEEA"   # electrolyte
C_IMP_RING  = "#EF9A9A"   # impedance ring wire
C_GRAPHENE  = "#37474F"   # graphene/silver coating
C_MOLD      = "#F5F5F5"   # mold resin (light)
C_MOLD_E    = "#757575"
C_SKIN      = "#FFCCBC"   # skin

# ── Dimensions (mm → scaled to plot units) ─────────────────────
# Using mm directly, matplotlib units = mm
DISC_R      = 11.8/2
DISC_T      = 2.5
LIP_W       = 0.5
LIP_H       = 0.3
LIP_Z       = 0.5
CROWN       = 0.3
PAD_R       = 8.0/2
PAD_H       = 0.3
ABS_RI      = 8.5/2
ABS_RO      = 11.0/2
ABS_D       = 1.0
FLOW_R      = 1.5/2
CH_W        = 0.3
CH_D        = 0.2
DOT_R       = 0.125
DOT_H       = 0.15

# Electrode body (for panel B)
EP_R        = 24.0/2
EP_BOT_H    = 5.0
CAV_R       = 12.0/2
CAV_H       = 1.0
FR4_Z       = 3.0
FR4_T       = 1.6
SPIRAL_R    = 8.0/2
SPIRAL_H    = 0.8
IMP_RI      = 14.0/2 - 0.4
IMP_RO      = 14.0/2 + 0.4
GROOVE_R    = 11.5/2
GROOVE_W    = 0.5
GROOVE_DEP  = 0.3

SCALE = 8   # mm per unit — everything stays in mm

fig, axes = plt.subplots(1, 2, figsize=(18, 11),
                          facecolor="#1C1C1C",
                          gridspec_kw={"width_ratios": [1, 1.4]})
fig.subplots_adjust(left=0.04, right=0.98, top=0.93, bottom=0.04, wspace=0.06)

for ax in axes:
    ax.set_facecolor("#2A2A2A")
    ax.set_aspect("equal")
    ax.axis("off")

# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def rect(ax, x, y, w, h, fc, ec, lw=0.8, alpha=1.0, zorder=2):
    p = mpatches.Rectangle((x, y), w, h, facecolor=fc,
                             edgecolor=ec, linewidth=lw,
                             alpha=alpha, zorder=zorder)
    ax.add_patch(p)

def mirror_rect(ax, x0, y0, w, h, fc, ec, **kw):
    """Draw rect on +x side and mirror on -x side."""
    rect(ax, x0, y0, w, h, fc, ec, **kw)
    rect(ax, -(x0 + w), y0, w, h, fc, ec, **kw)

def annot(ax, text, xy, xytext, color="#EEEEEE", fontsize=7.5, ha="left"):
    ax.annotate(text, xy=xy, xytext=xytext,
                fontsize=fontsize, color=color,
                arrowprops=dict(arrowstyle="->", color="#888888",
                                lw=0.8, connectionstyle="arc3,rad=0.1"),
                ha=ha, va="center",
                bbox=dict(boxstyle="round,pad=0.2", fc="#1C1C1C",
                          ec="#444444", alpha=0.85))

def hline(ax, x0, x1, y, color="#555555", lw=0.6, ls="--"):
    ax.plot([x0, x1], [y, y], color=color, lw=lw, ls=ls, zorder=1)

def centerline(ax, x, y0, y1):
    ax.plot([x, x], [y0, y1], color="#444", lw=0.5, ls=":", zorder=1)

# ═══════════════════════════════════════════════════════════════
# PANEL A — PAD DISC CROSS-SECTION ALONE
# ═══════════════════════════════════════════════════════════════
ax = axes[0]
ax.set_title("A — Pad Disc: Cross-Section (all features)",
             color="#EEEEEE", fontsize=10, pad=8, loc="left")

OX, OY = 0, 1.0   # disc centre

# z=0 is bottom (skin surface), z=DISC_T is top (electrode face)

# ── Main disc body ───────────────────────────────────────────
# Left side: -DISC_R..0, right: 0..+DISC_R
# Draw as two rects plus crown approximation
disc_body_y = OY
mirror_rect(ax, OX, disc_body_y, DISC_R, DISC_T, C_DISC, C_DISC_E, lw=1.0)

# Crown: approx parabola at bottom surface (convex skin side = y=OY)
crown_x = np.linspace(-DISC_R, DISC_R, 120)
crown_y = OY + CROWN * (1 - (crown_x/DISC_R)**2)
ax.fill_between(crown_x, OY, crown_y, color=C_GRAPHENE, alpha=0.7, zorder=3)
ax.plot(crown_x, crown_y, color="#546E7A", lw=1.0, zorder=4)

# ── Graphene/silver coating band ─────────────────────────────
coat_t = 0.06
ax.fill_between(crown_x, crown_y, crown_y + coat_t,
                color=C_GRAPHENE, alpha=0.9, zorder=4)

# ── Centre flow hole ─────────────────────────────────────────
rect(ax, -FLOW_R, disc_body_y - 0.05, 2*FLOW_R, DISC_T + 0.1,
     "#2A2A2A", "#888", lw=0.8, zorder=5)

# ── Retention lip (both sides) ──────────────────────────────
lip_y = OY + LIP_Z - LIP_W/2
for sign in [1, -1]:
    lx = sign * DISC_R
    lw_dir = sign * LIP_H
    rect(ax, lx, lip_y, lw_dir, LIP_W, C_DISC_E, C_DISC_E, lw=0, zorder=5)

# ── Contact pad raised area (top face, electrode side) ───────
pad_top = OY + DISC_T
rect(ax, -PAD_R, pad_top, 2*PAD_R, PAD_H, C_COPPER, "#BF360C", lw=0.7, zorder=5)

# ── Absorbent ring seat groove ────────────────────────────────
abs_top = OY + DISC_T
# groove drawn as two flanking strips (groove is the gap between ABS_RI and ABS_RO)
# Left side: negative X
mirror_rect(ax, ABS_RI, abs_top - ABS_D, ABS_RO - ABS_RI, ABS_D,
            C_COTTON, C_COTTON_E, lw=0.8, zorder=5)
# Fill with cotton
mirror_rect(ax, ABS_RI + 0.05, abs_top - ABS_D + 0.1,
            ABS_RO - ABS_RI - 0.1, ABS_D - 0.2,
            C_COTTON, C_COTTON_E, lw=0, alpha=0.8, zorder=6)

# ── Electrolyte distribution channels (bottom) ───────────────
ch_y = OY
for cx in [DISC_R * 0.4]:
    rect(ax, cx - CH_W/2, ch_y - CH_D, CH_W, CH_D, "#80DEEA", "#006064", lw=0, zorder=6)
    rect(ax, -(cx + CH_W/2), ch_y - CH_D, CH_W, CH_D, "#80DEEA", "#006064", lw=0, zorder=6)

# ── Hex dot bumps on skin surface (schematic, 4 each side) ───
dot_y = crown_y
for xi in np.arange(FLOW_R + 0.5, DISC_R - 0.3, 1.0):
    dy = OY + CROWN * (1 - (xi/DISC_R)**2)
    ax.add_patch(mpatches.Rectangle((xi - DOT_R, dy), 2*DOT_R, DOT_H,
                                     fc="#37474F", ec="none", zorder=6))
    ax.add_patch(mpatches.Rectangle((-xi - DOT_R, dy), 2*DOT_R, DOT_H,
                                     fc="#37474F", ec="none", zorder=6))

# ── Centreline ───────────────────────────────────────────────
centerline(ax, OX, OY - 0.5, OY + DISC_T + PAD_H + 1.0)

# ── Dim lines ────────────────────────────────────────────────
def dim_h(ax, x0, x1, y, label, above=True, col="#AAAAAA"):
    yo = y + (0.25 if above else -0.25)
    ax.annotate("", xy=(x1, yo), xytext=(x0, yo),
                arrowprops=dict(arrowstyle="<->", color=col, lw=0.8))
    ax.text((x0+x1)/2, yo + (0.12 if above else -0.18), label,
            color=col, fontsize=6.5, ha="center", va="bottom" if above else "top")

def dim_v(ax, x, y0, y1, label, right=True, col="#AAAAAA"):
    xo = x + (0.25 if right else -0.25)
    ax.annotate("", xy=(xo, y1), xytext=(xo, y0),
                arrowprops=dict(arrowstyle="<->", color=col, lw=0.8))
    ax.text(xo + (0.12 if right else -0.12), (y0+y1)/2, label,
            color=col, fontsize=6.5, ha="left" if right else "right", va="center")

# Overall disc dims
dim_h(ax, -DISC_R, DISC_R, OY + DISC_T + PAD_H + 0.35, "∅11.8 mm")
dim_v(ax, DISC_R, OY, OY + DISC_T, "2.5 mm", right=True)

# Annotations
annot(ax, "Retention lip\n(0.5 × 0.3 mm snap-fit)",
      (DISC_R + LIP_H*0.5, lip_y + LIP_W/2),
      (DISC_R + 1.6, lip_y + 1.2))

annot(ax, "Centre flow hole\n(∅1.5 mm)",
      (FLOW_R, OY + DISC_T*0.5), (2.5, OY + DISC_T + 1.0))

annot(ax, "Raised contact pad\n(∅8 mm, 0.3 mm)",
      (PAD_R*0.6, pad_top + PAD_H*0.5), (3.5, pad_top + 1.2))

annot(ax, "Cotton ring seat\n(∅8.5–11 mm, 1 mm deep)",
      (ABS_RI + (ABS_RO - ABS_RI)*0.5, abs_top - ABS_D*0.5),
      (4.5, abs_top - ABS_D - 0.8), ha="left")

annot(ax, "Convex crown\n(0.3 mm over ∅12 mm)",
      (DISC_R*0.55, OY + CROWN*0.3), (-3.0, OY - 0.9), ha="right")

annot(ax, "Graphene/Ag coating\n(skin-contact zone ∅10 mm)",
      (DISC_R*0.3, OY + coat_t/2), (-3.5, OY + 0.6), ha="right")

annot(ax, "Electrolyte channel\n(0.3 × 0.2 mm radial)",
      (DISC_R*0.4, OY - CH_D/2), (2.5, OY - 1.0))

annot(ax, "Hex dot texture\n(∅0.25 mm, 0.5 mm pitch)",
      (DISC_R*0.75, OY + DOT_H/2 + CROWN*0.1), (3.8, OY - 0.7))

annot(ax, "Fingernail grip\n(1.5 mm notch, lip absent)",
      (DISC_R + 0.1, OY + 0.4), (3.5, OY + 0.3))

ax.set_xlim(-8, 9)
ax.set_ylim(-1.5, 7)

# ═══════════════════════════════════════════════════════════════
# PANEL B — ASSEMBLY CROSS-SECTION (disc in electrode)
# ═══════════════════════════════════════════════════════════════
ax = axes[1]
ax.set_title("B — Assembly Cross-Section: Pad Disc in EpiScreen v2 Electrode",
             color="#EEEEEE", fontsize=10, pad=8, loc="left")

# Origin: electrode bottom face (skin side) at y=0
EY = 0   # electrode bottom

# ── Main electrode body (silicone) ───────────────────────────
# Outer wall cross-section
mirror_rect(ax, CAV_R, EY, EP_R - CAV_R, EP_BOT_H, C_ELECTRODE, C_ELEC_E, lw=1.0)
# Thin bottom wall under pad cavity
rect(ax, -CAV_R, EY, 2*CAV_R, 0.3, C_ELECTRODE, C_ELEC_E, lw=0.5, alpha=0.5)

# ── FR-4 seat ledge ──────────────────────────────────────────
fr4_y = EY + FR4_Z
mirror_rect(ax, SPIRAL_R, fr4_y, EP_R - SPIRAL_R - 0.1, FR4_T,
            "#78909C", "#37474F", lw=0.8)

# ── Copper spiral (schematic) ────────────────────────────────
sp_y = fr4_y + FR4_T
rect(ax, -SPIRAL_R, sp_y, 2*SPIRAL_R, SPIRAL_H, C_COPPER, "#E65100", lw=0.8)

# ── Impedance ring wire ──────────────────────────────────────
imp_y = EY + 0.8
for sign in [1, -1]:
    ax.add_patch(plt.Circle((sign * 14.0/2, imp_y), 0.3,
                             fc=C_IMP_RING, ec="#C62828", lw=0.8, zorder=6))

# ── Retention groove in electrode wall ──────────────────────
groove_y = EY + DISC_T - LIP_Z
for sign in [1, -1]:
    gx = sign * (CAV_R - GROOVE_DEP)
    gw = sign * GROOVE_DEP
    rect(ax, gx, groove_y, gw, GROOVE_W,
         "#80CBC4", "#004D40", lw=0.7, zorder=6)

# ── PAD DISC (inserted, disc bottom at y=EY+0) ───────────────
DY = EY   # disc bottom
disc_top = DY + DISC_T

# Disc body (two halves)
mirror_rect(ax, FLOW_R, DY, DISC_R - FLOW_R, DISC_T,
            C_DISC, C_DISC_E, lw=1.2, alpha=0.92, zorder=4)

# Crown curve
cx = np.linspace(-DISC_R, DISC_R, 120)
cy_base = DY + CROWN * (1 - (cx / DISC_R)**2)
ax.fill_between(cx, DY, cy_base, color=C_GRAPHENE, alpha=0.8, zorder=5)
ax.plot(cx, cy_base, color="#546E7A", lw=0.8, zorder=6)

# Graphene coat
ax.fill_between(cx, cy_base, cy_base + 0.06, color=C_GRAPHENE, alpha=0.95, zorder=6)

# Retention lip (snapped into groove)
lip_y_asm = DY + LIP_Z - LIP_W/2
for sign in [1, -1]:
    lx = sign * DISC_R
    lw_dir = sign * LIP_H
    rect(ax, lx, lip_y_asm, lw_dir, LIP_W, C_DISC_E, C_DISC_E, lw=0, zorder=7)

# Contact pad raised area
rect(ax, -PAD_R, disc_top, 2*PAD_R, PAD_H, C_COPPER, "#BF360C", lw=0.7, zorder=7)

# Cotton ring in seat
abs_y0 = disc_top - ABS_D
mirror_rect(ax, ABS_RI, abs_y0, ABS_RO - ABS_RI, ABS_D,
            C_COTTON, C_COTTON_E, lw=0.8, alpha=0.9, zorder=7)

# Electrolyte flow channel
rect(ax, -FLOW_R, DY, 2*FLOW_R, DISC_T + PAD_H + 0.5,
     C_ELECTRO, "#006064", lw=0, alpha=0.4, zorder=3)

# Electrolyte in reservoir (above FR-4)
res_y = fr4_y + FR4_T
rect(ax, -(EP_R - 0.5), res_y, 2*(EP_R - 0.5), 1.2,
     C_ELECTRO, "#006064", lw=0, alpha=0.25, zorder=2)

# ── Skin surface ─────────────────────────────────────────────
skin_y = EY - 0.5
rect(ax, -EP_R - 0.5, skin_y - 0.5, 2*(EP_R + 0.5), 0.5,
     C_SKIN, "#BCAAA4", lw=0.8, alpha=0.8, zorder=1)
ax.text(0, skin_y - 0.3, "Skin surface", color="#5D4037",
        fontsize=7, ha="center", va="center")

# Centreline
centerline(ax, 0, skin_y - 0.6, EY + EP_BOT_H + 1.0)

# Annotations
annot(ax, "Snap-fit lip\nengages groove", (DISC_R + LIP_H/2, lip_y_asm + LIP_W/2),
      (DISC_R + 2.2, lip_y_asm + 2.0))

annot(ax, "Contact pad on\ncopper spiral", (PAD_R*0.5, disc_top + PAD_H/2),
      (2.5, disc_top + 2.0))

annot(ax, "Cotton ring\n(user-replaceable)", (ABS_RI + 0.5, abs_y0 + ABS_D*0.5),
      (5.0, abs_y0 + 2.2))

annot(ax, "Flow hole aligns\nwith electrode pin\n(electrolyte path)",
      (FLOW_R, disc_top*0.5), (3.5, disc_top*0.5 + 1.0))

annot(ax, "Impedance ring\nwire (26 AWG)",
      (14.0/2, imp_y), (5.0, imp_y + 1.5))

annot(ax, "Convex skin surface\n+ graphene coating",
      (DISC_R*0.6, cy_base[80] + 0.05), (4.5, cy_base[80] - 1.0))

annot(ax, "FR-4 substrate", (SPIRAL_R + 0.5, fr4_y + FR4_T/2),
      (5.5, fr4_y - 0.8), ha="left")

annot(ax, "Copper spiral\n(EEG signal pick-up)",
      (SPIRAL_R*0.5, sp_y + SPIRAL_H/2), (-3.0, sp_y + 2.0), ha="right")

annot(ax, "Electrolyte reservoir\n(filled via fill port)",
      (EP_R*0.5, res_y + 0.6), (EP_R + 0.5, res_y + 1.5), ha="left")

ax.set_xlim(-14, 17)
ax.set_ylim(-1.5, 11)

# ── Figure title ─────────────────────────────────────────────
fig.suptitle("EpiScreen v2 — Removable Pad Disc: Design & Assembly",
             color="#EEEEEE", fontsize=13, fontweight="bold", y=0.98)

# ── Legend ───────────────────────────────────────────────────
legend_elements = [
    mpatches.Patch(fc=C_DISC,      ec=C_DISC_E,  label="Silicone pad disc"),
    mpatches.Patch(fc=C_ELECTRODE, ec=C_ELEC_E,  label="Main electrode body (silicone)"),
    mpatches.Patch(fc=C_COPPER,    ec="#E65100",  label="Copper spiral / contact pad"),
    mpatches.Patch(fc=C_COTTON,    ec=C_COTTON_E, label="Cotton/cellulose ring (replaceable)"),
    mpatches.Patch(fc=C_ELECTRO,   ec="#006064",  label="Electrolyte path"),
    mpatches.Patch(fc=C_GRAPHENE,  ec="none",     label="Graphene/Ag coating"),
    mpatches.Patch(fc=C_IMP_RING,  ec="#C62828",  label="Impedance ring wire (26 AWG)"),
    mpatches.Patch(fc=C_SKIN,      ec="#BCAAA4",  label="Skin surface"),
]
fig.legend(handles=legend_elements, loc="lower center", ncol=4,
           fontsize=7.5, framealpha=0.15, labelcolor="#EEEEEE",
           facecolor="#2A2A2A", edgecolor="#555555",
           bbox_to_anchor=(0.5, 0.005))

path = os.path.join(OUT, "pad_disc_cross_section.png")
fig.savefig(path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Saved → {path}  ({os.path.getsize(path)//1024} KB)")
plt.close()
