#!/usr/bin/env python3
"""
Episteme AI — Error Analysis & Answer Comparison
Compare model predictions with TruthfulQA ground truth and identify errors.

Usage:
    python error_analysis.py
    python error_analysis.py --episteme episteme_empirical_results.csv --truthqa TruthfulQA.csv --output error_report.html
"""

import argparse
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from difflib import SequenceMatcher
from matplotlib.gridspec import GridSpec


def load_data(episteme_csv, truthqa_csv):
    """Load both datasets."""
    episteme_df = pd.read_csv(episteme_csv)
    truthqa_df = pd.read_csv(truthqa_csv)
    return episteme_df, truthqa_df


def similarity_ratio(a, b):
    """Calculate string similarity ratio."""
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()


def match_questions(episteme_df, truthqa_df):
    """Match questions between datasets using similarity."""
    matches = []
    
    for idx, ep_row in episteme_df.iterrows():
        ep_question = str(ep_row['Query']).lower().strip()
        
        best_match = None
        best_score = 0
        
        for tidx, tq_row in truthqa_df.iterrows():
            tq_question = str(tq_row['Question']).lower().strip()
            score = similarity_ratio(ep_question, tq_question)
            
            if score > best_score:
                best_score = score
                best_match = tidx
        
        if best_score > 0.85:  # Confidence threshold for matching
            matches.append({
                'episteme_idx': idx,
                'truthqa_idx': best_match,
                'match_score': best_score,
                'question': ep_row['Query'],
                'ep_raw': ep_row['Raw_Output'],
                'ep_calibrated': ep_row['Calibrated_Output'],
                'ep_confidence': ep_row['Confidence_Pct'],
                'ep_is_correct': ep_row['Is_Correct'],
                'ep_audit_status': ep_row['Audit_Status'],
                'truthqa_best_answer': truthqa_df.loc[best_match, 'Best Answer'],
                'truthqa_correct_answers': truthqa_df.loc[best_match, 'Correct Answers'],
                'truthqa_incorrect_answers': truthqa_df.loc[best_match, 'Incorrect Answers'],
                'truthqa_category': truthqa_df.loc[best_match, 'Category'],
                'truthqa_type': truthqa_df.loc[best_match, 'Type'],
            })
    
    return pd.DataFrame(matches)


def analyze_errors(matches_df):
    """Analyze errors in the matched data."""
    
    errors = []
    
    for idx, row in matches_df.iterrows():
        is_error = (row['ep_is_correct'] == 0)
        
        if is_error:
            error = {
                'question': row['question'],
                'category': row['truthqa_category'],
                'type': row['truthqa_type'],
                'confidence': row['ep_confidence'],
                'audit_status': row['ep_audit_status'],
                'model_answer': row['ep_raw'][:200],  # First 200 chars
                'best_answer': row['truthqa_best_answer'],
                'model_answer_full': row['ep_raw'],
                'is_hallucination': 'hallucination' in row['ep_audit_status'].lower() if pd.notna(row['ep_audit_status']) else False,
            }
            errors.append(error)
    
    return pd.DataFrame(errors)


