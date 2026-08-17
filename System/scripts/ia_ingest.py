#!/usr/bin/env python3
"""
Internet Archive discovery and download script for Sutrai.
Searches for religion/mythology texts and downloads them.
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime

try:
    from internetarchive import get_item, search_items, get_session
except ImportError:
    print("internetarchive not installed. Run: pip install internetarchive")
    sys.exit(1)

BASE_DIR = Path(r"G:\My Drive\AI\Sutrai\Archive\texts\sacred\mythology-arc")

def search_ia(query, max_results=20):
    """Search Internet Archive for items."""
    print(f"\nSearching IA for: {query}")
    results = []
    try:
        for item in search_items(query):
            results.append(item)
            if len(results) >= max_results:
                break
    except Exception as e:
        print(f"  Search error: {e}")
    return results

def download_ia_item(item_id, output_dir, formats=None):
    """Download an item from Internet Archive."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        item = get_item(item_id)
        
        # Get metadata
        metadata = item.metadata or {}
        title = metadata.get('title', item_id)
        
        # Filter for text files
        text_files = []
        for file_info in item.files:
            fname = file_info.get('name', '')
            fformat = file_info.get('format', '')
            
            # Look for text formats
            if any(ext in fname.lower() for ext in ['.txt', '.htm', '.html', 'text']):
                text_files.append(file_info)
            elif 'text' in fformat.lower():
                text_files.append(file_info)
        
        if not text_files:
            # Try any downloadable file
            for file_info in item.files:
                fname = file_info.get('name', '')
                if any(ext in fname.lower() for ext in ['.pdf', '.epub', '.djvu']):
                    text_files.append(file_info)
                    break
        
        downloaded = []
        for file_info in text_files[:3]:  # Limit to 3 files per item
            fname = file_info.get('name', '')
            dest = output_dir / item_id / fname
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            if dest.exists():
                print(f"  Already exists: {fname}")
                downloaded.append(str(dest))
                continue
            
            # Download via ia tool
            url = f"https://archive.org/download/{item_id}/{fname}"
            subprocess.run(['curl', '-sL', url, '-o', str(dest)], check=True)
            
            if dest.exists() and dest.stat().st_size > 1000:
                print(f"  Downloaded: {fname} ({dest.stat().st_size} bytes)")
                downloaded.append(str(dest))
            else:
                print(f"  Failed: {fname}")
                dest.unlink(missing_ok=True)
        
        return downloaded
        
    except Exception as e:
        print(f"  Error downloading {item_id}: {e}")
        return []

def main():
    # Create output dir
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Search queries for religion/mythology texts
    queries = [
        "mythology religion folklore",
        "sacred texts mythology",
        "comparative mythology religion",
        "world mythology legends",
        "religious texts ancient",
    ]
    
    all_results = []
    seen_ids = set()
    
    for query in queries:
        results = search_ia(query, max_results=10)
        for item in results:
            item_id = item.get('identifier', '')
            if item_id in seen_ids:
                continue
            seen_ids.add(item_id)
            all_results.append(item)
        
        time.sleep(2)  # Be nice to IA servers
    
    print(f"\nFound {len(all_results)} unique items")
    
    # Download first 10 items
    for i, item in enumerate(all_results[:10]):
        item_id = item.get('identifier', 'unknown')
        title = item.get('title', 'Unknown')[:60]
        print(f"\n[{i+1}] {item_id}: {title}")
        
        downloaded = download_ia_item(item_id, BASE_DIR)
        time.sleep(3)  # Rate limiting
    
    print(f"\nDone! Check {BASE_DIR}")

if __name__ == "__main__":
    main()
