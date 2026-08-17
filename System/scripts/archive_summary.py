#!/usr/bin/env python3
"""
Create an archive summary report.

Documents what's in the Sutrai archive, what's classified,
and what the segmentation quality looks like.
"""

import re
from pathlib import Path

STORY_DIR = Path(r"G:\My Drive\AI\Sutrai\Stories\by-source\ia")

def main():
    files = sorted(STORY_DIR.glob("*.md"))

    summary = []
    total_units = 0

    for f in files:
        text = f.read_text(encoding='utf-8', errors='ignore')

        title_m = re.search(r'title: "([^"]*)"', text)
        title = title_m.group(1) if title_m else f.name

        units_match = re.search(r'extracted_units:\n(.*?)(?=\n(?:themes:|motifs:|adaptation_status:))', text, re.S)
        units_text = units_match.group(1) if units_match else ""
        num_units = len(re.findall(r'^- id: ', units_text, re.M))
        total_units += num_units

        themes = re.findall(r'^themes:\s*\n((?:  - [^\n]+\n)+)', text, re.M)
        motifs = re.findall(r'^motifs:\s*\n((?:  - [^\n]+\n)+)', text, re.M)

        summary.append({
            'file': f.name,
            'title': title,
            'units': num_units,
            'themes': len(themes),
            'motifs': len(motifs),
        })

    print(f"Archive Summary: {len(files)} source files, {total_units} total units")
    print()
    print("Files with most units:")
    for s in sorted(summary, key=lambda x: -x['units'])[:10]:
        print(f"  {s['units']:5} units | {s['title']}")

    print()
    print("Files with fewest units:")
    for s in sorted(summary, key=lambda x: x['units'])[:10]:
        print(f"  {s['units']:5} units | {s['title']}")

if __name__ == "__main__":
    main()
