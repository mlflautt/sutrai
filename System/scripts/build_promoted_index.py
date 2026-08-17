#!/usr/bin/env python3
"""
Build promoted-stories index from the promoted story files.
"""

import yaml
from pathlib import Path

PROMOTED_DIR = Path(r"G:\My Drive\AI\Sutrai\Stories\by-source\ia\promoted")
INDEX_PATH = Path(r"G:\My Drive\AI\Sutrai\System\indexes\promoted-stories.yaml")

def main():
    files = sorted(PROMOTED_DIR.glob("*.md"))
    stories = []
    
    for f in files:
        text = f.read_text(encoding='utf-8', errors='ignore')
        parts = text.split('---', 2)
        if len(parts) < 3:
            continue
        try:
            fm = yaml.safe_load(parts[1])
        except Exception:
            continue
        
        stories.append({
            'id': fm.get('id', f.stem),
            'title': fm.get('title', f.stem),
            'source': fm.get('source', {}).get('name', ''),
            'tradition': fm.get('source', {}).get('tradition', ''),
            'reference': fm.get('source', {}).get('reference', ''),
            'file': f"Stories/by-source/ia/promoted/{f.name}",
        })
    
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        yaml.dump({'promoted_stories': stories}, f, default_flow_style=False, allow_unicode=True)
    
    print(f"Indexed {len(stories)} promoted stories")
    
    # Print by tradition
    trad_counts = {}
    for s in stories:
        t = s['tradition']
        trad_counts[t] = trad_counts.get(t, 0) + 1
    print(f"\nBy tradition:")
    for t, c in sorted(trad_counts.items(), key=lambda x: -x[1]):
        print(f"  {c:3}  {t}")

if __name__ == "__main__":
    main()
