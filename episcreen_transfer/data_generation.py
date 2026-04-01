"""
STEP 1 & 3: Synthetic EEG Data Generation
- CHB-MIT-like data (23-ch bipolar, extract FP1-F7 equivalent)
- "My electrode" data (single-channel, noisier, no seizures)
"""

import numpy as np
from scipy import signal
import os


def pink_noise(n_samples, rng):
    """Generate pink (1/f) noise via spectral shaping."""
    white = rng.standard_normal(n_samples)
    S = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n_samples)
    freqs[0] = 1  # avoid div by zero
    S = S / np.sqrt(freqs)
    return np.fft.irfft(S, n=n_samples)


def alpha_bursts(n_samples, fs, rng, freq_range=(8, 13), burst_prob=0.3):
    """Generate intermittent alpha rhythm bursts."""
    t = np.arange(n_samples) / fs
    sig = np.zeros(n_samples)
    burst_len = int(fs * 1.0)  # 1-second bursts
    for start in range(0, n_samples - burst_len, burst_len):
        if rng.random() < burst_prob:
            freq = rng.uniform(*freq_range)
            amp = rng.uniform(10, 30)  # uV
            envelope = np.hanning(burst_len)
            sig[start:start + burst_len] += amp * envelope * np.sin(2 * np.pi * freq * t[:burst_len])
    return sig


def beta_activity(n_samples, fs, rng, freq_range=(13, 30)):
    """Generate low-amplitude beta activity."""
    t = np.arange(n_samples) / fs
    freq = rng.uniform(*freq_range)
    amp = rng.uniform(3, 8)
    return amp * np.sin(2 * np.pi * freq * t + rng.uniform(0, 2 * np.pi))


def generate_normal_eeg(n_samples, fs, rng):
    """Generate normal EEG: pink noise + alpha bursts + beta, 20-100 uV range."""
    sig = pink_noise(n_samples, rng) * 15  # base pink noise ~15 uV
    sig += alpha_bursts(n_samples, fs, rng)
    sig += beta_activity(n_samples, fs, rng)
    # Scale to realistic amplitude range
    sig = sig / np.std(sig) * rng.uniform(15, 35)  # std ~15-35 uV
    return sig


