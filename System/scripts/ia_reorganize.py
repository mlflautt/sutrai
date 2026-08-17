#!/usr/bin/env python3
"""
Reorganize IA downloads into proper Sutrai archive structure.
Moves files from nested subdirectories into clean structure.
"""

import os
import shutil
from pathlib import Path

BASE_DIR = Path(r"G:\My Drive\AI\Sutrai\Archive\texts\sacred\mythology-arc")

def main():
    # Find all djvu.txt files in subdirectories
    for txt_file in BASE_DIR.rglob("*_djvu.txt"):
        # Get item_id from parent directory
        item_id = txt_file.parent.name
        
        # Create safe filename from item_id
        safe_name = item_id.replace('.', '_').replace('-', '_')[:60]
        new_name = f"{safe_name}.txt"
        dest = BASE_DIR / new_name
        
        if dest.exists():
            print(f"SKIP (exists): {new_name}")
            continue
        
        # Move file
        shutil.move(str(txt_file), str(dest))
        print(f"Moved: {new_name}")
    
    # Remove empty subdirectories
    for subdir in sorted(BASE_DIR.iterdir(), reverse=True):
        if subdir.is_dir():
            try:
                subdir.rmdir()  # Only removes empty dirs
                print(f"Removed: {subdir.name}")
            except OSError:
                pass  # Directory not empty
    
    print("\nDone!")

if __name__ == "__main__":
    main()
