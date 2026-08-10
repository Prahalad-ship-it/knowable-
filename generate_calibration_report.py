#!/usr/bin/env python3
"""
Episteme AI — Model Calibration Report Generator
Comprehensive calibration analysis with reliability diagrams and statistical tests.

Usage:
    python generate_calibration_report.py
    python generate_calibration_report.py --csv episteme_empirical_results.csv --output calibration_report.html
"""

import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from scipy import stats
from matplotlib.gridspec import GridSpec


def load_csv_data(csv_path):
    """Load empirical results from CSV."""
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=['Confidence_Pct', 'Is_Correct']).copy()
    return df


def calculate_calibration_metrics(df):
    """Calculate comprehensive calibration metrics."""
    
    confidence = df['Confidence_Pct'].values / 100.0
    is_correct = df['Is_Correct'].values.astype(int)
    
    n_samples = len(df)
    n_bins = 10
    
    # === ECE ===
    bin_edges = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    mce = 0.0
    bin_data = []
    
    for i in range(n_bins):
        mask = (confidence > bin_edges[i]) & (confidence <= bin_edges[i + 1])
        if np.sum(mask) > 0:
            bin_confidence = np.mean(confidence[mask])
            bin_accuracy = np.mean(is_correct[mask])
            bin_count = np.sum(mask)
            gap = np.abs(bin_confidence - bin_accuracy)
            
            ece += (bin_count / n_samples) * gap
            mce = max(mce, gap)
            
            bin_data.append({
                'bin_lower': bin_edges[i],
                'bin_upper': bin_edges[i + 1],
                'confidence': bin_confidence,
                'accuracy': bin_accuracy,
                'count': bin_count,
                'gap': gap
            })
    
    # === Brier Score ===
    brier_score = np.mean((confidence - is_correct) ** 2)
    
    # === Calibration Slope & Intercept ===
    try:
        from sklearn.linear_model import LogisticRegression
        X = confidence.reshape(-1, 1)
        model = LogisticRegression()
        model.fit(X, is_correct)
        calibration_slope = float(model.coef_[0][0])
        calibration_intercept = float(model.intercept_[0])
    except:
        calibration_slope = np.nan
        calibration_intercept = np.nan
    
    # === Refinement ===
    refinement = 1.0 - ece
    
    # === Negative Log Loss ===
    eps = 1e-15
    confidence_clipped = np.clip(confidence, eps, 1 - eps)
    neg_log_loss = -np.mean(
        is_correct * np.log(confidence_clipped) + 
        (1 - is_correct) * np.log(1 - confidence_clipped)
    )
    
    # === Over/Under Confidence ===
    over_confident = np.sum((confidence > 0.7) & (is_correct == 0))
    under_confident = np.sum((confidence < 0.5) & (is_correct == 1))
    
    metrics = {
        'n_samples': n_samples,
        'ece': ece,
        'mce': mce,
        'brier_score': brier_score,
        'refinement': refinement,
        'neg_log_loss': neg_log_loss,
        'calibration_slope': calibration_slope,
        'calibration_intercept': calibration_intercept,
        'over_confident': over_confident,
        'under_confident': under_confident,
        'bin_data': bin_data,
        'confidence': confidence,
        'is_correct': is_correct,
    }
    
    return metrics