def generate_seizure_event(duration_sec, fs, rng):
    """
    Generate a seizure event: spike-wave at 3-4 Hz with evolving frequency,
    increased amplitude.
    """
    n_samples = int(duration_sec * fs)
    t = np.arange(n_samples) / fs

    # Evolving spike-wave frequency (3 Hz -> 4 Hz -> slowing)
    freq_profile = np.concatenate([
        np.linspace(3, 4, n_samples // 3),
        np.linspace(4, 3.5, n_samples // 3),
        np.linspace(3.5, 2.5, n_samples - 2 * (n_samples // 3))
    ])
    phase = np.cumsum(2 * np.pi * freq_profile / fs)

    # Spike-wave: sharp spike + slow wave
    spike_wave = np.sin(phase) + 0.5 * np.sin(2 * phase)  # harmonic for spike shape

    # Amplitude envelope: buildup -> sustained -> offset
    envelope = np.ones(n_samples)
    ramp = min(n_samples // 4, int(2 * fs))
    envelope[:ramp] = np.linspace(0.3, 1.0, ramp)
    envelope[-ramp:] = np.linspace(1.0, 0.3, ramp)

    # Higher amplitude than normal (factor 3-5x)
    amp = rng.uniform(80, 200)  # uV
    seizure = amp * envelope * spike_wave

    # Add some rhythmic fast activity
    seizure += rng.uniform(10, 30) * np.sin(2 * np.pi * rng.uniform(14, 20) * t)

    return seizure


def bandpass_filter(data, fs, low=0.5, high=45, order=4):
    """Apply bandpass filter."""
    sos = signal.butter(order, [low, high], btype='band', fs=fs, output='sos')
    return signal.sosfiltfilt(sos, data)


def notch_filter(data, fs, freq=50, Q=30):
    """Apply notch filter at specified frequency."""
    b, a = signal.iirnotch(freq, Q, fs)
    return signal.filtfilt(b, a, data)


def generate_chbmit_patient(patient_id, fs=256, rng=None):
    """
    Generate 1 hour of normal EEG + 2-5 seizure events for one synthetic patient.
    Returns: (eeg_signal, labels) both at sample level, fs=256 Hz.
    Labels: 0=normal, 1=seizure.
    """
    if rng is None:
        rng = np.random.default_rng(patient_id)

    duration_sec = 3600  # 1 hour
    n_samples = duration_sec * fs
    eeg = generate_normal_eeg(n_samples, fs, rng)
    labels = np.zeros(n_samples, dtype=int)

    # Insert 2-5 seizure events
    n_seizures = rng.integers(2, 6)
    seizure_info = []

    for i in range(n_seizures):
        sz_dur = rng.uniform(10, 60)  # 10-60 seconds
        sz_samples = int(sz_dur * fs)

        # Place seizure at random position (avoid edges and overlap)
        max_start = n_samples - sz_samples - fs * 30
        attempts = 0
        while attempts < 100:
            start = rng.integers(fs * 60, max_start)
            end = start + sz_samples
            # Check no overlap with existing seizures (30s buffer)
            overlap = False
            for s_start, s_end in seizure_info:
                if not (end + fs * 30 < s_start or start - fs * 30 > s_end):
                    overlap = True
                    break
            if not overlap:
                break
            attempts += 1

        seizure_waveform = generate_seizure_event(sz_dur, fs, rng)
        # Blend: ramp into seizure
        blend_len = min(int(fs * 1), sz_samples // 4)
        blend = np.linspace(0, 1, blend_len)

        eeg[start:end] = eeg[start:end] * (1 - np.concatenate([
            blend, np.ones(sz_samples - 2 * blend_len), blend[::-1]
        ])) + seizure_waveform

        labels[start:end] = 1
        seizure_info.append((start, end))

    # Apply filters
    eeg = bandpass_filter(eeg, fs, 0.5, 45)
    eeg = notch_filter(eeg, fs, 50)

    return eeg, labels, seizure_info


def segment_and_label(eeg, labels, fs=256, window_sec=2):
    """Segment into 2-second windows, assign label (1 if >50% seizure)."""
    win_samples = window_sec * fs
    n_windows = len(eeg) // win_samples
    segments = []
    seg_labels = []

    for i in range(n_windows):
        start = i * win_samples
        end = start + win_samples
        seg = eeg[start:end]
        lbl = labels[start:end]
        segments.append(seg)
        seg_labels.append(1 if np.mean(lbl) > 0.5 else 0)

    return np.array(segments), np.array(seg_labels)


def balance_classes(segments, labels, rng):
    """Balance classes by undersampling the majority class."""
    idx_0 = np.where(labels == 0)[0]
    idx_1 = np.where(labels == 1)[0]

    if len(idx_0) == 0 or len(idx_1) == 0:
        return segments, labels

    minority = min(len(idx_0), len(idx_1))
    idx_0_sub = rng.choice(idx_0, size=minority, replace=False)
    idx_1_sub = rng.choice(idx_1, size=minority, replace=False)
    idx = np.concatenate([idx_0_sub, idx_1_sub])
    rng.shuffle(idx)
    return segments[idx], labels[idx]


def generate_all_chbmit(n_patients=5, fs=256, seed=42):
    """Generate synthetic CHB-MIT data for all patients."""
    rng = np.random.default_rng(seed)
    all_data = {}

    for pid in range(n_patients):
        p_rng = np.random.default_rng(seed + pid * 100)
        eeg, labels, sz_info = generate_chbmit_patient(pid, fs, p_rng)
        segments, seg_labels = segment_and_label(eeg, labels, fs)

        all_data[pid] = {
            'raw_eeg': eeg,
            'raw_labels': labels,
            'segments': segments,
            'seg_labels': seg_labels,
            'seizure_info': sz_info,
        }
        n_sz = np.sum(seg_labels == 1)
        n_norm = np.sum(seg_labels == 0)
        print(f"  Patient {pid}: {len(segments)} segments, "
              f"{n_sz} seizure, {n_norm} normal, "
              f"{len(sz_info)} seizure events")

    return all_data


# --- STEP 3: "My Electrode" data ---

def electrode_pop_artifact(n_samples, fs, rng, n_pops=5):
    """Generate occasional electrode pop artifacts."""
    sig = np.zeros(n_samples)
    for _ in range(n_pops):
        pos = rng.integers(0, n_samples - int(0.1 * fs))
        pop_len = int(rng.uniform(0.02, 0.1) * fs)
        amp = rng.uniform(200, 500)  # large transient
        pop = amp * np.exp(-np.linspace(0, 5, pop_len)) * rng.choice([-1, 1])
        sig[pos:pos + pop_len] += pop
    return sig


def generate_my_electrode_data(duration_sec=3600, fs=256, seed=99):
    """
    Generate realistic single-channel EEG from low-cost electrode.
    More noise, more 50 Hz contamination, electrode pops. NO seizures.
    """
    rng = np.random.default_rng(seed)
    n_samples = duration_sec * fs

    # Base EEG (same generation as CHB-MIT normal)
    eeg = generate_normal_eeg(n_samples, fs, rng)

    # Additional noise for low-cost hardware
    # 1. Higher baseline noise (2x)
    eeg += rng.standard_normal(n_samples) * 12

    # 2. More 50 Hz contamination (partially survives notch)
    t = np.arange(n_samples) / fs
    line_noise = 15 * np.sin(2 * np.pi * 50 * t + rng.uniform(0, 2 * np.pi))
    line_noise += 5 * np.sin(2 * np.pi * 100 * t)  # harmonic
    eeg += line_noise

    # 3. Electrode pop artifacts (occasional)
    eeg += electrode_pop_artifact(n_samples, fs, rng, n_pops=rng.integers(3, 10))

    # 4. Slow drift (motion/sweat)
    drift = 20 * np.sin(2 * np.pi * 0.05 * t)
    eeg += drift

    # Apply same filters as CHB-MIT
    eeg = bandpass_filter(eeg, fs, 0.5, 45)
    eeg = notch_filter(eeg, fs, 50)

    labels = np.zeros(n_samples, dtype=int)

    return eeg, labels


def inject_synthetic_seizures(eeg, fs=256, n_seizures=5, seed=77):
    """
    Inject synthetic seizure-like waveforms into my electrode data for testing.
    Returns modified EEG and seizure locations.
    """
    rng = np.random.default_rng(seed)
    eeg_modified = eeg.copy()
    labels = np.zeros(len(eeg), dtype=int)
    seizure_info = []

    for i in range(n_seizures):
        sz_dur = rng.uniform(10, 30)
        sz_samples = int(sz_dur * fs)
        start = rng.integers(fs * 60, len(eeg) - sz_samples - fs * 60)

        seizure = generate_seizure_event(sz_dur, fs, rng)

        blend_len = min(int(fs * 1), sz_samples // 4)
        blend = np.linspace(0, 1, blend_len)
        mask = np.concatenate([blend, np.ones(sz_samples - 2 * blend_len), blend[::-1]])

        eeg_modified[start:start + sz_samples] = (
            eeg_modified[start:start + sz_samples] * (1 - mask) + seizure
        )
        labels[start:start + sz_samples] = 1
        seizure_info.append((start, start + sz_samples))

    return eeg_modified, labels, seizure_info
