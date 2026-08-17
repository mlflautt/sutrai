#!/usr/bin/env python3
"""
Parse ChatGPT CSV and download Tier A texts from Internet Archive.
Uses the Python internetarchive library directly.
"""

import csv
import time
import subprocess
from pathlib import Path

CSV_PATH = Path(r"C:\Users\Mitchell\AppData\Local\hermes\attachments\sutrai_ia_250_sources-2.csv")
BASE_DIR = Path(r"G:\My Drive\AI\Sutrai\Archive\texts\sacred\mythology-arc")

def parse_csv():
    """Parse the CSV and return Tier A items."""
    items = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'A — core' in row.get('tier', ''):
                items.append(row)
    return items

def search_and_download(query, title, max_results=3):
    """Search IA and download first result."""
    try:
        # Search using ia CLI (returns item IDs)
        result = subprocess.run(
            ['ia', 'search', query, '--itemlist', f'--parameters=page=1&rows={max_results}'],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"  Search error: {result.stderr[:100]}")
            return None
        
        ids = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        if not ids:
            print(f"  No results")
            return None
        
        item_id = ids[0]
        print(f"  Found: {item_id}")
        
        # Download using ia CLI
        dest = BASE_DIR / item_id
        dest.mkdir(parents=True, exist_ok=True)
        
        result = subprocess.run(
            ['ia', 'download', item_id, '--glob=*_djvu.txt', f'--destdir={BASE_DIR}', '--checksum'],
            capture_output=True, text=True, timeout=120
        )
        
        if result.returncode == 0:
            print(f"  ✓ Downloaded")
            return item_id
        else:
            print(f"  ✗ Download failed: {result.stderr[:100]}")
            return None
        
    except Exception as e:
        print(f"  Error: {e}")
        return None

def main():
    items = parse_csv()
    print(f"Found {len(items)} Tier A items\n")
    
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    downloaded = []
    failed = []
    
    for i, item in enumerate(items):
        title = item.get('title', 'Unknown')[:50]
        # Extract query from the ia_query field (remove 'ia search ' prefix)
        full_query = item.get('ia_query', '')
        # The query is like: ia search 'title:"..." creator:"..."'
        # Extract just the search part
        if full_query.startswith("ia search '") and full_query.endswith("'"):
            query = full_query[11:-1]  # Remove "ia search " and trailing "'"
        else:
            query = full_query
        
        print(f"[{i+1}/{len(items)}] {title}")
        print(f"  Query: {query[:60]}...")
        
        result = search_and_download(query, title)
        if result:
            downloaded.append(result)
        else:
            failed.append(title)
        
        time.sleep(2)
    
    print(f"\n{'='*50}")
    print(f"Downloaded: {len(downloaded)}")
    print(f"Failed: {len(failed)}")

if __name__ == "__main__":
    main()
