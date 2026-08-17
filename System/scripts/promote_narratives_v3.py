#!/usr/bin/env python3
"""
Promote extracted narratives to standalone story files.
Filters out noise and writes genuine stories with YAML frontmatter.
"""

import re
import yaml
from pathlib import Path

EXTRACTED_PATH = Path(r"G:\My Drive\AI\Sutrai\Archive\texts\sacred\narrative_stories_v3.yaml")
OUTPUT_DIR = Path(r"G:\My Drive\AI\Sutrai\Stories\by-source\ia\promoted_v3")
SOURCE_DIR = Path(r"G:\My Drive\AI\Sutrai\Archive\texts\sacred\mythology-arc")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Noise patterns to filter out
NOISE_PATTERNS = [
    r'UNIVERSITY OF WISCONSIN',
    r'PRINTED AT',
    r'PUBLISHING',
    r'COPYRIGHT',
    r'FRONTISPIECE',
    r'ILLUSTRATION',
    r'^CONTENTS$',
    r'^INDEX$',
    r'^PREFACE$',
    r'^INTRODUCTION$',
    r'^BIBLIOGRAPHY$',
    r'^ACKNOWLEDGMENT$',
    r'^NOTES$',
    r'^APPENDIX$',
    r'^GLOSSARY$',
    r'^THE END$',
    r'^END OF',
    r'^[IVX]+\.\s*$',  # Just roman numerals
    r'^\d+\.\s*$',  # Just numbers
]


def is_noise(title, text):
    """Check if a narrative is noise/front-matter."""
    title_upper = title.upper()
    text_upper = text.upper()
    
    for pattern in NOISE_PATTERNS:
        if re.search(pattern, title_upper):
            return True
        if re.search(pattern, text_upper[:500]):
            return True
    
    # Check if title is just a section header
    if re.match(r'^(NURSERY|LEGENDS|LITERARY)\s+(FAIRY\s+)?TALES?$', title_upper):
        return True
    
    # Check if it's mostly uppercase (scan artifacts)
    words = text.split()
    if len(words) > 20:
        upper_words = sum(1 for w in words[:50] if w.isupper() and len(w) > 2)
        if upper_words / min(50, len(words)) > 0.7:
            return True
    
    return False


def clean_text(text):
    """Clean up OCR artifacts."""
    # Fix common OCR issues
    text = text.replace('  ', ' ')
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[|]{2,}', '', text)  # Remove scan lines
    return text.strip()


def generate_story_id(source_stem, narrative_idx, title):
    """Generate a clean story ID."""
    # Clean title for ID
    title_clean = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower())
    title_clean = title_clean.strip('-')[:50]
    return f"{source_stem}_{narrative_idx:03d}_{title_clean}"


def extract_metadata_from_text(text):
    """Extract potential metadata from story text."""
    meta = {}
    
    # Look for cultural markers
    cultures = {
        'tsimshian': 'Tsimshian',
        'chinook': 'Chinook',
        'pawnee': 'Pawnee',
        'chinese': 'Chinese',
        'celtic': 'Celtic',
        'norse': 'Norse',
        'greek': 'Greek',
        'egyptian': 'Egyptian',
        'japanese': 'Japanese',
        'indian': 'Indian',
        'african': 'African',
        'west african': 'West African',
        'yoruba': 'Yoruba',
        'arabian': 'Arabian',
        'persian': 'Persian',
        'hindu': 'Hindu',
        'armenian': 'Armenian',
        'nahuatl': 'Nahuatl',
        'aztec': 'Aztec',
        'mabinogion': 'Welsh',
        'kalevala': 'Finnish',
        'saga': 'Norse/Icelandic',
        'edda': 'Norse',
        'vedic': 'Vedic',
        'purana': 'Hindu',
        'mahabharata': 'Hindu',
        'ramayana': 'Hindu',
        'bible': 'Biblical',
        'quran': 'Islamic',
    }
    
    text_lower = text.lower()
    for kw, culture in cultures.items():
        if kw in text_lower[:5000]:
            meta['culture'] = culture
            break
    
    # Detect story type
    if any(kw in text_lower[:2000] for kw in ['once upon', 'there was', 'there lived', 'long ago']):
        meta['story_type'] = 'fairy_tale'
    elif any(kw in text_lower[:2000] for kw in ['trickster', 'coyote', 'raven', 'anansi', 'spider']):
        meta['story_type'] = 'trickster_tale'
    elif any(kw in text_lower[:2000] for kw in ['origin of', 'how the', 'why the', 'creation']):
        meta['story_type'] = 'origin_myth'
    elif any(kw in text_lower[:2000] for kw in ['hero', 'quest', 'journey', 'battle', 'warrior']):
        meta['story_type'] = 'hero_tale'
    elif any(kw in text_lower[:2000] for kw in ['god', 'goddess', 'deity', 'divine']):
        meta['story_type'] = 'divine_myth'
    else:
        meta['story_type'] = 'legend'
    
    return meta


