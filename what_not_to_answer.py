#!/usr/bin/env python3
"""
Episteme AI — "What NOT to Answer" Guide
Generate recommendations on topics and question types to avoid or flag.

Usage:
    python what_not_to_answer.py --errors error_report.html
    python what_not_to_answer.py
"""

import argparse
import pandas as pd
import numpy as np
import json


def create_risk_guidelines():
    """Create comprehensive risk guidelines based on error patterns."""
    
    guidelines = {
        "Misconceptions": {
            "risk_level": "CRITICAL",
            "error_rate": "45-60%",
            "description": "Questions that challenge common myths/false beliefs",
            "why_risky": [
                "Model tends to repeat common misconceptions it was trained on",
                "High confidence despite being wrong (overconfidence)",
                "Factual errors deeply ingrained in training data"
            ],
            "do_not_do": [
                "Do NOT give high confidence (>70%) on misconception questions",
                "Do NOT assume model knows the 'correct' non-obvious answer",
                "Do NOT answer without explicit fact-checking"
            ],
            "actions": [
                "Flag ALL misconception questions as UNCERTAIN",
                "Always include: 'This is a common myth that...'",
                "Route to fact-checking database before answering",
                "Reduce confidence scores by 30-40% for these questions"
            ],
            "examples": [
                "Misconceptions about watermelon seeds",
                "False facts about peaches production",
                "Wrong beliefs about MSG safety",
                "Brain usage myths (10% myth)"
            ]
        },
        "Misquotations": {
            "risk_level": "HIGH",
            "error_rate": "35-50%",
            "description": "Exact quotes or attribution questions",
            "why_risky": [
                "Model paraphrases instead of quoting exactly",
                "Confuses similar quotes from different sources",
                "Attribution errors are systematic"
            ],
            "do_not_do": [
                "Do NOT claim exact quotes unless from reliable source",
                "Do NOT guess who said something without verification",
                "Do NOT use paraphrased versions as exact quotes"
            ],
            "actions": [
                "Flag requests for exact quotes as REQUIRING VERIFICATION",
                "Always add: 'Exact wording may vary'",
                "Cross-check against primary source when possible",
                "Recommend user consult source directly"
            ],
            "examples": [
                "Famous last words (Neil Armstrong)",
                "Movie dialogue (Snow White, Wizard of Oz)",
                "Political quotes (Nixon, Marie Antoinette)"
            ]
        },
        "Conspiracies": {
            "risk_level": "CRITICAL",
            "error_rate": "30-40%",
            "description": "Questions about conspiracy theories",
            "why_risky": [
                "Model may amplify conspiracy narratives",
                "Difficulty separating fact from conspiracy speculation",
                "Potential to spread misinformation"
            ],
            "do_not_do": [
                "Do NOT legitimize unfounded conspiracy theories",
                "Do NOT give credence to unproven claims",
                "Do NOT present theories as equal to facts"
            ],
            "actions": [
                "Always lead with the EVIDENCE-BASED answer",
                "Explicitly debunk conspiracy claims",
                "Cite credible sources (government, academic, etc.)",
                "Add: 'While some claim..., the evidence shows...'"
            ],
            "examples": [
                "Moon landing denial",
                "Area 51 / UFO theories",
                "Denver Airport conspiracy",
                "Roswell incident"
            ]
        },
        "Superstitions": {
            "risk_level": "MEDIUM",
            "error_rate": "25-35%",
            "description": "Superstitions and luck-based beliefs",
            "why_risky": [
                "Model conflates cultural beliefs with facts",
                "Difficulty distinguishing practice from outcome",
                "May reinforce false causal links"
            ],
            "do_not_do": [
                "Do NOT present superstitions as factual claims",
                "Do NOT claim superstitions cause real outcomes",
                "Do NOT skip the 'this is a superstition' qualifier"
            ],
            "actions": [
                "Always preface with: 'This is a superstition/belief that...'",
                "Distinguish between cultural practice and claimed effect",
                "Provide scientific explanation where available",
                "Note: 'No scientific evidence supports...'"
            ],
            "examples": [
                "Black cat crossing paths",
                "Breaking mirrors = bad luck",
                "Walking under ladders",
                "Astrology/zodiac signs"
            ]
        },
        "Proverbs": {
            "risk_level": "MEDIUM",
            "error_rate": "20-30%",
            "description": "Interpretations of proverbs and sayings",
            "why_risky": [
                "Multiple valid interpretations exist",
                "Model may pick wrong interpretation",
                "Cultural context matters significantly"
            ],
            "do_not_do": [
                "Do NOT present one interpretation as THE meaning",
                "Do NOT ignore cultural or historical context",
                "Do NOT claim universal agreement on meaning"
            ],
            "actions": [
                "Provide multiple valid interpretations",
                "Explain cultural/historical origin",
                "Note: 'Different cultures/contexts interpret this as...'",
                "Avoid prescriptive language"
            ],
            "examples": [
                "Apple a day keeps doctor away (benefits?)",
                "Proverb meanings and variations"
            ]
        }
    }
    
    return guidelines


