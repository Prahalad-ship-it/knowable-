import os
import re
import json
from openai import OpenAI

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")
if not NVIDIA_API_KEY:
    print("Warning: NVIDIA_API_KEY is not set in environment variables")

NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

SYSTEM_PROMPT = """You are an advanced Research Agent engineered with calibrated epistemic humility. Unlike standard AI systems that output unearned confidence, your core cognitive architecture requires you to rigorously quantify what you know, what you do not know, and what you are uncertain about. Your goal is to move from high uncertainty to high certainty by identifying and filling your own knowledge gaps.

### COGNITIVE FRAMEWORK: EPISTEMIC HUMILITY
Before answering any complex prompt, you must evaluate your own confidence across three dimensions:
1. Data Sufficiency (Do I have the necessary facts?)
2. Logical Certainty (Is my reasoning sound or speculative?)
3. Edge-Case Risks (Where could this information fail?)

### OUTPUT STRUCTURE
You must structure every response using the following XML-style tags:

<confidence_score>
- [Overall Confidence: X/10]
- [Data Sufficiency: X/10]
- [Reasoning Certainty: X/10]
- [Justification]: A brief sentence explaining why you scored yourself this way.
</confidence_score>

<assumptions_and_gaps>
- List explicit assumptions you are making.
- List critical information or real-time data that you are missing.
</assumptions_and_gaps>

<calibrated_response>
Your actual answer here. If confidence is low (< 7/10), use caveated language like "The current data suggests..." or "A plausible hypothesis is..."
</calibrated_response>

<knowledge_gap_resolution>
If confidence is low or gaps exist, define exactly how to resolve it. Propose a specific technical strategy or external data fetch needed to turn this unknown into a known.
</knowledge_gap_resolution>"""


def extract_tag(text, tag):
    match = re.search(rf'<{tag}[^>]*>([\s\S]*?)</{tag}>', text, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def parse_scores(conf_block):
    def get_score(label):
        m = re.search(rf'{label}:\s*(\d+)', conf_block, re.IGNORECASE)
        return int(m.group(1)) if m else 5

    justification_match = re.search(r'\[Justification\][:\s]*([^\n\-]+)', conf_block, re.IGNORECASE)
    justification = justification_match.group(1).strip() if justification_match else ""

    return {
        "overall": get_score("Overall Confidence"),
        "data_sufficiency": get_score("Data Sufficiency"),
        "reasoning_certainty": get_score("Reasoning Certainty"),
        "justification": justification
    }


def query_agent(user_query: str) -> dict:
    response = client.chat.completions.create(
        model="meta/llama-3.1-8b-instruct",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ],
        temperature=0.3,
        max_tokens=1200
    )

    raw = response.choices[0].message.content

    conf_block = extract_tag(raw, "confidence_score")
    scores = parse_scores(conf_block)

    gaps_block = extract_tag(raw, "assumptions_and_gaps")
    gaps = [
        line.lstrip("-*• ").strip()
        for line in gaps_block.split("\n")
        if line.strip() and len(line.strip()) > 5
    ]

    calibrated = extract_tag(raw, "calibrated_response") or raw

    resolution_block = extract_tag(raw, "knowledge_gap_resolution")
    resolutions = [
        line.lstrip("-*•0123456789. ").strip()
        for line in resolution_block.split("\n")
        if line.strip() and len(line.strip()) > 5
    ]

    return {
        "scores": scores,
        "gaps": gaps,
        "calibrated_response": calibrated,
        "resolutions": resolutions,
        "raw": raw
    }


def confidence_label(score):
    if score >= 7:
        return "HIGH ✅"
    elif score >= 5:
        return "MODERATE ⚠️"
    return "LOW ❌"


def print_result(result):
    scores = result["scores"]
    print("\n" + "="*60)
    print("EPISTEMIC CONFIDENCE SCORES")
    print("="*60)
    print(f"  Overall Confidence : {scores['overall']}/10  {confidence_label(scores['overall'])}")
    print(f"  Data Sufficiency   : {scores['data_sufficiency']}/10  {confidence_label(scores['data_sufficiency'])}")
    print(f"  Reasoning Certainty: {scores['reasoning_certainty']}/10  {confidence_label(scores['reasoning_certainty'])}")
    if scores["justification"]:
        print(f"\n  Justification: {scores['justification']}")

    print("\n" + "-"*60)
    print("CALIBRATED RESPONSE")
    print("-"*60)
    print(result["calibrated_response"])

    if result["gaps"]:
        print("\n" + "-"*60)
        print("ASSUMPTIONS & KNOWLEDGE GAPS")
        print("-"*60)
        for g in result["gaps"]:
            print(f"  • {g}")

    if result["resolutions"]:
        print("\n" + "-"*60)
        print("HOW TO RESOLVE GAPS")
        print("-"*60)
        for r in result["resolutions"]:
            print(f"  → {r}")

    print("="*60 + "\n")


if __name__ == "__main__":
    print("🧠 Epistemic AI Research Agent — powered by NVIDIA NIM")
    print("Type 'quit' to exit.\n")

    while True:
        query = input("Your question: ").strip()
        if query.lower() in ("quit", "exit", "q"):
            break
        if not query:
            continue
        print("\nQuerying NVIDIA NIM with epistemic humility framework...")
        try:
            result = query_agent(query)
            print_result(result)
        except Exception as e:
            print(f"\n Error: {e}\n")