#!/usr/bin/env python3
"""Export and inspect flywheel JSONL payloads saved by triage processor.

Usage examples:
  # list files
  python tools/export_flywheel.py --list

  # preview first 5 lines of today's file
  python tools/export_flywheel.py --preview data/flywheel-20260808.jsonl --lines 5

  # export selected files into a single JSONL for training
  python tools/export_flywheel.py --export data/flywheel-20260808.jsonl --out export/train-20260808.jsonl

This is intentionally minimal and uses only the standard library.
"""
from __future__ import annotations

import argparse
import json
import os
from typing import Iterable, Dict


def list_data_files(directory: str = "data") -> Iterable[str]:
    if not os.path.isdir(directory):
        return []
    for name in sorted(os.listdir(directory)):
        if name.endswith('.jsonl'):
            yield os.path.join(directory, name)


def preview_file(path: str, lines: int = 10) -> None:
    if not os.path.isfile(path):
        print(f"File not found: {path}")
        return
    with open(path, 'r', encoding='utf-8') as fh:
        for i, line in enumerate(fh):
            if i >= lines:
                break
            try:
                obj = json.loads(line)
                print(json.dumps(obj, indent=2, ensure_ascii=False))
            except Exception:
                print(line.strip())


def export_files(paths: Iterable[str], out: str) -> None:
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    count = 0
    with open(out, 'w', encoding='utf-8') as outf:
        for p in paths:
            if not os.path.isfile(p):
                continue
            with open(p, 'r', encoding='utf-8') as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    # Basic validation
                    try:
                        _ = json.loads(line)
                        outf.write(line + '\n')
                        count += 1
                    except Exception:
                        # skip malformed
                        continue
    print(f"Exported {count} lines to {out}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Inspect and export flywheel JSONL payloads")
    parser.add_argument('--list', action='store_true', help='List data/*.jsonl files')
    parser.add_argument('--preview', type=str, help='Preview a file')
    parser.add_argument('--lines', type=int, default=10, help='Number of lines to preview')
    parser.add_argument('--export', nargs='+', help='One or more files to export (or use --all)')
    parser.add_argument('--all', action='store_true', help='Export all files in data/')
    parser.add_argument('--out', type=str, help='Output file path for export')

    args = parser.parse_args(argv)

    if args.list:
        for f in list_data_files('data'):
            print(f)
        return

    if args.preview:
        preview_file(args.preview, lines=args.lines)
        return

    if args.export or args.all:
        out = args.out or 'export/flywheel-export.jsonl'
        if args.all:
            paths = list(list_data_files('data'))
        else:
            paths = args.export
        export_files(paths, out)
        return

    parser.print_help()


if __name__ == '__main__':
    main()
