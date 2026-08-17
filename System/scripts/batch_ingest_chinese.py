#!/usr/bin/env python3
"""
Sutrai Chinese text ingestion script.
Downloads Chinese religious/philosophical texts from ctext.org and other sources.
"""

import os
import sys
import json
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"G:\My Drive\AI\Sutrai\Archive\texts\sacred\chinese")

# Chinese texts to download
# (source, text_id, filename, title_chinese, title_english, category, tradition, notes)
CHINESE_TEXTS = [
    {
        "source": "ctext",
        "text_id": "shanhaijing",
        "filename": "shanhaijing",
        "title_chinese": "山海經",
        "title_english": "Classic of Mountains and Seas",
        "category": "mythology",
        "tradition": "Chinese",
        "notes": "Ancient Chinese geography and mythology text. Describes mythical creatures, lands, and peoples."
    },
    {
        "source": "ctext",
        "text_id": "huainanzi",
        "filename": "huainanzi",
        "title_chinese": "淮南子",
        "title_english": "Huainanzi",
        "category": "philosophical",
        "tradition": "Chinese",
        "notes": "Daoist philosophical text with creation myths and cosmology."
    },
    {
        "source": "ctext",
        "text_id": "soushenji",
        "filename": "soushenji",
        "title_chinese": "搜神記",
        "title_english": "In Search of the Supernatural",
        "category": "folklore",
        "tradition": "Chinese",
        "notes": "Collection of supernatural stories and legends from ancient China."
    },
]

def download_ctext(text_id: str, output_path: Path) -> bool:
    """Download text from ctext.org using the text export plugin."""
    url = f"https://ctext.org/plugins/textexport/{text_id}"
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode('utf-8')
            output_path.write_text(content, encoding='utf-8')
            return True
    except Exception as e:
        print(f"  Error downloading from ctext: {e}")
        return False

def main():
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting Chinese text ingestion...")
    print(f"Output directory: {BASE_DIR}")
    
    for text in CHINESE_TEXTS:
        print(f"\n[{text['text_id']}] {text['title_english']}")
        
        txt_path = BASE_DIR / f"{text['filename']}.txt"
        
        if not txt_path.exists():
            print(f"  Downloading from ctext.org...")
            if download_ctext(text['text_id'], txt_path):
                print(f"  Downloaded: {txt_path.stat().st_size} bytes")
            else:
                print(f"  FAILED")
                continue
        else:
            print(f"  Already exists")
    
    print(f"\nChinese text ingestion complete")

if __name__ == "__main__":
    main()