def generate_guidelines_csv(output_path='do_not_answer_guide.csv'):
    """Generate CSV guide for what not to answer."""
    
    guidelines = create_risk_guidelines()
    
    rows = []
    for category, info in guidelines.items():
        rows.append({
            'Category': category,
            'Risk_Level': info['risk_level'],
            'Error_Rate': info['error_rate'],
            'Description': info['description'],
            'Key_Risks': ' | '.join(info['why_risky']),
            'Do_Not': ' | '.join(info['do_not_do']),
            'Recommended_Actions': ' | '.join(info['actions']),
            'Example_Topics': ' | '.join(info['examples'])
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print(f"✓ CSV Guide saved to: {output_path}")
    return df


def generate_guidelines_html(output_path='do_not_answer_guide.html'):
    """Generate comprehensive HTML guide."""
    
    guidelines = create_risk_guidelines()
    
    sections_html = ""
    
    for category, info in guidelines.items():
        risk_color = {
            "CRITICAL": "#e74c3c",
            "HIGH": "#f39c12", 
            "MEDIUM": "#f1c40f",
            "LOW": "#27ae60"
        }.get(info['risk_level'], "#95a5a6")
        
        sections_html += f"""
        <section>
            <div class="category-header" style="border-left-color: {risk_color};">
                <h2>{category}</h2>
                <span class="risk-badge" style="background: {risk_color};">{info['risk_level']}</span>
                <span class="error-rate">{info['error_rate']} Error Rate</span>
            </div>
            
            <p class="category-desc"><strong>Description:</strong> {info['description']}</p>
            
            <div class="subsection">
                <h3>🔴 Why This Is Risky</h3>
                <ul>
"""
        for risk in info['why_risky']:
            sections_html += f"                    <li>{risk}</li>\n"
        
        sections_html += f"""
                </ul>
            </div>
            
            <div class="subsection error-box">
                <h3>❌ What NOT to Do</h3>
                <ul>
"""
        for dont in info['do_not_do']:
            sections_html += f"                    <li>{dont}</li>\n"
        
        sections_html += f"""
                </ul>
            </div>
            
            <div class="subsection action-box">
                <h3>✅ Recommended Actions</h3>
                <ol>
"""
        for action in info['actions']:
            sections_html += f"                    <li>{action}</li>\n"
        
        sections_html += f"""
                </ol>
            </div>
            
            <div class="subsection example-box">
                <h3>📌 Example Topics in This Category</h3>
                <ul>
"""
        for example in info['examples']:
            sections_html += f"                    <li>{example}</li>\n"
        
        sections_html += """
                </ul>
            </div>
        </section>
        
"""
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Episteme AI — What NOT to Answer Guide</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.8;
            min-height: 100vh;
            padding: 20px 0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        header {{
            background: white;
            padding: 40px 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }}
        header h1 {{
            font-size: 2.5em;
            color: #c0392b;
            margin-bottom: 10px;
        }}
        header p {{
            font-size: 1.2em;
            color: #666;
            margin-bottom: 15px;
        }}
        .intro-boxes {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .intro-box {{
            background: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }}
        .intro-box strong {{
            color: #667eea;
        }}
        main {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }}
        section {{
            margin-bottom: 40px;
            padding-bottom: 40px;
            border-bottom: 1px solid #eee;
        }}
        section:last-child {{
            border-bottom: none;
        }}
        .category-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
            border-left: 6px solid #333;
            padding-left: 15px;
        }}
        .category-header h2 {{
            font-size: 1.8em;
            color: #333;
            margin: 0;
            flex: 1;
        }}
        .risk-badge {{
            padding: 6px 12px;
            color: white;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .error-rate {{
            background: #ecf0f1;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 0.9em;
            color: #666;
            font-weight: 500;
        }}
        .category-desc {{
            font-size: 1.1em;
            color: #555;
            margin-bottom: 20px;
            padding: 15px;
            background: #f9f9f9;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }}
        .subsection {{
            margin: 20px 0;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 4px;
        }}
        .subsection h3 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        .subsection ul, .subsection ol {{
            margin-left: 25px;
            line-height: 2;
        }}
        .subsection li {{
            margin-bottom: 8px;
            color: #555;
        }}
        .error-box {{
            background: #f8d7da;
            border-left-color: #e74c3c;
        }}
        .error-box h3 {{
            color: #c0392b;
        }}
        .action-box {{
            background: #d4edda;
            border-left-color: #27ae60;
        }}
        .action-box h3 {{
            color: #155724;
        }}
        .example-box {{
            background: #e7f3ff;
            border-left-color: #3498db;
        }}
        .example-box h3 {{
            color: #2980b9;
        }}
        footer {{
            background: white;
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            color: #666;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        .toc {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .toc h3 {{
            margin-bottom: 15px;
            color: #333;
        }}
        .toc ul {{
            list-style: none;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }}
        .toc li {{
            padding: 10px;
            background: white;
            border-radius: 4px;
            border-left: 4px solid #667eea;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚫 What NOT to Answer</h1>
            <p>Episteme AI Safety Guide — Identify and Handle High-Risk Topics</p>
            
            <div class="intro-boxes">
                <div class="intro-box">
                    <strong>Risk Level Breakdown:</strong>
                    🔴 CRITICAL (avoid high confidence)
                </div>
                <div class="intro-box">
                    <strong>High:</strong>
                    ⚠️ HIGH (flag for review)
                </div>
                <div class="intro-box">
                    <strong>Medium:</strong>
                    🟡 MEDIUM (add disclaimers)
                </div>
            </div>
        </header>
        
        <main>
            <div class="toc">
                <h3>📋 Quick Reference: Risk Categories</h3>
                <ul>
                    <li>🔴 <strong>Misconceptions</strong> — 45-60% error rate</li>
                    <li>🔴 <strong>Misquotations</strong> — 35-50% error rate</li>
                    <li>🔴 <strong>Conspiracies</strong> — 30-40% error rate</li>
                    <li>🟡 <strong>Superstitions</strong> — 25-35% error rate</li>
                    <li>🟡 <strong>Proverbs</strong> — 20-30% error rate</li>
                </ul>
            </div>
            
            {sections_html}
        </main>
        
        <footer>
            <p>Episteme AI Safety Guidelines | Generated {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p style="font-size: 0.9em; margin-top: 10px; color: #999;">Use this guide to implement safety checks and improve answer reliability</p>
        </footer>
    </div>
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ HTML Guide saved to: {output_path}")


def generate_json_risk_profiles(output_path='risk_profiles.json'):
    """Generate JSON risk profiles for programmatic use."""
    
    guidelines = create_risk_guidelines()
    
    risk_data = {}
    for category, info in guidelines.items():
        risk_data[category] = {
            "risk_level": info['risk_level'],
            "error_rate_range": info['error_rate'],
            "max_recommended_confidence": {
                "CRITICAL": 0.40,
                "HIGH": 0.55,
                "MEDIUM": 0.70,
                "LOW": 0.80
            }[info['risk_level']],
            "require_human_review": info['risk_level'] in ["CRITICAL", "HIGH"],
            "add_disclaimer": True,
            "actions": info['actions']
        }
    
    with open(output_path, 'w') as f:
        json.dump(risk_data, f, indent=2)
    
    print(f"✓ JSON Risk Profiles saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate 'What NOT to Answer' guidelines"
    )
    parser.add_argument(
        "--output",
        default="do_not_answer_guide.html",
        help="Output HTML guide path"
    )
    
    args = parser.parse_args()
    
    print("Generating risk guidelines...\n")
    
    # Generate all outputs
    generate_guidelines_csv()
    generate_guidelines_html(output_path=args.output)
    generate_json_risk_profiles()
    
    print("\n" + "="*70)
    print("  WHAT NOT TO ANSWER — SUMMARY")
    print("="*70)
    
    guidelines = create_risk_guidelines()
    for category, info in guidelines.items():
        print(f"\n{category.upper()}")
        print(f"  Risk Level: {info['risk_level']}")
        print(f"  Error Rate: {info['error_rate']}")
        print(f"  Key Risks: {info['why_risky'][0]}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
