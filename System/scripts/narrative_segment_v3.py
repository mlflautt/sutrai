#!/usr/bin/env python3
"""
Precise narrative segmenter - extracts actual myths/stories from IA texts.
"""

import re
import yaml
from pathlib import Path

SOURCE_DIR = Path(r"G:\My Drive\AI\Sutrai\Archive\texts\sacred\mythology-arc")


def find_myth_section_start(text):
    """Find the line where actual myths begin."""
    lines = text.split('\n')
    
    patterns = [
        r'^I\.?\s*TSIMSHIAN\s+MYTHS',
        r'^I\.?\s*(CELTIC|NORSE|GREEK|EGYPTIAN|CHINESE|JAPANESE|NATIVE|AMERICAN|INDIAN|AFRICAN|POLYNESIAN|HINDU|ARABIAN|PERSIAN|ARAB|WELSH|IRISH|MABINOGION|SAGA|EDDA|KALEVALA|MAHABHARATA|RAMAYANA)\s+MYTHS',
        r'^I\.?\s*(MYTHS|LEGENDS|TALES|STORIES|FABLES|NARRATIVES)',
        r'^(MYTHS|LEGENDS|TALES|STORIES|FABLES)\s+(OF|FROM|THE)',
    ]
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        for pattern in patterns:
            if re.search(pattern, stripped, re.I):
                return i
    
    return -1


def extract_structured_myths(text, section_start):
    """Extract myths with sub-parts from a structured myth section."""
    lines = text.split('\n')
    myths = []
    
    content = lines[section_start:]
    
    # Find top-level myth entries: "1. Txa'msem (The Raven Legend)*"
    myth_starts = []
    for i, line in enumerate(content):
        stripped = line.strip()
        if re.match(r'^\d+\.\s+[A-Z\'][A-Za-z\']', stripped):
            myth_starts.append((section_start + i, stripped))
    
    if not myth_starts:
        return []
    
    for idx, (start, title) in enumerate(myth_starts):
        # Find sub-parts: "(1) ORIGIN OF ...", "(2) ORIGIN OF ..."
        sub_parts = []
        end_search = myth_starts[idx + 1][0] if idx + 1 < len(myth_starts) else len(lines)
        
        for j in range(start + 1, end_search):
            line = lines[j].strip()
            if re.match(r'^\(\d+\)\s+[A-Z]', line):
                sub_parts.append((j, line))
        
        if sub_parts:
            # Extract each sub-part
            for sp_idx, (sp_start, sp_title) in enumerate(sub_parts):
                sp_end = sub_parts[sp_idx + 1][0] - 1 if sp_idx + 1 < len(sub_parts) else end_search - 1
                segment_lines = lines[sp_start:sp_end + 1]
                segment_text = '\n'.join(segment_lines).strip()
                if len(segment_text) > 300:
                    myths.append({
                        'title': f"{title} | {sp_title}",
                        'start_line': sp_start + 1,
                        'end_line': sp_end + 1,
                        'text': segment_text[:3000],
                        'full_length': len(segment_text),
                    })
        else:
            # No sub-parts, extract whole myth
            end = myth_starts[idx + 1][0] - 1 if idx + 1 < len(myth_starts) else len(lines) - 1
            segment_lines = lines[start:end + 1]
            segment_text = '\n'.join(segment_lines).strip()
            if len(segment_text) > 300:
                myths.append({
                    'title': title,
                    'start_line': start + 1,
                    'end_line': end + 1,
                    'text': segment_text[:3000],
                    'full_length': len(segment_text),
                })
    
    return myths


