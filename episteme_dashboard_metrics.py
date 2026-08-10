#!/usr/bin/env python3
"""
Episteme AI Comprehensive Metrics Dashboard
Visualizes all experimental results including ECE, MCE, Brier Score, AUROC, and more.

Usage:
    python episteme_dashboard_metrics.py
    python episteme_dashboard_metrics.py --csv episteme_empirical_results.csv --output dashboard.png
"""

import argparse
import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.metrics import roc_auc_score, roc_curve
from matplotlib.gridspec import GridSpec


def calculate_metrics(df):
    """Calculate all calibration and performance metrics from the dataframe."""
    
    confidence = df['Confidence_Pct'].values / 100.0  # normalize to [0, 1]
    is_correct = df['Is_Correct'].values.astype(int)
    
    n_samples = len(df)
    
    # === EXPECTED CALIBRATION ERROR (ECE) ===
    n_bins = 10
    bin_edges = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    bin_data = []
    
    for i in range(n_bins):
        mask = (confidence > bin_edges[i]) & (confidence <= bin_edges[i + 1])
        if np.sum(mask) > 0:
            bin_accuracy = np.mean(is_correct[mask])
            bin_confidence = np.mean(confidence[mask])
            bin_count = np.sum(mask)
            gap = np.abs(bin_confidence - bin_accuracy)
            ece += (bin_count / n_samples) * gap
            bin_data.append({
                'bin': f'{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}',
                'confidence': bin_confidence,
                'accuracy': bin_accuracy,
                'count': bin_count,
                'gap': gap
            })
    
    # === MAXIMUM CALIBRATION ERROR (MCE) ===
    mce = max([b['gap'] for b in bin_data]) if bin_data else 0.0
    
    # === BRIER SCORE ===
    brier_score = np.mean((confidence - is_correct) ** 2)
    
    # === AUROC ===
    try:
        if len(np.unique(is_correct)) >= 2:
            auroc = roc_auc_score(is_correct, confidence)
        else:
            auroc = np.nan
    except:
        auroc = np.nan
    
    # === AUDIT STATUS ===
    audit_count = np.sum(df['Audit_Status'] == 'AUDIT_FLAGGED_LOW_CONFIDENCE')
    audit_ratio = (audit_count / n_samples) * 100
    
    # === ENTROPY STATS ===
    entropy_mean = df['Entropy'].mean()
    entropy_std = df['Entropy'].std()
    
    # === LATENCY STATS ===
    latency_mean = df['Latency_MS'].mean()
    latency_std = df['Latency_MS'].std()
    
    metrics = {
        'ece': ece,
        'mce': mce,
        'brier_score': brier_score,
        'auroc': auroc,
        'n_samples': n_samples,
        'audit_flagged': audit_count,
        'audit_ratio': audit_ratio,
        'entropy_mean': entropy_mean,
        'entropy_std': entropy_std,
        'latency_mean': latency_mean,
        'latency_std': latency_std,
        'bin_data': bin_data,
        'confidence': confidence,
        'is_correct': is_correct,
    }
    
    return metrics


