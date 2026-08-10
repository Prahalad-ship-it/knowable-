#!/usr/bin/env python3
"""
Episteme AI — Uncertainty Patterns Analysis
Analyzes confidence-entropy relationships and uncertainty distribution patterns.

Usage:
    python analyze_uncertainty_patterns.py
    python analyze_uncertainty_patterns.py --json episteme_uncertainty_dataset.json --output analysis_report.html
"""

import argparse
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
from matplotlib.gridspec import GridSpec


def load_json_data(json_path):
    """Load uncertainty dataset from JSON."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.DataFrame(data)


def analyze_uncertainty_patterns(df):
    """Analyze uncertainty patterns in the dataset."""
    
    confidence = df['confidence_pct'].values / 100.0
    entropy = df['entropy'].values
    
    # Basic stats
    stats_dict = {
        'n_samples': len(df),
        'confidence_mean': np.mean(confidence),
        'confidence_std': np.std(confidence),
        'confidence_min': np.min(confidence),
        'confidence_max': np.max(confidence),
        'entropy_mean': np.mean(entropy),
        'entropy_std': np.std(entropy),
        'entropy_min': np.min(entropy),
        'entropy_max': np.max(entropy),
    }
    
    # Correlation
    correlation, p_value = stats.pearsonr(confidence, entropy)
    stats_dict['correlation_confidence_entropy'] = correlation
    stats_dict['correlation_p_value'] = p_value
    
    # Uncertainty tiers
    low_conf = np.sum(confidence < 0.5)
    medium_conf = np.sum((confidence >= 0.5) & (confidence < 0.75))
    high_conf = np.sum(confidence >= 0.75)
    
    stats_dict['low_confidence_count'] = low_conf
    stats_dict['medium_confidence_count'] = medium_conf
    stats_dict['high_confidence_count'] = high_conf
    
    # Entropy tiers
    low_entropy = np.sum(entropy < 0.75)
    medium_entropy = np.sum((entropy >= 0.75) & (entropy < 1.0))
    high_entropy = np.sum(entropy >= 1.0)
    
    stats_dict['low_entropy_count'] = low_entropy
    stats_dict['medium_entropy_count'] = medium_entropy
    stats_dict['high_entropy_count'] = high_entropy
    
    # High uncertainty cases (low confidence AND high entropy)
    high_uncertainty = np.sum((confidence < 0.6) & (entropy > 1.0))
    stats_dict['high_uncertainty_cases'] = high_uncertainty
    
    # Low uncertainty cases (high confidence AND low entropy)
    low_uncertainty = np.sum((confidence >= 0.75) & (entropy < 0.85))
    stats_dict['low_uncertainty_cases'] = low_uncertainty
    
    return stats_dict, confidence, entropy


def generate_visualizations(df, confidence, entropy, output_prefix='uncertainty_analysis'):
    """Generate visualization plots."""
    
    fig = plt.figure(figsize=(16, 10), dpi=120)
    fig.suptitle('Episteme AI — Uncertainty Patterns Analysis', 
                 fontsize=16, fontweight='bold')
    
    gs = GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3)
    
    # 1. Confidence Distribution
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.hist(confidence * 100, bins=30, color='#1f77b4', alpha=0.7, edgecolor='black')
    ax1.axvline(np.mean(confidence) * 100, color='red', linestyle='--', linewidth=2, label='Mean')
    ax1.set_xlabel('Confidence (%)')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Confidence Distribution')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Entropy Distribution
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.hist(entropy, bins=30, color='#ff7f0e', alpha=0.7, edgecolor='black')
    ax2.axvline(np.mean(entropy), color='red', linestyle='--', linewidth=2, label='Mean')
    ax2.set_xlabel('Entropy')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Entropy Distribution')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Confidence vs Entropy Scatter
    ax3 = fig.add_subplot(gs[0, 2])
    scatter = ax3.scatter(confidence * 100, entropy, c=confidence * 100, 
                         cmap='RdYlGn', alpha=0.6, s=50, edgecolor='black', linewidth=0.5)
    ax3.set_xlabel('Confidence (%)')
    ax3.set_ylabel('Entropy')
    ax3.set_title('Confidence vs Entropy Relationship')
    plt.colorbar(scatter, ax=ax3, label='Confidence (%)')
    ax3.grid(True, alpha=0.3)
    
    # 4. Confidence Tiers
    ax4 = fig.add_subplot(gs[1, 0])
    low = np.sum(confidence < 0.5)
    medium = np.sum((confidence >= 0.5) & (confidence < 0.75))
    high = np.sum(confidence >= 0.75)
    tiers = [low, medium, high]
    labels = [f'Low\n(<50%)\n{low}', f'Medium\n(50-75%)\n{medium}', f'High\n(≥75%)\n{high}']
    colors = ['#d62728', '#ff7f0e', '#2ca02c']
    ax4.bar(labels, tiers, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax4.set_ylabel('Count')
    ax4.set_title('Confidence Tiers')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 5. Entropy Tiers
    ax5 = fig.add_subplot(gs[1, 1])
    low_e = np.sum(entropy < 0.75)
    medium_e = np.sum((entropy >= 0.75) & (entropy < 1.0))
    high_e = np.sum(entropy >= 1.0)
    entropy_tiers = [low_e, medium_e, high_e]
    labels_e = [f'Low\n(<0.75)\n{low_e}', f'Medium\n(0.75-1.0)\n{medium_e}', f'High\n(≥1.0)\n{high_e}']
    ax5.bar(labels_e, entropy_tiers, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax5.set_ylabel('Count')
    ax5.set_title('Entropy Tiers')
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 6. Uncertainty Classification
    ax6 = fig.add_subplot(gs[1, 2])
    high_unc = np.sum((confidence < 0.6) & (entropy > 1.0))
    medium_unc = np.sum(((confidence >= 0.6) & (confidence < 0.75)) | 
                        ((entropy >= 0.85) & (entropy <= 1.0)))
    low_unc = np.sum((confidence >= 0.75) & (entropy < 0.85))
    
    unc_data = [high_unc, medium_unc, low_unc]
    unc_labels = [f'High\n{high_unc}', f'Medium\n{medium_unc}', f'Low\n{low_unc}']
    unc_colors = ['#d62728', '#ffa500', '#2ca02c']
    wedges, texts, autotexts = ax6.pie(unc_data, labels=unc_labels, autopct='%1.1f%%',
                                         colors=unc_colors, startangle=90)
    ax6.set_title('Overall Uncertainty Classification')
    
    plt.savefig(f'{output_prefix}_plots.png', dpi=300, bbox_inches='tight')
    print(f"✓ Visualizations saved to: {output_prefix}_plots.png")


def generate_html_report(df, stats_dict, confidence, entropy, output_path='uncertainty_analysis_report.html'):
    """Generate comprehensive HTML report."""
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Episteme AI — Uncertainty Patterns Analysis Report</title>
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #667eea;
        }}
        .metric-card h3 {{
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 10px;
            letter-spacing: 1px;
        }}
        .metric-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .metric-card .subtext {{
            font-size: 0.85em;
            color: #666;
            margin-top: 10px;
        }}
        section {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        section h2 {{
            color: #667eea;
            font-size: 1.5em;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .stats-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .stats-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        .stats-table td:first-child {{
            font-weight: 600;
            color: #667eea;
            width: 40%;
        }}
        .stats-table tr:hover {{
            background: #f9f9f9;
        }}
        .highlight {{
            background: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            border-radius: 4px;
            margin: 15px 0;
        }}
        .confidence-low {{ background: #ffebee; border-left-color: #d32f2f; }}
        .confidence-medium {{ background: #fff3e0; border-left-color: #f57c00; }}
        .confidence-high {{ background: #e8f5e9; border-left-color: #388e3c; }}
        .correlation {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
        }}
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
            <h1>📊 Uncertainty Patterns Analysis Report</h1>
            <p>Episteme AI — Deep dive into confidence and entropy distributions across {stats_dict['n_samples']} Q&A samples</p>
        </header>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Total Samples</h3>
                <div class="value">{stats_dict['n_samples']}</div>
            </div>
            <div class="metric-card">
                <h3>Mean Confidence</h3>
                <div class="value">{stats_dict['confidence_mean']*100:.1f}%</div>
                <div class="subtext">Std: ±{stats_dict['confidence_std']*100:.1f}%</div>
            </div>
            <div class="metric-card">
                <h3>Mean Entropy</h3>
                <div class="value">{stats_dict['entropy_mean']:.3f}</div>
                <div class="subtext">Std: ±{stats_dict['entropy_std']:.3f}</div>
            </div>
            <div class="metric-card">
                <h3>Confidence-Entropy Correlation</h3>
                <div class="value">{stats_dict['correlation_confidence_entropy']:.3f}</div>
                <div class="subtext">p-value: {stats_dict['correlation_p_value']:.2e}</div>
            </div>
        </div>
        
        <section>
            <h2>📈 Confidence Analysis</h2>
            <table class="stats-table">
                <tr>
                    <td>Minimum Confidence</td>
                    <td>{stats_dict['confidence_min']*100:.2f}%</td>
                </tr>
                <tr>
                    <td>Maximum Confidence</td>
                    <td>{stats_dict['confidence_max']*100:.2f}%</td>
                </tr>
                <tr>
                    <td>Mean Confidence</td>
                    <td>{stats_dict['confidence_mean']*100:.2f}%</td>
                </tr>
                <tr>
                    <td>Standard Deviation</td>
                    <td>±{stats_dict['confidence_std']*100:.2f}%</td>
                </tr>
            </table>
            
            <h3 style="margin-top: 20px; color: #333;">Confidence Distribution by Tier:</h3>
            <div class="highlight confidence-low">
                <strong>🔴 Low Confidence (&lt;50%)</strong><br>
                {stats_dict['low_confidence_count']} samples ({stats_dict['low_confidence_count']/stats_dict['n_samples']*100:.1f}%)
            </div>
            <div class="highlight confidence-medium">
                <strong>🟡 Medium Confidence (50-75%)</strong><br>
                {stats_dict['medium_confidence_count']} samples ({stats_dict['medium_confidence_count']/stats_dict['n_samples']*100:.1f}%)
            </div>
            <div class="highlight confidence-high">
                <strong>🟢 High Confidence (≥75%)</strong><br>
                {stats_dict['high_confidence_count']} samples ({stats_dict['high_confidence_count']/stats_dict['n_samples']*100:.1f}%)
            </div>
        </section>
        
        <section>
            <h2>🌊 Entropy Analysis</h2>
            <table class="stats-table">
                <tr>
                    <td>Minimum Entropy</td>
                    <td>{stats_dict['entropy_min']:.4f}</td>
                </tr>
                <tr>
                    <td>Maximum Entropy</td>
                    <td>{stats_dict['entropy_max']:.4f}</td>
                </tr>
                <tr>
                    <td>Mean Entropy</td>
                    <td>{stats_dict['entropy_mean']:.4f}</td>
                </tr>
                <tr>
                    <td>Standard Deviation</td>
                    <td>±{stats_dict['entropy_std']:.4f}</td>
                </tr>
            </table>
            
            <h3 style="margin-top: 20px; color: #333;">Entropy Distribution by Tier:</h3>
            <div class="highlight confidence-high">
                <strong>🟢 Low Entropy (&lt;0.75)</strong><br>
                {stats_dict['low_entropy_count']} samples ({stats_dict['low_entropy_count']/stats_dict['n_samples']*100:.1f}%)
            </div>
            <div class="highlight confidence-medium">
                <strong>🟡 Medium Entropy (0.75-1.0)</strong><br>
                {stats_dict['medium_entropy_count']} samples ({stats_dict['medium_entropy_count']/stats_dict['n_samples']*100:.1f}%)
            </div>
            <div class="highlight confidence-low">
                <strong>🔴 High Entropy (≥1.0)</strong><br>
                {stats_dict['high_entropy_count']} samples ({stats_dict['high_entropy_count']/stats_dict['n_samples']*100:.1f}%)
            </div>
        </section>
        
        <section>
            <h2>🔗 Confidence-Entropy Relationship</h2>
            <div class="correlation">
                <strong>Pearson Correlation Coefficient: {stats_dict['correlation_confidence_entropy']:.4f}</strong><br>
                <strong>P-value: {stats_dict['correlation_p_value']:.2e}</strong><br><br>
                <em>Interpretation:</em> There is a <strong>{'negative' if stats_dict['correlation_confidence_entropy'] < 0 else 'positive'}</strong> correlation 
                between confidence and entropy. This means that as confidence {'decreases' if stats_dict['correlation_confidence_entropy'] < 0 else 'increases'}, 
                entropy tends to {'increase' if stats_dict['correlation_confidence_entropy'] < 0 else 'decrease'}.
            </div>
        </section>
        
        <section>
            <h2>⚠️ Uncertainty Classification</h2>
            <table class="stats-table">
                <tr>
                    <td>High Uncertainty Cases</td>
                    <td><strong>{stats_dict['high_uncertainty_cases']}</strong> (Low Conf &lt;60% AND High Entropy &gt;1.0)</td>
                </tr>
                <tr>
                    <td>Low Uncertainty Cases</td>
                    <td><strong>{stats_dict['low_uncertainty_cases']}</strong> (High Conf ≥75% AND Low Entropy &lt;0.85)</td>
                </tr>
            </table>
            <div class="highlight confidence-low" style="margin-top: 15px;">
                <strong>⚠️ High Uncertainty Cases: {stats_dict['high_uncertainty_cases']}</strong><br>
                These are queries where the model is both less confident AND producing high entropy outputs.
                These merit additional review and may require human expert validation.
            </div>
        </section>
        
        <section>
            <h2>📊 Visualizations</h2>
            <p>Below are comprehensive visualizations of uncertainty patterns:</p>
            <img src="uncertainty_analysis_plots.png" alt="Uncertainty Analysis Plots">
        </section>
        
        <footer>
            <p>Generated by Episteme AI Analysis Suite | {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ HTML Report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze uncertainty patterns in Episteme AI dataset"
    )
    parser.add_argument(
        "--json",
        default="episteme_uncertainty_dataset.json",
        help="Path to uncertainty dataset JSON"
    )
    parser.add_argument(
        "--output",
        default="uncertainty_analysis_report.html",
        help="Output HTML report path"
    )
    
    args = parser.parse_args()
    
    print(f"Loading data from: {args.json}")
    df = load_json_data(args.json)
    
    print(f"Analyzing {len(df)} samples...")
    stats_dict, confidence, entropy = analyze_uncertainty_patterns(df)
    
    # Print summary to console
    print("\n" + "="*60)
    print("  UNCERTAINTY PATTERNS ANALYSIS — SUMMARY")
    print("="*60)
    print(f"Samples: {stats_dict['n_samples']}")
    print(f"Confidence: {stats_dict['confidence_mean']*100:.2f}% ± {stats_dict['confidence_std']*100:.2f}%")
    print(f"Entropy: {stats_dict['entropy_mean']:.4f} ± {stats_dict['entropy_std']:.4f}")
    print(f"Confidence-Entropy Correlation: {stats_dict['correlation_confidence_entropy']:.4f}")
    print(f"High Uncertainty Cases: {stats_dict['high_uncertainty_cases']}")
    print(f"Low Uncertainty Cases: {stats_dict['low_uncertainty_cases']}")
    print("="*60 + "\n")
    
    # Generate visualizations
    generate_visualizations(df, confidence, entropy, output_prefix='uncertainty_analysis')
    
    # Generate report
    generate_html_report(df, stats_dict, confidence, entropy, output_path=args.output)


if __name__ == "__main__":
    main()