def generate_visualizations(matches_df, errors_df, output_prefix='error_analysis'):
    """Generate error analysis visualizations."""
    
    fig = plt.figure(figsize=(16, 12), dpi=120)
    fig.suptitle('Episteme AI — Error Analysis & Answer Comparison', 
                 fontsize=18, fontweight='bold')
    
    gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.3)
    
    # 1. Error Rate by Category
    ax1 = fig.add_subplot(gs[0, 0])
    error_by_cat = errors_df['category'].value_counts()
    colors_cat = ['#d62728' if x > 5 else '#ff7f0e' if x > 2 else '#ffd700' for x in error_by_cat.values]
    error_by_cat.plot(kind='barh', ax=ax1, color=colors_cat, edgecolor='black')
    ax1.set_xlabel('Error Count')
    ax1.set_title('Errors by Category', fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='x')
    
    # 2. Error Rate by Type
    ax2 = fig.add_subplot(gs[0, 1])
    error_by_type = errors_df['type'].value_counts()
    colors_type = ['#d62728', '#ff7f0e', '#ffd700']
    error_by_type.plot(kind='bar', ax=ax2, color=colors_type[:len(error_by_type)], edgecolor='black')
    ax2.set_ylabel('Error Count')
    ax2.set_xlabel('Question Type')
    ax2.set_title('Errors by Type', fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 3. Confidence Distribution in Errors
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.hist(errors_df['confidence'], bins=20, color='#d62728', alpha=0.7, edgecolor='black')
    ax3.axvline(errors_df['confidence'].mean(), color='red', linestyle='--', linewidth=2, label='Mean')
    ax3.set_xlabel('Confidence (%)')
    ax3.set_ylabel('Frequency')
    ax3.set_title('Error Confidence Distribution', fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Audit Status in Errors
    ax4 = fig.add_subplot(gs[1, 1])
    audit_status = errors_df['audit_status'].value_counts()
    colors_audit = ['#ff7f0e', '#2ca02c']
    ax4.pie(audit_status.values, labels=audit_status.index, autopct='%1.1f%%',
           colors=colors_audit[:len(audit_status)], startangle=90)
    ax4.set_title('Audit Status in Errors', fontweight='bold')
    
    # 5. Error vs Correct by Confidence
    ax5 = fig.add_subplot(gs[2, 0])
    conf_bins = np.arange(0, 105, 10)
    error_conf = errors_df['confidence'].values
    correct_conf = matches_df[matches_df['ep_is_correct'] == 1]['ep_confidence'].values
    ax5.hist(error_conf, bins=conf_bins, alpha=0.6, label='Errors', color='#d62728', edgecolor='black')
    ax5.hist(correct_conf, bins=conf_bins, alpha=0.6, label='Correct', color='#2ca02c', edgecolor='black')
    ax5.set_xlabel('Confidence (%)')
    ax5.set_ylabel('Count')
    ax5.set_title('Error vs Correct by Confidence', fontweight='bold')
    ax5.legend()
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 6. Summary Stats
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.axis('off')
    total = len(matches_df)
    error_count = len(errors_df)
    error_rate = (error_count / total) * 100
    
    summary_text = f"""
ERROR ANALYSIS SUMMARY

Total Matched Q&A: {total}
Total Errors: {error_count}
Error Rate: {error_rate:.1f}%
Correct Rate: {100-error_rate:.1f}%

Mean Error Confidence: {errors_df['confidence'].mean():.1f}%
Mean Correct Confidence: {matches_df[matches_df['ep_is_correct']==1]['ep_confidence'].mean():.1f}%

Top Error Categories:
"""
    
    for cat, count in error_by_cat.head(3).items():
        summary_text += f"\n  • {cat}: {count} errors"
    
    summary_text += f"""

Top Problematic Types:
"""
    
    for typ, count in error_by_type.head(2).items():
        summary_text += f"\n  • {typ}: {count} errors"
    
    ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes, fontsize=10,
            verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='#fff3cd', alpha=0.8, pad=1))
    
    plt.savefig(f'{output_prefix}_plots.png', dpi=300, bbox_inches='tight')
    print(f"✓ Error analysis plots saved to: {output_prefix}_plots.png")