def plot_dashboard(metrics, output_path='episteme_dashboard_metrics.png'):
    """Create a comprehensive metrics dashboard."""
    
    fig = plt.figure(figsize=(16, 12), dpi=120)
    fig.suptitle('Episteme AI — Comprehensive Metrics Dashboard', 
                 fontsize=18, fontweight='bold', y=0.98)
    
    gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3, 
                  top=0.94, bottom=0.05, left=0.06, right=0.96)
    
    # ========== TOP ROW: KEY METRICS ==========
    
    # Metric 1: ECE
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis('off')
    ax1.text(0.5, 0.7, f"{metrics['ece']:.4f}", 
             ha='center', va='center', fontsize=32, fontweight='bold', 
             color='#1f77b4')
    ax1.text(0.5, 0.35, "Expected\nCalibration Error", 
             ha='center', va='center', fontsize=11, color='#666666')
    ax1.add_patch(mpatches.Rectangle((0.05, 0.05), 0.9, 0.9, 
                                      fill=False, edgecolor='#1f77b4', linewidth=2))
    
    # Metric 2: MCE
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis('off')
    ax2.text(0.5, 0.7, f"{metrics['mce']:.4f}", 
             ha='center', va='center', fontsize=32, fontweight='bold', 
             color='#ff7f0e')
    ax2.text(0.5, 0.35, "Maximum\nCalibration Error", 
             ha='center', va='center', fontsize=11, color='#666666')
    ax2.add_patch(mpatches.Rectangle((0.05, 0.05), 0.9, 0.9, 
                                      fill=False, edgecolor='#ff7f0e', linewidth=2))
    
    # Metric 3: AUROC
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.axis('off')
    auroc_text = f"{metrics['auroc']:.4f}" if not np.isnan(metrics['auroc']) else "N/A"
    ax3.text(0.5, 0.7, auroc_text, 
             ha='center', va='center', fontsize=32, fontweight='bold', 
             color='#2ca02c')
    ax3.text(0.5, 0.35, "AUROC\n(Hallucination Detection)", 
             ha='center', va='center', fontsize=11, color='#666666')
    ax3.add_patch(mpatches.Rectangle((0.05, 0.05), 0.9, 0.9, 
                                      fill=False, edgecolor='#2ca02c', linewidth=2))
    
    # ========== MIDDLE ROW: DISTRIBUTIONS & RELIABILITY ==========
    
    # Brier Score
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.axis('off')
    ax4.text(0.5, 0.7, f"{metrics['brier_score']:.4f}", 
             ha='center', va='center', fontsize=32, fontweight='bold', 
             color='#d62728')
    ax4.text(0.5, 0.35, "Brier Score", 
             ha='center', va='center', fontsize=11, color='#666666')
    ax4.add_patch(mpatches.Rectangle((0.05, 0.05), 0.9, 0.9, 
                                      fill=False, edgecolor='#d62728', linewidth=2))
    
    # Confidence Distribution
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.hist(metrics['confidence'] * 100, bins=30, color='#1f77b4', alpha=0.7, edgecolor='black')
    ax5.axvline(np.mean(metrics['confidence']) * 100, color='red', linestyle='--', linewidth=2, label='Mean')
    ax5.set_xlabel('Confidence (%)', fontsize=10)
    ax5.set_ylabel('Frequency', fontsize=10)
    ax5.set_title('Confidence Distribution', fontsize=11, fontweight='bold')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # Reliability Diagram
    ax6 = fig.add_subplot(gs[1, 2])
    bin_data = metrics['bin_data']
    if bin_data:
        bin_centers = [b['confidence'] for b in bin_data]
        bin_accuracies = [b['accuracy'] for b in bin_data]
        bin_counts = [b['count'] for b in bin_data]
        
        ax6.plot([0, 1], [0, 1], 'k--', label='Perfect calibration', linewidth=1.5)
        ax6.scatter(bin_centers, bin_accuracies, s=[c*2 for c in bin_counts], 
                   alpha=0.6, color='#1f77b4', edgecolor='black', linewidth=1)
        
        for i, (bc, ba) in enumerate(zip(bin_centers, bin_accuracies)):
            ax6.plot([bc, bc], [bc, ba], color='#ff7f0e', alpha=0.4, linewidth=1.5)
    
    ax6.set_xlim(0, 1)
    ax6.set_ylim(0, 1)
    ax6.set_xlabel('Predicted Confidence', fontsize=10)
    ax6.set_ylabel('Empirical Accuracy', fontsize=10)
    ax6.set_title('Reliability Diagram', fontsize=11, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    ax6.legend()
    
    # ========== BOTTOM ROW: ADDITIONAL METRICS ==========
    
    # Audit Status
    ax7 = fig.add_subplot(gs[2, 0])
    audit_data = [metrics['audit_flagged'], metrics['n_samples'] - metrics['audit_flagged']]
    audit_labels = [f"Flagged\n({metrics['audit_flagged']})", 
                   f"Passed\n({metrics['n_samples'] - metrics['audit_flagged']})"]
    colors_audit = ['#ff7f0e', '#2ca02c']
    ax7.pie(audit_data, labels=audit_labels, autopct='%1.1f%%', colors=colors_audit, 
           startangle=90)
    ax7.set_title('Audit Status Distribution', fontsize=11, fontweight='bold')
    
    # Entropy Statistics
    ax8 = fig.add_subplot(gs[2, 1])
    ax8.text(0.5, 0.8, f"{metrics['entropy_mean']:.4f}", 
             ha='center', va='center', fontsize=24, fontweight='bold', 
             color='#9467bd')
    ax8.text(0.5, 0.55, "Mean Entropy", 
             ha='center', va='center', fontsize=10, color='#666666')
    ax8.text(0.5, 0.35, f"Std: {metrics['entropy_std']:.4f}", 
             ha='center', va='center', fontsize=10, color='#999999')
    ax8.set_xlim(0, 1)
    ax8.set_ylim(0, 1)
    ax8.axis('off')
    ax8.add_patch(mpatches.Rectangle((0.05, 0.05), 0.9, 0.9, 
                                      fill=False, edgecolor='#9467bd', linewidth=2))
    
    # Summary Statistics
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.axis('off')
    summary_text = f"""
SUMMARY STATISTICS

Total Q&A Samples: {metrics['n_samples']}
Audit Flagged: {metrics['audit_flagged']} ({metrics['audit_ratio']:.1f}%)

Latency (ms):
  Mean: {metrics['latency_mean']:.1f}
  Std: {metrics['latency_std']:.1f}

Model Performance:
  ✓ Calibration: ECE={metrics['ece']:.4f}
  ✓ Robustness: MCE={metrics['mce']:.4f}
  ✓ Confidence: Brier={metrics['brier_score']:.4f}
    """
    ax9.text(0.05, 0.95, summary_text, transform=ax9.transAxes, 
            fontsize=9, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Dashboard saved to: {output_path}")
    
    return fig


def print_summary(metrics):
    """Print a text summary of all metrics."""
    print("\n" + "="*60)
    print("  EPISTEME AI EXPERIMENTAL RESULTS SUMMARY")
    print("="*60)
    print(f"Expected Calibration Error (ECE)     : {metrics['ece']:.4f}")
    print(f"Maximum Calibration Error (MCE)      : {metrics['mce']:.4f}")
    print(f"Brier Score                          : {metrics['brier_score']:.4f}")
    auroc_str = f"{metrics['auroc']:.4f}" if not np.isnan(metrics['auroc']) else "N/A"
    print(f"AUROC (Hallucination Detection)      : {auroc_str}")
    print(f"Uncertainty Audit Entries Flagged    : {metrics['audit_flagged']}")
    print(f"Total Q&A Samples                    : {metrics['n_samples']}")
    print(f"Audit Flagged Ratio                  : {metrics['audit_ratio']:.2f}%")
    print(f"Mean Entropy                         : {metrics['entropy_mean']:.4f}")
    print(f"Mean Latency (ms)                    : {metrics['latency_mean']:.2f}")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Episteme AI Comprehensive Metrics Dashboard"
    )
    parser.add_argument(
        "--csv",
        default="episteme_empirical_results.csv",
        help="Path to the empirical results CSV file"
    )
    parser.add_argument(
        "--output",
        default="episteme_dashboard_metrics.png",
        help="Output image file path"
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display the plot (requires display environment)"
    )
    
    args = parser.parse_args()
    
    # Load data
    print(f"Loading data from: {args.csv}")
    df = pd.read_csv(args.csv)
    
    # Validate columns
    required_cols = ['Confidence_Pct', 'Is_Correct', 'Audit_Status', 'Entropy', 'Latency_MS']
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Clean data
    df = df.dropna(subset=['Confidence_Pct', 'Is_Correct']).copy()
    
    # Calculate metrics
    print(f"Processing {len(df)} samples...")
    metrics = calculate_metrics(df)
    
    # Print summary
    print_summary(metrics)
    
    # Create and save dashboard
    print(f"Creating dashboard...")
    plot_dashboard(metrics, output_path=args.output)
    
    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
