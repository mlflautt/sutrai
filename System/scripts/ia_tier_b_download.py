#!/usr/bin/env python3
"""
Parse ChatGPT CSV and download Tier B (strong second wave) texts from Internet Archive.

Improvements over Tier A:
- Tries full title+creator query first
- Falls back to title-only query if no results
- Falls back to loose title-substring query as last resort
- Skips items already downloaded in Tier A (dedupe by title)
"""

import csv
import time
import subprocess
import re
from pathlib import Path

CSV_PATH = Path(r"C:\Users\Mitchell\AppData\Local\hermes\attachments\sutrai_ia_250_sources-2.csv")
BASE_DIR = Path(r"G:\My Drive\AI\Sutrai\Archive\texts\sacred\mythology-arc")
TIER_A_DIR = BASE_DIR  # Same target dir; we dedupe by checking existing files

def parse_csv():
    """Parse the CSV and return Tier B items."""
    items = []
    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'B —' in row.get('tier', ''):
                items.append(row)
    return items

def extract_query(full_query):
    """Extract the Lucene query string from 'ia search '...'' wrapper."""
    if full_query.startswith("ia search '") and full_query.endswith("'"):
        return full_query[11:-1]
    return full_query

def title_from_query(query):
    """Extract the title:value from a query string."""
    m = re.search(r'title:"([^"]+)"', query)
    return m.group(1) if m else None

def creator_from_query(query):
    """Extract the creator:value from a query string."""
    m = re.search(r'creator:"([^"]+)"', query)
    return m.group(1) if m else None

def search_ia(query, max_results=3):
    """Search IA and return item IDs."""
    try:
        result = subprocess.run(
            ['ia', 'search', query, '--itemlist', f'--parameters=page=1&rows={max_results}'],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return []
        ids = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        return ids[:max_results]
    except Exception:
        return []

def download_ia(item_id):
    """Download djvu.txt for an item. Returns True on success."""
    try:
        result = subprocess.run(
            ['ia', 'download', item_id, '--glob=*_djvu.txt', f'--destdir={BASE_DIR}', '--checksum'],
            capture_output=True, text=True, timeout=120
        )
        return result.returncode == 0
    except Exception:
        return False

def already_have(title):
    """Check if a text with similar title was already downloaded (Tier A)."""
    # Normalize title for loose matching
    norm = re.sub(r'[^a-z0-9]', '', title.lower())
    for f in BASE_DIR.glob("*_djvu.txt"):
        fname = re.sub(r'[^a-z0-9]', '', f.stem.lower())
        # Check if key words overlap (first 20 chars of normalized title)
        if norm[:20] in fname or fname[:20] in norm:
            return True
    return False

def search_and_download(row):
    """Try multiple query strategies. Returns item_id or None."""
    full_query = row.get('ia_query', '')
    base_query = extract_query(full_query)
    title = title_from_query(base_query)
    creator = creator_from_query(base_query)

    strategies = []

    # Strategy 1: full title + creator (original)
    if title and creator:
        strategies.append(f'title:"{title}" creator:"{creator}" mediatype:texts')
    # Strategy 2: title only
    if title:
        strategies.append(f'title:"{title}" mediatype:texts')
    # Strategy 3: loose title substring (first 4 words)
    if title:
        words = title.split()[:4]
        loose = ' '.join(words)
        strategies.append(f'title:"{loose}*" mediatype:texts')
    # Strategy 4: anyword search on title
    if title:
        strategies.append(f'"{title}" mediatype:texts')

    for i, q in enumerate(strategies, 1):
        ids = search_ia(q, max_results=3)
        if ids:
            item_id = ids[0]
            if download_ia(item_id):
                return item_id
            # Download failed; try next result from same query
            if len(ids) > 1 and download_ia(ids[1]):
                return ids[1]
    return None

def main():
    items = parse_csv()
    print(f"Found {len(items)} Tier B items\n")

    BASE_DIR.mkdir(parents=True, exist_ok=True)

    downloaded = []
    failed = []
    skipped = []

    for i, item in enumerate(items):
        title = item.get('title', 'Unknown')
        print(f"[{i+1}/{len(items)}] {title[:55]}")

        # Skip if we already have something similar from Tier A
        if already_have(title):
            print(f"  ~ Already present (skip)")
            skipped.append(title)
            continue

        result = search_and_download(item)
        if result:
            downloaded.append(result)
            print(f"  ✓ {result}")
        else:
            failed.append(title)
            print(f"  ✗ No results")

        time.sleep(1.5)  # gentle rate limit

    print(f"\n{'='*50}")
    print(f"Downloaded: {len(downloaded)}")
    print(f"Skipped (dup): {len(skipped)}")
    print(f"Failed: {len(failed)}")
    if failed:
        print("\nFailed titles:")
        for t in failed:
            print(f"  - {t}")

if __name__ == "__main__":
    main()
