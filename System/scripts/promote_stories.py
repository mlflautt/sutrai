#!/usr/bin/env python3
"""
Promote high-value narrative units to standalone story files.

Reads full text from source files only for units that pass initial filtering.
"""

import re
import yaml
from pathlib import Path

STORY_DIR = Path(r"G:\My Drive\AI\Sutrai\Stories\by-source\ia")
PROMOTED_DIR = Path(r"G:\My Drive\AI\Sutrai\Stories\by-source\ia\promoted")
INDEX_PATH = Path(r"G:\My Drive\AI\Sutrai\System\indexes\promoted-stories.yaml")
SOURCE_DIR = Path(r"G:\My Drive\AI\Sutrai\Archive\texts\sacred\mythology-arc")

STORY_KEYWORDS = [
    'myth', 'legend', 'saga', 'tale', 'fable', 'fairy tale',
    'hero', 'god', 'goddess', 'deity', 'divine',
    'king', 'queen', 'prince', 'princess',
    'dragon', 'giant', 'monster', 'demon',
    'quest', 'journey', 'adventure',
    'love', 'war', 'battle', 'magic',
    'flood', 'creation', 'origin', 'destiny',
    'cursed', 'blessed', 'enchanted', 'transformed',
    'prometheus', 'hercules', 'odysseus', 'beowulf', 'gilgamesh',
    'rama', 'sita', 'krishna', 'buddha', 'shiva', 'vishnu',
    'odin', 'thor', 'loki', 'zeus', 'athena', 'apollo',
    'osiris', 'isis', 'anubis', 'ra', 'amaterasu',
    'coyote', 'raven', 'anansi', 'spider',
]

ANTI_KEYWORDS = [
    'introduction', 'preface', 'conclusion', 'appendix',
    'footnote', 'reference', 'bibliography', 'index',
    'chapter', 'section', 'volume', 'page',
    'translated by', 'edited by', 'published by',
    'analysis', 'study', 'interpretation', 'commentary',
    'op. cit.', 'ibid.', 'loc. cit.',
]

def is_story_text(text):
    if len(text) < 200:
        return False
    text_lower = text.lower()
    anti_score = sum(1 for kw in ANTI_KEYWORDS if kw in text_lower)
    if anti_score >= 2:
        return False
    story_score = sum(1 for kw in STORY_KEYWORDS if kw in text_lower)
    return story_score >= 1

def extract_full_text(source_file, line_start, line_end):
    try:
        text = source_file.read_text(encoding='utf-8', errors='ignore')
        lines = text.split('\n')
        start = max(0, line_start - 1)
        end = min(len(lines), line_end)
        return '\n'.join(lines[start:end]).strip()
    except Exception:
        return None

def slugify(s):
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s.lower()).strip('-')
    return s[:60]

def main():
    PROMOTED_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(STORY_DIR.glob("*.md"))
    
    promoted = []
    total_units = 0
    story_units = 0
    
    for f in files:
        stem = f.stem
        text = f.read_text(encoding='utf-8', errors='ignore')
        
        source_file = SOURCE_DIR / f"{stem}.txt"
        if not source_file.exists():
            continue
        
        parts = text.split('---', 2)
        if len(parts) < 3:
            continue
        try:
            fm = yaml.safe_load(parts[1])
        except Exception:
            continue
        
        units = fm.get('extracted_units', [])
        themes = fm.get('themes', [])
        motifs = fm.get('motifs', [])
        title = fm.get('title', stem)
        source_info = fm.get('source', {})
        tradition = source_info.get('tradition', 'unknown') if isinstance(source_info, dict) else 'unknown'
        
        # Read full source text once
        full_source = source_file.read_text(encoding='utf-8', errors='ignore')
        source_lines = full_source.split('\n')
        
        for unit in units:
            total_units += 1
            
            ref = unit.get('reference', '')
            m = re.match(r'lines (\d+)-(\d+)', ref)
            if not m:
                continue
            
            line_start, line_end = int(m.group(1)), int(m.group(2))
            start = max(0, line_start - 1)
            end = min(len(source_lines), line_end)
            full_text = '\n'.join(source_lines[start:end]).strip()
            
            if len(full_text) < 200:
                continue
            
            if not is_story_text(full_text):
                continue
            
            story_units += 1
            
            uid = unit.get('id', 'unknown')
            story_id = f"promoted-{slugify(uid)}"
            story_file = PROMOTED_DIR / f"{story_id}.md"
            
            story_fm = {
                'id': story_id,
                'title': uid.replace('-', ' ').title(),
                'source': {
                    'name': title,
                    'tradition': tradition,
                    'source_text': f"Archive/texts/sacred/mythology-arc/{stem}.txt",
                    'reference': f"lines {line_start}-{line_end}",
                },
                'themes': themes,
                'motifs': motifs,
                'adaptation_status': 'unprocessed',
            }
            
            fm_text = "---\n" + yaml.safe_dump(story_fm, default_flow_style=False, allow_unicode=True) + "---\n\n"
            body = f"# {uid.replace('-', ' ').title()}\n\n**Source:** {title} ({tradition})\n**Lines:** {line_start}-{line_end}\n\n{full_text[:2000]}\n\n"
            
            story_file.write_text(fm_text + body, encoding='utf-8')
            promoted.append({
                'id': story_id,
                'title': uid.replace('-', ' ').title(),
                'source': stem,
                'tradition': tradition,
                'lines': f"{line_start}-{line_end}",
            })
    
    with open(INDEX_PATH, 'w', encoding='utf-8') as out:
        yaml.dump({'promoted_stories': promoted}, out, default_flow_style=False, allow_unicode=True)
    
    print(f"Total units scanned: {total_units}")
    print(f"Story units found: {story_units}")
    print(f"Promoted: {len(promoted)}")
    print(f"\nBy tradition:")
    trad_counts = {}
    for p in promoted:
        trad_counts[p['tradition']] = trad_counts.get(p['tradition'], 0) + 1
    for t, c in sorted(trad_counts.items(), key=lambda x: -x[1]):
        print(f"  {c:3}  {t}")

if __name__ == "__main__":
    main()
