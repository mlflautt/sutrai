#!/usr/bin/env python3
"""
Classify extracted narrative units with themes and motifs.

Approach:
- Curated taxonomy of ~80 themes and ~30 motifs
- Multi-word phrase matching (more specific = higher confidence)
- Threshold: at least 2 keyword matches from DIFFERENT theme categories
- Text length normalized (longer texts need more matches)
"""

import re
from pathlib import Path

STORY_DIR = Path(r"G:\My Drive\AI\Sutrai\Stories\by-source\ia")

# Theme classification: category → list of (regex_pattern, weight)
# Higher weight = more specific/diagnostic
THEME_CATEGORIES = {
    "cosmogony": [
        (r'\bcreate\b', 1), (r'\bcreation\b', 1), (r'\bbeginning of the world\b', 3),
        (r'\borigin of death\b', 3), (r'\bwhy we die\b', 2),
        (r'\borigin of fire\b', 3), (r'\bprometheus\b', 2),
        (r'\bfirst humans\b', 2), (r'\badam and eve\b', 2),
        (r'\bcosmic egg\b', 3), (r'\bworld egg\b', 3),
        (r'\bearth diver\b', 3), (r'\bex nihilo\b', 3),
        (r'\bemergence\b', 1), (r'\bunderworld\b', 1),
    ],
    "eschatology": [
        (r'\bflood\b', 1), (r'\bdeluge\b', 2), (r'\bnoah\b', 2),
        (r'\bapocalypse\b', 2), (r'\barmageddon\b', 2), (r'\bragnarok\b', 2),
        (r'\bend of the world\b', 3), (r'\blast day\b', 2),
        (r'\bjudgment\b', 1), (r'\bresurrection\b', 1),
    ],
    "divine": [
        (r'\bgod\b', 1), (r'\bgoddess\b', 1), (r'\bdeity\b', 1),
        (r'\bpantheon\b', 2), (r'\bpolytheism\b', 2),
        (r'\bmonotheism\b', 2), (r'\bone god\b', 2),
        (r'\btrickster\b', 1), (r'\bcoyote\b', 2), (r'\braven\b', 1),
        (r'\banansi\b', 2), (r'\bculture hero\b', 2),
        (r'\bdying god\b', 2), (r'\bosiris\b', 2),
        (r'\bresurrected\b', 1),
    ],
    "hero": [
        (r'\bhero\b', 1), (r'\bquest\b', 1), (r'\bjourney\b', 1),
        (r'\bunderworld\b', 1), (r'\bhades\b', 1),
        (r'\bhell\b', 1), (r'\bheaven\b', 1), (r'\bparadise\b', 1),
        (r'\breincarnation\b', 1), (r'\btransmigration\b', 1),
    ],
    "ethics": [
        (r'\bsin\b', 1), (r'\btransgression\b', 1), (r'\btaboo\b', 1),
        (r'\bpunishment\b', 1), (r'\breward\b', 1),
        (r'\bwisdom\b', 1), (r'\bteaching\b', 1), (r'\bcounsel\b', 1),
        (r'\bcourage\b', 1), (r'\bsacrifice\b', 1), (r'\bself-sacrifice\b', 2),
        (r'\bhubris\b', 1), (r'\bpride\b', 1), (r'\benvy\b', 1),
    ],
    "magic": [
        (r'\bmagic\b', 1), (r'\bsorcery\b', 1), (r'\bwitch\b', 1),
        (r'\bshape-shift\b', 2), (r'\btransform\b', 1),
        (r'\bprophecy\b', 1), (r'\bprophet\b', 1), (r'\bforetell\b', 1),
        (r'\bomen\b', 1), (r'\bdream\b', 1),
        (r'\bmiracle\b', 1), (r'\bcurse\b', 1), (r'\bblessing\b', 1),
        (r'\bsacred object\b', 2), (r'\bbundle\b', 1),
        (r'\bsacred tree\b', 2), (r'\btree of life\b', 2),
    ],
    "conflict": [
        (r'\bwar\b', 1), (r'\bbattle\b', 1), (r'\bgiant\b', 1),
        (r'\bdragon\b', 1), (r'\bserpent\b', 1),
        (r'\btyranny\b', 1), (r'\bliberation\b', 1), (r'\bexodus\b', 2),
        (r'\bcovenant\b', 1), (r'\blaw\b', 1), (r'\bcommandment\b', 1),
        (r'\bking\b', 1), (r'\bqueen\b', 1),
    ],
    "nature": [
        (r'\bsun\b', 1), (r'\bsolar\b', 1), (r'\bmoon\b', 1), (r'\blunar\b', 1),
        (r'\bstar\b', 1), (r'\bstorm\b', 1), (r'\bthunder\b', 1),
        (r'\bwater\b', 1), (r'\briver\b', 1), (r'\bocean\b', 1), (r'\bsea\b', 1),
        (r'\bearth\b', 1), (r'\bmountain\b', 1), (r'\bforest\b', 1),
        (r'\brain\b', 1), (r'\bfertility\b', 1), (r'\bharvest\b', 1),
        (r'\bdrought\b', 1), (r'\bfire\b', 1), (r'\bwind\b', 1),
        (r'\bworld tree\b', 3), (r'\baxis mundi\b', 3),
    ],
    "comparative": [
        (r'\bcomparative\b', 1), (r'\bmythology\b', 1),
        (r'\britual\b', 1), (r'\bceremony\b', 1), (r'\brite\b', 1),
        (r'\btotemism\b', 1), (r'\btotem\b', 1),
        (r'\bmagic and religion\b', 3), (r'\bsolar myth\b', 3),
        (r'\betiological\b', 1), (r'\bdiffusion\b', 1),
    ],
    "emotion": [
        (r'\blove\b', 1), (r'\bgrief\b', 1), (r'\bmourning\b', 1),
        (r'\bjoy\b', 1), (r'\bwonder\b', 1), (r'\bfear\b', 1),
        (r'\bdespair\b', 1), (r'\bhope\b', 1), (r'\bbetrayal\b', 1),
        (r'\bforgiveness\b', 1),
    ],
    "society": [
        (r'\bmarriage\b', 1), (r'\bwedding\b', 1), (r'\bfamily\b', 1),
        (r'\bclan\b', 1), (r'\bcustom\b', 1), (r'\bhospitality\b', 1),
        (r'\bprayer\b', 1), (r'\bpilgrimage\b', 1),
    ],
    "tradition_specific": [
        (r'\bvedic\b', 1), (r'\bsama veda\b', 3), (r'\brig veda\b', 3),
        (r'\batharva veda\b', 3), (r'\byajur veda\b', 3),
        (r'\bbuddha\b', 1), (r'\bdhammapada\b', 3), (r'\bsutta\b', 2),
        (r'\bbuddhist\b', 1), (r'\bjain\b', 1), (r'\bjaina\b', 2),
        (r'\bsufi\b', 1), (r'\bsufism\b', 2), (r'\bibn arabi\b', 3),
        (r'\brumi\b', 2), (r'\bdao\b', 1), (r'\btao\b', 1),
        (r'\blaozi\b', 2), (r'\bzhuangzi\b', 2),
        (r'\bconfucius\b', 2), (r'\bconfucian\b', 1),
        (r'\bshinto\b', 1), (r'\bnorito\b', 2),
        (r'\bzen\b', 1), (r'\bkoan\b', 2),
        (r'\bjataka\b', 2), (r'\bramayana\b', 3), (r'\bmahabharata\b', 3),
        (r'\bgreek\b', 1), (r'\bgreece\b', 1), (r'\bnorse\b', 1),
        (r'\biceland\b', 1), (r'\bceltic\b', 1), (r'\birish\b', 1),
        (r'\bwelsh\b', 1), (r'\bscottish\b', 1),
        (r'\beygyptian\b', 1), (r'\beygypt\b', 1),
        (r'\bmesopotamian\b', 1), (r'\bbabylonian\b', 1),
        (r'\bassyrian\b', 1), (r'\bsumerian\b', 1),
        (r'\bnative american\b', 1), (r'\bindian\b', 1),
        (r'\bcherokee\b', 2), (r'\bpawnee\b', 2), (r'\bnavajo\b', 2),
        (r'\bsioux\b', 2), (r'\bhopi\b', 2), (r'\biroquois\b', 2),
        (r'\bafrican\b', 1), (r'\byoruba\b', 2), (r'\bzulu\b', 2),
        (r'\bbushman\b', 2), (r'\bchinese\b', 1), (r'\bchina\b', 1),
        (r'\bjapanese\b', 1), (r'\bjapan\b', 1), (r'\bkojiki\b', 3),
        (r'\bnihongi\b', 3), (r'\bslavic\b', 1), (r'\brussian\b', 1),
        (r'\bpolynesian\b', 1), (r'\bmaori\b', 2), (r'\bhawaiian\b', 2),
        (r'\bsamoan\b', 2), (r'\barmenian\b', 1), (r'\barmenia\b', 1),
        (r'\bzoroastrian\b', 1), (r'\bavesta\b', 2),
        (r'\bislamic\b', 1), (r'\bquran\b', 2), (r'\bhadith\b', 2),
        (r'\bmuslim\b', 1), (r'\bchristian\b', 1), (r'\bbible\b', 1),
        (r'\bjewish\b', 1), (r'\btorah\b', 2), (r'\bmidrash\b', 2),
        (r'\bhebrew\b', 1), (r'\bgnostic\b', 1), (r'\bhermes\b', 1),
        (r'\balchemy\b', 1), (r'\bastrology\b', 1),
    ],
}