def find_myth_section_start(text, source_stem):
    """Find the line where actual myths begin for specific sources."""
    lines = text.split('\n')
    stem_lower = source_stem.lower()
    
    if 'tsimshian' in stem_lower:
        # Look for "I. TSIMSHIAN MYTHS"
        for i, line in enumerate(lines):
            if re.match(r'^I\.?\s*TSIMSHIAN\s+MYTHS', line.strip(), re.I):
                return i
    
    return -1


def main():
    with open(EXTRACTED_PATH, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    extracted = data.get('extracted_narratives', {})
    
    total_written = 0
    total_filtered = 0
    
    for source_stem, source_data in extracted.items():
        narratives = source_data.get('narratives', [])
        if not narratives:
            continue
        
        # Load full source text
        source_file = SOURCE_DIR / f"{source_stem}.txt"
        if not source_file.exists():
            # Try case-insensitive
            matches = list(SOURCE_DIR.glob(f"{source_stem}*.txt"))
            if matches:
                source_file = matches[0]
            else:
                print(f"Warning: Source file not found for {source_stem}")
                continue
        
        full_text = source_file.read_text(encoding='utf-8', errors='ignore')
        
        # Find myth section start for this source
        myth_section_start = find_myth_section_start(full_text, source_stem)
        
        story_idx = 0
        for n in narratives:
            if is_noise(n['title'], n['text']):
                total_filtered += 1
                continue
            
            # For Tsimshian, skip narratives before the myth section
            if myth_section_start >= 0 and n['start_line'] <= myth_section_start + 1:
                total_filtered += 1
                continue
            
            # Get full text from source
            start = n['start_line'] - 1
            end = n['end_line']
            full_story = full_text.split('\n')[start:end]
            full_story_text = '\n'.join(full_story).strip()
            full_story_text = clean_text(full_story_text)
            
            if len(full_story_text) < 500:
                total_filtered += 1
                continue
            
            story_idx += 1
            story_id = generate_story_id(source_stem, story_idx, n['title'])
            
            # Build frontmatter
            meta = extract_metadata_from_text(full_story_text)
            
            frontmatter = {
                'id': story_id,
                'source': source_stem,
                'title': n['title'],
                'source_lines': f"{n['start_line']}-{n['end_line']}",
                'length': len(full_story_text),
                'culture': meta.get('culture', 'Unknown'),
                'story_type': meta.get('story_type', 'legend'),
                'status': 'promoted',
            }
            
            # Write story file
            output_file = OUTPUT_DIR / f"{story_id}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('---\n')
                yaml.dump(frontmatter, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                f.write('---\n\n')
                f.write(full_story_text)
            
            total_written += 1
        
        if story_idx > 0:
            print(f"  {source_stem}: wrote {story_idx} stories, filtered {len(narratives) - story_idx}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total stories written: {total_written}")
    print(f"Total filtered out: {total_filtered}")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()