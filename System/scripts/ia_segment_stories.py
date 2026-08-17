#!/usr/bin/env python3
"""
Segment cleaned IA texts into structured story markdown files.

For each cleaned <stem>.txt in Archive/texts/sacred/mythology-arc/:
  - Detect chapter/section headings (CHAPTER, Roman numerals, ALL-CAPS titles)
  - Create Stories/by-source/ia/<stem>.md with YAML frontmatter
  - Each detected section becomes an extracted_unit (id, text snippet, reference)

Addressable units (extracted_units) give us hundreds of narratable segments
without exploding into thousands of tiny files. Curator agents can later
promote high-value units to standalone story files.

Also appends entries to System/indexes/story-index.yaml.
"""

import re
import yaml
from pathlib import Path

BASE_DIR = Path(r"G:\My Drive\AI\Sutrai\Archive\texts\sacred\mythology-arc")
STORY_DIR = Path(r"G:\My Drive\AI\Sutrai\Stories\by-source\ia")
INDEX_PATH = Path(r"G:\My Drive\AI\Sutrai\System\indexes\story-index.yaml")

# Heading detection patterns (line must match AND be short enough to be a heading)
HEADING_RE = [
    re.compile(r'^CHAPTER\s+([IVXLC0-9]+)[.\s]', re.I),
    re.compile(r'^([IVXLC]{1,6})\.\s',),          # "I. " "XII. "
    re.compile(r'^([0-9]{1,3})\.\s+(?=[A-Z])'),   # "1. The " numbered sections
    re.compile(r'^([A-Z][A-Z\'’\- ]{4,45})$'),    # ALL CAPS title line
    re.compile(r'^(THE\s+[A-Z][A-Z\'’\- ]{4,40})$'),  # "THE X OF Y"
]

def is_heading(line):
    s = line.strip()
    if not (3 <= len(s) <= 60):
        return False
    for rx in HEADING_RE:
        if rx.match(s):
            # Exclude common false positives
            if s in ('THE', 'AND', 'OR', 'OF', 'IN', 'A', 'AN', 'TO', 'FROM'):
                return False
            return True
    return False

def slugify(s):
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s.lower()).strip('-')
    return s[:50]

def main():
    STORY_DIR.mkdir(parents=True, exist_ok=True)

    # Load source-index to get proper titles/traditions for each stem
    source_meta = {}
    with open(INDEX_PATH.parent / "source-index.yaml", 'r', encoding='utf-8') as f:
        # Only parse ia- entries; lightweight grep
        text = f.read()
    # Simple parse: find each ia- block
    blocks = re.findall(r"- id: (ia-[^\n]+)\n((?:  [^\n]+\n)*)", text)
    for sid, body in blocks:
        stem = sid.replace('ia-', '', 1)
        title_m = re.search(r'title: "([^"]*)"', body)
        trad_m = re.search(r'tradition: (.+)$', body, re.M)
        source_meta[stem] = {
            'title': title_m.group(1) if title_m else None,
            'tradition': trad_m.group(1).strip() if trad_m else None,
        }

    files = sorted(BASE_DIR.glob("*.txt"))
    story_entries = []

    for f in files:
        stem = f.stem
        meta = source_meta.get(stem, {})
        title_str = meta.get('title') or stem.replace('_', ' ').title()
        tradition_str = meta.get('tradition') or 'Internet Archive (unmapped)'
        text = f.read_text(encoding='utf-8', errors='ignore')
        lines = text.split('\n')

        # Find heading line indices
        headings = []  # (line_idx, heading_text)
        for i, ln in enumerate(lines):
            if is_heading(ln):
                headings.append((i, ln.strip()))

        # Build segments
        segments = []
        for j, (idx, htxt) in enumerate(headings):
            start = idx
            end = headings[j+1][0] if j+1 < len(headings) else len(lines)
            body = '\n'.join(lines[start+1:end]).strip()
            # Skip tiny segments (likely false positive)
            if len(body) < 80:
                continue
            segments.append({
                'heading': htxt,
                'body': body,
                'line_start': start + 1,
                'line_end': end,
            })

        # If no headings found, treat whole file as one segment
        if not segments:
            body = text.strip()
            if len(body) < 80:
                continue
            segments.append({'heading': 'Full Text', 'body': body, 'line_start': 1, 'line_end': len(lines)})

        # Build frontmatter as a dict, then serialize with yaml.safe_dump
        # so escaping is handled automatically.
        fm_dict = {
            'id': f"ia-{stem}",
            'title': title_str,
            'source': {
                'name': title_str,
                'tradition': tradition_str,
                'original_language': 'English (translation)',
                'source_text': f"Archive/texts/sacred/mythology-arc/{f.name}",
                'reference': f"IA identifier: {stem}",
            },
            'extracted_units': [],
            'themes': ['to-be-classified'],
            'motifs': ['to-be-classified'],
            'adaptation_status': 'unprocessed',
        }
        # Build extracted_units as list of dicts
        units = []
        for k, seg in enumerate(segments, 1):
            uid = f"{slugify(seg['heading']) or 'section'}-{k}"
            snippet = seg['body'][:150].replace('\n', ' ')
            snippet = re.sub(r'\s+', ' ', snippet).strip()
            units.append({'id': uid, 'text': f"{snippet}...", 'reference': f"lines {seg['line_start']}-{seg['line_end']}"})
        fm_dict['extracted_units'] = units
        fm = "---\n" + yaml.safe_dump(fm_dict, default_flow_style=False, allow_unicode=True) + "---\n\n"
        fm += f"# {title_str}\n\n"
        fm += f"Source: Internet Archive identifier `{stem}`\n\n"
        fm += f"Detected sections: {len(segments)}\n\n"
        fm += "## Sections\n\n"
        for k, seg in enumerate(segments, 1):
            fm += f"### {k}. {seg['heading']}\n"
            fm += f"*lines {seg['line_start']}-{seg['line_end']}*\n\n"
            fm += seg['body'][:500].replace('\n', ' ') + "...\n\n"

        out_path = STORY_DIR / f"{stem}.md"
        out_path.write_text(fm, encoding='utf-8')

        story_entries.append({
            'id': f"ia-{stem}",
            'title': title_str,
            'source_id': f"ia-{stem}",
            'unit_count': len(segments),
            'file': f"Stories/by-source/ia/{stem}.md",
        })

    # Append to story-index.yaml
    idx_lines = ["\n"]
    for e in story_entries:
        idx_lines.append(f"  - id: {e['id']}")
        idx_lines.append(f"    title: \"{e['title']}\"")
        idx_lines.append(f"    source_id: {e['source_id']}")
        idx_lines.append(f"    unit_count: {e['unit_count']}")
        idx_lines.append(f"    file: {e['file']}")
        idx_lines.append(f"    adaptation_status: unprocessed")
        idx_lines.append("")
    with open(INDEX_PATH, 'a', encoding='utf-8') as out:
        out.write("\n".join(idx_lines))

    print(f"Segmented {len(files)} texts → {len(story_entries)} story files.")
    total_units = sum(e['unit_count'] for e in story_entries)
    print(f"Total extracted units (addressable segments): {total_units}")

if __name__ == "__main__":
    main()
