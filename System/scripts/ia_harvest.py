#!/usr/bin/env python3
"""
Sutrai Internet Archive harvester.
Searches, filters, and downloads texts from archive.org.

Architecture:
  search → metadata filter → relevance score → download queue → download
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime

try:
    from internetarchive import get_item, search_items, get_session
except ImportError:
    print("internetarchive not installed. Run: pip install internetarchive")
    sys.exit(1)

BASE_DIR = Path(r"G:\My Drive\AI\Sutrai\Archive\texts\sacred\mythology-arc")
METADATA_DIR = BASE_DIR / "metadata"

# Filters
TARGET_LANGUAGES = {"en", "eng", "english", "zh", "chi", "chinese"}
TARGET_SUBJECTS = {"mythology", "religion", "folklore", "legends", "sacred", "spirituality"}
MIN_YEAR = 1600
MAX_YEAR = 1950
TARGET_FORMATS = {".txt", ".pdf", ".epub"}

def search(query, max_results=100):
    """Search Internet Archive."""
    print(f"Searching: {query}")
    results = []
    try:
        for item in search_items(query, max_results=max_results):
            results.append(item)
    except Exception as e:
        print(f"  Search error: {e}")
    print(f"  Found: {len(results)} items")
    return results

def get_metadata(item_id):
    """Get metadata for an IA item."""
    try:
        item = get_item(item_id)
        return item.metadata or {}
    except Exception as e:
        return {}

def filter_item(metadata):
    """Filter items based on quality criteria."""
    # Language check
    language = metadata.get('language', '')
    if isinstance(language, list):
        language = language[0] if language else ''
    language = language.lower()
    
    if not any(lang in language for lang in TARGET_LANGUAGES):
        return False, "language"
    
    # Year check
    date_str = metadata.get('date', metadata.get('year', ''))
    if date_str:
        try:
            year = int(date_str[:4])
            if year < MIN_YEAR or year > MAX_YEAR:
                return False, "date"
        except ValueError:
            pass
    
    # Subject check
    subjects = metadata.get('subject', [])
    if isinstance(subjects, str):
        subjects = [subjects]
    subjects_lower = [s.lower() for s in subjects]
    
    if not any(any(ts in s for ts in TARGET_SUBJECTS) for s in subjects_lower):
        return False, "subject"
    
    return True, "pass"

def score_relevance(metadata):
    """Score item relevance for Sutrai."""
    score = 0
    subjects = metadata.get('subject', [])
    if isinstance(subjects, str):
        subjects = [subjects]
    subjects_lower = ' '.join(s.lower() for s in subjects)
    
    # Direct mythology/religion terms
    if 'mythology' in subjects_lower:
        score += 10
    if 'religion' in subjects_lower:
        score += 8
    if 'folklore' in subjects_lower:
        score += 8
    if 'legends' in subjects_lower:
        score += 7
    if 'sacred' in subjects_lower:
        score += 6
    
    # Prefer older texts (public domain, established scholarship)
    date_str = metadata.get('date', metadata.get('year', ''))
    if date_str:
        try:
            year = int(date_str[:4])
            if 1850 <= year <= 1930:
                score += 5  # Golden age of comparative mythology
            elif year < 1850:
                score += 3
        except ValueError:
            pass
    
    # Prefer certain creators
    creator = (metadata.get('creator', '') or '').lower()
    known_scholars = ['frazer', 'spence', 'lang', 'fiske', 'brinton', 'gray', 'bullfinch']
    if any(scholar in creator for scholar in known_scholars):
        score += 5
    
    return score

def download_item(item_id, output_dir, formats=None):
    """Download files from an IA item."""
    if formats is None:
        formats = ['.txt', '.pdf']
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        item = get_item(item_id)
        metadata = item.metadata or {}
        title = metadata.get('title', item_id)[:60]
        
        # Get file list
        files = item.files or []
        downloaded = []
        
        for file_info in files:
            fname = file_info.get('name', '')
            fformat = file_info.get('format', '')
            
            # Skip IA-generated files
            if 'derivative' in fformat.lower() or '_thumb' in fname:
                continue
            
            # Check format
            if not any(ext in fname.lower() for ext in formats):
                continue
            
            # Skip very large files
            size = int(file_info.get('size', 0))
            if size > 50 * 1024 * 1024:  # 50MB
                continue
            
            dest = output_dir / fname
            if dest.exists():
                continue
            
            # Download
            url = f"https://archive.org/download/{item_id}/{fname}"
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Sutrai-Archive-Harvester/1.0'
            })
            
            try:
                with urllib.request.urlopen(req, timeout=60) as response:
                    content = response.read()
                    dest.write_bytes(content)
                    
                    if dest.stat().size > 1000:
                        print(f"  ✓ {fname} ({dest.stat().size:,} bytes)")
                        downloaded.append(str(dest))
                    else:
                        dest.unlink(missing_ok=True)
            except Exception as e:
                print(f"  ✗ {fname}: {e}")
            
            time.sleep(1)  # Rate limit
        
        return downloaded
        
    except Exception as e:
        print(f"  Error with {item_id}: {e}")
        return []

def main():
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Search queries
    queries = [
        "mythology religion folklore",
        "comparative mythology",
        "world mythology legends",
        "sacred texts ancient",
    ]
    
    candidates = []
    seen_ids = set()
    
    for query in queries:
        results = search(query, max_results=25)
        for item in results:
            item_id = item.get('identifier', '')
            if item_id in seen_ids:
                continue
            seen_ids.add(item_id)
            candidates.append(item)
        time.sleep(2)
    
    print(f"\nTotal candidates: {len(candidates)}")
    
    # Filter and score
    approved = []
    for item in candidates:
        item_id = item.get('identifier', '')
        metadata = dict(item)
        
        passed, reason = filter_item(metadata)
        if not passed:
            continue
        
        score = score_relevance(metadata)
        approved.append({
            'id': item_id,
            'title': metadata.get('title', 'Unknown'),
            'creator': metadata.get('creator', 'Unknown'),
            'date': metadata.get('date', 'Unknown'),
            'score': score,
            'metadata': metadata
        })
    
    # Sort by score
    approved.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"Approved: {len(approved)}")
    print(f"\nTop 10:")
    for i, item in enumerate(approved[:10]):
        print(f"  {i+1}. [{item['score']}] {item['title'][:50]} — {item.get('creator', '?')[:30]} ({item.get('date', '?')})")
    
    # Download top items
    download_count = min(5, len(approved))
    print(f"\nDownloading top {download_count} items...")
    
    for i, item in enumerate(approved[:download_count]):
        item_id = item['id']
        print(f"\n[{i+1}] {item['title'][:60]}")
        
        downloaded = download_item(item_id, BASE_DIR / item_id)
        
        # Save metadata
        meta_path = METADATA_DIR / f"{item_id}.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(item['metadata'], f, indent=2, ensure_ascii=False)
        
        time.sleep(3)
    
    print(f"\nDone! Files in: {BASE_DIR}")

if __name__ == "__main__":
    main()