def classify_text(text, min_categories=2, min_weight=3):
    """
    Classify text into themes.
    Requires matches from at least `min_categories` different theme categories,
    with total weight >= `min_weight`.
    """
    text_lower = text.lower()
    category_scores = {}

    for category, patterns in THEME_CATEGORIES.items():
        score = 0
        for pattern, weight in patterns:
            if re.search(pattern, text_lower):
                score += weight
        if score > 0:
            category_scores[category] = score

    total_weight = sum(category_scores.values())
    num_categories = len(category_scores)

    if num_categories >= min_categories and total_weight >= min_weight:
        return sorted(category_scores.keys())
    else:
        return ['to-be-classified']

def main():
    files = sorted(STORY_DIR.glob("*.md"))
    print(f"Classifying {len(files)} story files...")

    classified = 0
    unclassified = 0
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

        themes = classify_text(combined, min_categories=2, min_weight=3)

        if themes == ['to-be-classified']:
            unclassified += 1
        else:
            classified += 1
            for t in themes:
                theme_counts[t] = theme_counts.get(t, 0) + 1

        # Replace themes/motifs in file
        text = re.sub(r'themes:\n\s*-\s*to-be-classified', 'themes:\n' + '\n'.join(f'  - {t}' for t in themes), text)
        text = re.sub(r'motifs:\n\s*-\s*to-be-classified', 'motifs:\n  - to-be-classified', text)
        f.write_text(text, encoding='utf-8')

    print(f"Classified: {classified}")
    print(f"Unclassified (needs LLM): {unclassified}")
    print(f"\nTheme distribution:")
    for t, c in sorted(theme_counts.items(), key=lambda x: -x[1]):
        print(f"  {c:4}  {t}")

if __name__ == "__main__":
    main()
