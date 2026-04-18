"""
NeoGuard aEEG â€” Amplitude-Integrated EEG for Neonatal Seizure Monitoring

Pure signal-processing pipeline (no ML):
  1. Bandpass filter 2â€“15 Hz (4th-order Butterworth)
  2. Rectify (absolute value)
  3. Envelope detection (Hilbert transform)
  4. Downsample to 1 Hz
  5. Compute upper/lower margins (90th/10th percentile in 60-s windows)
  6. Rule-based background classification & seizure detection
"""

import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt, hilbert, decimate
from pathlib import Path
from dataclasses import dataclass

# â”€â”€â”€ Constants â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
FS = 256          # sampling rate (Hz)
BAND = (2, 15)    # aEEG bandpass
BUTTER_ORDER = 4
ENVELOPE_WINDOW_SEC = 0.5
DOWNSAMPLE_TARGET = 1  # Hz
MARGIN_WINDOW_SEC = 60
SEIZURE_NARROW_UV = 2.0
SEIZURE_RISE_UV = 10.0
SEIZURE_DURATION_SEC = 30


# â”€â”€â”€ Data classes â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@dataclass
class AEEGResult:
    """Container for the full aEEG analysis output."""
    time_sec: np.ndarray          # time axis (1 Hz)
    envelope_1hz: np.ndarray      # aEEG envelope downsampled to 1 Hz (ÂµV)
    upper_margin: np.ndarray      # 90th percentile per 60-s window
    lower_margin: np.ndarray      # 10th percentile per 60-s window
    classifications: list         # list of (start_sec, end_sec, label)
    seizure_alerts: list          # list of (start_sec, end_sec)


# â”€â”€â”€ 1. Bandpass filter â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def bandpass_filter(signal: np.ndarray, fs: int = FS,
                    low: float = BAND[0], high: float = BAND[1],
                    order: int = BUTTER_ORDER) -> np.ndarray:
    sos = butter(order, [low, high], btype="band", fs=fs, output="sos")
    # Use interpolation to handle NaNs to avoid step artifacts
    clean = pd.Series(signal).interpolate(limit_direction='both').bfill().ffill().values
    return sosfiltfilt(sos, clean)


# â”€â”€â”€ 2â€“4. Envelope & downsample â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def compute_envelope(signal: np.ndarray, fs: int = FS) -> np.ndarray:
    """Rectify â†’ Hilbert envelope â†’ downsample to 1 Hz."""
    rectified = np.abs(signal)
    analytic = hilbert(rectified)
    envelope = np.abs(analytic)

    # Moving-average smoothing (0.5 s window) before downsampling
    win = int(fs * ENVELOPE_WINDOW_SEC)
    kernel = np.ones(win) / win
    envelope = np.convolve(envelope, kernel, mode="same")

    # Downsample: fs â†’ 1 Hz
    factor = int(fs / DOWNSAMPLE_TARGET)
    envelope_1hz = decimate(envelope, factor, zero_phase=True)
    return envelope_1hz


# â”€â”€â”€ 5. Upper / lower margins â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def compute_margins(envelope_1hz: np.ndarray,
                    window_sec: int = MARGIN_WINDOW_SEC):
    n = len(envelope_1hz)
    upper = np.full(n, np.nan)
    lower = np.full(n, np.nan)
    half = window_sec // 2

    for i in range(n):
        start = max(0, i - half)
        end = min(n, i + half)
        chunk = envelope_1hz[start:end]
        upper[i] = np.percentile(chunk, 90)
        lower[i] = np.percentile(chunk, 10)

    return upper, lower


# â”€â”€â”€ 6. Background classification â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_LABELS = ("CNV", "DNV", "BS", "LV", "FT")

def classify_window(upper_val: float, lower_val: float,
                    bandwidth: float) -> str:
    if upper_val < 5 and lower_val < 5:
        return "FT"
    if upper_val < 10:
        return "LV"
    if lower_val < 5 and upper_val > 25:
        return "BS"
    if lower_val < 5 and upper_val > 10:
        return "DNV"
    if lower_val > 5 and upper_val > 10:
        return "CNV"
    return "DNV"  # fallback


def classify_background(upper: np.ndarray, lower: np.ndarray):
    """Return list of (start_sec, end_sec, label) segments."""
    n = len(upper)
    labels = []
    for i in range(n):
        bw = upper[i] - lower[i]
        labels.append(classify_window(upper[i], lower[i], bw))

    # Run-length encode into segments
    segments = []
    seg_start = 0
    for i in range(1, n):
        if labels[i] != labels[seg_start]:
            segments.append((seg_start, i, labels[seg_start]))
            seg_start = i
    segments.append((seg_start, n, labels[seg_start]))
    return segments