def extract_fairy_tales(text):
    """Extract fairy tales from story collections (e.g., Chinese Fairy Book)."""
    lines = text.split('\n')
    tales = []
    
    # Find the actual stories start (after TOC, preface, etc.)
    story_section = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Skip front matter
        if any(kw in stripped for kw in ['CONTENTS', 'PREFACE', 'INTRODUCTION', 'ILLUSTRATION', 'FRONTISPIECE', 'PUBLISHING', 'COPYRIGHT', 'DEDICATION', 'ACKNOWLEDGMENT']):
            continue
        # Look for first story
        if re.match(r'^\d+\.\s+[A-Z][A-Z\s]{10,}$', stripped):
            # Check next lines for narrative
            peek = '\n'.join(lines[i:i+30]).lower()
            if any(kw in peek for kw in ['once', 'upon', 'there was', 'there lived', 'king', 'queen', 'princess', 'prince', 'magic', 'fairy', 'spell', 'enchanted', 'went', 'came', 'said', 'spoke', 'herd', 'weaving', 'maiden']):
                story_section = i
                break
        # Alternative: "THE THREE RHYMSTERS" style all-caps titles
        if re.match(r'^THE\s+[A-Z\s]{10,}$', stripped) or re.match(r'^[A-Z][A-Z\s]{15,}$', stripped):
            if not any(w in stripped for w in ['CONTENTS', 'INDEX', 'ILLUSTRATION', 'FRONTISPIECE', 'PUBLISHING', 'COMPANY', 'COPYRIGHT', 'PREFACE', 'INTRODUCTION', 'BIBLIOGRAPHY', 'ACKNOWLEDGMENT', 'NOTES', 'APPENDIX', 'CHAPTER', 'BOOK']):
                peek = '\n'.join(lines[i:i+30]).lower()
                if any(kw in peek for kw in ['once', 'upon', 'there was', 'there lived', 'king', 'queen', 'princess', 'prince', 'magic', 'fairy', 'spell', 'enchanted', 'went', 'came', 'said', 'spoke']):
                    story_section = i
                    break
    
    if story_section == -1:
        return []
    
    # Now extract individual tales
    tale_starts = []
    for i in range(story_section, len(lines)):
        stripped = lines[i].strip()
        if len(stripped) < 5 or len(stripped) > 200:
            continue
        
        # All-caps story titles
        if re.match(r'^[A-Z][A-Z\s]{10,}$', stripped):
            if not any(w in stripped for w in ['CONTENTS', 'INDEX', 'ILLUSTRATION', 'FRONTISPIECE', 'PUBLISHING', 'COMPANY', 'COPYRIGHT', 'PREFACE', 'INTRODUCTION', 'BIBLIOGRAPHY', 'ACKNOWLEDGMENT', 'NOTES', 'APPENDIX', 'CHAPTER', 'BOOK', 'THE END', 'END OF', 'NOTES ON', 'GLOSSARY']):
                tale_starts.append((i, stripped))
        # "Chapter X - Title" for some books
        elif re.match(r'^(CHAPTER|Chapter)\s+\d+', stripped):
            if 'fairy' in stripped.lower() or 'tale' in stripped.lower() or 'story' in stripped.lower():
                tale_starts.append((i, stripped))
    
    # Create boundaries
    for idx, (start, title) in enumerate(tale_starts):
        end = tale_starts[idx + 1][0] - 1 if idx + 1 < len(tale_starts) else len(lines) - 1
        if end - start > 30:
            segment_lines = lines[start:end+1]
            segment_text = '\n'.join(segment_lines).strip()
            if len(segment_text) > 500:
                tales.append({
                    'title': title,
                    'start_line': start + 1,
                    'end_line': end + 1,
                    'text': segment_text[:3000],
                    'full_length': len(segment_text),
                })
    
    return tales


def extract_chinook_tales(text):
    """Extract Chinook texts - they have numbered entries with native text + translation."""
    lines = text.split('\n')
    tales = []
    
    # Find start of actual texts
    text_section = -1
    for i, line in enumerate(lines):
        if re.match(r'^\d+\.\s+[A-Z\'][A-Z\']', line.strip()):
            text_section = i
            break
    
    if text_section == -1:
        return []
    
    # Extract each numbered entry
    tale_starts = []
    for i in range(text_section, len(lines)):
        stripped = lines[i].strip()
        if re.match(r'^\d+\.\s+[A-Z\']', stripped):
            tale_starts.append((i, stripped))
    
    for idx, (start, title) in enumerate(tale_starts):
        end = tale_starts[idx + 1][0] - 1 if idx + 1 < len(tale_starts) else len(lines) - 1
        if end - start > 20:
            segment_lines = lines[start:end+1]
            segment_text = '\n'.join(segment_lines).strip()
            if len(segment_text) > 300:
                tales.append({
                    'title': title,
                    'start_line': start + 1,
                    'end_line': end + 1,
                    'text': segment_text[:3000],
                    'full_length': len(segment_text),
                })
    
    return tales


