#!/usr/bin/env python3
"""
Lean batch downloader for Internet Archive.
Downloads high-priority texts for Sutrai archive.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

BASE_DIR = Path(r"G:\My Drive\AI\Sutrai\Archive\texts\sacred\mythology-arc")

# High-priority texts to download (item_id, description, format_glob)
TARGETS = [
    # Hindu/Vedic
    ("vedichymns0046unse", "Vedic Hymns", "*_djvu.txt"),
    ("bhagavadgt00besagoog", "Bhagavad Gita", "*_djvu.txt"),
    ("beginningshindu00lanmgoog", "Beginnings of Hindu Religion", "*_djvu.txt"),
    ("brahmanastudyon00grisgoog", "Brahmana Study", "*_djvu.txt"),
    
    # Celtic
    ("celticmythology00macbgoog", "Celtic Mythology (Macbain)", "*_djvu.txt"),
    ("mabinogion0000unse", "Mabinogion", "*_djvu.txt"),
    ("celticmythandleg00squiuoft", "Celtic Myth and Legend (Squire)", "*_djvu.txt"),
    
    # Norse expanded
    ("heimsrkringla0000unse", "Heimskringla", "*_djvu.txt"),
    ("volsasaga0000unse", "Volsunga Saga", "*_djvu.txt"),
    ("heroesofasgard0000unse", "Heroes of Asgard", "*_djvu.txt"),
    ("norsemythinengli00herf", "Norse Mythology in English", "*_djvu.txt"),
    
    # Comparative mythology
    ("goldenboughs10fraz", "Golden Bough (Frazer)", "*_djvu.txt"),
    ("mythritualandrel00langgoog", "Myth, Ritual and Religion (Lang)", "*_djvu.txt"),
    ("modernmythology00lang", "Modern Mythology (Lang)", "*_djvu.txt"),
    ("mytholog00murriala", "Mythology (Murray)", "*_djvu.txt"),
    
    # Greek/Roman expanded
    ("classmythsinen00gayl", "Classic Myths in English (Gayley)", "*_djvu.txt"),
    ("classicmytholog00wittgoog", "Classic Mythology (Witt)", "*_djvu.txt"),
    ("aguidetomytholo00clargoog", "Guide to Mythology (Clark)", "*_djvu.txt"),
    
    # Zoroastrian
    ("zoroastrianis0000millgoog", "Zoroastrianism (Mills)", "*_djvu.txt"),
    ("zartushtnamah0000unse", "Zartusht-Namah", "*_djvu.txt"),
    
    # African
    ("africanmythology0000unse", "African Mythology", "*_djvu.txt"),
    ("egyptianmythol0000unse", "Egyptian Mythology", "*_djvu.txt"),
    
    # Japanese/Shinto
    ("kojiki0000unse", "Kojiki", "*_djvu.txt"),
    ("japanesefairy0000unse", "Japanese Fairy Tales", "*_djvu.txt"),
    
    # Buddhist expanded
    ("dhammapada0000unse", "Dhammapada", "*_djvu.txt"),
    ("lotussutra0000unse", "Lotus Sutra", "*_djvu.txt"),
    
    # Mesopotamian
    ("enumaelish0000unse", "Enuma Elish", "*_djvu.txt"),
    ("gilgamesh0000unse", "Epic of Gilgamesh", "*_djvu.txt"),
    
    # Slavic
    ("slavicmytholog0000unse", "Slavic Mythology", "*_djvu.txt"),
    ("russianfairyta0000unse", "Russian Fairy Tales", "*_djvu.txt"),
    
    # Native American expanded
    ("navajomythspraye00mattrich", "Navajo Myths (Prayer)", "*_djvu.txt"),
    ("pawneemythology0000dors", "Pawnee Mythology (Dorsey)", "*_djvu.txt"),
    ("tlingitmythsand00swan", "Tlingit Myths (Swanton)", "*_djvu.txt"),
]

def download(item_id, desc, glob):
    """Download a single item."""
    dest = BASE_DIR / item_id
    dest.mkdir(parents=True, exist_ok=True)
    
    # Check if already downloaded
    existing = list(dest.glob(glob.replace("*", "*")))
    if existing:
        print(f"  SKIP (exists): {desc}")
        return True
    
    print(f"  Downloading: {desc}...")
    try:
        result = subprocess.run(
            ["ia", "download", item_id, f"--glob={glob}", 
             f"--destdir={BASE_DIR}", "--checksum"],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            print(f"  ✓ Done")
            return True
        else:
            print(f"  ✗ Failed: {result.stderr[:100]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  ✗ Timeout")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Sutrai IA Lean Batch Downloader")
    print(f"Target: {len(TARGETS)} texts")
    print(f"Destination: {BASE_DIR}")
    print("=" * 50)
    
    success = 0
    fail = 0
    skip = 0
    
    for i, (item_id, desc, glob) in enumerate(TARGETS):
        print(f"\n[{i+1}/{len(TARGETS)}] {item_id}")
        result = download(item_id, desc, glob)
        if result:
            success += 1
        else:
            fail += 1
        
        time.sleep(2)  # Rate limiting
    
    print(f"\n{'='*50}")
    print(f"Complete: {success} succeeded, {fail} failed")

if __name__ == "__main__":
    main()
