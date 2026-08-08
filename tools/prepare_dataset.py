#!/usr/bin/env python3
"""Prepare fine-tune dataset from persisted flywheel JSONL.

Features:
- Read JSONL files from `data/` or given paths
- Optional PII redaction (emails, phones, SSNs) with conservative regexes
- Extract prompt/response pairs when available (keys: 'query' and 'response')
- Output a single JSONL of {"prompt":..., "completion":...} suitable for fine-tune prep
"""
from __future__ import annotations

import argparse
import json
import os
import re
from typing import Iterable


EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\(\d{3}\)|\d{3})[\s-]?\d{3}[\s-]?\d{4}")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def iter_jsonl(paths: Iterable[str]):
    for p in paths:
        if not os.path.isfile(p):
            continue
        with open(p, 'r', encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    continue


def redact_text(s: str) -> str:
    s = EMAIL_RE.sub('[REDACTED_EMAIL]', s)
    s = PHONE_RE.sub('[REDACTED_PHONE]', s)
    s = SSN_RE.sub('[REDACTED_SSN]', s)
    return s


def prepare(paths: Iterable[str], out: str, redact: bool = True) -> int:
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    count = 0
    with open(out, 'w', encoding='utf-8') as outf:
        for obj in iter_jsonl(paths):
            # Only process records that contain both query and response
            q = obj.get('query') or obj.get('prompt') or obj.get('user_query')
            r = obj.get('response') or obj.get('calibrated_response') or obj.get('answer')
            if not q or not r:
                continue
            if redact:
                q = redact_text(q)
                r = redact_text(r)
            rec = {'prompt': q, 'completion': r}
            outf.write(json.dumps(rec, ensure_ascii=False) + '\n')
            count += 1
    return count


def main(argv=None):
    parser = argparse.ArgumentParser(description='Prepare training JSONL from flywheel data')
    parser.add_argument('--files', nargs='*', help='Input JSONL files (default: data/*.jsonl)')
    parser.add_argument('--out', type=str, default='export/fine_tune.jsonl', help='Output JSONL')
    parser.add_argument('--no-redact', dest='redact', action='store_false')
    args = parser.parse_args(argv)

    if not args.files:
        files = [os.path.join('data', f) for f in os.listdir('data') if f.endswith('.jsonl')]
    else:
        files = args.files

    count = prepare(files, args.out, redact=args.redact)
    print(f'Wrote {count} prompt/completion pairs to {args.out}')


if __name__ == '__main__':
    main()
