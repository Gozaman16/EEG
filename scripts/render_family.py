#!/usr/bin/env python3
"""
Assembly Family Photo — publication-quality 300 DPI PNG
Renders all EpiScreen system components in a "family photo" layout.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patches as mp
from matplotlib.patches import FancyArrowPatch, Arc, FancyBboxPatch, Circle, Wedge
from matplotlib.collections import PatchCollection
import matplotlib.patheffects as pe
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "renders")
os.makedirs(OUT, exist_ok=True)

# ── colour palette ─────────────────────────────────────────────────────────────
C = {
    "silicone":   (0.55, 0.78, 0.96, 0.85),
    "silicone_e": (0.25, 0.55, 0.82, 1.0),
    "fr4":        (0.18, 0.58, 0.18, 1.0),
    "copper":     (0.85, 0.55, 0.20, 1.0),
    "reservoir":  (0.98, 0.95, 0.20, 0.55),
    "graphene":   (0.10, 0.10, 0.12, 1.0),
    "mold":       (0.60, 0.62, 0.65, 0.55),
    "mold_e":     (0.35, 0.37, 0.40, 1.0),
    "channel":    (0.92, 0.15, 0.15, 1.0),
    "white":      (0.97, 0.97, 0.97, 1.0),
    "steel":      (0.78, 0.80, 0.85, 1.0),
    "band":       (0.25, 0.27, 0.32, 1.0),
    "band_e":     (0.10, 0.12, 0.18, 1.0),
    "coin":       (0.88, 0.76, 0.22, 1.0),
    "coin_e":     (0.65, 0.52, 0.08, 1.0),
    "bg":         (0.97, 0.97, 0.98, 1.0),
    "grid":       (0.88, 0.88, 0.90, 1.0),
    "text":       (0.10, 0.10, 0.15, 1.0),
    "accent":     (0.15, 0.35, 0.70, 1.0),
    "pin":        (0.12, 0.12, 0.14, 1.0),
}

def set_publication_style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.labelsize": 9,
        "axes.titlesize": 10,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "figure.facecolor": C["bg"],
        "axes.facecolor": C["bg"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.spines.bottom": False,
    })

# ═══════════════════════════════════════════════════════════════════════════════
# Drawing helpers — all in mm units, drawn as 2D front elevations
# ═══════════════════════════════════════════════════════════════════════════════

def draw_electrode_front(ax, cx, cy, od, h, fr4_z, fr4_d, fr4_t,
                          res_id, res_od, res_h, spiral_d,
                          bot_cav_d, bot_cav_h, label, pins=None,
                          pin_rad=0, pin_h=0):
    """Draw front elevation of a cylindrical electrode."""
    r = od / 2

    # Body fill
    body = mp.FancyBboxPatch(
        (cx - r, cy), 2*r, h,
        boxstyle="square,pad=0",
        facecolor=C["silicone"], edgecolor=C["silicone_e"], linewidth=1.2, zorder=3
    )
    ax.add_patch(body)

    # Bottom skin-contact recess (darker band)
    skin = mp.Rectangle((cx - bot_cav_d/2, cy - bot_cav_h), bot_cav_d, bot_cav_h,
                          facecolor=C["graphene"], edgecolor="none", zorder=4)
    ax.add_patch(skin)

    # FR-4 disk line
    fr4 = mp.Rectangle((cx - fr4_d/2, cy + fr4_z), fr4_d, fr4_t,
                         facecolor=C["fr4"], edgecolor=(0.1, 0.4, 0.1), linewidth=0.8, zorder=5)
    ax.add_patch(fr4)

    # Copper spiral (small disc below FR-4)
    sp = mp.Rectangle((cx - spiral_d/2, cy + fr4_z - 0.5), spiral_d, 0.5,
                        facecolor=C["copper"], edgecolor=(0.6, 0.3, 0.0), linewidth=0.6, zorder=5)
    ax.add_patch(sp)

    # Reservoir ring (hatched, semi-transparent)
    res_z = fr4_z + fr4_t
    res_inner_l = cx - res_id/2
    res_outer_l = cx - res_od/2
    # left wall of reservoir
    res_l = mp.Rectangle((cx - res_od/2, cy + res_z), (res_od - res_id)/2, res_h,
                           facecolor=C["reservoir"], edgecolor=(0.7, 0.7, 0), linewidth=0.6, zorder=4)
    res_r = mp.Rectangle((cx + res_id/2, cy + res_z), (res_od - res_id)/2, res_h,
                           facecolor=C["reservoir"], edgecolor=(0.7, 0.7, 0), linewidth=0.6, zorder=4)
    ax.add_patch(res_l)
    ax.add_patch(res_r)

    # Outer silhouette (edge lines)
    ax.plot([cx - r, cx - r], [cy, cy + h], color=C["silicone_e"], lw=1.5, zorder=6)
    ax.plot([cx + r, cx + r], [cy, cy + h], color=C["silicone_e"], lw=1.5, zorder=6)
    ax.plot([cx - r, cx + r], [cy + h, cy + h], color=C["silicone_e"], lw=1.5, zorder=6)

    # Pins for HairSite
    if pins and pin_h > 0:
        for px_off in [0] + [pin_rad * np.cos(np.radians(a)) for a in [0, 60, 120, 180, 240, 300]]:
            px = cx + px_off
            ax.plot([px, px], [cy - bot_cav_h - pin_h, cy - bot_cav_h],
                    color=C["pin"], lw=1.5, zorder=7,
                    solid_capstyle='round')

    # Cable exit notch hint (right side)
    notch = mp.Rectangle((cx + r - 0.2, cy + fr4_z), 3, h - fr4_z,
                           facecolor=C["bg"], edgecolor="none", zorder=7)
    ax.add_patch(notch)

    # Label below
    ax.text(cx, cy - bot_cav_h - (3 if not pins else pin_h + 2),
            label, ha='center', va='top',
            fontsize=8.5, fontweight='bold', color=C["text"], zorder=10)

    return cy + h   # top y


def draw_mounting_system(ax, cx, cy, label, kind="headband_adult"):
    """Draw simplified front elevation of mounting hardware."""
    if kind == "headband_adult":
        # Clip block
        bw, bh = 30, 12
        eb = mp.FancyBboxPatch((cx - bw/2, cy), bw, bh,
                                boxstyle="round,pad=0.5",
                                facecolor=C["band"], edgecolor=C["band_e"],
                                linewidth=1.2, zorder=3)
        ax.add_patch(eb)
        # Band stubs
        for dx in [-bw/2 - 15, bw/2]:
            band = mp.Rectangle((dx + (cx if dx < 0 else cx), cy + 3), 15, 2.5,
                                  facecolor=C["band"], edgecolor=C["band_e"], lw=0.8, zorder=3)
            ax.add_patch(band)
        # Electrode stub at top
        draw_electrode_front(ax, cx, cy + bh, 24, 6,
                              3, 19, 1.6, 13, 19, 1.5, 8, 12, 1, "", pins=None)
        top = cy + bh + 6
    elif kind == "headband_neo":
        bw, bh = 22, 9
        eb = mp.FancyBboxPatch((cx - bw/2, cy), bw, bh,
                                boxstyle="round,pad=0.4",
                                facecolor=C["band"], edgecolor=C["band_e"],
                                linewidth=1.2, zorder=3)
        ax.add_patch(eb)
        for dx in [-bw/2 - 10, bw/2]:
            band = mp.Rectangle((dx + (cx if dx < 0 else cx), cy + 2), 10, 2,
                                  facecolor=C["band"], edgecolor=C["band_e"], lw=0.8, zorder=3)
            ax.add_patch(band)
        draw_electrode_front(ax, cx, cy + bh, 15, 5,
                              2.5, 12, 1.0, 8.5, 12, 1.2, 5, 8, 0.8, "", pins=None)
        top = cy + bh + 5
    elif kind == "helmet":
        # Circular adapter + flange
        ad = 38; fh = 8
        flange = mp.Rectangle((cx - 25, cy), 50, fh,
                                facecolor=C["band"], edgecolor=C["band_e"], lw=1.2, zorder=3)
        adapter = mp.FancyBboxPatch((cx - ad/2, cy + fh), ad, 12,
                                     boxstyle="round,pad=1",
                                     facecolor=C["band"], edgecolor=C["band_e"],
                                     lw=1.2, zorder=3)
        ax.add_patch(flange)
        ax.add_patch(adapter)
        # Mounting bolt holes
        for bx in [-17, 17]:
            bolt = Circle((cx + bx, cy + 4), 1.7,
                           facecolor=C["bg"], edgecolor=C["band_e"], lw=0.8, zorder=5)
            ax.add_patch(bolt)
        # Electrode stub
        draw_electrode_front(ax, cx, cy + fh + 12, 24, 5,
                              3, 19, 1.6, 13, 19, 1.5, 8, 12, 1, "", pins=None)
        top = cy + fh + 17

    ax.text(cx, cy - 3, label, ha='center', va='top',
            fontsize=8.5, fontweight='bold', color=C["text"], zorder=10)
    return top


def draw_scale_bar(ax, x, y, length_mm=30):
    """Draw a labelled scale bar."""
    ax.annotate("", xy=(x + length_mm, y), xytext=(x, y),
                arrowprops=dict(arrowstyle="<->", color=C["text"], lw=1.0))
    ax.text(x + length_mm/2, y - 1.5, f"{length_mm} mm",
            ha='center', va='top', fontsize=7.5, color=C["text"])
    # Tick marks every 5 mm
    for t in range(0, length_mm + 1, 5):
        th = 1.5 if t % 10 == 0 else 0.8
        ax.plot([x + t, x + t], [y, y + th], color=C["text"], lw=0.6, zorder=5)


def draw_turkish_lira(ax, cx, cy):
    """Draw a 1 Turkish Lira coin (23 mm dia, front view)."""
    # Outer ring
    coin = Circle((cx, cy + 11.5), 11.5,
                   facecolor=C["coin"], edgecolor=C["coin_e"], linewidth=1.0, zorder=3)
    ax.add_patch(coin)
    # Inner ring
    inner = Circle((cx, cy + 11.5), 8,
                    facecolor=(0.92, 0.80, 0.28), edgecolor=C["coin_e"], linewidth=0.5, zorder=4)
    ax.add_patch(inner)
    ax.text(cx, cy + 11.5, "₺1", ha='center', va='center',
            fontsize=7, fontweight='bold', color=C["coin_e"], zorder=6)
    ax.text(cx, cy + 11.5 + 14, "1 Turkish\nLira (23 mm)",
            ha='center', va='bottom', fontsize=6.5, color=C["text"],
            style='italic', zorder=6)


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — Family Photo
# ═══════════════════════════════════════════════════════════════════════════════

set_publication_style()

fig, ax = plt.subplots(figsize=(14, 9))
fig.patch.set_facecolor(C["bg"])
ax.set_facecolor(C["bg"])
ax.set_aspect('equal')
ax.axis('off')

# ── Panel title and subtitle ───────────────────────────────────────────────────
ax.text(0.5, 0.985, "EpiScreen Electrode System — Component Overview",
        transform=ax.transAxes, ha='center', va='top',
        fontsize=13, fontweight='bold', color=C["text"])
ax.text(0.5, 0.965, "All dimensions in mm  •  Designed for resin 3D-printed silicone casting molds",
        transform=ax.transAxes, ha='center', va='top',
        fontsize=8, color=(0.4, 0.4, 0.45))

# Row labels (section headers)
ax.text(0.5, 0.935, "─── Electrode Bodies ───",
        transform=ax.transAxes, ha='center', va='top',
        fontsize=9, color=C["accent"], fontweight='bold')

# coordinate bounds (mm space): x from -90 to +90, y from -40 to +90
ax.set_xlim(-90, 90)
ax.set_ylim(-42, 92)

# ── TOP ROW: three electrode types ─────────────────────────────────────────────
# EpiScreen (24 mm)
draw_electrode_front(ax, cx=-55, cy=30, od=24, h=10,
                     fr4_z=3, fr4_d=19, fr4_t=1.6,
                     res_id=13, res_od=19, res_h=1.5,
                     spiral_d=8, bot_cav_d=12, bot_cav_h=1.0,
                     label="EpiScreen\n(24 mm)")

# NeoGuard (15 mm)
draw_electrode_front(ax, cx=0, cy=30, od=15, h=8,
                     fr4_z=2.5, fr4_d=12, fr4_t=1.0,
                     res_id=8.5, res_od=12, res_h=1.2,
                     spiral_d=5, bot_cav_d=8, bot_cav_h=0.8,
                     label="NeoGuard\n(15 mm)")

# HairSite (24 mm + pins)
draw_electrode_front(ax, cx=55, cy=30, od=24, h=12,
                     fr4_z=3, fr4_d=19, fr4_t=1.6,
                     res_id=13, res_od=19, res_h=1.5,
                     spiral_d=8, bot_cav_d=12, bot_cav_h=1.0,
                     label="HairSite\n(24 mm + 7 pins)",
                     pins=True, pin_rad=6, pin_h=8)

# Turkish Lira coin (size reference next to NeoGuard)
draw_turkish_lira(ax, cx=28, cy=29)

# Scale bar
draw_scale_bar(ax, x=-89, y=28, length_mm=30)

# ── Dimension callouts for EpiScreen ──────────────────────────────────────────
# Outer diameter arrow
ax.annotate("", xy=(-55 + 12, 20), xytext=(-55 - 12, 20),
            arrowprops=dict(arrowstyle="<->", color=C["accent"], lw=0.9))
ax.text(-55, 18.5, "Ø 24", ha='center', fontsize=7, color=C["accent"])

# Height arrow
ax.annotate("", xy=(-55 - 15, 30 + 10), xytext=(-55 - 15, 30),
            arrowprops=dict(arrowstyle="<->", color=C["accent"], lw=0.9))
ax.text(-55 - 16, 35, "10", ha='right', fontsize=7, color=C["accent"])

# NeoGuard diameter
ax.annotate("", xy=(0 + 7.5, 21), xytext=(0 - 7.5, 21),
            arrowprops=dict(arrowstyle="<->", color=C["accent"], lw=0.9))
ax.text(0, 19.8, "Ø 15", ha='center', fontsize=7, color=C["accent"])

# HairSite pin length
ax.annotate("", xy=(55 + 14, 21), xytext=(55 + 14, 29),
            arrowprops=dict(arrowstyle="<->", color=C["channel"], lw=0.9))
ax.text(55 + 15.5, 25, "8 mm\npins", ha='left', fontsize=6.5, color=C["channel"])

# ── Section divider ────────────────────────────────────────────────────────────
ax.plot([-88, 88], [22, 22], color=C["grid"], lw=0.8, ls='--', zorder=1)
ax.text(0, 21, "─── Mounting Systems ───",
        ha='center', va='top', fontsize=9, color=C["accent"], fontweight='bold')

# ── BOTTOM ROW: mounting systems ───────────────────────────────────────────────
draw_mounting_system(ax, cx=-55, cy=-38, label="Adult Headband\n(22 mm band)", kind="headband_adult")
draw_mounting_system(ax, cx=0,   cy=-34, label="Neonatal Headband\n(16 mm band)", kind="headband_neo")
draw_mounting_system(ax, cx=55,  cy=-38, label="ImpactGuard\nHelmet Adapter", kind="helmet")

# ── Legend ─────────────────────────────────────────────────────────────────────
legend_x, legend_y = 68, 88
legend_items = [
    (C["silicone"],  C["silicone_e"],  "Silicone body"),
    (C["fr4"],       C["fr4"],         "FR-4 PCB disk"),
    (C["copper"],    C["copper"],      "Copper spiral"),
    (C["reservoir"], (0.7,0.7,0),      "Reservoir ring"),
    (C["graphene"],  C["graphene"],    "Graphene coating"),
    (C["band"],      C["band_e"],      "Mount body (resin)"),
]
ax.text(legend_x, legend_y, "Legend", ha='left', fontsize=8,
        fontweight='bold', color=C["text"])
for i, (fc, ec, label) in enumerate(legend_items):
    ry = legend_y - 3.5 - i * 4.5
    rect = mp.Rectangle((legend_x, ry), 3.5, 3, facecolor=fc,
                          edgecolor=ec, linewidth=0.7, zorder=5)
    ax.add_patch(rect)
    ax.text(legend_x + 5, ry + 1.5, label, va='center', fontsize=7.5, color=C["text"])

# ── Footer ─────────────────────────────────────────────────────────────────────
ax.text(0.5, 0.01, "EpiScreen EEG Electrode System  •  ISEF 2026  •  All units: mm",
        transform=ax.transAxes, ha='center', va='bottom',
        fontsize=7, color=(0.5, 0.5, 0.55), style='italic')

plt.tight_layout(pad=0.3)
out_path = os.path.join(OUT, "assembly_family.png")
fig.savefig(out_path, dpi=300, bbox_inches='tight',
            facecolor=C["bg"], edgecolor='none')
plt.close()
print(f"Saved: {out_path}")
