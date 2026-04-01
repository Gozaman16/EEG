"""
STEP 2: Feature Extraction and Model Training
- 13 features: 5 band powers, line length, zero-crossing, 3 Hjorth, kurtosis, skewness, sample entropy
- Random Forest + MLP (CNN substitute, <50K params)
- Leave-one-patient-out CV
"""

import numpy as np
from scipy import signal, stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    confusion_matrix, classification_report,
    roc_curve, auc, accuracy_score
)
import warnings

warnings.filterwarnings('ignore')


# --- Feature extraction ---

def band_power(seg, fs=256):
    """Compute power in 5 standard EEG bands."""
    bands = {
        'delta': (0.5, 4),
        'theta': (4, 8),
        'alpha': (8, 13),
        'beta': (13, 30),
        'gamma': (30, 45),
    }
    freqs, psd = signal.welch(seg, fs=fs, nperseg=min(len(seg), fs))
    powers = []
    for name, (lo, hi) in bands.items():
        idx = np.logical_and(freqs >= lo, freqs <= hi)
        powers.append(np.trapezoid(psd[idx], freqs[idx]) if np.any(idx) else 0)
    return powers  # 5 values


def line_length(seg):
    """Sum of absolute differences between consecutive samples."""
    return np.sum(np.abs(np.diff(seg))) / len(seg)


def zero_crossing_rate(seg):
    """Number of zero crossings per sample."""
    return np.sum(np.abs(np.diff(np.sign(seg))) > 0) / len(seg)


def hjorth_parameters(seg):
    """Activity, Mobility, Complexity."""
    activity = np.var(seg)
    d1 = np.diff(seg)
    d2 = np.diff(d1)
    mobility = np.sqrt(np.var(d1) / (activity + 1e-10))
    complexity = np.sqrt(np.var(d2) / (np.var(d1) + 1e-10)) / (mobility + 1e-10)
    return [activity, mobility, complexity]


def sample_entropy(seg, m=2, r_factor=0.2):
    """Approximate sample entropy (fast implementation)."""
    N = len(seg)
    r = r_factor * np.std(seg)
    if r < 1e-10 or N < 20:
        return 0.0

    # Subsample for speed if segment is long
    if N > 256:
        seg = seg[:256]
        N = 256

    def count_matches(m_val):
        templates = np.array([seg[i:i + m_val] for i in range(N - m_val)])
        count = 0
        for i in range(len(templates)):
            dist = np.max(np.abs(templates[i] - templates[i + 1:]), axis=1)
            count += np.sum(dist < r)
        return count

    A = count_matches(m + 1)
    B = count_matches(m)

    if B == 0:
        return 0.0
    return -np.log((A + 1e-10) / (B + 1e-10))


def extract_features(seg, fs=256):
    """Extract all 13 features from a single segment."""
    feats = []
    feats.extend(band_power(seg, fs))         # 5 features
    feats.append(line_length(seg))             # 1
    feats.append(zero_crossing_rate(seg))      # 1
    feats.extend(hjorth_parameters(seg))       # 3
    feats.append(stats.kurtosis(seg))          # 1
    feats.append(stats.skew(seg))              # 1
    feats.append(sample_entropy(seg))          # 1
    return np.array(feats)  # 13 features


FEATURE_NAMES = [
    'Delta Power', 'Theta Power', 'Alpha Power', 'Beta Power', 'Gamma Power',
    'Line Length', 'Zero Crossing Rate',
    'Hjorth Activity', 'Hjorth Mobility', 'Hjorth Complexity',
    'Kurtosis', 'Skewness', 'Sample Entropy'
]


def extract_all_features(segments, fs=256):
    """Extract features from all segments."""
    features = np.array([extract_features(seg, fs) for seg in segments])
    return features


# --- Model training ---

def create_rf_model():
    """Create Random Forest classifier."""
    return RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1,
    )


