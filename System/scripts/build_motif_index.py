#!/usr/bin/env python3
"""
Build cross-tradition motif index from classified story files.

Creates:
  System/indexes/motif-index.yaml — searchable motif→stories mapping
"""

import re
import yaml
from pathlib import Path

STORY_DIR = Path(r"G:\My Drive\AI\Sutrai\Stories\by-source\ia")
INDEX_PATH = Path(r"G:\My Drive\AI\Sutrai\System\indexes\motif-index.yaml")
SOURCE_INDEX_PATH = Path(r"G:\My Drive\AI\Sutrai\System\indexes\source-index.yaml")

def main():
    # Load source-index to get traditions for each stem
    source_meta = {}
    with open(SOURCE_INDEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    blocks = re.findall(r"- id: (ia-[^\n]+)\n((?:  [^\n]+\n)*)", text)
    for sid, body in blocks:
        stem = sid.replace('ia-', '', 1)
        trad_m = re.search(r'tradition: (.+)$', body, re.M)
        title_m = re.search(r'title: "([^"]*)"', body)
        source_meta[stem] = {
            'tradition': trad_m.group(1).strip() if trad_m else 'unknown',
            'title': title_m.group(1) if title_m else stem,
        }

    files = sorted(STORY_DIR.glob("*.md"))
    print(f"Indexing motifs from {len(files)} story files...")

    # Build motif index
    motif_index = {}  # motif_id → { description, stories: [{id, title, tradition}] }

    for f in files:
        stem = f.stem
        text = f.read_text(encoding='utf-8', errors='ignore')

        # Get title
        title_m = re.search(r'title: "([^"]*)"', text)
        title = title_m.group(1) if title_m else stem

        # Get tradition from source-index
        meta = source_meta.get(stem, {})
        tradition = meta.get('tradition', 'unknown')

        # Extract motifs
        in_motifs = False
        motifs = []
        for line in text.split('\n'):
            if line.startswith('motifs:'):
                in_motifs = True
                continue
            if line.startswith('adaptation_status:') or (line.startswith('source:') and in_motifs):
                in_motifs = False
                continue
            m = re.match(r'^  - (.+)$', line)
            if m and in_motifs:
                motifs.append(m.group(1))

        for motif in motifs:
            if motif not in motif_index:
                motif_index[motif] = {
                    'description': '',  # Will be filled from taxonomy
                    'stories': [],
                }
            motif_index[motif]['stories'].append({
                'id': f'ia-{stem}',
                'title': title,
                'tradition': tradition,
            })

    # Fill descriptions from taxonomy if available
    try:
        from taxonomy import MOTIF_TAXONOMY
        for motif_id, entry in motif_index.items():
            if motif_id in MOTIF_TAXONOMY:
                entry['description'] = MOTIF_TAXONOMY[motif_id]
    except ImportError:
        pass

    # Sort by story count descending
    motif_index_sorted = dict(
        sorted(motif_index.items(), key=lambda x: len(x[1]['stories']), reverse=True)
    )

    # Write index
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        yaml.dump({'motif_index': motif_index_sorted}, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"Indexed {len(motif_index)} motifs across {len(files)} files.")
    print(f"\nTop 20 motifs by story count:")
    for motif_id, entry in list(motif_index_sorted.items())[:20]:
        traditions = set(s['tradition'] for s in entry['stories'])
        print(f"  {len(entry['stories']):3} stories | {len(traditions):2} traditions | {motif_id}")

if __name__ == "__main__":
    main()
