#!/usr/bin/env python3
"""
Tag motifs across 94 story files using curated keyword matching.

Motifs are specific narrative elements (deities, objects, events) that
recur across cultures. This script tags them using word-boundary regex
matching against a curated taxonomy.
"""

import re
from pathlib import Path

STORY_DIR = Path(r"G:\My Drive\AI\Sutrai\Stories\by-source\ia")

# Motif patterns: (regex_pattern, motif_id)
# Word-boundary matched to avoid false positives
MOTIF_PATTERNS = [
    # Creator/origin motifs
    (r'\bcreator\b', 'creator-god'),
    (r'\bsupreme being\b', 'creator-goddess'),
    (r'\bmother goddess\b', 'mother-goddess'),
    (r'\bgreat mother\b', 'mother-goddess'),
    (r'\bsky father\b', 'sky-father'),
    (r'\bzeus\b', 'sky-father'),
    (r'\bjupiter\b', 'sky-father'),
    (r'\bearth mother\b', 'earth-mother'),
    (r'\bgaia\b', 'earth-mother'),

    # Solar/lunar
    (r'\bsun god\b', 'sun-deity'),
    (r'\bsun goddess\b', 'sun-deity'),
    (r'\bmoon god\b', 'moon-deity'),
    (r'\bmoon goddess\b', 'moon-deity'),

    # Weather/nature deities
    (r'\bthunder god\b', 'thunder-deity'),
    (r'\bthor\b', 'thunder-deity'),
    (r'\bsea god\b', 'water-deity'),
    (r'\bposeidon\b', 'water-deity'),
    (r'\bfire god\b', 'fire-deity'),
    (r'\bagni\b', 'fire-deity'),
    (r'\bunderworld god\b', 'underworld-deity'),
    (r'\bhades\b', 'underworld-deity'),    # Dying/resurrected
    (r'\bdying god\b', 'dying-god'),
    (r'\bosiris\b', 'dying-god'),    # Wisdom/war/love deities
    (r'\bwisdom god\b', 'god-of-wisdom'),
    (r'\bathena\b', 'god-of-wisdom'),
    (r'\bwar god\b', 'god-of-war'),
    (r'\bares\b', 'god-of-war'),
    (r'\blove goddess\b', 'goddess-of-love'),
    (r'\baphrodite\b', 'goddess-of-love'),

    # Harvest/hunt/fate
    (r'\bharvest goddess\b', 'goddess-of-harvest'),
    (r'\bdemeter\b', 'goddess-of-harvest'),
    (r'\bhunt goddess\b', 'goddess-of-hunt'),
    (r'\bartemis\b', 'goddess-of-hunt'),
    (r'\bfate goddess\b', 'goddess-of-fate'),
    (r'\bmoirai\b', 'goddess-of-fate'),

    # Death/trickster
    (r'\bdeath god\b', 'god-of-death'),
    (r'\btrickster god\b', 'god-of-trickster'),
    (r'\bloki\b', 'god-of-trickster'),

    # Specific named deities (cross-cultural)
    (r'\bindra\b', 'god-of-thunder'),
    (r'\bapollo\b', 'god-of-sun'),
    (r'\bdiana\b', 'god-of-moon'),
    (r'\bvulcan\b', 'god-of-fire'),
    (r'\baeolus\b', 'god-of-wind'),
    (r'\bvaruna\b', 'god-of-water'),
    (r'\bceres\b', 'god-of-earth'),
    (r'\buranus\b', 'god-of-sky'),
    (r'\bpluto\b', 'god-of-underworld'),
    (r'\bjupiter\b', 'god-of-heaven'),
    (r'\bsatan\b', 'god-of-hell'),
    (r'\bplutus\b', 'god-of-wealth'),
    (r'\bmercury\b', 'god-of-travel'),
    (r'\bhygieia\b', 'god-of-healing'),
    (r'\bhephaestus\b', 'god-of-crafts'),
    (r'\bpriapus\b', 'god-of-fertility'),
    (r'\bhebe\b', 'god-of-youth'),
    (r'\bgeras\b', 'god-of-old-age'),
    (r'\btelos\b', 'god-of-end'),
    (r'\baion\b', 'god-of-eternity'),
    (r'\bapeiron\b', 'god-of-infinity'),
    (r'\bpan\b', 'god-of-all'),
    (r'\bhen\b', 'god-of-one'),
    (r'\bpolys\b', 'god-of-many'),

    # Sacred objects/plants
    (r'\bsacred object\b', 'sacred-object'),
    (r'\bbundle\b', 'sacred-object'),
    (r'\bsacred tree\b', 'sacred-plant'),
    (r'\btree of life\b', 'sacred-plant'),
    (r'\bsacred animal\b', 'sacred-animal'),
    (r'\btotem\b', 'sacred-animal'),

    # Transformation/magic
    (r'\bshape-shift\b', 'shape-shifting'),
    (r'\btransform\b', 'shape-shifting'),
    (r'\bcurse\b', 'curse'),
    (r'\bblessing\b', 'blessing'),
    (r'\bmiracle\b', 'miracle'),
    (r'\bprophecy\b', 'prophecy'),
    (r'\bdream\b', 'dream'),
    (r'\bomen\b', 'omen'),

    # Heroic motifs
    (r'\bhero\b', 'hero'),
    (r'\bquest\b', 'heroic-quest'),
    (r'\bunderworld\b', 'descent-to-underworld'),
    (r'\bhades\b', 'descent-to-underworld'),
    (r'\bhell\b', 'hell'),
    (r'\bheaven\b', 'heaven'),
    (r'\bparadise\b', 'heaven'),

    # Conflict
    (r'\bwar\b', 'war'),
    (r'\bbattle\b', 'war'),
    (r'\bdragon\b', 'dragon-slaying'),
    (r'\bserpent\b', 'dragon-slaying'),
    (r'\bgiant\b', 'giant-slaying'),
    (r'\btyrant\b', 'tyranny'),
    (r'\bliberation\b', 'liberation'),
    (r'\bexodus\b', 'liberation'),

    # Cosmogony
    (r'\bflood\b', 'flood'),
    (r'\bdeluge\b', 'flood'),
    (r'\bcreation\b', 'creation'),
    (r'\borigin\b', 'origin'),

    # Sacred marriage/rites
    (r'\bmarriage\b', 'marriage'),
    (r'\bwedding\b', 'marriage'),
    (r'\britual\b', 'ritual'),
    (r'\bceremony\b', 'ritual'),
    (r'\bsacrifice\b', 'sacrifice'),
    (r'\bprayer\b', 'prayer'),
    (r'\bpilgrimage\b', 'pilgrimage'),

    # Social
    (r'\bking\b', 'kingship'),
    (r'\bqueen\b', 'kingship'),
    (r'\bcovenant\b', 'covenant'),
    (r'\blaw\b', 'lawgiving'),
    (r'\bcommandment\b', 'lawgiving'),
    (r'\boath\b', 'oath'),
    (r'\bcustom\b', 'social-customs'),
    (r'\bhospitality\b', 'hospitality'),
    (r'\bjustice\b', 'justice'),
    (r'\bmercy\b', 'mercy'),
    (r'\bforgiveness\b', 'forgiveness'),
    (r'\benvy\b', 'envy'),
    (r'\bpride\b', 'hubris'),
    (r'\bhubris\b', 'hubris'),

    # Emotion
    (r'\blove\b', 'love'),
    (r'\bgrief\b', 'grief'),
    (r'\bmourning\b', 'mourning'),
    (r'\bjoy\b', 'joy'),
    (r'\bwonder\b', 'wonder'),
    (r'\bfear\b', 'fear'),
    (r'\bdespair\b', 'despair'),
    (r'\bhope\b', 'hope'),
    (r'\bbetrayal\b', 'betrayal'),
    (r'\bjoy\b', 'joy'),
]

