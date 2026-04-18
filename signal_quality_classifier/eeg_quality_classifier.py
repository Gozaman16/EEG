#!/usr/bin/env python3
"""
EEG Signal Quality Classifier
==============================
Complete pipeline: synthetic data generation, preprocessing, feature extraction,
model training, visualization, and real-time prediction.

To use with real data, change EEG_CSV_PATH and LABEL_CSV_PATH below.
  - EEG CSV: columns [timestamp, voltage]
  - Label CSV: columns [start_time, end_time, label]  (label: 1=clean, 0=artifact)
"""

import os
import warnings
import numpy as np
import pandas as pd
from scipy import signal as sig
from scipy.stats import kurtosis, skew
from sklearn.model_selection import (
    train_test_split, StratifiedKFold, cross_val_score, GridSearchCV,
)
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score, roc_curve,
    confusion_matrix, classification_report,
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

warnings.filterwarnings("ignore")

# ============================================================================
# CONFIGURATION â€” change these two paths to use real data
# ============================================================================
EEG_CSV_PATH = None      # e.g. "/path/to/eeg_recording.csv"
LABEL_CSV_PATH = None    # e.g. "/path/to/labels.csv"

FS = 256                 # sampling rate (Hz)
DURATION_MIN = 30        # synthetic recording length (minutes)
WINDOW_SEC = 2           # window length (seconds)
OVERLAP = 0.5            # 50 % overlap
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

np.random.seed(42)


# ============================================================================
# 0. SYNTHETIC DATA GENERATION
# ============================================================================
def generate_synthetic_eeg(fs=256, duration_min=30):
    """Generate realistic single-channel EEG with embedded artifacts."""
    n_samples = fs * 60 * duration_min
    t = np.arange(n_samples) / fs

    # --- Base EEG via superimposed oscillations ---
    eeg = np.zeros(n_samples)
    # Delta (0.5-4 Hz)
    for f in np.linspace(0.5, 4, 4):
        eeg += 20 * np.sin(2 * np.pi * f * t + np.random.uniform(0, 2 * np.pi))
    # Theta (4-8 Hz)
    for f in np.linspace(4, 8, 4):
        eeg += 10 * np.sin(2 * np.pi * f * t + np.random.uniform(0, 2 * np.pi))
    # Alpha (8-13 Hz) â€” dominant
    for f in np.linspace(8, 13, 5):
        eeg += 15 * np.sin(2 * np.pi * f * t + np.random.uniform(0, 2 * np.pi))
    # Beta (13-30 Hz)
    for f in np.linspace(13, 30, 6):
        eeg += 5 * np.sin(2 * np.pi * f * t + np.random.uniform(0, 2 * np.pi))
    # Gamma (30-50 Hz)
    for f in np.linspace(30, 50, 5):
        eeg += 2 * np.sin(2 * np.pi * f * t + np.random.uniform(0, 2 * np.pi))
    # Pink noise (1/f)
    white = np.random.randn(n_samples)
    fft_w = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n_samples, 1 / fs)
    freqs[0] = 1  # avoid div-by-zero
    fft_w *= 1.0 / np.sqrt(freqs)
    eeg += 8 * np.fft.irfft(fft_w, n=n_samples)

    # --- Labels (1 = clean, 0 = artifact) ---
    labels = np.ones(n_samples, dtype=int)

    # --- Embed artifacts ---
    def _random_segments(n_events, min_dur, max_dur):
        segs = []
        for _ in range(n_events):
            dur = np.random.uniform(min_dur, max_dur)
            start = np.random.uniform(1, duration_min * 60 - dur - 1)
            s = int(start * fs)
            e = int((start + dur) * fs)
            segs.append((s, min(e, n_samples)))
        return segs

    # Eye blinks â€” sharp positive deflections ~200-400 ms
    for s, e in _random_segments(120, 0.2, 0.4):
        blink_len = e - s
        blink = 150 * np.exp(-0.5 * ((np.linspace(-3, 3, blink_len)) ** 2))
        eeg[s:e] += blink
        labels[s:e] = 0

    # Muscle artifact â€” high-freq burst, 0.3-1 s
    for s, e in _random_segments(80, 0.3, 1.0):
        muscle = 60 * np.random.randn(e - s)
        b_m, a_m = sig.butter(2, [20 / (fs / 2), 100 / (fs / 2)], btype="band")
        # only filter if segment long enough
        if e - s > 15:
            muscle = sig.filtfilt(b_m, a_m, muscle)
        eeg[s:e] += muscle
        labels[s:e] = 0

    # Electrode pop â€” sudden step, 0.1-0.3 s
    for s, e in _random_segments(40, 0.1, 0.3):
        pop_amp = np.random.choice([-1, 1]) * np.random.uniform(200, 500)
        eeg[s:e] += pop_amp
        labels[s:e] = 0

    # 50 Hz power-line contamination â€” bursts of 2-5 s
    for s, e in _random_segments(30, 2.0, 5.0):
        line = 40 * np.sin(2 * np.pi * 50 * t[s:e])
        eeg[s:e] += line
        labels[s:e] = 0

    # Head movement â€” slow drift, 1-3 s
    for s, e in _random_segments(50, 1.0, 3.0):
        drift = 80 * np.cumsum(np.random.randn(e - s)) / fs
        eeg[s:e] += drift
        labels[s:e] = 0

    return t, eeg, labels


