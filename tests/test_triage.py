#!/usr/bin/env python3
"""Quick sanity test for triage_protocol_processor.

Run from repository root:
    python -u tests/test_triage.py

This script prints tokens, computed metrics, and triggers the flywheel fallback log.
"""
import asyncio
import math
import sys
import os

# Ensure repository root is on sys.path so the module imports in test runs
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from triage_protocol_processor import (
    sanitize_and_tokenize_triage_text,
    calculate_triage_confidence,
    hand_off_to_flywheel,
    OnlineTriageStats,
)


def main() -> int:
    raw = "**SpO₂** ≥ 94 % within `10` min, HEART score ≥ 4"
    print("raw_text:", raw)

    tokens = sanitize_and_tokenize_triage_text(raw)
    print("tokens:", tokens)

    def find(tok):
        try:
            return tokens.index(tok)
        except ValueError:
            return None

    idx_94 = find("94%")
    idx_10 = find("10")
    idx_4 = find("4")
    critical_indices = [i for i in (idx_94, idx_10, idx_4) if i is not None]
    print("critical_indices:", critical_indices)

    n = len(tokens)
    if n == 0:
        print("No tokens parsed; aborting.")
        return 2

    # Build p-values with one critical below threshold to trigger audit
    p = [0.9] * n
    if idx_94 is not None:
        p[idx_94] = 0.45
    if idx_10 is not None:
        p[idx_10] = 0.85
    if idx_4 is not None:
        p[idx_4] = 0.6

    logprobs = [math.log(pi) for pi in p]

    metrics = calculate_triage_confidence(logprobs, critical_indices)
    print("metrics:")
    for k, v in metrics.items():
        if k == "p_values":
            print(f"  {k}: [length={len(v)}]")
        else:
            print(f"  {k}: {v}")

    # Fire the flywheel (fallback prints to stdout when webhook_url=None)
    try:
        asyncio.run(hand_off_to_flywheel(raw, metrics, trigger_status=True, webhook_url=None))
    except Exception as e:
        print("hand_off_to_flywheel raised:", e)
        return 3

    print("Done — flywheel should have logged a JSON payload above.")
    # --- Now test incremental OnlineTriageStats by replaying the same logprobs ---
    online = OnlineTriageStats()
    # mark critical by same indices
    crit_set = set(critical_indices)
    for i, lp in enumerate(logprobs):
        online.add_logprob(lp, is_critical=(i in crit_set))

    online_metrics = online.snapshot()
    print("online_metrics:")
    for k, v in online_metrics.items():
        print(f"  {k}: {v}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