def classify_motifs(text):
    """Classify text into motifs using word-boundary keyword matching."""
    text_lower = text.lower()
    motifs = set()

    for pattern, motif_id in MOTIF_PATTERNS:
        if re.search(pattern, text_lower):
            motifs.add(motif_id)

    return sorted(motifs) if motifs else ['to-be-classified']

def main():
    files = sorted(STORY_DIR.glob("*.md"))
    print(f"Tagging motifs for {len(files)} story files...")

    tagged = 0
    theme_counts = {}

    for f in files:
        text = f.read_text(encoding='utf-8', errors='ignore')
        # Extract units section
        units_match = re.search(r'extracted_units:\n(.*?)(?=\n(?:themes:|motifs:|adaptation_status:))', text, re.S)
        if not units_match:
            continue

        units_text = units_match.group(1)
        # Get all text snippets from units
        snippets = re.findall(r"text:\s*'([^']*)'", units_text)
        combined = " ".join(snippets)

        motifs = classify_motifs(combined)

        if motifs == ['to-be-classified']:
            pass  # Leave as-is
        else:
            tagged += 1
            for m in motifs:
                theme_counts[m] = theme_counts.get(m, 0) + 1

        # Replace motifs in file
        motifs_str = '\n'.join(f'  - {m}' for m in motifs)
        text = re.sub(r'motifs:\n\s*-\s*to-be-classified', f'motifs:\n{motifs_str}', text)
        f.write_text(text, encoding='utf-8')

    print(f"Tagged: {tagged}")
    print(f"\nMotif distribution:")
    for t, c in sorted(theme_counts.items(), key=lambda x: -x[1]):
        print(f"  {c:4}  {t}")

if __name__ == "__main__":
    main()