# ============================================================================
# 1. DATA LOADING & PREPROCESSING
# ============================================================================
def load_data(eeg_path, label_path, fs):
    """Load real EEG CSV and label file."""
    df = pd.read_csv(eeg_path)
    t = df.iloc[:, 0].values
    voltage = df.iloc[:, 1].values

    lab_df = pd.read_csv(label_path)
    labels = np.ones(len(voltage), dtype=int)  # default clean
    for _, row in lab_df.iterrows():
        s = int(row["start_time"] * fs)
        e = int(row["end_time"] * fs)
        labels[s:e] = int(row["label"])
    return t, voltage, labels


def bandpass_filter(data, low=0.5, high=50.0, fs=256, order=4):
    """4th-order Butterworth bandpass."""
    nyq = fs / 2
    b, a = sig.butter(order, [low / nyq, high / nyq], btype="band")
    return sig.filtfilt(b, a, data)


def notch_filter(data, freq=50.0, fs=256, Q=30):
    """Notch filter for power-line interference."""
    b, a = sig.iirnotch(freq, Q, fs)
    return sig.filtfilt(b, a, data)


def segment_windows(eeg, labels, fs, win_sec=2, overlap=0.5):
    """Segment into overlapping windows, assign label per window."""
    win_len = int(win_sec * fs)
    step = int(win_len * (1 - overlap))
    windows, win_labels = [], []
    for start in range(0, len(eeg) - win_len + 1, step):
        end = start + win_len
        w = eeg[start:end]
        # label: artifact if >25 % of window is artifact
        lbl = 0 if np.mean(labels[start:end] == 0) > 0.25 else 1
        windows.append(w)
        win_labels.append(lbl)
    return np.array(windows), np.array(win_labels)


# ============================================================================
# 2. FEATURE EXTRACTION
# ============================================================================
def sample_entropy(x, m=2, r_frac=0.2):
    """Compute sample entropy (manual implementation)."""
    N = len(x)
    r = r_frac * np.std(x)
    if r == 0:
        return 0.0

    def _count_matches(template_len):
        count = 0
        templates = np.array([x[i:i + template_len] for i in range(N - template_len)])
        for i in range(len(templates)):
            dists = np.max(np.abs(templates[i + 1:] - templates[i]), axis=1)
            count += np.sum(dists < r)
        return count

    A = _count_matches(m + 1)
    B = _count_matches(m)
    if B == 0:
        return 0.0
    return -np.log(A / B) if A > 0 else 0.0