def create_cnn_model():
    """
    Create MLP classifier as CNN substitute (<50K params).
    Architecture: input(13) -> 64 -> 32 -> 16 -> 2
    Params: 13*64+64 + 64*32+32 + 32*16+16 + 16*2+2 = 896+2112+528+34 = 3570
    Well under 50K.
    """
    return MLPClassifier(
        hidden_layer_sizes=(64, 32, 16),
        activation='relu',
        solver='adam',
        max_iter=500,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.15,
        batch_size=32,
        learning_rate='adaptive',
        learning_rate_init=0.001,
    )


def leave_one_patient_out_cv(patient_data, model_type='rf'):
    """
    Leave-one-patient-out cross-validation.
    Returns per-fold and aggregate metrics.
    """
    patient_ids = sorted(patient_data.keys())
    all_results = []

    for test_pid in patient_ids:
        # Collect training data from other patients
        train_X, train_y = [], []
        for pid in patient_ids:
            if pid == test_pid:
                continue
            feats = patient_data[pid]['features']
            labs = patient_data[pid]['balanced_labels']
            train_X.append(feats)
            train_y.append(labs)

        train_X = np.vstack(train_X)
        train_y = np.concatenate(train_y)

        test_X = patient_data[test_pid]['features']
        test_y = patient_data[test_pid]['balanced_labels']

        # Normalize features
        mean = train_X.mean(axis=0)
        std = train_X.std(axis=0) + 1e-10
        train_X_norm = (train_X - mean) / std
        test_X_norm = (test_X - mean) / std

        # Train model
        if model_type == 'rf':
            model = create_rf_model()
        else:
            model = create_cnn_model()

        model.fit(train_X_norm, train_y)
        y_pred = model.predict(test_X_norm)
        y_proba = model.predict_proba(test_X_norm)

        # Metrics
        cm = confusion_matrix(test_y, y_pred)
        tn, fp, fn, tp = cm.ravel()

        sensitivity = tp / (tp + fn + 1e-10)
        specificity = tn / (tn + fp + 1e-10)

        # False alarm rate per hour (based on 2-sec windows in 1 hour)
        n_normal_windows = np.sum(test_y == 0)
        hours = n_normal_windows * 2 / 3600  # 2-sec windows
        false_alarm_rate = fp / (hours + 1e-10)

        fpr, tpr, _ = roc_curve(test_y, y_proba[:, 1])
        roc_auc = auc(fpr, tpr)

        result = {
            'test_patient': test_pid,
            'confusion_matrix': cm,
            'sensitivity': sensitivity,
            'specificity': specificity,
            'false_alarm_rate_per_hour': false_alarm_rate,
            'roc_auc': roc_auc,
            'fpr': fpr,
            'tpr': tpr,
            'y_true': test_y,
            'y_pred': y_pred,
            'y_proba': y_proba[:, 1],
            'model': model,
            'norm_mean': mean,
            'norm_std': std,
        }
        all_results.append(result)

        print(f"  Patient {test_pid}: sens={sensitivity:.3f}, "
              f"spec={specificity:.3f}, FA/hr={false_alarm_rate:.1f}, "
              f"AUC={roc_auc:.3f}")

    return all_results


def compute_detection_latency(y_true, y_pred, fs=256, window_sec=2):
    """
    Compute average detection latency: time from seizure onset to first detection.
    Returns latency in seconds.
    """
    latencies = []
    in_seizure = False
    seizure_start = None

    for i in range(len(y_true)):
        if y_true[i] == 1 and not in_seizure:
            in_seizure = True
            seizure_start = i
        elif y_true[i] == 0 and in_seizure:
            in_seizure = False
            seizure_start = None

        if in_seizure and y_pred[i] == 1 and seizure_start is not None:
            latency = (i - seizure_start) * window_sec
            latencies.append(latency)
            in_seizure = False  # count only first detection per seizure
            seizure_start = None

    return np.mean(latencies) if latencies else float('nan')
