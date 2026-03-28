#!/usr/bin/env python3
"""
Exploded Assembly View — publication-quality 300 DPI PNG
Shows all EpiScreen electrode components separated vertically
with assembly arrows and callout labels.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mp
from matplotlib.patches import FancyArrowPatch
import matplotlib.patheffects as pe
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "renders")
os.makedirs(OUT, exist_ok=True)

C = {
    "silicone":   (0.55, 0.78, 0.96, 0.80),
    "silicone_e": (0.20, 0.50, 0.80, 1.0),
    "fr4":        (0.18, 0.58, 0.18, 1.0),
    "fr4_e":      (0.08, 0.38, 0.08, 1.0),
    "copper":     (0.85, 0.55, 0.20, 1.0),
    "copper_e":   (0.60, 0.32, 0.05, 1.0),
    "reservoir":  (0.98, 0.95, 0.10, 0.55),
    "reservoir_e":(0.75, 0.72, 0.00, 1.0),
    "graphene":   (0.10, 0.10, 0.12, 1.0),
    "mold":       (0.62, 0.64, 0.68, 0.50),
    "mold_e":     (0.30, 0.32, 0.36, 1.0),
    "channel":    (0.92, 0.12, 0.12, 1.0),
    "white":      (0.97, 0.97, 0.97, 1.0),
    "white_e":    (0.70, 0.70, 0.72, 1.0),
    "arrow":      (0.15, 0.30, 0.72, 1.0),
    "text":       (0.08, 0.08, 0.12, 1.0),
    "bg":         (0.97, 0.97, 0.98, 1.0),
    "grid":       (0.88, 0.88, 0.90, 1.0),
    "accent":     (0.15, 0.35, 0.70, 1.0),
    "dim":        (0.50, 0.50, 0.55, 1.0),
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "figure.dpi": 300,
    "savefig.dpi": 300,
})

# ── Electrode parameters ──────────────────────────────────────────────────────
OD = 24.0; R = OD/2
WALL = 1.5; MOLD_R = 16.0
GAP = 14          # vertical gap between exploded components (mm in drawing units)
CX = 0            # centre X

# Component base Z positions (exploded, in drawing mm)
components = [
    # (z_base, height, label_right, label_left)
    (0,    WALL + 5,  "Bottom Mold",       "Resin (SLA/DLP)\nOD 32 mm"),
    (25,   0.5,       "Copper Spiral",     "Cu trace, 8 mm Ø\ngraphene-coated"),
    (40,   5,         "Silicone Body\n(lower half)", "Shore 20A\nlight-blue semi-transparent"),
    (58,   1.6,       "FR-4 Disk",         "19 mm Ø × 1.6 mm\nPCB green"),
    (72,   1.5,       "Emici Halka\n(absorbent ring)", "White poly sponge\nID 13 / OD 18 mm"),
    (86,   1.5,       "Reservoir Void",    "Ring channel\nID 13 / OD 19 mm"),
    (100,  4,         "Microchannel\nWires (×3)", "0.5 mm steel wire\n30-45° angle"),
    (116,  5,         "Silicone Body\n(upper half)", "Shore 20A\nwith cable notch"),
    (132,  WALL + 6,  "Top Mold",          "Resin (SLA/DLP)\nwith pour hole + vents"),
]

fig, ax = plt.subplots(figsize=(9, 16))
fig.patch.set_facecolor(C["bg"])
ax.set_facecolor(C["bg"])
ax.set_aspect('equal')
ax.axis('off')

ax.set_xlim(-55, 55)
ax.set_ylim(-5, 160)

# Title
ax.text(0, 157, "EpiScreen Electrode — Exploded Assembly View",
        ha='center', va='top', fontsize=11, fontweight='bold', color=C["text"])
ax.text(0, 154.5, "All components shown in assembly order (bottom → top)",
        ha='center', va='top', fontsize=7.5, color=C["dim"])

# ── Draw each layer ───────────────────────────────────────────────────────────

def draw_mold_half(ax, cx, z, h, is_top=False):
    """Draw a mold half (grey, with wall visible)."""
    r_inner = R
    r_outer = MOLD_R
    # Outer rectangle
    outer = mp.FancyBboxPatch((cx - r_outer, z), r_outer*2, h,
                               boxstyle="square,pad=0",
                               facecolor=C["mold"], edgecolor=C["mold_e"],
                               linewidth=1.2, zorder=3)
    ax.add_patch(outer)
    # Inner cavity cutout (white/bg)
    cav_y = z + WALL if not is_top else z
    cav_h = h - WALL if not is_top else h - WALL
    inner = mp.Rectangle((cx - r_inner, cav_y), r_inner*2, cav_h + 0.1,
                           facecolor=C["bg"], edgecolor="none", zorder=4)
    ax.add_patch(inner)

    if is_top:
        # Pour hole at top centre
        pour = mp.Rectangle((cx - 3, z + h - 5), 6, 5.1,
                              facecolor=C["bg"], edgecolor="none", zorder=5)
        ax.add_patch(pour)
        pour_label = mp.FancyArrow(cx, z + h + 0.5, 0, 1.5, width=0.3,
                                    head_width=1.2, head_length=0.8,
                                    facecolor=C["accent"], zorder=6)
        ax.add_patch(pour_label)
        ax.text(cx + 1.5, z + h + 2.5, "Pour hole\n(Ø 6 mm)",
                ha='left', fontsize=6.5, color=C["accent"], va='bottom')

        # Vent holes
        for vx in [-12, 12]:
            vp = mp.Rectangle((cx + vx - 0.5, z + h - 3), 1, 3.1,
                                facecolor=C["bg"], edgecolor="none", zorder=5)
            ax.add_patch(vp)
        ax.text(cx - 18, z + h - 1.5, "Vents\n(Ø 1 mm ×2)",
                ha='right', fontsize=6.5, color=C["dim"], va='center')

        # Alignment pins (male, project downward)
        for px in [-13, 13]:
            pin = mp.Rectangle((cx + px - PIN_D/2, z - PIN_H), PIN_D, PIN_H + 0.1,
                                 facecolor=C["mold_e"], edgecolor="none", zorder=5)
            ax.add_patch(pin)
    else:
        # Alignment pin holes (female)
        for px in [-13, 13]:
            ph = mp.Rectangle((cx + px - PIN_D/2 - 0.15, z + h - PIN_H - 0.1),
                                PIN_D + 0.3, PIN_H + 0.2,
                                facecolor=C["bg"], edgecolor=C["mold_e"],
                                linewidth=0.6, zorder=5)
            ax.add_patch(ph)

        # Spiral platform (raised bump inside cavity)
        plat = mp.Rectangle((cx - 4, z + WALL), 8, 0.8,
                              facecolor=C["mold_e"], edgecolor="none", zorder=5)
        ax.add_patch(plat)

    # Cable exit notch (right side)
    notch = mp.Rectangle((cx + r_outer - 3.5, z + (3 if not is_top else 0)), 3.6, h,
                           facecolor=C["bg"], edgecolor="none", zorder=5)
    ax.add_patch(notch)

PIN_D = 2.0; PIN_H = 3.0

z_idx = 0
for (z, h, label_r, label_l) in components:
    layer_c = z_idx
    if z_idx == 0:   # Bottom mold
        draw_mold_half(ax, CX, z, h, is_top=False)
    elif z_idx == 1: # Copper spiral
        sp = mp.Rectangle((CX - 4, z), 8, h,
                           facecolor=C["copper"], edgecolor=C["copper_e"],
                           linewidth=0.8, zorder=3)
        ax.add_patch(sp)
        # Spiral trace hint
        for r in np.arange(0.8, 3.8, 0.7):
            arc = mp.Arc((CX, z + h/2), r*2, r*2, angle=0, theta1=20, theta2=340,
                          color=C["copper_e"], linewidth=0.4, zorder=4)
            ax.add_patch(arc)
    elif z_idx == 2: # Silicone lower
        body = mp.Rectangle((CX - R, z), OD, h,
                              facecolor=C["silicone"], edgecolor=C["silicone_e"],
                              linewidth=1.1, zorder=3)
        ax.add_patch(body)
        # Skin-contact bottom
        skin = mp.Rectangle((CX - 6, z - 1), 12, 1.1,
                              facecolor=C["graphene"], edgecolor="none", zorder=4)
        ax.add_patch(skin)
        # Micro-texture hint
        for rx in np.arange(-5.5, 5.5, 0.5):
            ax.plot([CX + rx, CX + rx], [z - 1, z - 0.7],
                    color=(0.3, 0.3, 0.3), lw=0.3, zorder=5, alpha=0.6)
    elif z_idx == 3: # FR-4
        fr4 = mp.Rectangle((CX - 9.5, z), 19, h,
                             facecolor=C["fr4"], edgecolor=C["fr4_e"],
                             linewidth=0.9, zorder=3)
        ax.add_patch(fr4)
        # Copper trace rings
        for r in [2.5, 4.5, 6.5, 8.0]:
            arc = mp.Arc((CX, z + h/2), r*2, r*2, angle=0, theta1=10, theta2=350,
                          color=C["copper"], linewidth=0.5, zorder=4)
            ax.add_patch(arc)
    elif z_idx == 4: # Emici halka
        ring_o = mp.Rectangle((CX - 9, z), 18, h,
                                facecolor=C["white"], edgecolor=C["white_e"],
                                linewidth=0.8, zorder=3)
        ring_i = mp.Rectangle((CX - 6.5, z - 0.1), 13, h + 0.2,
                                facecolor=C["bg"], edgecolor="none", zorder=4)
        ax.add_patch(ring_o)
        ax.add_patch(ring_i)
    elif z_idx == 5: # Reservoir void
        res_o = mp.Rectangle((CX - 9.5, z), 19, h,
                               facecolor=C["reservoir"], edgecolor=C["reservoir_e"],
                               linewidth=0.8, zorder=3, linestyle='--')
        res_i = mp.Rectangle((CX - 6.5, z - 0.1), 13, h + 0.2,
                               facecolor=C["bg"], edgecolor="none", zorder=4)
        ax.add_patch(res_o)
        ax.add_patch(res_i)
    elif z_idx == 6: # Microchannel wires
        for offset_x in [-8, 0, 8]:
            wire = mp.FancyArrow(CX + offset_x, z, 3, h + 1.5,
                                  width=0.4, head_width=0.9, head_length=0.8,
                                  facecolor=C["channel"], edgecolor="none", zorder=3)
            ax.add_patch(wire)
        ax.text(CX - 20, z + h/2, "Steel wire\n(Ø 0.5 mm)",
                ha='right', fontsize=6.5, color=C["channel"], va='center')
    elif z_idx == 7: # Silicone upper
        body = mp.Rectangle((CX - R, z), OD, h,
                              facecolor=C["silicone"], edgecolor=C["silicone_e"],
                              linewidth=1.1, zorder=3)
        ax.add_patch(body)
        # Cable notch
        notch = mp.Rectangle((CX + R - 0.5, z + 3), 3.5, h - 3,
                               facecolor=C["bg"], edgecolor="none", zorder=4)
        ax.add_patch(notch)
    elif z_idx == 8: # Top mold
        draw_mold_half(ax, CX, z, h, is_top=True)
        # Reservoir ring protrusion (downward bump on top mold inner face)
        res_ring_o = mp.Rectangle((CX - 9.5, z + WALL - 1.6), 19, 1.6,
                                   facecolor=C["mold_e"], edgecolor="none", zorder=5)
        res_ring_i = mp.Rectangle((CX - 6.5, z + WALL - 1.7), 13, 1.8,
                                   facecolor=C["bg"], edgecolor="none", zorder=6)
        ax.add_patch(res_ring_o)
        ax.add_patch(res_ring_i)
        ax.text(CX - 20, z + WALL - 0.8, "Reservoir\nprotrusion",
                ha='right', fontsize=6.5, color=C["dim"], va='center')

    # ── Assembly arrow (upward, between components) ───────────────────────────
    if z_idx < len(components) - 1:
        next_z = components[z_idx + 1][0]
        gap_mid = z + h + (next_z - z - h) / 2
        if next_z - z - h > 3:
            arr = mp.FancyArrow(CX + R + 5, z + h + 0.5,
                                 0, next_z - z - h - 3,
                                 width=0.4, head_width=2.0, head_length=1.5,
                                 facecolor=C["arrow"], edgecolor="none", zorder=6)
            ax.add_patch(arr)

    # ── Right label (component name) ──────────────────────────────────────────
    label_z = z + h / 2
    ax.annotate(label_r,
                xy=(CX + R, label_z), xytext=(CX + R + 8, label_z),
                ha='left', va='center', fontsize=7.5,
                fontweight='bold', color=C["text"],
                arrowprops=dict(arrowstyle="-", color=C["grid"], lw=0.7))

    # ── Left label (material/spec) ─────────────────────────────────────────────
    ax.annotate(label_l,
                xy=(CX - R, label_z), xytext=(CX - R - 8, label_z),
                ha='right', va='center', fontsize=6.5,
                color=C["dim"],
                arrowprops=dict(arrowstyle="-", color=C["grid"], lw=0.5))

    z_idx += 1

# ── Parting line marker ────────────────────────────────────────────────────────
part_z = components[7][0] - 1   # between silicone top and top mold
ax.plot([-MOLD_R - 5, MOLD_R + 5], [part_z, part_z],
        color=C["accent"], lw=1.0, ls=':', zorder=7)
ax.text(MOLD_R + 6, part_z, "Parting\nline", ha='left', va='center',
        fontsize=6.5, color=C["accent"])

# ── Dimension callout ─────────────────────────────────────────────────────────
ax.annotate("", xy=(CX - R - 22, components[8][0] + components[8][1]),
            xytext=(CX - R - 22, components[0][0]),
            arrowprops=dict(arrowstyle="<->", color=C["accent"], lw=0.9))
total_h = components[8][0] + components[8][1] - components[0][0]
mid_h = (components[8][0] + components[8][1] + components[0][0]) / 2
ax.text(CX - R - 24, mid_h, f"Exploded\nview\n(~{total_h:.0f} mm\ntotal)",
        ha='right', va='center', fontsize=6.5, color=C["accent"])

# ── Footer ────────────────────────────────────────────────────────────────────
ax.text(0, -3.5,
        "EpiScreen EEG Electrode System  •  ISEF 2026  •  "
        "Electrode assembled height: 10 mm, Mold total: 17 mm",
        ha='center', va='top', fontsize=6.5, color=C["dim"], style='italic')

plt.tight_layout(pad=0.3)
out_path = os.path.join(OUT, "assembly_exploded.png")
fig.savefig(out_path, dpi=300, bbox_inches='tight',
            facecolor=C["bg"], edgecolor='none')
plt.close()
print(f"Saved: {out_path}")