def classify_and_extract(source_path):
    """Classify text type and extract narratives."""
    text = source_path.read_text(encoding='utf-8', errors='ignore')
    stem = source_path.stem
    stem_lower = stem.lower()
    
    # Tsimshian mythology - special handling
    if 'tsimshian' in stem_lower:
        section = find_myth_section_start(text)
        if section >= 0:
            return extract_structured_myths(text, section)
    
    # Chinook texts - special handling
    if 'chinook' in stem_lower:
        return extract_chinook_tales(text)
    
    # Fairy tale collections
    if any(kw in stem_lower for kw in ['fairy', 'celtic', 'norse', 'greek', 'egyptian', 'chinese', 'japanese', 'native', 'american', 'indian', 'african', 'polynesian', 'welsh', 'irish', 'armenian', 'nahuatl', 'ancient irish', 'ancient nahuatl', 'mabinogion', 'kalevala', 'saga', 'edda']):
        return extract_fairy_tales(text)
    
    # Mythology/legends collections
    if any(kw in stem_lower for kw in ['mythology', 'myths', 'legends', 'tales', 'folk', 'celticmyth', 'classicmyth', 'guide to myth']):
        section = find_myth_section_start(text)
        if section >= 0:
            return extract_structured_myths(text, section)
        return extract_fairy_tales(text)
    
    # Religious texts - extract chapters
    if any(kw in stem_lower for kw in ['bhagavad', 'gita', 'brahmana', 'satapatha', 'veda', 'upani', 'sutra', 'purana', 'vishnu', 'beginnings hindu']):
        return extract_religious_chapters(text)
    
    return []


def extract_religious_chapters(text):
    """Extract chapters from religious texts."""
    lines = text.split('\n')
    chapters = []
    
    chapter_starts = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r'^(CHAPTER|Chapter|BOOK|Book|SURA|Sura|SUTRA|Sutra|CANTO|Canto|VERSE|Verse)\s+\d+', stripped):
            chapter_starts.append((i, stripped))
    
    for idx, (start, title) in enumerate(chapter_starts):
        end = chapter_starts[idx + 1][0] - 1 if idx + 1 < len(chapter_starts) else len(lines) - 1
        if end - start > 50:
            segment_lines = lines[start:end+1]
            segment_text = '\n'.join(segment_lines).strip()
            if len(segment_text) > 500:
                chapters.append({
                    'title': title,
                    'start_line': start + 1,
                    'end_line': end + 1,
                    'text': segment_text[:3000],
                    'full_length': len(segment_text),
                })
    
    return chapters


def main():
    files = sorted(SOURCE_DIR.glob("*.txt"))
    
    all_results = {}
    total = 0
    
    for src in files:
        stem = src.stem
        print(f"\n=== {stem} ===")
        
        narratives = classify_and_extract(src)
        
        print(f"  Found {len(narratives)} narratives")
        for n in narratives[:5]:
            print(f"    L{n['start_line']}-{n['end_line']} ({n['full_length']} chars): {n['title'][:80]}")
        if len(narratives) > 5:
            print(f"    ... and {len(narratives) - 5} more")
        
        if narratives:
            all_results[stem] = {'narratives': narratives}
            total += len(narratives)
    
    print(f"\n=== SUMMARY ===")
    print(f"Files processed: {len(files)}")
    print(f"Files with narratives: {len(all_results)}")
    print(f"Total narratives extracted: {total}")
    
    # Save
    with open(SOURCE_DIR.parent / 'narrative_stories_v3.yaml', 'w', encoding='utf-8') as f:
        yaml.dump({'extracted_narratives': all_results}, f, default_flow_style=False, allow_unicode=True)
    
    print(f"\nSaved to Archive/texts/sacred/narrative_stories_v3.yaml")


if __name__ == "__main__":
    main()