def hjorth_parameters(x):
    """Compute Hjorth activity, mobility, complexity."""
    dx = np.diff(x)
    ddx = np.diff(dx)
    activity = np.var(x)
    mobility = np.sqrt(np.var(dx) / activity) if activity > 0 else 0
    mob_dx = np.sqrt(np.var(ddx) / np.var(dx)) if np.var(dx) > 0 else 0
    complexity = mob_dx / mobility if mobility > 0 else 0
    return activity, mobility, complexity


def extract_features(window, fs=256):
    """Extract all features from a single window."""
    feats = {}

    # --- Time domain ---
    feats["mean"] = np.mean(window)
    feats["std"] = np.std(window)
    feats["rms"] = np.sqrt(np.mean(window ** 2))
    feats["peak_to_peak"] = np.ptp(window)
    # zero-crossing rate
    zc = np.sum(np.diff(np.sign(window - np.mean(window))) != 0)
    feats["zero_crossing_rate"] = zc / len(window)
    feats["kurtosis"] = kurtosis(window)
    feats["skewness"] = skew(window)
    feats["line_length"] = np.sum(np.abs(np.diff(window)))

    # --- Frequency domain (Welch PSD) ---
    freqs, psd = sig.welch(window, fs=fs, nperseg=min(256, len(window)))
    feats["total_power"] = np.trapz(psd, freqs)

    bands = {
        "delta": (0.5, 4),
        "theta": (4, 8),
        "alpha": (8, 13),
        "beta": (13, 30),
        "gamma": (30, 50),
    }
    for name, (lo, hi) in bands.items():
        idx = np.logical_and(freqs >= lo, freqs <= hi)
        feats[f"{name}_power"] = np.trapz(psd[idx], freqs[idx]) if np.any(idx) else 0

    total = feats["total_power"] if feats["total_power"] > 0 else 1e-12
    feats["theta_beta_ratio"] = feats["theta_power"] / max(feats["beta_power"], 1e-12)
    feats["alpha_total_ratio"] = feats["alpha_power"] / total

    # --- Nonlinear ---
    feats["sample_entropy"] = sample_entropy(window)
    act, mob, comp = hjorth_parameters(window)
    feats["hjorth_activity"] = act
    feats["hjorth_mobility"] = mob
    feats["hjorth_complexity"] = comp

    return feats


def extract_all_features(windows, fs=256):
    """Extract features for all windows; returns DataFrame."""
    rows = []
    for i, w in enumerate(windows):
        if i % 200 == 0:
            print(f"  Extracting features: {i}/{len(windows)}", end="\r")
        rows.append(extract_features(w, fs))
    print(f"  Extracted features for {len(windows)} windows.     ")
    return pd.DataFrame(rows)


