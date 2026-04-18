#!/usr/bin/env python3
"""
EpiScreen Transfer Learning Pipeline
=====================================
Tests whether a seizure detection model trained on clinical CHB-MIT-like data
can transfer to a low-cost single-channel (FP1) semi-dry electrode.

Usage:
    python run_pipeline.py

All outputs saved to ./episcreen_transfer/
To swap in real data, change DATA_DIR and MY_ELECTRODE_PATH below.
"""

import numpy as np
import os
import sys
import time
import joblib

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_generation import (
    generate_all_chbmit,
    generate_my_electrode_data,
    inject_synthetic_seizures,
    segment_and_label,
    balance_classes,
)
from features import (
    extract_all_features,
    FEATURE_NAMES,
    leave_one_patient_out_cv,
    compute_detection_latency,
    create_rf_model,
    create_cnn_model,
)
from visualization import (
    fig1_seizure_vs_clean,
    fig2_feature_distributions,
    fig3_tsne_domain_shift,
    fig4_confusion_matrix,
    fig5_false_alarm_timeline,
    fig6_roc_curve,
)

# ============================================================
# CONFIGURATION - Change these paths to swap in real data
# ============================================================
SAVE_DIR = os.path.dirname(os.path.abspath(__file__))
FS = 256
WINDOW_SEC = 2
N_PATIENTS = 5
SEED = 42

# To swap real data: set these to file paths containing
# numpy arrays of shape (n_samples,) at 256 Hz.
# MY_ELECTRODE_PATH = "/path/to/my_electrode_recording.npy"
MY_ELECTRODE_PATH = None  # None = use synthetic data


