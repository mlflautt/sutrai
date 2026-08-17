#!/usr/bin/env python3
"""
Identify story-collection texts vs. scholarly texts.

Story collections contain named, discrete narratives (fairy tales, myths, sagas).
Scholarly texts contain analysis, commentary, or continuous prose.

Creates a manifest mapping each source file to its category and
story-extraction strategy.
"""

import re
from pathlib import Path

STORY_DIR = Path(r"G:\My Drive\AI\Sutrai\Stories\by-source\ia")

# Patterns that indicate story-collection structure
STORY_INDICATORS = [
    r'\bCHAPTER\b', r'\bChap\.\s*[0-9]+', r'^[IVXLC]+\.\s',
    r'\bThe\s+[A-Z][a-z]+\s+(?:of|and|who|that|in|on|with|from|to|for)\b',  # "The X of Y"
    r'\bHow\s+[a-z]', r'\bThe\s+[a-z]+\s+(?:tale|story|legend|myth|saga|fable)\b',
    r'\bMYTH\b', r'\bLEGEND\b', r'\bSAGA\b', r'\bTALE\b',
    r'\bPart\s+[0-9]+\b', r'\bPART\s+[0-9]+\b',
]

# Patterns that indicate scholarly/continuous text
SCHOLARLY_INDICATORS = [
    r'\bIbid\.\b', r'\bop\.\s*cit\.\b', r'\bloc\.\s*cit\.\b',
    r'\bed\.\s*by\b', r'\btrans\.\s*by\b', r'\bp\.\s*[0-9]+\b',
    r'\bVol\.\s*[0-9]+\b', r'\bVolume\s+[0-9]+\b',
    r'\bintroduction\b', r'\bpreface\b', r'\bconclusion\b',
    r'\breference\b', r'\bbibliography\b', r'\bindex\b',
    r'\banalysis\b', r'\bstudy\b', r'\btreatise\b',
    r'\breligion\b', r'\bmythology\b', r'\bfolklore\b',
    r'\bcomparative\b', r'\binterpretation\b',
]

def categorize_text(text):
    """Return ('story_collection'|'scholarly'|'mixed', confidence)."""
    story_score = 0
    scholarly_score = 0

    for pattern in STORY_INDICATORS:
        matches = len(re.findall(pattern, text, re.M))
        story_score += matches

    for pattern in SCHOLARLY_INDICATORS:
        matches = len(re.findall(pattern, text, re.M))
        scholarly_score += matches

    # Normalize by text length
    text_len = len(text)
    if text_len == 0:
        return 'unknown', 0

    story_score_norm = story_score / (text_len / 10000)
    scholarly_score_norm = scholarly_score / (text_len / 10000)

    if story_score_norm > scholarly_score_norm * 1.5:
        return 'story_collection', story_score_norm
    elif scholarly_score_norm > story_score_norm * 1.5:
        return 'scholarly', scholarly_score_norm
    else:
        return 'mixed', max(story_score_norm, scholarly_score_norm)

def main():
    files = sorted(STORY_DIR.glob("*.md"))
    manifest = {}

    for f in files:
        text = f.read_text(encoding='utf-8', errors='ignore')
        category, confidence = categorize_text(text)
        manifest[f.name] = {
            'category': category,
            'confidence': round(confidence, 2),
        }

    # Print summary
    cats = {}
    for name, info in manifest.items():
        cat = info['category']
        cats.setdefault(cat, []).append(name)

    print(f"Total files: {len(manifest)}")
    for cat, names in sorted(cats.items()):
        print(f"  {cat}: {len(names)}")
    print()

    # Print story collections
    if 'story_collection' in cats:
        print("Story collections:")
        for name in sorted(cats['story_collection']):
            print(f"  {name}")

    return manifest

if __name__ == "__main__":
    main()
