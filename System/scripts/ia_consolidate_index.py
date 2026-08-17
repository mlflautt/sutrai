#!/usr/bin/env python3
"""
Consolidate downloaded IA files into source-index.yaml — OFFLINE version.
No network calls. Matches each downloaded .txt stem against CSV metadata
by normalized substring overlap; falls back to humanized filename.
"""

import csv
import re
from pathlib import Path

CSV_PATH = Path(r"C:\Users\Mitchell\AppData\Local\hermes\attachments\sutrai_ia_250_sources-2.csv")
BASE_DIR = Path(r"G:\My Drive\AI\Sutrai\Archive\texts\sacred\mythology-arc")
INDEX_PATH = Path(r"G:\My Drive\AI\Sutrai\System\indexes\source-index.yaml")

def norm(s):
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())

def humanize(stem):
    s = re.sub(r'_djvu$', '', stem)
    s = re.sub(r'[^a-zA-Z0-9]+', ' ', s).strip()
    return s.title() if s else stem

def main():
    # Load CSV
    rows = []
    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            rows.append(row)

    # Precompute normalized title keys per row
    row_keys = []
    for row in rows:
        title = row.get('title', '')
        ntitle = norm(title)
        # Use first 6 significant words as a key
        words = [w for w in re.findall(r'[a-z0-9]+', title.lower())][:6]
        key = ''.join(words)
        row_keys.append((key, ntitle, row))

    files = sorted(BASE_DIR.glob("*.txt"))
    print(f"Downloaded files: {len(files)}; CSV rows: {len(rows)}")

    entries = []
    unmapped = []
    for f in files:
        stem = f.stem
        nstem = norm(stem)
        best = None
        best_score = 0
        for key, ntitle, row in row_keys:
            # score = length of longest common substring-ish via substring checks
            score = 0
            if key and key in nstem:
                score = len(key)
            elif nstem and nstem in key:
                score = len(nstem)
            elif ntitle and ntitle in nstem:
                score = len(ntitle)
            if score > best_score:
                best_score = score
                best = row
        if best and best_score >= 8:
            title = best.get('title', '').strip() or humanize(stem)
            tradition = best.get('tradition', '').strip() or 'Internet Archive'
            author = best.get('author_translator_editor', '').strip()
            year = best.get('edition_year', '').strip()
        else:
            title = humanize(stem)
            tradition = 'Internet Archive (unmapped)'
            author = ''
            year = ''
            unmapped.append(stem)

        entry = [
            f"  - id: ia-{stem}",
            f"    title: \"{title}\"",
            f"    category: mythology-arc",
            f"    tradition: {tradition}",
        ]
        if author:
            entry.append(f"    author: \"{author}\"")
        if year:
            entry.append(f"    edition_year: {year}")
        entry += [
            f"    original_language: English (translation)",
            f"    license: Public Domain",
            f"    file_formats: [txt]",
            f"    archive_path: Archive/texts/sacred/mythology-arc/{f.name}",
            f"    ia_identifier: {stem}",
            f"    extracted_story_count: 0",
            "",
        ]
        entries.append("\n".join(entry))

    with open(INDEX_PATH, 'a', encoding='utf-8') as out:
        out.write("\n".join(entries) + "\n")

    print(f"Appended {len(entries)} entries to source-index.yaml")
    print(f"Unmapped (filename as title): {len(unmapped)}")

if __name__ == "__main__":
    main()