def generate_calibration_plots(df, metrics, output_prefix='calibration_report'):
    """Generate calibration visualization plots."""
    
    fig = plt.figure(figsize=(16, 12), dpi=120)
    fig.suptitle('Episteme AI — Model Calibration Analysis', 
                 fontsize=18, fontweight='bold')
    
    gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.3)
    
    confidence = metrics['confidence']
    is_correct = metrics['is_correct']
    bin_data = metrics['bin_data']
    
    # 1. Reliability Diagram (Perfect Calibration)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot([0, 1], [0, 1], 'k--', linewidth=2, label='Perfect Calibration')
    
    if bin_data:
        bin_centers = [b['confidence'] for b in bin_data]
        bin_accuracies = [b['accuracy'] for b in bin_data]
        bin_counts = [b['count'] for b in bin_data]
        
        ax1.plot(bin_centers, bin_accuracies, 'o-', linewidth=2, markersize=8, 
                color='#1f77b4', label='Model Calibration')
        
        # Error bars
        for bc, ba, count in zip(bin_centers, bin_accuracies, bin_counts):
            if count > 0:
                ax1.plot([bc, bc], [bc, ba], color='#ff7f0e', alpha=0.5, linewidth=2)
    
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.set_xlabel('Predicted Confidence', fontsize=11)
    ax1.set_ylabel('Empirical Accuracy', fontsize=11)
    ax1.set_title('Reliability Diagram', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 2. Confidence Histogram with Accuracy Overlay
    ax2 = fig.add_subplot(gs[0, 1])
    n_bins_hist = 20
    ax2.hist(confidence[is_correct == 0] * 100, bins=n_bins_hist, alpha=0.6, 
            label='Incorrect', color='#d62728', edgecolor='black')
    ax2.hist(confidence[is_correct == 1] * 100, bins=n_bins_hist, alpha=0.6, 
            label='Correct', color='#2ca02c', edgecolor='black')
    ax2.set_xlabel('Confidence (%)', fontsize=11)
    ax2.set_ylabel('Frequency', fontsize=11)
    ax2.set_title('Confidence Distribution by Correctness', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 3. Expected Calibration Error Breakdown
    ax3 = fig.add_subplot(gs[1, 0])
    if bin_data:
        bin_ranges = [f"{b['bin_lower']:.1f}-{b['bin_upper']:.1f}" for b in bin_data]
        gaps = [b['gap'] for b in bin_data]
        colors = ['#d62728' if g > 0.2 else '#ff7f0e' if g > 0.1 else '#2ca02c' for g in gaps]
        ax3.bar(range(len(bin_ranges)), gaps, color=colors, alpha=0.7, edgecolor='black')
        ax3.set_xticks(range(len(bin_ranges)))
        ax3.set_xticklabels(bin_ranges, rotation=45, ha='right')
        ax3.axhline(metrics['ece'], color='red', linestyle='--', linewidth=2, label=f"ECE={metrics['ece']:.4f}")
    ax3.set_ylabel('Calibration Gap', fontsize=11)
    ax3.set_xlabel('Confidence Bin', fontsize=11)
    ax3.set_title('ECE Breakdown by Bin', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. Calibration Curve (Expected vs Observed)
    ax4 = fig.add_subplot(gs[1, 1])
    if bin_data:
        bin_centers = np.array([b['confidence'] for b in bin_data])
        bin_accuracies = np.array([b['accuracy'] for b in bin_data])
        
        ax4.scatter(bin_centers, bin_accuracies, s=100, alpha=0.6, 
                   color='#1f77b4', edgecolor='black', linewidth=1, label='Observed')
        ax4.plot(bin_centers, bin_centers, 'k--', linewidth=2, label='Expected (Perfect)')
        ax4.fill_between(bin_centers, bin_centers, bin_accuracies, alpha=0.2, color='#ff7f0e')
    
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.set_xlabel('Expected Confidence', fontsize=11)
    ax4.set_ylabel('Observed Accuracy', fontsize=11)
    ax4.set_title('Expected vs Observed Accuracy', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    # 5. Error Metrics Summary
    ax5 = fig.add_subplot(gs[2, 0])
    ax5.axis('off')
    metrics_text = f"""
CALIBRATION METRICS

Expected Calibration Error (ECE)
  {metrics['ece']:.4f}
  
Maximum Calibration Error (MCE)
  {metrics['mce']:.4f}
  
Brier Score
  {metrics['brier_score']:.4f}
  
Negative Log Loss
  {metrics['neg_log_loss']:.4f}
  
Refinement
  {metrics['refinement']:.4f}
    """
    ax5.text(0.1, 0.95, metrics_text, transform=ax5.transAxes, fontsize=10,
            verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='#e3f2fd', alpha=0.8, pad=1))
    
    # 6. Over/Under Confidence Analysis
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.axis('off')
    confidence_text = f"""
CONFIDENCE ISSUES

Over-Confident Cases
  (Conf > 70% but Incorrect)
  Count: {metrics['over_confident']}
  ({metrics['over_confident']/metrics['n_samples']*100:.1f}%)
  
Under-Confident Cases
  (Conf < 50% but Correct)
  Count: {metrics['under_confident']}
  ({metrics['under_confident']/metrics['n_samples']*100:.1f}%)
  
Total Samples: {metrics['n_samples']}
    """
    ax6.text(0.1, 0.95, confidence_text, transform=ax6.transAxes, fontsize=10,
            verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='#fff3e0', alpha=0.8, pad=1))
    
    plt.savefig(f'{output_prefix}_plots.png', dpi=300, bbox_inches='tight')
    print(f"✓ Calibration plots saved to: {output_prefix}_plots.png")


def generate_html_calibration_report(df, metrics, output_path='calibration_report.html'):
    """Generate comprehensive HTML calibration report."""
    
    bin_data = metrics['bin_data']
    bin_table_rows = ""
    for i, b in enumerate(bin_data):
        bin_table_rows += f"""
        <tr>
            <td>Bin {i+1}</td>
            <td>{b['bin_lower']:.2f} - {b['bin_upper']:.2f}</td>
            <td>{b['confidence']:.4f}</td>
            <td>{b['accuracy']:.4f}</td>
            <td>{b['gap']:.4f}</td>
            <td>{b['count']}</td>
        </tr>
        """
    
    audit_passed = np.sum(df['Audit_Status'] == 'PASSED_CALIBRATION')
    audit_flagged = np.sum(df['Audit_Status'] == 'AUDIT_FLAGGED_LOW_CONFIDENCE')
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Episteme AI — Model Calibration Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 40px 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #3498db;
        }}
        .metric-card.warning {{ border-left-color: #f39c12; }}
        .metric-card.danger {{ border-left-color: #e74c3c; }}
        .metric-card.success {{ border-left-color: #27ae60; }}
        .metric-card h3 {{
            color: #2c3e50;
            font-size: 0.85em;
            text-transform: uppercase;
            margin-bottom: 10px;
            letter-spacing: 1px;
        }}
        .metric-card .value {{
            font-size: 2em;
            font-weight: bold;
        }}
        .metric-card .subtext {{
            font-size: 0.85em;
            color: #666;
            margin-top: 8px;
        }}
        section {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        section h2 {{
            color: #2c3e50;
            font-size: 1.5em;
            margin-bottom: 20px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .table-responsive {{
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th {{
            background: #ecf0f1;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #bdc3c7;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:hover {{
            background: #f9f9f9;
        }}
        .highlight {{
            background: #fff3cd;
            padding: 15px;
            border-left: 4px solid #f39c12;
            border-radius: 4px;
            margin: 15px 0;
        }}
        .highlight.danger {{
            background: #f8d7da;
            border-left-color: #e74c3c;
        }}
        .highlight.success {{
            background: #d4edda;
            border-left-color: #27ae60;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .status-badge.good {{ background: #d4edda; color: #155724; }}
        .status-badge.warning {{ background: #fff3cd; color: #856404; }}
        .status-badge.bad {{ background: #f8d7da; color: #721c24; }}
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        .interpretation {{
            background: #e8f4f8;
            padding: 15px;
            border-left: 4px solid #3498db;
            border-radius: 4px;
            margin: 15px 0;
        }}
        footer {{
            text-align: center;
            color: #666;
            padding: 20px;
            border-top: 1px solid #eee;
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 Model Calibration Report</h1>
            <p>Episteme AI — Comprehensive calibration analysis across {metrics['n_samples']} samples</p>
        </header>
        
        <div class="metrics-grid">
            <div class="metric-card {'danger' if metrics['ece'] > 0.3 else 'warning' if metrics['ece'] > 0.15 else 'success'}">
                <h3>Expected Calibration Error</h3>
                <div class="value">{metrics['ece']:.4f}</div>
                <div class="subtext">Lower is better (ideal: 0)</div>
            </div>
            <div class="metric-card {'danger' if metrics['mce'] > 0.5 else 'warning' if metrics['mce'] > 0.25 else 'success'}">
                <h3>Maximum Calibration Error</h3>
                <div class="value">{metrics['mce']:.4f}</div>
                <div class="subtext">Max gap between confidence and accuracy</div>
            </div>
            <div class="metric-card {'danger' if metrics['brier_score'] > 0.5 else 'warning' if metrics['brier_score'] > 0.25 else 'success'}">
                <h3>Brier Score</h3>
                <div class="value">{metrics['brier_score']:.4f}</div>
                <div class="subtext">Lower is better (ideal: 0)</div>
            </div>
            <div class="metric-card {'success' if metrics['refinement'] > 0.85 else 'warning' if metrics['refinement'] > 0.7 else 'danger'}">
                <h3>Refinement</h3>
                <div class="value">{metrics['refinement']:.4f}</div>
                <div class="subtext">1 - ECE (higher is better)</div>
            </div>
        </div>
        
        <section>
            <h2>📊 Key Calibration Metrics</h2>
            <div class="interpretation">
                <strong>📈 ECE (Expected Calibration Error): {metrics['ece']:.4f}</strong><br>
                The ECE measures the average gap between predicted confidence and empirical accuracy across confidence bins.
                {'✓ GOOD: ECE is low, indicating well-calibrated predictions.' if metrics['ece'] < 0.15 else '⚠️ WARNING: ECE is moderate, indicating some calibration issues.' if metrics['ece'] < 0.3 else '❌ POOR: ECE is high, indicating significant calibration problems.'}
            </div>
            
            <div class="interpretation">
                <strong>📈 MCE (Maximum Calibration Error): {metrics['mce']:.4f}</strong><br>
                MCE is the maximum gap in any single confidence bin. This represents the worst-case calibration error.
                {'✓ GOOD: MCE is acceptable, worst-case error is limited.' if metrics['mce'] < 0.25 else '⚠️ WARNING: MCE indicates some confidence bins are poorly calibrated.' if metrics['mce'] < 0.5 else '❌ POOR: MCE is very high, some confidence levels are highly miscalibrated.'}
            </div>
            
            <div class="interpretation">
                <strong>📈 Brier Score: {metrics['brier_score']:.4f}</strong><br>
                The Brier Score is the mean squared difference between predicted probabilities and actual outcomes.
                {'✓ GOOD: Brier Score indicates strong probabilistic calibration.' if metrics['brier_score'] < 0.15 else '⚠️ WARNING: Brier Score indicates moderate calibration.' if metrics['brier_score'] < 0.35 else '❌ POOR: Brier Score indicates weak probabilistic calibration.'}
            </div>
            
            <table>
                <tr>
                    <td><strong>Negative Log Loss</strong></td>
                    <td>{metrics['neg_log_loss']:.4f}</td>
                </tr>
                <tr>
                    <td><strong>Calibration Slope</strong></td>
                    <td>{metrics['calibration_slope']:.4f} (Ideal: 1.0)</td>
                </tr>
                <tr>
                    <td><strong>Calibration Intercept</strong></td>
                    <td>{metrics['calibration_intercept']:.4f} (Ideal: 0.0)</td>
                </tr>
                <tr>
                    <td><strong>Total Samples</strong></td>
                    <td>{metrics['n_samples']}</td>
                </tr>
            </table>
        </section>
        
        <section>
            <h2>⚠️ Confidence Issues</h2>
            <div class="highlight danger">
                <strong>🔴 Over-Confident Cases</strong><br>
                <strong>Count: {metrics['over_confident']}</strong> ({metrics['over_confident']/metrics['n_samples']*100:.1f}% of samples)<br>
                These are predictions where the model was >70% confident but still incorrect.
                These cases suggest the model may be too confident in its predictions.
            </div>
            
            <div class="highlight">
                <strong>🟡 Under-Confident Cases</strong><br>
                <strong>Count: {metrics['under_confident']}</strong> ({metrics['under_confident']/metrics['n_samples']*100:.1f}% of samples)<br>
                These are predictions where the model was <50% confident but still correct.
                These cases suggest the model may be unnecessarily hesitant in some scenarios.
            </div>
        </section>
        
        <section>
            <h2>🔍 Audit Status Distribution</h2>
            <table>
                <tr>
                    <td><strong>Passed Calibration</strong></td>
                    <td><span class="status-badge good">✓ {audit_passed} ({audit_passed/metrics['n_samples']*100:.1f}%)</span></td>
                </tr>
                <tr>
                    <td><strong>Audit Flagged (Low Confidence)</strong></td>
                    <td><span class="status-badge warning">⚠ {audit_flagged} ({audit_flagged/metrics['n_samples']*100:.1f}%)</span></td>
                </tr>
            </table>
        </section>
        
        <section>
            <h2>📋 Calibration Bin Details</h2>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Bin</th>
                            <th>Confidence Range</th>
                            <th>Mean Confidence</th>
                            <th>Empirical Accuracy</th>
                            <th>Calibration Gap</th>
                            <th>Sample Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        {bin_table_rows}
                    </tbody>
                </table>
            </div>
        </section>
        
        <section>
            <h2>📊 Visualizations</h2>
            <p>Comprehensive calibration analysis plots:</p>
            <img src="calibration_report_plots.png" alt="Calibration Report Plots">
        </section>
        
        <section>
            <h2>✅ Recommendations</h2>
            <ul style="line-height: 2;">
                <li><strong>ECE Improvement:</strong> Focus on the bins with the largest calibration gaps. Implement temperature scaling or Platt scaling for better calibration.</li>
                <li><strong>Over-confidence:</strong> If over-confident cases are high, consider increasing the regularization or using confidence penalty in the loss function.</li>
                <li><strong>Under-confidence:</strong> If under-confident cases are prevalent, the model may benefit from confidence boosting or removal of excessive regularization.</li>
                <li><strong>Monitoring:</strong> Track calibration metrics over time. Re-calibrate the model periodically as data distributions shift.</li>
                <li><strong>Decision Thresholds:</strong> Use calibration curves to set optimal decision thresholds for business-critical applications.</li>
            </ul>
        </section>
        
        <footer>
            <p>Generated by Episteme AI Calibration Suite | {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Calibration Report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate comprehensive model calibration report"
    )
    parser.add_argument(
        "--csv",
        default="episteme_empirical_results.csv",
        help="Path to empirical results CSV"
    )
    parser.add_argument(
        "--output",
        default="calibration_report.html",
        help="Output HTML report path"
    )
    
    args = parser.parse_args()
    
    print(f"Loading data from: {args.csv}")
    df = load_csv_data(args.csv)
    
    print(f"Calculating calibration metrics for {len(df)} samples...")
    metrics = calculate_calibration_metrics(df)
    
    # Print summary to console
    print("\n" + "="*60)
    print("  CALIBRATION METRICS — SUMMARY")
    print("="*60)
    print(f"Expected Calibration Error (ECE)      : {metrics['ece']:.4f}")
    print(f"Maximum Calibration Error (MCE)       : {metrics['mce']:.4f}")
    print(f"Brier Score                           : {metrics['brier_score']:.4f}")
    print(f"Refinement                            : {metrics['refinement']:.4f}")
    print(f"Over-Confident Cases                  : {metrics['over_confident']}")
    print(f"Under-Confident Cases                 : {metrics['under_confident']}")
    print("="*60 + "\n")
    
    # Generate plots
    generate_calibration_plots(df, metrics, output_prefix='calibration_report')
    
    # Generate HTML report
    generate_html_calibration_report(df, metrics, output_path=args.output)


if __name__ == "__main__":
    main()