# â”€â”€â”€ 7. Seizure detection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def detect_seizures(upper: np.ndarray, lower: np.ndarray,
                    narrow_uv: float = SEIZURE_NARROW_UV,
                    rise_uv: float = SEIZURE_RISE_UV,
                    min_dur: int = SEIZURE_DURATION_SEC):
    """
    Rule-based seizure detection:
      A) Sudden narrowing of aEEG band (bandwidth < narrow_uv) followed
         by a rise in amplitude â€” classic seizure signature.
      B) Rapid rise in lower margin: lower margin increases by > 15 ÂµV
         within a 30-second window AND lower margin exceeds rise_uv,
         sustained for at least min_dur seconds.
    """
    n = len(upper)
    bandwidth = upper - lower
    alerts = []

    # --- criterion A: narrowing followed by rise ---
    i = 0
    while i < n:
        if bandwidth[i] < narrow_uv:
            narrow_start = i
            j = i + 1
            while j < min(i + 120, n):
                if bandwidth[j] > narrow_uv * 3:
                    rise_end = j
                    while rise_end < min(j + 120, n) and bandwidth[rise_end] > narrow_uv:
                        rise_end += 1
                    if (rise_end - narrow_start) >= min_dur:
                        alerts.append((narrow_start, rise_end))
                    i = rise_end
                    break
                j += 1
            else:
                i = j
        else:
            i += 1

    # --- criterion B: rapid rise in lower margin ---
    # Compute rate of change of lower margin (smoothed over 10 s)
    lookback = 30  # seconds
    rise_threshold = 15  # ÂµV increase over lookback window
    in_event = False
    evt_start = 0
    for i in range(lookback, n):
        delta = lower[i] - lower[i - lookback]
        if delta > rise_threshold and lower[i] > rise_uv:
            if not in_event:
                in_event = True
                evt_start = i - lookback
        else:
            if in_event:
                # Extend to find where amplitude returns to baseline
                evt_end = i
                if (evt_end - evt_start) >= min_dur:
                    alerts.append((evt_start, evt_end))
                in_event = False
    if in_event and (n - evt_start) >= min_dur:
        alerts.append((evt_start, n))

    # Merge overlapping alerts
    if not alerts:
        return alerts
    alerts.sort()
    merged = [alerts[0]]
    for s, e in alerts[1:]:
        if s <= merged[-1][1] + 60:  # merge if within 60s
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged


# â”€â”€â”€ Main pipeline â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def analyse_aeeg(raw_eeg: np.ndarray, fs: int = FS) -> AEEGResult:
    """Full aEEG pipeline: raw EEG â†’ trend + classification + alerts."""
    filtered = bandpass_filter(raw_eeg, fs)
    envelope_1hz = compute_envelope(filtered, fs)
    time_sec = np.arange(len(envelope_1hz))
    upper, lower = compute_margins(envelope_1hz)
    classifications = classify_background(upper, lower)
    seizure_alerts = detect_seizures(upper, lower)
    return AEEGResult(time_sec, envelope_1hz, upper, lower,
                      classifications, seizure_alerts)


# â”€â”€â”€ Synthetic neonatal EEG generator â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _random_freq_mix(duration_sec, fs, freq_range=(0.5, 15),
                     n_components=8, amp_range=(1, 10)):
    """Generate a mixture of sinusoids with random phases."""
    t = np.arange(int(duration_sec * fs)) / fs
    sig = np.zeros_like(t)
    rng = np.random.default_rng()
    for _ in range(n_components):
        f = rng.uniform(*freq_range)
        a = rng.uniform(*amp_range)
        phi = rng.uniform(0, 2 * np.pi)
        sig += a * np.sin(2 * np.pi * f * t + phi)
    return sig