def main():
    start_time = time.time()
    os.makedirs(SAVE_DIR, exist_ok=True)

    print("=" * 65)
    print("  EpiScreen Transfer Learning Pipeline")
    print("  Single-channel epilepsy detection: CHB-MIT -> FP1 electrode")
    print("=" * 65)

    # ===========================================================
    # STEP 1: Generate synthetic CHB-MIT data
    # ===========================================================
    print("\n[STEP 1] Generating synthetic CHB-MIT-like data...")
    print(f"  {N_PATIENTS} patients, 1 hour each, 2-5 seizure events")
    chb_data = generate_all_chbmit(n_patients=N_PATIENTS, fs=FS, seed=SEED)

    # Extract features and balance classes
    print("\n[STEP 2] Extracting features (13 per 2-sec window)...")
    rng = np.random.default_rng(SEED)
    for pid in chb_data:
        segs = chb_data[pid]['segments']
        labs = chb_data[pid]['seg_labels']
        feats = extract_all_features(segs, FS)

        # Balance classes
        bal_segs, bal_labs = balance_classes(segs, labs, rng)
        bal_feats = extract_all_features(bal_segs, FS)

        chb_data[pid]['features'] = bal_feats
        chb_data[pid]['balanced_labels'] = bal_labs
        chb_data[pid]['all_features'] = feats
        chb_data[pid]['all_labels'] = labs

        print(f"  Patient {pid}: {len(bal_feats)} balanced segments "
              f"({np.sum(bal_labs==1)} sz, {np.sum(bal_labs==0)} normal)")

    # ===========================================================
    # STEP 2: Train models with LOPO CV
    # ===========================================================
    print("\n[STEP 2b] Training Random Forest (Leave-One-Patient-Out CV)...")
    rf_results = leave_one_patient_out_cv(chb_data, model_type='rf')

    print("\n[STEP 2c] Training MLP/CNN-substitute (LOPO CV)...")
    mlp_results = leave_one_patient_out_cv(chb_data, model_type='mlp')

    # Compute detection latency
    for results, name in [(rf_results, 'RF'), (mlp_results, 'MLP')]:
        latencies = []
        for r in results:
            lat = compute_detection_latency(r['y_true'], r['y_pred'], FS, WINDOW_SEC)
            latencies.append(lat)
        avg_lat = np.nanmean(latencies)
        print(f"  {name} avg detection latency: {avg_lat:.1f} sec")

    # Select best model (by mean AUC)
    rf_auc = np.mean([r['roc_auc'] for r in rf_results])
    mlp_auc = np.mean([r['roc_auc'] for r in mlp_results])
    print(f"\n  RF mean AUC: {rf_auc:.3f}, MLP mean AUC: {mlp_auc:.3f}")

    if rf_auc >= mlp_auc:
        best_results = rf_results
        best_name = 'Random Forest'
    else:
        best_results = mlp_results
        best_name = 'MLP'
    print(f"  Selected: {best_name}")

    # Train final model on all CHB-MIT data
    print("\n  Training final model on all CHB-MIT data...")
    all_train_X = np.vstack([chb_data[pid]['features'] for pid in chb_data])
    all_train_y = np.concatenate([chb_data[pid]['balanced_labels'] for pid in chb_data])
    norm_mean = all_train_X.mean(axis=0)
    norm_std = all_train_X.std(axis=0) + 1e-10
    all_train_X_norm = (all_train_X - norm_mean) / norm_std

    if best_name == 'Random Forest':
        final_model = create_rf_model()
    else:
        final_model = create_cnn_model()
    final_model.fit(all_train_X_norm, all_train_y)

    # Save model
    model_path = os.path.join(SAVE_DIR, 'seizure_detector.joblib')
    joblib.dump({
        'model': final_model,
        'norm_mean': norm_mean,
        'norm_std': norm_std,
        'feature_names': FEATURE_NAMES,
        'fs': FS,
        'window_sec': WINDOW_SEC,
    }, model_path)
    print(f"  Model saved: {model_path}")

    # ===========================================================
    # STEP 3: Generate "my electrode" data
    # ===========================================================
    print("\n[STEP 3] Generating synthetic 'my electrode' data...")

    if MY_ELECTRODE_PATH is not None:
        print(f"  Loading real data from: {MY_ELECTRODE_PATH}")
        my_eeg = np.load(MY_ELECTRODE_PATH)
        my_labels = np.zeros(len(my_eeg), dtype=int)
    else:
        print("  Using synthetic data (low-cost electrode simulation)")
        my_eeg, my_labels = generate_my_electrode_data(
            duration_sec=3600, fs=FS, seed=99
        )

    my_segments, my_seg_labels = segment_and_label(my_eeg, my_labels, FS, WINDOW_SEC)
    my_features = extract_all_features(my_segments, FS)
    print(f"  {len(my_segments)} segments extracted from my electrode data")

    # ===========================================================
    # STEP 4: Transfer Evaluation
    # ===========================================================
    print("\n[STEP 4] Transfer evaluation...")

    # 4a: False alarm rate on clean data
    my_features_norm = (my_features - norm_mean) / norm_std
    my_predictions = final_model.predict(my_features_norm)
    n_fa = np.sum(my_predictions == 1)
    hours = len(my_predictions) * WINDOW_SEC / 3600
    fa_rate = n_fa / hours
    print(f"  Clean data: {n_fa} false alarms in {hours:.1f} hr = {fa_rate:.1f} FA/hr")

    # Analyze which segments trigger false alarms
    fa_indices = np.where(my_predictions == 1)[0]

    # 4b: Inject synthetic seizures and test detection
    print("  Injecting synthetic seizures into my electrode data...")
    my_eeg_sz, my_labels_sz, my_sz_info = inject_synthetic_seizures(
        my_eeg, fs=FS, n_seizures=5, seed=77
    )
    my_seg_sz, my_seg_labels_sz = segment_and_label(my_eeg_sz, my_labels_sz, FS, WINDOW_SEC)
    my_feat_sz = extract_all_features(my_seg_sz, FS)
    my_feat_sz_norm = (my_feat_sz - norm_mean) / norm_std
    my_pred_sz = final_model.predict(my_feat_sz_norm)

    # Detection metrics on injected seizures
    sz_windows = np.where(my_seg_labels_sz == 1)[0]
    detected = np.sum(my_pred_sz[sz_windows] == 1)
    total_sz = len(sz_windows)
    sz_sensitivity = detected / total_sz if total_sz > 0 else 0
    print(f"  Injected seizure detection: {detected}/{total_sz} windows "
          f"(sensitivity={sz_sensitivity:.3f})")

    det_latency = compute_detection_latency(
        my_seg_labels_sz, my_pred_sz, FS, WINDOW_SEC
    )
    print(f"  Detection latency on my electrode: {det_latency:.1f} sec")

    # ===========================================================
    # STEP 5: Visualizations
    # ===========================================================
    print("\n[STEP 5] Generating visualizations...")

    # Collect all CHB-MIT features (unbalanced, for distribution comparison)
    chb_all_feats = np.vstack([chb_data[pid]['all_features'] for pid in chb_data])

    fig1_seizure_vs_clean(
        chb_data[0]['raw_eeg'], chb_data[0]['raw_labels'],
        my_eeg, FS, chb_data[0]['seizure_info'], SAVE_DIR
    )

    fig2_feature_distributions(chb_all_feats, my_features, FEATURE_NAMES, SAVE_DIR)

    fig3_tsne_domain_shift(chb_all_feats, my_features, SAVE_DIR)

    fig4_confusion_matrix(best_results, SAVE_DIR)

    fig5_false_alarm_timeline(my_predictions, WINDOW_SEC, SAVE_DIR)

    fig6_roc_curve(best_results, SAVE_DIR)

    # ===========================================================
    # STEP 6: Summary Report
    # ===========================================================
    print("\n" + "=" * 65)
    print("  SUMMARY REPORT")
    print("=" * 65)

    # CHB-MIT model performance
    print("\n--- CHB-MIT Model Performance (LOPO CV) ---")
    print(f"  Model: {best_name}")
    sensitivities = [r['sensitivity'] for r in best_results]
    specificities = [r['specificity'] for r in best_results]
    aucs = [r['roc_auc'] for r in best_results]
    fa_rates_cv = [r['false_alarm_rate_per_hour'] for r in best_results]

    print(f"  Sensitivity:  {np.mean(sensitivities):.3f} Â± {np.std(sensitivities):.3f}")
    print(f"  Specificity:  {np.mean(specificities):.3f} Â± {np.std(specificities):.3f}")
    print(f"  AUC:          {np.mean(aucs):.3f} Â± {np.std(aucs):.3f}")
    print(f"  FA rate (CV): {np.mean(fa_rates_cv):.1f} Â± {np.std(fa_rates_cv):.1f} /hr")

    all_latencies = []
    for r in best_results:
        lat = compute_detection_latency(r['y_true'], r['y_pred'], FS, WINDOW_SEC)
        all_latencies.append(lat)
    print(f"  Detection latency: {np.nanmean(all_latencies):.1f} sec")

    # Transfer metrics
    print("\n--- Transfer to My Electrode ---")
    print(f"  False alarm rate (clean): {fa_rate:.1f} /hr")
    print(f"  Seizure sensitivity (injected): {sz_sensitivity:.3f}")
    print(f"  Detection latency: {det_latency:.1f} sec")

    # Failure mode analysis
    print("\n--- Failure Mode Analysis ---")
    if len(fa_indices) > 0:
        fa_features = my_features[fa_indices]
        non_fa_features = my_features[my_predictions == 0]

        print("  Features most different in false alarm windows:")
        for i, name in enumerate(FEATURE_NAMES):
            fa_mean = np.mean(fa_features[:, i])
            nfa_mean = np.mean(non_fa_features[:, i])
            ratio = fa_mean / (nfa_mean + 1e-10)
            if abs(ratio - 1) > 0.3:
                direction = "higher" if ratio > 1 else "lower"
                print(f"    {name}: {ratio:.2f}x {direction} in FA windows")

        # Check if false alarms cluster in time (artifact-related)
        fa_times = fa_indices * WINDOW_SEC
        fa_gaps = np.diff(fa_times)
        clustered = np.sum(fa_gaps < 10)  # within 10 seconds
        print(f"  Clustered FAs (<10s apart): {clustered}/{len(fa_gaps)} "
              f"({'artifact bursts likely' if clustered > len(fa_gaps)*0.3 else 'sporadic'})")
    else:
        print("  No false alarms detected!")

    # Domain shift assessment
    print("\n--- Domain Shift Assessment ---")
    chb_feat_means = np.mean(chb_all_feats, axis=0)
    my_feat_means = np.mean(my_features, axis=0)
    chb_feat_stds = np.std(chb_all_feats, axis=0) + 1e-10
    shift_magnitude = np.abs(chb_feat_means - my_feat_means) / chb_feat_stds

    print("  Feature-wise domain shift (standardized mean difference):")
    for i, name in enumerate(FEATURE_NAMES):
        severity = "LOW" if shift_magnitude[i] < 0.5 else (
            "MODERATE" if shift_magnitude[i] < 1.0 else "HIGH")
        print(f"    {name}: {shift_magnitude[i]:.2f} ({severity})")

    # Conclusion
    print("\n--- Conclusion ---")
    feasible = (sz_sensitivity > 0.5 and fa_rate < 20)

    if feasible:
        print("  TRANSFER IS PARTIALLY FEASIBLE.")
        print("  The clinical model shows meaningful seizure detection on")
        print("  low-cost hardware, though false alarm rate needs reduction.")
        print("  Recommended next steps:")
        print("    1. Collect real electrode data to validate synthetic results")
        print("    2. Apply domain adaptation (feature alignment/normalization)")
        print("    3. Fine-tune noise rejection for electrode artifacts")
        print("    4. Collect real seizure recordings for final validation")
    else:
        print("  TRANSFER REQUIRES SIGNIFICANT ADAPTATION.")
        print("  The domain shift between clinical and low-cost hardware")
        print("  degrades performance beyond acceptable thresholds.")
        print("  Recommended next steps:")
        print("    1. Domain adaptation techniques (CORAL, adversarial)")
        print("    2. Noise-robust feature engineering")
        print("    3. Hardware-specific artifact rejection preprocessing")
        print("    4. Collect matched seizure data from clinical setting")

    elapsed = time.time() - start_time
    print(f"\n  Pipeline completed in {elapsed:.1f} seconds")
    print(f"  All outputs saved to: {SAVE_DIR}")
    print("=" * 65)

    # Save summary to text file
    summary_path = os.path.join(SAVE_DIR, 'summary_report.txt')
    with open(summary_path, 'w') as f:
        f.write("EpiScreen Transfer Learning Pipeline - Summary Report\n")
        f.write("=" * 55 + "\n\n")
        f.write(f"Model: {best_name}\n")
        f.write(f"Patients: {N_PATIENTS} synthetic CHB-MIT\n")
        f.write(f"Sampling rate: {FS} Hz, Window: {WINDOW_SEC}s\n")
        f.write(f"Features: {len(FEATURE_NAMES)} ({', '.join(FEATURE_NAMES)})\n\n")
        f.write("CHB-MIT Performance (LOPO CV):\n")
        f.write(f"  Sensitivity: {np.mean(sensitivities):.3f} Â± {np.std(sensitivities):.3f}\n")
        f.write(f"  Specificity: {np.mean(specificities):.3f} Â± {np.std(specificities):.3f}\n")
        f.write(f"  AUC: {np.mean(aucs):.3f} Â± {np.std(aucs):.3f}\n")
        f.write(f"  FA rate: {np.mean(fa_rates_cv):.1f} Â± {np.std(fa_rates_cv):.1f} /hr\n")
        f.write(f"  Detection latency: {np.nanmean(all_latencies):.1f} sec\n\n")
        f.write("Transfer to My Electrode:\n")
        f.write(f"  False alarm rate: {fa_rate:.1f} /hr\n")
        f.write(f"  Seizure sensitivity: {sz_sensitivity:.3f}\n")
        f.write(f"  Detection latency: {det_latency:.1f} sec\n\n")
        f.write(f"Conclusion: {'Partially feasible' if feasible else 'Requires significant adaptation'}\n")
    print(f"  Summary saved: {summary_path}")


if __name__ == '__main__':
    main()
Pressing key...Stopping...

Stop Agent
