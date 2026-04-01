"""
NeoGuard aEEG — Visualization module.

Generates four publication-quality figures (300 DPI, PNG):
  Fig 1: Raw neonatal EEG (30-second example)
  Fig 2: Full 4-hour aEEG trend with margins & classification bands
  Fig 3: Zoomed seizure event (raw EEG above, aEEG below)
  Fig 4: Background classification pie chart
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
from pathlib import Path

from neoguard_aeeg import AEEGResult, FS

# ─── Colour map for background classes ───────────────────────────────────────
CLASS_COLORS = {
    "CNV":  "#4CAF50",   # green
    "DNV":  "#FFC107",   # yellow/amber
    "BS":   "#FF9800",   # orange
    "LV":   "#F44336",   # red
    "FT":   "#B71C1C",   # dark red
}

DPI = 300


def _hours_axis(sec: np.ndarray) -> np.ndarray:
    return sec / 3600.0


# ─── Fig 1: Raw EEG 30-second snippet ────────────────────────────────────────
def plot_raw_eeg(raw_eeg: np.ndarray, fs: int, out_dir: Path,
                 start_sec: float = 0, duration_sec: float = 30):
    i0 = int(start_sec * fs)
    i1 = int((start_sec + duration_sec) * fs)
    segment = raw_eeg[i0:i1]
    t = np.arange(len(segment)) / fs + start_sec

    fig, ax = plt.subplots(figsize=(14, 3.5))
    ax.plot(t, segment, linewidth=0.4, color="#1565C0")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude (µV)")
    ax.set_title("Fig 1 — Raw Neonatal EEG (30-second segment)")
    ax.set_xlim(t[0], t[-1])
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "fig1_raw_eeg.png", dpi=DPI)
    plt.close(fig)


# ─── Fig 2: Full aEEG trend ──────────────────────────────────────────────────
def plot_aeeg_trend(result: AEEGResult, out_dir: Path):
    hours = _hours_axis(result.time_sec)

    fig, ax = plt.subplots(figsize=(16, 5))

    # Background classification colour bands
    for start_s, end_s, label in result.classifications:
        color = CLASS_COLORS.get(label, "#EEEEEE")
        ax.axvspan(start_s / 3600, end_s / 3600,
                   alpha=0.20, color=color, linewidth=0)

    # Upper / lower margins (filled band)
    ax.fill_between(hours, result.lower_margin, result.upper_margin,
                    alpha=0.35, color="#1565C0", label="aEEG band")
    ax.plot(hours, result.upper_margin, linewidth=0.7, color="#0D47A1",
            label="Upper margin (P90)")
    ax.plot(hours, result.lower_margin, linewidth=0.7, color="#42A5F5",
            label="Lower margin (P10)")

    # Seizure markers
    for s, e in result.seizure_alerts:
        mid = (s + e) / 2 / 3600
        ax.plot(mid, 100, marker="v", color="red", markersize=10,
                zorder=5)
        ax.axvspan(s / 3600, e / 3600, alpha=0.25, color="red",
                   linewidth=0)

    # Semi-log y-axis 1–100 µV
    ax.set_yscale("log")
    ax.set_ylim(1, 100)
    ax.set_yticks([1, 2, 5, 10, 20, 50, 100])
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("Amplitude (µV, log scale)")
    ax.set_title("Fig 2 — 4-Hour aEEG Trend with Background Classification")
    ax.set_xlim(0, hours[-1])
    ax.grid(True, alpha=0.3, which="both")

    # Legend for classification colours
    patches = [mpatches.Patch(color=CLASS_COLORS[k], alpha=0.5, label=k)
               for k in ("CNV", "DNV", "BS", "LV", "FT")]
    patches.append(mpatches.Patch(color="red", alpha=0.4, label="Seizure"))
    ax.legend(handles=patches, loc="upper right", fontsize=8, ncol=3)

    fig.tight_layout()
    fig.savefig(out_dir / "fig2_aeeg_trend.png", dpi=DPI)
    plt.close(fig)


# ─── Fig 3: Zoomed seizure ───────────────────────────────────────────────────
def plot_seizure_zoom(raw_eeg: np.ndarray, fs: int,
                      result: AEEGResult, out_dir: Path,
                      seizure_idx: int = 0, pad_sec: int = 60):
    if not result.seizure_alerts:
        return
    s, e = result.seizure_alerts[min(seizure_idx, len(result.seizure_alerts) - 1)]

    # Raw EEG window
    raw_start = max(0, (s - pad_sec) * fs)
    raw_end = min(len(raw_eeg), (e + pad_sec) * fs)
    raw_seg = raw_eeg[int(raw_start):int(raw_end)]
    t_raw = np.arange(len(raw_seg)) / fs + (s - pad_sec)

    # aEEG window
    aeeg_start = max(0, s - pad_sec)
    aeeg_end = min(len(result.envelope_1hz), e + pad_sec)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7),
                                    height_ratios=[1, 1])

    # Top: raw EEG
    ax1.plot(t_raw, raw_seg, linewidth=0.3, color="#1565C0")
    ax1.axvspan(s, e, alpha=0.2, color="red", label="Seizure")
    ax1.set_ylabel("Amplitude (µV)")
    ax1.set_title(f"Fig 3 — Seizure Event (raw EEG & aEEG) at "
                  f"{s/60:.1f}–{e/60:.1f} min")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)

    # Bottom: aEEG trend
    t_aeeg = result.time_sec[aeeg_start:aeeg_end]
    ax2.fill_between(t_aeeg,
                     result.lower_margin[aeeg_start:aeeg_end],
                     result.upper_margin[aeeg_start:aeeg_end],
                     alpha=0.35, color="#1565C0")
    ax2.plot(t_aeeg, result.upper_margin[aeeg_start:aeeg_end],
             linewidth=0.8, color="#0D47A1")
    ax2.plot(t_aeeg, result.lower_margin[aeeg_start:aeeg_end],
             linewidth=0.8, color="#42A5F5")
    ax2.axvspan(s, e, alpha=0.2, color="red")
    ax2.set_yscale("log")
    ax2.set_ylim(1, 100)
    ax2.set_yticks([1, 2, 5, 10, 20, 50, 100])
    ax2.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Amplitude (µV, log)")
    ax2.grid(True, alpha=0.3, which="both")

    fig.tight_layout()
    fig.savefig(out_dir / "fig3_seizure_zoom.png", dpi=DPI)
    plt.close(fig)


# ─── Fig 4: Classification pie chart ─────────────────────────────────────────
def plot_classification_pie(result: AEEGResult, out_dir: Path):
    durations = {}
    for s, e, label in result.classifications:
        durations[label] = durations.get(label, 0) + (e - s)

    # Add seizure time
    seizure_total = sum(e - s for s, e in result.seizure_alerts)
    if seizure_total > 0:
        durations["SEIZURE"] = seizure_total

    labels = list(durations.keys())
    sizes = list(durations.values())
    color_map = {**CLASS_COLORS, "SEIZURE": "#F44336"}
    colors = [color_map.get(l, "#999999") for l in labels]

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct="%1.1f%%",
        startangle=140, pctdistance=0.8)
    for t in autotexts:
        t.set_fontsize(9)
    ax.set_title("Fig 4 — aEEG Background Classification Summary")
    fig.tight_layout()
    fig.savefig(out_dir / "fig4_classification_pie.png", dpi=DPI)
    plt.close(fig)


# ─── Generate all figures ────────────────────────────────────────────────────
def generate_all_figures(raw_eeg: np.ndarray, fs: int,
                         result: AEEGResult, out_dir: str | Path):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    plot_raw_eeg(raw_eeg, fs, out, start_sec=100, duration_sec=30)
    plot_aeeg_trend(result, out)
    plot_seizure_zoom(raw_eeg, fs, result, out, seizure_idx=0)
    plot_classification_pie(result, out)
    print(f"All figures saved to {out}/")
