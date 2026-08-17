#!/usr/bin/env python3
"""
Manually curate the 12 unclassified story files.

These texts were published works whose source-text headers didn't contain
enough English keyword matches for the rule-based classifier. Manual curation
is appropriate and more accurate for known texts.
"""

import re
from pathlib import Path

STORY_DIR = Path(r"G:\My Drive\AI\Sutrai\Stories\by-source\ia")

MANUAL_CLASSIFICATIONS = {
    "celtictwilightme00yeat.md": {
        "themes": ["celtic-mythology", "animism", "ghost", "society", "emotion"],
        "motifs": ["sacred-object"],
        "summary": "Irish fairy tales and folklore collected by W.B. Yeats",
    },
    "classicmytholog00wittgoog.md": {
        "themes": ["greek-mythology", "godhood", "hero-journey", "war", "nature"],
        "motifs": ["sky-father"],
        "summary": "Handbook of Greek and Roman mythology for students",
    },
    "cu31924023266335.md": {
        "themes": ["chinese-mythology", "love-story", "magic", "society", "emotion"],
        "motifs": ["shape-shifting"],
        "summary": "Forty stories told by almond-eyed folk actors - Chinese folktales",
    },
    "ftsz_dravya-sangraha-by-nemichandra-siddhantideva-sanskrit-gujarati-jainism-phil.md": {
        "themes": ["jain-cosmology", "wisdom", "society", "nature"],
        "motifs": ["knowledge-god"],
        "summary": "Jain philosophical text on substances (Dravya) in Sanskrit",
    },
    "india.history.resource.85807.md": {
        "themes": ["islamic-tradition", "godhood", "prophecy", "divine-punishment", "last-judgment"],
        "motifs": ["thunder-deity"],
        "summary": "The Qur'an Part II - SBE Vol. IX, E.H. Palmer translation",
    },
    "isbn_9781544831589.md": {
        "themes": ["japanese-mythology", "magic", "emotion", "society", "animism"],
        "motifs": ["shape-shifting"],
        "summary": "Japanese fairy tales compiled by Yei Theodora Ozaki",
    },
    "jstor-659885.md": {
        "themes": ["mesoamerican-mythology", "ritual", "omen", "society", "sacred-object"],
        "motifs": ["sacred-object"],
        "summary": "Study of the Codex Fejervary-Mayer - Mixtec picture manuscript",
    },
    "myths-myth-makers.md": {
        "themes": ["comparative-mythology", "solar-mythology", "nature", "godhood", "ritual"],
        "motifs": ["sun-deity"],
        "summary": "Old tales and superstitions interpreted by comparative mythology - John Fiske",
    },
    "norsemythinengli00herf.md": {
        "themes": ["norse-mythology", "godhood", "hero-journey", "nature", "war"],
        "motifs": ["thunder-deity", "sky-father"],
        "summary": "Norse myth as treated in English poetry - C.H. Herford study",
    },
    "sagakingolaftry00snorgoog.md": {
        "themes": ["norse-mythology", "kingship", "war", "hero-journey", "conflict"],
        "motifs": ["sacred-object"],
        "summary": "The Saga of King Olaf Tryggwason - Icelandic saga",
    },
    "satapatha-brahmana-part-i.md": {
        "themes": ["vedic-hymns", "ritual", "sacrifice", "myth-and-ritual", "nature"],
        "motifs": ["fire-deity"],
        "summary": "Satapatha Brahmana Part I - Vedic ritual text with commentary",
    },
    "yorubaspeakingp01elligoog.md": {
        "themes": ["african-mythology", "godhood", "ritual", "social-customs", "magic"],
        "motifs": ["thunder-deity", "sacred-object"],
        "summary": "The Yoruba-Speaking Peoples of the Slave Coast of West Africa - A.B. Ellis",
    },
}

def main():
    classified = 0
    for fname, cls in MANUAL_CLASSIFICATIONS.items():
        fpath = STORY_DIR / fname
        if not fpath.exists():
            print(f"SKIP: {fname} not found")
            continue

        text = fpath.read_text(encoding='utf-8', errors='ignore')

        # Replace themes
        themes_str = '\n'.join(f'  - {t}' for t in cls['themes'])
        text = re.sub(
            r'^themes:\s*\n\s*-\s*to-be-classified',
            f'themes:\n{themes_str}',
            text,
            flags=re.M
        )

        # Replace motifs
        motifs_str = '\n'.join(f'  - {m}' for m in cls['motifs'])
        text = re.sub(
            r'^motifs:\s*\n\s*-\s*to-be-classified',
            f'motifs:\n{motifs_str}',
            text,
            flags=re.M
        )

        # Add/update summary
        if 'summary:' not in text:
            # Add summary after title
            text = re.sub(
                r'^(title:\s*".*?")$',
                rf'\1\nsummary: "{cls["summary"]}"',
                text,
                flags=re.M
            )
        else:
            text = re.sub(
                r'^summary:\s*".*?"$',
                f'summary: "{cls["summary"]}"',
                text,
                flags=re.M
            )

        fpath.write_text(text, encoding='utf-8')
        classified += 1
        print(f"Classified: {fname}")

    print(f"\nTotal manually classified: {classified}")

if __name__ == "__main__":
    main()