def generate_synthetic_eeg(total_hours: float = 4.0, fs: int = FS,
                           seed: int = 42) -> tuple[np.ndarray, list]:
    """
    Generate 4 hours of synthetic neonatal EEG with:
      - Normal continuous background (CNV)
      - Burst-suppression epochs
      - 2-3 seizure events
    Returns (eeg_array, event_log) where event_log lists
    (start_sec, end_sec, type).
    """
    rng = np.random.default_rng(seed)
    total_samples = int(total_hours * 3600 * fs)
    total_sec = int(total_hours * 3600)
    eeg = np.zeros(total_samples)
    events = []

    # â”€â”€ Schedule events (seconds) â”€â”€
    # 0â€“40 min:  CNV
    # 40â€“60 min: DNV
    # 60â€“90 min: BS
    # 90â€“92 min: seizure 1
    # 92â€“150 min: CNV
    # 150â€“152 min: seizure 2
    # 152â€“200 min: DNV
    # 200â€“201.5 min: seizure 3
    # 201.5â€“240 min: CNV

    schedule = [
        (0,    2400,  "CNV"),      # 0â€“40 min
        (2400, 3600,  "DNV"),      # 40â€“60 min
        (3600, 5400,  "BS"),       # 60â€“90 min
        (5400, 5520,  "SEIZURE"),  # 90â€“92 min
        (5520, 9000,  "CNV"),      # 92â€“150 min
        (9000, 9120,  "SEIZURE"),  # 150â€“152 min
        (9120, 12000, "DNV"),      # 152â€“200 min
        (12000,12090, "SEIZURE"),  # 200â€“201.5 min
        (12090,14400, "CNV"),      # 201.5â€“240 min
    ]

    for start_s, end_s, etype in schedule:
        i0 = start_s * fs
        i1 = min(end_s * fs, total_samples)
        dur = (i1 - i0) / fs
        events.append((start_s, end_s, etype))

        if etype == "CNV":
            # Continuous normal: 20â€“50 ÂµV, broadband
            seg = _random_freq_mix(dur, fs, (0.5, 15), 10, (3, 8))
            seg *= rng.uniform(20, 50) / (np.std(seg) + 1e-9)
            noise = rng.normal(0, 1.5, len(seg))
            eeg[i0:i1] = (seg + noise)[:i1 - i0]

        elif etype == "DNV":
            # Discontinuous normal: alternating low (<5 ÂµV) and
            # medium-amplitude (15â€“40 ÂµV) activity with ~10s cycling
            n_samps = i1 - i0
            seg = _random_freq_mix(dur, fs, (0.5, 12), 8, (1, 3))
            t_seg = np.arange(n_samps) / fs
            # Square-wave modulation: ~5s low, ~5s high
            mod = (np.sin(2 * np.pi * 0.1 * t_seg) > 0).astype(float)
            # Low periods: ~2 ÂµV noise; high periods: 10â€“20 ÂµV
            # (keeping upper margin in 10â€“25 range to distinguish from BS)
            target_high = rng.uniform(10, 20)
            seg_norm = seg / (np.std(seg) + 1e-9)
            seg_out = np.where(mod > 0.5,
                               seg_norm * target_high,
                               rng.normal(0, 1.5, n_samps))
            eeg[i0:i1] = seg_out[:n_samps]

        elif etype == "BS":
            # Burst suppression: alternating bursts (50â€“100 ÂµV, 2â€“5 s)
            # and suppression (<5 ÂµV, 5â€“15 s)
            pos = i0
            while pos < i1:
                # Suppression
                sup_dur = rng.uniform(5, 15)
                sup_samps = int(sup_dur * fs)
                end_pos = min(pos + sup_samps, i1)
                eeg[pos:end_pos] = rng.normal(0, 1.5, end_pos - pos)
                pos = end_pos
                if pos >= i1:
                    break
                # Burst
                burst_dur = rng.uniform(2, 5)
                burst_samps = int(burst_dur * fs)
                end_pos = min(pos + burst_samps, i1)
                burst = _random_freq_mix(burst_dur, fs, (1, 12), 6, (5, 15))
                burst *= rng.uniform(50, 100) / (np.std(burst) + 1e-9)
                length = end_pos - pos
                eeg[pos:end_pos] = burst[:length]
                pos = end_pos

        elif etype == "SEIZURE":
            # Rhythmic 2â€“3 Hz, evolving amplitude, 30â€“120 sec
            t_seg = np.arange(i1 - i0) / fs
            freq = rng.uniform(2.0, 3.0)
            # Evolving envelope: ramp up â†’ plateau â†’ taper
            dur_seg = t_seg[-1] if len(t_seg) > 0 else 1
            env = np.sqrt(np.clip(np.sin(np.pi * t_seg / dur_seg), 0, None))
            env = 30 + 70 * env  # 30â€“100 ÂµV range
            seizure_sig = env * np.sin(2 * np.pi * freq * t_seg)
            # Add harmonic
            seizure_sig += 0.3 * env * np.sin(2 * np.pi * 2 * freq * t_seg +
                                                rng.uniform(0, np.pi))
            noise = rng.normal(0, 2, len(t_seg))
            eeg[i0:i1] = (seizure_sig + noise)[:i1 - i0]

    return eeg, events


# â”€â”€â”€ I/O helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def load_eeg_csv(path: str | Path) -> np.ndarray:
    """Load single-channel EEG from CSV (one value per row or column named 'eeg')."""
    df = pd.read_csv(path)
    if "eeg" in df.columns:
        return df["eeg"].values.astype(float)
    return df.iloc[:, 0].values.astype(float)


def save_results(result: AEEGResult, raw_eeg: np.ndarray,
                 events: list, out_dir: str | Path):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # aEEG trend CSV
    trend_df = pd.DataFrame({
        "time_sec": result.time_sec,
        "envelope_uV": result.envelope_1hz,
        "upper_margin_uV": result.upper_margin,
        "lower_margin_uV": result.lower_margin,
    })
    trend_df.to_csv(out / "aeeg_trend.csv", index=False)

    # Classification log
    rows = []
    for s, e, label in result.classifications:
        rows.append({"start_sec": s, "end_sec": e, "label": label})
    for s, e in result.seizure_alerts:
        rows.append({"start_sec": s, "end_sec": e, "label": "SEIZURE_ALERT"})
    log_df = pd.DataFrame(rows).sort_values("start_sec")
    log_df.to_csv(out / "classification_log.csv", index=False)

    # Raw EEG CSV
    pd.DataFrame({"eeg": raw_eeg}).to_csv(out / "raw_eeg.csv", index=False)
Pressing key...Stopping...

Stop Agent
