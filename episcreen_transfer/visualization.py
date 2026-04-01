"""
STEP 5: Visualization - All figures saved as PNG at 300 DPI.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE
from sklearn.metrics import confusion_matrix, roc_curve, auc
import os


def set_style():
    sns.set_theme(style='whitegrid', font_scale=1.1)
    plt.rcParams['figure.dpi'] = 100
    plt.rcParams['savefig.dpi'] = 300
    plt.rcParams['figure.figsize'] = (10, 6)


def fig1_seizure_vs_clean(chb_eeg, chb_labels, my_eeg, fs, seizure_info, save_dir):
    """Fig 1: Example CHB-MIT seizure vs my electrode clean EEG."""
    set_style()
    fig, axes = plt.subplots(3, 1, figsize=(14, 8), sharex=False)

    # CHB-MIT normal segment
    normal_start = int(10 * fs)
    normal_end = normal_start + int(4 * fs)
    t_norm = np.arange(normal_end - normal_start) / fs
    axes[0].plot(t_norm, chb_eeg[normal_start:normal_end], 'b', linewidth=0.5)
    axes[0].set_title('CHB-MIT: Normal EEG (FP1-F7 equivalent)', fontweight='bold')
    axes[0].set_ylabel('Amplitude (μV)')
    axes[0].set_ylim([-150, 150])

    # CHB-MIT seizure segment
    if seizure_info:
        sz_start = seizure_info[0][0]
        sz_end = min(sz_start + int(4 * fs), seizure_info[0][1])
        t_sz = np.arange(sz_end - sz_start) / fs
        axes[1].plot(t_sz, chb_eeg[sz_start:sz_end], 'r', linewidth=0.5)
        axes[1].set_title('CHB-MIT: Seizure EEG', fontweight='bold')
        axes[1].set_ylabel('Amplitude (μV)')
        axes[1].set_ylim([-300, 300])

    # My electrode clean
    my_start = int(100 * fs)
    my_end = my_start + int(4 * fs)
    t_my = np.arange(my_end - my_start) / fs
    axes[2].plot(t_my, my_eeg[my_start:my_end], 'g', linewidth=0.5)
    axes[2].set_title('My Electrode: Clean EEG (FP1, semi-dry)', fontweight='bold')
    axes[2].set_ylabel('Amplitude (μV)')
    axes[2].set_xlabel('Time (seconds)')
    axes[2].set_ylim([-150, 150])

    for ax in axes:
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.3)

    plt.tight_layout()
    path = os.path.join(save_dir, 'fig1_seizure_vs_clean.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


def fig2_feature_distributions(chb_features, my_features, feature_names, save_dir):
    """Fig 2: Violin plots of feature distributions CHB-MIT vs my electrode."""
    set_style()
    n_feats = len(feature_names)
    fig, axes = plt.subplots(3, 5, figsize=(20, 12))
    axes = axes.flatten()

    for i in range(n_feats):
        ax = axes[i]
        data_chb = chb_features[:, i]
        data_my = my_features[:, i]

        # Clip outliers for visualization
        for d in [data_chb, data_my]:
            q1, q99 = np.percentile(d, [1, 99])
            d_clip = np.clip(d, q1, q99)

        import pandas as pd
        df = pd.DataFrame({
            'Value': np.concatenate([data_chb, data_my]),
            'Source': ['CHB-MIT'] * len(data_chb) + ['My Electrode'] * len(data_my)
        })
        sns.violinplot(data=df, x='Source', y='Value', ax=ax,
                       palette=['steelblue', 'coral'], inner='quartile')
        ax.set_title(feature_names[i], fontsize=9, fontweight='bold')
        ax.set_xlabel('')
        ax.tick_params(labelsize=8)

    # Hide extra subplots
    for i in range(n_feats, len(axes)):
        axes[i].set_visible(False)

    fig.suptitle('Feature Distributions: CHB-MIT vs My Electrode', fontsize=14, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(save_dir, 'fig2_feature_distributions.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


def fig3_tsne_domain_shift(chb_features, my_features, save_dir):
    """Fig 3: t-SNE domain shift visualization."""
    set_style()

    # Subsample for speed
    n_sub = min(500, len(chb_features), len(my_features))
    rng = np.random.default_rng(42)
    idx_chb = rng.choice(len(chb_features), n_sub, replace=False)
    idx_my = rng.choice(len(my_features), n_sub, replace=False)

    X = np.vstack([chb_features[idx_chb], my_features[idx_my]])

    # Normalize
    mean = X.mean(axis=0)
    std = X.std(axis=0) + 1e-10
    X_norm = (X - mean) / std

    tsne = TSNE(n_components=2, random_state=42, perplexity=30, max_iter=1000)
    X_2d = tsne.fit_transform(X_norm)

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(X_2d[:n_sub, 0], X_2d[:n_sub, 1],
               c='steelblue', alpha=0.5, s=20, label='CHB-MIT (clinical)')
    ax.scatter(X_2d[n_sub:, 0], X_2d[n_sub:, 1],
               c='coral', alpha=0.5, s=20, label='My Electrode (low-cost)')
    ax.set_title('t-SNE: Domain Shift Between CHB-MIT and My Electrode',
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('t-SNE Dimension 1')
    ax.set_ylabel('t-SNE Dimension 2')
    ax.legend(fontsize=11, markerscale=2)

    plt.tight_layout()
    path = os.path.join(save_dir, 'fig3_tsne_domain_shift.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


def fig4_confusion_matrix(cv_results, save_dir):
    """Fig 4: Aggregated confusion matrix from CHB-MIT CV."""
    set_style()
    total_cm = np.zeros((2, 2), dtype=int)
    for r in cv_results:
        total_cm += r['confusion_matrix']

    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(total_cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Normal', 'Seizure'],
                yticklabels=['Normal', 'Seizure'],
                ax=ax, annot_kws={'size': 16})
    ax.set_xlabel('Predicted', fontsize=12)
    ax.set_ylabel('Actual', fontsize=12)
    ax.set_title('Confusion Matrix (CHB-MIT Leave-One-Patient-Out CV)',
                 fontsize=12, fontweight='bold')

    # Add metrics text
    tn, fp, fn, tp = total_cm.ravel()
    sens = tp / (tp + fn)
    spec = tn / (tn + fp)
    ax.text(0.5, -0.15, f'Sensitivity: {sens:.3f}  |  Specificity: {spec:.3f}',
            transform=ax.transAxes, ha='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='lightyellow'))

    plt.tight_layout()
    path = os.path.join(save_dir, 'fig4_confusion_matrix.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


def fig5_false_alarm_timeline(predictions, window_sec, save_dir):
    """Fig 5: False alarm timeline on my electrode data."""
    set_style()
    n_windows = len(predictions)
    time_hours = np.arange(n_windows) * window_sec / 3600

    fig, axes = plt.subplots(2, 1, figsize=(14, 6), gridspec_kw={'height_ratios': [2, 1]})

    # Top: prediction timeline
    fa_idx = np.where(predictions == 1)[0]
    axes[0].eventplot([time_hours[fa_idx]], lineoffsets=0.5, linelengths=0.8,
                       colors='red', linewidths=0.8)
    axes[0].set_title('False Alarm Timeline (My Electrode, No True Seizures)',
                       fontweight='bold')
    axes[0].set_ylabel('Detection')
    axes[0].set_yticks([0.5])
    axes[0].set_yticklabels(['Alert'])
    axes[0].set_xlim([0, time_hours[-1]])

    # Bottom: cumulative false alarms
    cum_fa = np.cumsum(predictions)
    axes[1].plot(time_hours, cum_fa, 'r-', linewidth=1.5)
    axes[1].set_xlabel('Time (hours)')
    axes[1].set_ylabel('Cumulative FAs')
    axes[1].set_xlim([0, time_hours[-1]])

    total_fa = np.sum(predictions)
    hours = time_hours[-1]
    fa_rate = total_fa / hours if hours > 0 else 0
    axes[1].text(0.02, 0.85, f'Total FAs: {total_fa}, Rate: {fa_rate:.1f}/hr',
                 transform=axes[1].transAxes, fontsize=10,
                 bbox=dict(boxstyle='round', facecolor='lightyellow'))

    plt.tight_layout()
    path = os.path.join(save_dir, 'fig5_false_alarm_timeline.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


def fig6_roc_curve(cv_results, save_dir):
    """Fig 6: ROC curves from CV with mean ROC."""
    set_style()
    fig, ax = plt.subplots(figsize=(8, 8))

    all_fpr = np.linspace(0, 1, 200)
    tprs = []

    for r in cv_results:
        ax.plot(r['fpr'], r['tpr'], alpha=0.3, linewidth=1,
                label=f"Patient {r['test_patient']} (AUC={r['roc_auc']:.3f})")
        interp_tpr = np.interp(all_fpr, r['fpr'], r['tpr'])
        interp_tpr[0] = 0.0
        tprs.append(interp_tpr)

    mean_tpr = np.mean(tprs, axis=0)
    mean_tpr[-1] = 1.0
    mean_auc = auc(all_fpr, mean_tpr)
    std_auc = np.std([r['roc_auc'] for r in cv_results])

    ax.plot(all_fpr, mean_tpr, 'b-', linewidth=2.5,
            label=f'Mean ROC (AUC={mean_auc:.3f} ± {std_auc:.3f})')

    std_tpr = np.std(tprs, axis=0)
    ax.fill_between(all_fpr, mean_tpr - std_tpr, mean_tpr + std_tpr,
                     alpha=0.15, color='blue')

    ax.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Chance')
    ax.set_xlabel('False Positive Rate', fontsize=12)
    ax.set_ylabel('True Positive Rate', fontsize=12)
    ax.set_title('ROC Curve (Leave-One-Patient-Out CV)', fontsize=13, fontweight='bold')
    ax.legend(loc='lower right', fontsize=9)
    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.02])

    plt.tight_layout()
    path = os.path.join(save_dir, 'fig6_roc_curve.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")
