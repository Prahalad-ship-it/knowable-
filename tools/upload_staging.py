#!/usr/bin/env python3
"""Stage exported datasets for manual upload.

This tool moves export files into `staging/` and optionally compresses them.
It avoids cloud SDKs so it works offline.
"""
from __future__ import annotations

import argparse
import os
import shutil
import gzip
from typing import Iterable


def stage_files(paths: Iterable[str], out_dir: str = 'staging', compress: bool = True):
    os.makedirs(out_dir, exist_ok=True)
    staged = []
    for p in paths:
        if not os.path.isfile(p):
            continue
        base = os.path.basename(p)
        dest = os.path.join(out_dir, base)
        shutil.copy2(p, dest)
        if compress:
            with open(dest, 'rb') as f_in, gzip.open(dest + '.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(dest)
            dest = dest + '.gz'
        staged.append(dest)
    return staged


def main(argv=None):
    parser = argparse.ArgumentParser(description='Stage files for manual upload')
    parser.add_argument('--files', nargs='+', required=True)
    parser.add_argument('--out', default='staging')
    parser.add_argument('--no-compress', dest='compress', action='store_false')
    args = parser.parse_args(argv)

    staged = stage_files(args.files, args.out, compress=args.compress)
    print('Staged files:')
    for s in staged:
        print(' ', s)


if __name__ == '__main__':
    main()
