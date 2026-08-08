#!/usr/bin/env python3
"""Simple trainer scaffold: split export into train/val and print instructions.

This does NOT run any GPU training. It prepares files and shows recommended
commands for downstream fine-tuning (adapter/LoRA or full fine-tune).
"""
from __future__ import annotations

import argparse
import json
import os
import random
from typing import List


def split_file(input_path: str, out_dir: str, val_frac: float = 0.05, seed: int = 42) -> List[str]:
    with open(input_path, 'r', encoding='utf-8') as fh:
        lines = [l for l in fh if l.strip()]

    random.Random(seed).shuffle(lines)
    n = len(lines)
    n_val = max(1, int(n * val_frac))
    val = lines[:n_val]
    train = lines[n_val:]

    os.makedirs(out_dir, exist_ok=True)
    train_path = os.path.join(out_dir, 'train.jsonl')
    val_path = os.path.join(out_dir, 'val.jsonl')
    with open(train_path, 'w', encoding='utf-8') as ft:
        for l in train:
            ft.write(l)
    with open(val_path, 'w', encoding='utf-8') as fv:
        for l in val:
            fv.write(l)

    return [train_path, val_path]


def main(argv=None):
    parser = argparse.ArgumentParser(description='Prepare train/val splits for fine-tuning')
    parser.add_argument('--input', required=True, help='Input JSONL (prompt/completion)')
    parser.add_argument('--out', default='export/split', help='Output directory')
    parser.add_argument('--val-frac', type=float, default=0.05)
    args = parser.parse_args(argv)

    train_path, val_path = split_file(args.input, args.out, val_frac=args.val_frac)
    print('Prepared:')
    print('  train ->', train_path)
    print('  val   ->', val_path)
    print('\nRecommended next steps:')
    print('  - Use your preferred fine-tune workflow (LoRA/adapters recommended for cost)')
    print('  - Example (pseudo): python finetune.py --train', train_path, '--val', val_path)


if __name__ == '__main__':
    main()
