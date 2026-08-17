#!/usr/bin/env python3
"""
Rebuild source-index.yaml IA entries with proper titles by reading the first
~4KB of each downloaded txt file and extracting a human title via heuristics.

Runs fully offline. For each <stem>.txt it:
  1. Reads the file header (first 4000 chars, cleaned).
  2. Looks for a likely TITLE pattern (ALL-CAPS title before OCR boilerplate,
     or a line like 'THE X OF Y' near the top).
  3. Falls back to CSV match (title substring) if found.
  4. Falls back to humanized stem.

Then repopulates the 'ia-' entries in source-index.yaml (overwrites existing
ia- block) sorted by stem, with title + tradition from CSV when matched.
"""

import csv
import re
from pathlib import Path

CSV_PATH = Path(r"C:\Users\Mitchell\AppData\Local\hermes\attachments\sutrai_ia_250_sources-2.csv")
BASE_DIR = Path(r"G:\My Drive\AI\Sutrai\Archive\texts\sacred\mythology-arc")
INDEX_PATH = Path(r"G:\My Drive\AI\Sutrai\System\indexes\source-index.yaml")

def norm(s):
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())

def title_from_file(text):
    """Extract a plausible title from OCR header text."""
    # Remove common OCR boilerplate
    cleaned = re.sub(r'(Google|Digitized by the Internet Archive|Microsoft|IVIicrosoft|Ontario Council|Kerala|LBSNAA|EX LIBRIS|http[s]?://\S+).*', ' ', text, flags=re.I)
    lines = [l.strip() for l in cleaned.split('\n') if l.strip()]
    # Look for an ALL-CAPS line of reasonable length near top
    for l in lines[:40]:
        l2 = re.sub(r'[^A-Za-z ]', '', l).strip()
        words = l2.split()
        if 3 <= len(words) <= 12 and sum(1 for w in words if w.isupper()) >= max(2, len(words)//2):
            # Title-case it
            return l2.title()
    # Fallback: first substantial alphabetic line
    for l in lines[:40]:
        l2 = re.sub(r'[^A-Za-z ]', '', l).strip()
        if 4 <= len(l2.split()) <= 14:
            return l2.title()
    return None

def main():
    # CSV lookup by normalized title
    rows = []
    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            rows.append(row)
    csv_by_title = {}
    for row in rows:
        t = row.get('title', '').strip()
        if t:
            csv_by_title.setdefault(norm(t), row)

    files = sorted(BASE_DIR.glob("*.txt"))
    entries = []
    for f in files:
        stem = f.stem
        text = f.read_text(errors='ignore')[:4000]
        title = title_from_file(text)
        # Try CSV match by stem substring against known titles
        meta = None
        nstem = norm(stem)
        for ntitle, row in csv_by_title.items():
            if ntitle and (ntitle in nstem or nstem[:12] in ntitle):
                meta = row
                break
        if meta:
            title = meta.get('title','').strip() or title
            tradition = meta.get('tradition','').strip() or 'Internet Archive'
            author = meta.get('author_translator_editor','').strip()
            year = meta.get('edition_year','').strip()
        else:
            tradition = 'Internet Archive (unmapped)'
            author = ''
            year = ''
        if not title:
            title = stem.replace('_',' ').title()

        block = [
            f"  - id: ia-{stem}",
            f"    title: \"{title}\"",
            f"    category: mythology-arc",
            f"    tradition: {tradition}",
        ]
        if author:
            block.append(f"    author: \"{author}\"")
        if year:
            block.append(f"    edition_year: {year}")
        block += [
            f"    original_language: English (translation)",
            f"    license: Public Domain",
            f"    file_formats: [txt]",
            f"    archive_path: Archive/texts/sacred/mythology-arc/{f.name}",
            f"    ia_identifier: {stem}",
            f"    extracted_story_count: 0",
            "",
        ]
        entries.append("\n".join(block))

    # Rebuild index: keep non-ia entries, append ia block
    orig = INDEX_PATH.read_text(encoding='utf-8')
    kept = [ln for ln in orig.split('\n') if not ln.strip().startswith('- id: ia-')]
    # Remove trailing blank lines
    while kept and kept[-1].strip() == '':
        kept.pop()
    new_text = "\n".join(kept) + "\n\n" + "\n".join(entries)
    INDEX_PATH.write_text(new_text, encoding='utf-8')
    print(f"Rebuilt index with {len(entries)} IA entries.")

if __name__ == "__main__":
    main()
