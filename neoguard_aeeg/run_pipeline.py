#!/usr/bin/env python3
"""
NeoGuard aEEG — Full pipeline runner.

Generates synthetic neonatal EEG, runs the aEEG analysis,
saves CSV outputs + classification log + all figures.
"""

import sys
from pathlib import Path

# Ensure package is importable when run from its own directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from neoguard_aeeg import (
    generate_synthetic_eeg, analyse_aeeg, save_results, FS
)
from visualize import generate_all_figures

OUT_DIR = Path(__file__).resolve().parent


def main():
    print("=== NeoGuard aEEG Pipeline ===")

    # 1. Generate synthetic neonatal EEG (4 hours)
    print("[1/4] Generating 4-hour synthetic neonatal EEG ...")
    raw_eeg, events = generate_synthetic_eeg(total_hours=4.0, fs=FS, seed=42)
    print(f"      {len(raw_eeg)} samples ({len(raw_eeg)/FS/3600:.1f} h)")

    # 2. Run aEEG analysis
    print("[2/4] Running aEEG analysis (filter → envelope → margins) ...")
    result = analyse_aeeg(raw_eeg, fs=FS)
    print(f"      Envelope length: {len(result.envelope_1hz)} samples (1 Hz)")
    print(f"      Background segments: {len(result.classifications)}")
    print(f"      Seizure alerts: {len(result.seizure_alerts)}")

    for i, (s, e) in enumerate(result.seizure_alerts):
        print(f"        Seizure {i+1}: {s/60:.1f} – {e/60:.1f} min")

    # 3. Save CSV outputs
    print(f"[3/4] Saving results to {OUT_DIR}/ ...")
    save_results(result, raw_eeg, events, OUT_DIR)

    # 4. Generate figures
    print("[4/4] Generating figures (300 DPI PNG) ...")
    generate_all_figures(raw_eeg, FS, result, OUT_DIR)

    print("\n=== Done ===")
    print(f"Output directory: {OUT_DIR}")
    print("Files:")
    for f in sorted(OUT_DIR.glob("*")):
        if f.suffix in (".csv", ".png"):
            size_kb = f.stat().st_size / 1024
            print(f"  {f.name:40s} {size_kb:8.1f} KB")


if __name__ == "__main__":
    main()