def generate_html_error_report(matches_df, errors_df, output_path='error_report.html'):
    """Generate comprehensive HTML error report."""
    
    total = len(matches_df)
    error_count = len(errors_df)
    error_rate = (error_count / total) * 100
    
    # Top error categories
    error_by_cat = errors_df['category'].value_counts().head(5)
    error_cat_rows = ""
    for cat, count in error_by_cat.items():
        pct = (count / error_count) * 100
        error_cat_rows += f"<tr><td>{cat}</td><td>{count}</td><td>{pct:.1f}%</td></tr>"
    
    # Top error types
    error_by_type = errors_df['type'].value_counts().head(5)
    error_type_rows = ""
    for typ, count in error_by_type.items():
        pct = (count / error_count) * 100
        error_type_rows += f"<tr><td>{typ}</td><td>{count}</td><td>{pct:.1f}%</td></tr>"
    
    # Sample errors
    sample_errors = errors_df.head(20)
    sample_rows = ""
    for idx, err in sample_errors.iterrows():
        sample_rows += f"""
        <tr>
            <td style="max-width: 200px; word-wrap: break-word;">{err['question'][:80]}...</td>
            <td>{err['category']}</td>
            <td>{err['type']}</td>
            <td>{err['confidence']:.1f}%</td>
            <td><span class="status-badge bad">✗</span></td>
        </tr>
        """
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Episteme AI — Error Analysis Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%);
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
            border-left: 4px solid #e74c3c;
        }}
        .metric-card h3 {{
            color: #c0392b;
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
            color: #c0392b;
            font-size: 1.5em;
            margin-bottom: 20px;
            border-bottom: 3px solid #e74c3c;
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
            background: #f8d7da;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #e74c3c;
            color: #c0392b;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:hover {{
            background: #fff5f5;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .status-badge.bad {{ background: #f8d7da; color: #721c24; }}
        .status-badge.warning {{ background: #fff3cd; color: #856404; }}
        .highlight {{
            background: #f8d7da;
            padding: 15px;
            border-left: 4px solid #e74c3c;
            border-radius: 4px;
            margin: 15px 0;
        }}
        .warning-box {{
            background: #fff3cd;
            padding: 15px;
            border-left: 4px solid #f39c12;
            border-radius: 4px;
            margin: 15px 0;
        }}
        .do-not-answer {{
            background: #f8d7da;
            padding: 15px;
            border-left: 4px solid #e74c3c;
            border-radius: 4px;
            margin: 15px 0;
            border-radius: 4px;
        }}
        .do-not-answer strong {{
            color: #c0392b;
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
        .confidence-low {{ color: #e74c3c; font-weight: 600; }}
        .confidence-high {{ color: #27ae60; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔴 Error Analysis Report</h1>
            <p>Episteme AI — Comprehensive error analysis comparing model predictions with TruthfulQA ground truth</p>
        </header>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Total Q&A Matched</h3>
                <div class="value">{total}</div>
                <div class="subtext">Similarity threshold: 0.85</div>
            </div>
            <div class="metric-card">
                <h3>Total Errors</h3>
                <div class="value">{error_count}</div>
                <div class="subtext">Incorrect predictions</div>
            </div>
            <div class="metric-card">
                <h3>Error Rate</h3>
                <div class="value">{error_rate:.1f}%</div>
                <div class="subtext">Accuracy: {100-error_rate:.1f}%</div>
            </div>
            <div class="metric-card">
                <h3>Mean Error Confidence</h3>
                <div class="value">{errors_df['confidence'].mean():.1f}%</div>
                <div class="subtext">Avg confidence when wrong</div>
            </div>
        </div>
        
        <section>
            <h2>📊 Error Distribution Analysis</h2>
            
            <h3 style="margin-top: 20px; color: #333;">Errors by Category</h3>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Error Count</th>
                            <th>% of Total Errors</th>
                        </tr>
                    </thead>
                    <tbody>
                        {error_cat_rows}
                    </tbody>
                </table>
            </div>
            
            <h3 style="margin-top: 20px; color: #333;">Errors by Type</h3>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Error Count</th>
                            <th>% of Total Errors</th>
                        </tr>
                    </thead>
                    <tbody>
                        {error_type_rows}
                    </tbody>
                </table>
            </div>
        </section>
        
        <section>
            <h2>⚠️ What NOT To Answer — Risk Categories</h2>
            
            <div class="highlight">
                <strong>🔴 HIGH RISK CATEGORIES</strong><br>
                The model performs poorly on these categories and should flag for human review:
                <ul style="margin-top: 10px; margin-left: 20px;">
"""
    
    for cat, count in error_by_cat.head(3).items():
        pct = (count / error_count) * 100
        html_content += f"""
                    <li><strong>{cat}</strong>: {count} errors ({pct:.1f}%)</li>
"""
    
    html_content += f"""
                </ul>
            </div>
            
            <div class="warning-box">
                <strong>⚠️ RECOMMENDATION FOR HIGH-RISK CATEGORIES:</strong><br>
                1. Flag answers in these categories as UNCERTAIN<br>
                2. Request human expert review before publishing<br>
                3. Do not use high confidence scores in these domains<br>
                4. Consider routing to specialized knowledge bases
            </div>
            
            <div class="do-not-answer">
                <strong>🚫 DO NOT ANSWER CONFIDENTLY:</strong><br>
                Categories with high error rates should trigger:
                <ul style="margin-top: 10px; margin-left: 20px;">
                    <li>Return low confidence even if model is uncertain</li>
                    <li>Add explicit disclaimer about domain limitations</li>
                    <li>Recommend human fact-checking</li>
                    <li>Suggest alternative data sources</li>
                </ul>
            </div>
        </section>
        
        <section>
            <h2>📋 Sample Error Cases (First 20)</h2>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Question</th>
                            <th>Category</th>
                            <th>Type</th>
                            <th>Confidence</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sample_rows}
                    </tbody>
                </table>
            </div>
        </section>
        
        <section>
            <h2>📊 Visualizations</h2>
            <p>Comprehensive error analysis charts:</p>
            <img src="error_analysis_plots.png" alt="Error Analysis Plots">
        </section>
        
        <section>
            <h2>🎯 Key Insights & Recommendations</h2>
            
            <div class="warning-box">
                <strong>1. Confidence Miscalibration</strong><br>
                The model shows high confidence even when making errors. 
                Mean error confidence: <span class="confidence-low">{errors_df['confidence'].mean():.1f}%</span><br>
                <em>Action:</em> Implement confidence scaling; reduce confidence scores by 20-30% in high-risk categories.
            </div>
            
            <div class="warning-box">
                <strong>2. Category-Specific Failures</strong><br>
                Certain categories ({error_by_cat.index[0]}, {error_by_cat.index[1] if len(error_by_cat) > 1 else 'N/A'}) show systematic errors.<br>
                <em>Action:</em> Invest in domain-specific training data and fact-checking pipelines.
            </div>
            
            <div class="warning-box">
                <strong>3. Type-Specific Vulnerabilities</strong><br>
                Type '{error_by_type.index[0]}' shows highest error concentration.<br>
                <em>Action:</em> Add special handling, validation, and review steps for this question type.
            </div>
            
            <div class="do-not-answer">
                <strong>4. IMMEDIATE ACTION ITEMS</strong><br>
                <ul style="margin-top: 10px; margin-left: 20px;">
                    <li>❌ Do NOT answer {error_by_cat.index[0]} questions with high confidence</li>
                    <li>❌ Flag all {error_by_type.index[0]} questions for human review</li>
                    <li>✓ Implement multi-layer fact-checking for identified risk categories</li>
                    <li>✓ Train specialized models for high-error domains</li>
                    <li>✓ Set maximum confidence thresholds per category</li>
                </ul>
            </div>
        </section>
        
        <footer>
            <p>Generated by Episteme AI Error Analysis Suite | {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Error Report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze errors by comparing model answers with TruthfulQA"
    )
    parser.add_argument(
        "--episteme",
        default="episteme_empirical_results.csv",
        help="Path to Episteme empirical results CSV"
    )
    parser.add_argument(
        "--truthqa",
        default="TruthfulQA.csv",
        help="Path to TruthfulQA CSV"
    )
    parser.add_argument(
        "--output",
        default="error_report.html",
        help="Output HTML report path"
    )
    
    args = parser.parse_args()
    
    print(f"Loading data...")
    episteme_df, truthqa_df = load_data(args.episteme, args.truthqa)
    
    print(f"Matching questions...")
    matches_df = match_questions(episteme_df, truthqa_df)
    
    print(f"Analyzing errors...")
    errors_df = analyze_errors(matches_df)
    
    # Print summary
    print("\n" + "="*70)
    print("  ERROR ANALYSIS — SUMMARY")
    print("="*70)
    print(f"Total Matched Q&A: {len(matches_df)}")
    print(f"Total Errors: {len(errors_df)}")
    print(f"Error Rate: {len(errors_df)/len(matches_df)*100:.1f}%")
    print(f"Mean Error Confidence: {errors_df['confidence'].mean():.1f}%")
    print(f"\nTop Error Categories:")
    for cat, count in errors_df['category'].value_counts().head(3).items():
        print(f"  • {cat}: {count} errors")
    print(f"\nTop Error Types:")
    for typ, count in errors_df['type'].value_counts().head(3).items():
        print(f"  • {typ}: {count} errors")
    print("="*70 + "\n")
    
    # Generate outputs
    generate_visualizations(matches_df, errors_df, output_prefix='error_analysis')
    generate_html_error_report(matches_df, errors_df, output_path=args.output)


if __name__ == "__main__":
    main()