# ============================================================================
# 3. MODEL TRAINING
# ============================================================================
def train_and_select(X, y):
    """Train RF, SVM, GBT with 5-fold CV; return best model & results."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc = scaler.transform(X_test)

    models = {
        "RandomForest": RandomForestClassifier(
            n_estimators=200, max_depth=15, random_state=42, n_jobs=-1
        ),
        "SVM_RBF": SVC(kernel="rbf", probability=True, random_state=42),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=200, max_depth=5, random_state=42
        ),
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results = {}

    for name, model in models.items():
        # SVM needs scaled data; tree models work either way
        Xtr = X_train_sc if "SVM" in name else X_train
        Xte = X_test_sc if "SVM" in name else X_test

        scores = cross_val_score(model, Xtr, y_train, cv=cv, scoring="f1")
        model.fit(Xtr, y_train)
        y_pred = model.predict(Xte)
        y_proba = model.predict_proba(Xte)[:, 1]

        f1 = f1_score(y_test, y_pred)
        acc = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)

        results[name] = {
            "model": model,
            "cv_f1_mean": scores.mean(),
            "cv_f1_std": scores.std(),
            "test_f1": f1,
            "test_acc": acc,
            "test_auc": auc,
            "y_pred": y_pred,
            "y_proba": y_proba,
        }
        print(f"  {name:20s}  CV-F1={scores.mean():.3f}Â±{scores.std():.3f}  "
              f"Test F1={f1:.3f}  AUC={auc:.3f}")

    # Select best by CV F1
    best_name = max(results, key=lambda k: results[k]["cv_f1_mean"])
    best = results[best_name]

    # If F1 < 0.85, try grid search on the best model type
    if best["test_f1"] < 0.85:
        print(f"\n  F1 < 0.85 â€” running GridSearchCV on {best_name}...")
        if best_name == "RandomForest":
            param_grid = {
                "n_estimators": [200, 400],
                "max_depth": [10, 20, None],
                "min_samples_split": [2, 5],
            }
            base = RandomForestClassifier(random_state=42, n_jobs=-1)
        elif best_name == "GradientBoosting":
            param_grid = {
                "n_estimators": [200, 400],
                "max_depth": [3, 5, 8],
                "learning_rate": [0.05, 0.1],
            }
            base = GradientBoostingClassifier(random_state=42)
        else:
            param_grid = {"C": [0.1, 1, 10], "gamma": ["scale", "auto"]}
            base = SVC(kernel="rbf", probability=True, random_state=42)

        Xtr = X_train_sc if "SVM" in best_name else X_train
        Xte = X_test_sc if "SVM" in best_name else X_test

        gs = GridSearchCV(base, param_grid, cv=cv, scoring="f1", n_jobs=-1)
        gs.fit(Xtr, y_train)
        y_pred = gs.predict(Xte)
        y_proba = gs.predict_proba(Xte)[:, 1]
        f1 = f1_score(y_test, y_pred)

        if f1 > best["test_f1"]:
            print(f"  GridSearch improved F1: {best['test_f1']:.3f} â†’ {f1:.3f}")
            best = {
                "model": gs.best_estimator_,
                "test_f1": f1,
                "test_acc": accuracy_score(y_test, y_pred),
                "test_auc": roc_auc_score(y_test, y_proba),
                "y_pred": y_pred,
                "y_proba": y_proba,
            }

    return best_name, best, scaler, X_test, y_test, X_train, y_train


# ============================================================================
# 4. VISUALIZATION
# ============================================================================
def plot_raw_eeg(t, eeg, sample_labels, fs, out_dir):
    """Fig 1: Raw EEG with clean/artifact colour-coded (first 30 s)."""
    n = min(30 * fs, len(eeg))
    fig, ax = plt.subplots(figsize=(14, 4))

    # Plot in segments by label
    i = 0
    while i < n:
        lbl = sample_labels[i]
        j = i
        while j < n and sample_labels[j] == lbl:
            j += 1
        color = "#2196F3" if lbl == 1 else "#F44336"
        ax.plot(t[i:j], eeg[i:j], color=color, linewidth=0.5)
        i = j

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude (ÂµV)")
    ax.set_title("Raw EEG â€” Blue: Clean, Red: Artifact (first 30 s)")
    ax.set_xlim(t[0], t[min(n, len(t) - 1)])
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig1_raw_eeg.png"), dpi=300)
    plt.close(fig)
    print("  Saved fig1_raw_eeg.png")


def plot_feature_importance(model, feature_names, out_dir):
    """Fig 2: Top-15 feature importances."""
    if hasattr(model, "feature_importances_"):
        imp = model.feature_importances_
    else:
        # For SVM, use permutation importance approximation via abs coefs
        imp = np.abs(model.decision_function(
            np.eye(len(feature_names))
        )) if hasattr(model, "decision_function") else np.zeros(len(feature_names))

    idx = np.argsort(imp)[-15:]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(range(len(idx)), imp[idx], color="#4CAF50")
    ax.set_yticks(range(len(idx)))
    ax.set_yticklabels([feature_names[i] for i in idx])
    ax.set_xlabel("Importance")
    ax.set_title("Top 15 Feature Importances")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig2_feature_importance.png"), dpi=300)
    plt.close(fig)
    print("  Saved fig2_feature_importance.png")


def plot_confusion_matrix(y_true, y_pred, out_dir):
    """Fig 3: Confusion matrix heatmap."""
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Artifact", "Clean"],
                yticklabels=["Artifact", "Clean"], ax=ax)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion Matrix")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig3_confusion_matrix.png"), dpi=300)
    plt.close(fig)
    print("  Saved fig3_confusion_matrix.png")


def plot_roc_curve(y_true, y_proba, auc_val, out_dir):
    """Fig 4: ROC curve."""
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(fpr, tpr, color="#1976D2", lw=2, label=f"AUC = {auc_val:.3f}")
    ax.plot([0, 1], [0, 1], "k--", lw=1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig4_roc_curve.png"), dpi=300)
    plt.close(fig)
    print("  Saved fig4_roc_curve.png")


def plot_example_windows(windows, win_labels, fs, out_dir):
    """Fig 5: Example clean vs artifact windows with their PSD."""
    clean_idx = np.where(win_labels == 1)[0]
    artif_idx = np.where(win_labels == 0)[0]

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # Pick representative examples
    ci = clean_idx[len(clean_idx) // 3]
    ai = artif_idx[len(artif_idx) // 3]

    for col, (idx, label, color) in enumerate([
        (ci, "Clean", "#2196F3"), (ai, "Artifact", "#F44336")
    ]):
        w = windows[idx]
        t_w = np.arange(len(w)) / fs

        axes[0, col].plot(t_w, w, color=color, linewidth=0.8)
        axes[0, col].set_title(f"{label} Window (Time Domain)")
        axes[0, col].set_xlabel("Time (s)")
        axes[0, col].set_ylabel("Amplitude (ÂµV)")

        freqs, psd = sig.welch(w, fs=fs, nperseg=min(256, len(w)))
        axes[1, col].semilogy(freqs, psd, color=color, linewidth=1.2)
        axes[1, col].set_title(f"{label} Window (PSD)")
        axes[1, col].set_xlabel("Frequency (Hz)")
        axes[1, col].set_ylabel("Power (ÂµVÂ²/Hz)")

    fig.suptitle("Example Windows: Clean vs Artifact", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(out_dir, "fig5_example_windows.png"), dpi=300)
    plt.close(fig)
    print("  Saved fig5_example_windows.png")


# ============================================================================
# 5. REAL-TIME PREDICTION
# ============================================================================
class EEGQualityPredictor:
    """Load saved model and predict on new 2-second segments."""

    def __init__(self, model_path, scaler_path, fs=256):
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.fs = fs
        self._needs_scaling = "SVM" in type(self.model).__name__

    def predict(self, segment):
        """
        Parameters
        ----------
        segment : np.ndarray
            Raw 2-second EEG segment (length = fs * 2).

        Returns
        -------
        label : str   "CLEAN" or "ARTIFACT"
        confidence : float  probability of the predicted class
        """
        # Preprocess
        segment = bandpass_filter(segment, fs=self.fs)
        segment = notch_filter(segment, fs=self.fs)

        feats = extract_features(segment, self.fs)
        X = np.array(list(feats.values())).reshape(1, -1)
        if self._needs_scaling:
            X = self.scaler.transform(X)

        proba = self.model.predict_proba(X)[0]
        pred_class = np.argmax(proba)
        label = "CLEAN" if pred_class == 1 else "ARTIFACT"
        confidence = proba[pred_class]
        return label, confidence


# ============================================================================
# 6. MAIN PIPELINE
# ============================================================================
def main():
    print("=" * 60)
    print("  EEG Signal Quality Classifier")
    print("=" * 60)

    # --- Data ---
    if EEG_CSV_PATH and LABEL_CSV_PATH:
        print("\n[1] Loading real data...")
        t, eeg, sample_labels = load_data(EEG_CSV_PATH, LABEL_CSV_PATH, FS)
    else:
        print("\n[1] Generating synthetic EEG data (256 Hz, 30 min)...")
        t, eeg, sample_labels = generate_synthetic_eeg(FS, DURATION_MIN)

    print(f"    Samples: {len(eeg):,}  Duration: {len(eeg)/FS/60:.1f} min")

    # --- Preprocessing ---
    print("\n[2] Preprocessing (bandpass 0.5-50 Hz, notch 50 Hz)...")
    eeg_filt = bandpass_filter(eeg, 0.5, 50, FS, order=4)
    eeg_filt = notch_filter(eeg_filt, 50, FS)

    # --- Segmentation ---
    print(f"\n[3] Segmenting into {WINDOW_SEC}s windows, {int(OVERLAP*100)}% overlap...")
    windows, win_labels = segment_windows(eeg_filt, sample_labels, FS, WINDOW_SEC, OVERLAP)
    n_clean = np.sum(win_labels == 1)
    n_artif = np.sum(win_labels == 0)
    print(f"    Total windows: {len(win_labels)}")
    print(f"    Clean: {n_clean} ({100*n_clean/len(win_labels):.1f}%)")
    print(f"    Artifact: {n_artif} ({100*n_artif/len(win_labels):.1f}%)")

    # --- Feature extraction ---
    print("\n[4] Extracting features...")
    feat_df = extract_all_features(windows, FS)
    feat_df["label"] = win_labels
    feat_df.to_csv(os.path.join(OUTPUT_DIR, "features.csv"), index=False)
    print(f"    Saved features.csv ({feat_df.shape[0]} rows, {feat_df.shape[1]} cols)")

    X = feat_df.drop("label", axis=1).values
    y = feat_df["label"].values
    feature_names = list(feat_df.columns[:-1])

    # --- Training ---
    print("\n[5] Training models (RF, SVM-RBF, GBT)...")
    best_name, best, scaler, X_test, y_test, X_train, y_train = train_and_select(X, y)

    # --- Save model ---
    model_path = os.path.join(OUTPUT_DIR, "signal_quality_model.pkl")
    scaler_path = os.path.join(OUTPUT_DIR, "scaler.pkl")
    joblib.dump(best["model"], model_path)
    joblib.dump(scaler, scaler_path)
    print(f"\n  Saved model: {model_path}")
    print(f"  Saved scaler: {scaler_path}")

    # --- Visualization ---
    print("\n[6] Generating visualizations...")
    plot_raw_eeg(t, eeg, sample_labels, FS, OUTPUT_DIR)
    plot_feature_importance(best["model"], feature_names, OUTPUT_DIR)
    plot_confusion_matrix(y_test, best["y_pred"], OUTPUT_DIR)
    plot_roc_curve(y_test, best["y_proba"], best["test_auc"], OUTPUT_DIR)
    plot_example_windows(windows, win_labels, FS, OUTPUT_DIR)

    # --- Summary ---
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  Total windows:      {len(win_labels)}")
    print(f"  Class distribution: Clean={n_clean}, Artifact={n_artif}")
    print(f"  Best model:         {best_name}")
    print(f"  Test Accuracy:      {best['test_acc']:.4f}")
    print(f"  Test F1-score:      {best['test_f1']:.4f}")
    print(f"  Test AUC:           {best['test_auc']:.4f}")
    print("=" * 60)

    # --- Quick demo of real-time predictor ---
    print("\n[7] Real-time prediction demo:")
    predictor = EEGQualityPredictor(model_path, scaler_path, FS)
    for i, desc in [(0, "first"), (len(windows)//2, "middle")]:
        label, conf = predictor.predict(windows[i])
        true_lbl = "CLEAN" if win_labels[i] == 1 else "ARTIFACT"
        print(f"    Window {desc}: predicted={label} ({conf:.2%}), actual={true_lbl}")

    print("\nDone! All outputs saved to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
Pressing key...Getting DOM...Stopping...

Stop Agent
