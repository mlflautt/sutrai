#!/usr/bin/env python3
"""
Flatten all nested IA item subdirectories into clean <item_id>.txt files
in the mythology-arc base directory. Deduplicates by item_id.
"""

import shutil
import re
from pathlib import Path

BASE_DIR = Path(r"G:\My Drive\AI\Sutrai\Archive\texts\sacred\mythology-arc")

def main():
    moved = 0
    seen_ids = set()
    # Collect existing flat files' item_ids
    for f in BASE_DIR.glob("*_djvu.txt"):
        seen_ids.add(f.stem.replace('_djvu', ''))

    for sub in sorted(BASE_DIR.iterdir()):
        if not sub.is_dir():
            continue
        item_id = sub.name
        txt = list(sub.glob("*_djvu.txt"))
        if not txt:
            # Check for any .txt
            txt = list(sub.glob("*.txt"))
        if not txt:
            continue
        src = txt[0]
        dest_name = f"{item_id}{src.suffix}"
        dest = BASE_DIR / dest_name
        if dest.exists():
            print(f"SKIP exists: {dest_name}")
        else:
            shutil.move(str(src), str(dest))
            moved += 1
            print(f"Moved: {dest_name}")
        # Try to remove the now-empty (or near-empty) dir
        try:
            sub.rmdir()
        except OSError:
            # remove leftover files then dir
            for leftover in sub.iterdir():
                try:
                    leftover.unlink()
                except OSError:
                    pass
            try:
                sub.rmdir()
            except OSError:
                pass

    print(f"\nMoved {moved} files. Flattened.")

if __name__ == "__main__":
    main()
