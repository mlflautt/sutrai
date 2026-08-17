#!/usr/bin/env python3
"""
OCR boilerplate cleaner for Internet Archive djvu.txt files.

Strips common IA/Google/MLibrary OCR artifacts:
- Google "This is a digital copy of a book..." preamble
- "Digitized by the Internet Archive in YYYY..." lines
- Microsoft/Kerala/LBSNAA/EX LIBRIS library stamps
- "Early Journal Content on JSTOR..." blocks
- Excessive whitespace, form-feed, control chars
- djvu page-break markers (_, .., ||)

Writes cleaned files back; moves originals to raw/ for safety.
"""

import re
import shutil
from pathlib import Path

BASE_DIR = Path(r"G:\My Drive\AI\Sutrai\Archive\texts\sacred\mythology-arc")
RAW_DIR = BASE_DIR / "raw"

BOILER_STARTS = [
    "Google This is a digital copy",
    "This is a digital copy of a book",
    "Digitized by the Internet Archive",
    "IVIicrosoft Corporation",
    "Microsoft Corporation",
    "Early Journal Content on JSTOR",
    "Known as the Early Journal Content",
    "This article is one of nearly",
    "We encourage people to read",
    "Read more about Early Journal",
    "JSTOR is a digital library",
    "http://www.archive.org/details/",
    "http://archive.org/details/",
    "Accession No.",
    "Book No.",
    "EX LIBRIS",
    "LBSNAA",
    "Kerala",
    "National Academy of Administration",
    "Mussoorie",
]

def clean_text(text):
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Remove control chars except newline/tab
    text = ''.join(ch for ch in text if ch in '\n\t' or ord(ch) >= 32)
    lines = text.split('\n')
    out = []
    skip_block = False
    for line in lines:
        stripped = line.strip()
        low = stripped.lower()
        # Skip boilerplate lines
        if any(stripped.startswith(b) or low.startswith(b.lower()) for b in BOILER_STARTS):
            skip_block = True
            continue
        # End of boilerplate: blank line resets
        if skip_block and stripped == '':
            skip_block = False
            continue
        if skip_block:
            continue
        # Remove standalone djvu artifact lines
        if re.fullmatch(r'[_.\-|]{3,}', stripped):
            continue
        # Collapse 3+ spaces (OCR spacing artifacts)
        line = re.sub(r' {3,}', ' ', line)
        # Collapse 3+ internal newlines (blank line runs)
        out.append(line)
    # Join, then collapse 3+ blank lines
    cleaned = '\n'.join(out)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    # Also collapse 2-space-indented junk like "t-'^  J' " OCR garbage lines: keep, but trim
    return cleaned.strip() + '\n'

def main():
    RAW_DIR.mkdir(exist_ok=True)
    files = sorted(BASE_DIR.glob("*.txt"))
    moved = 0
    cleaned = 0
    for f in files:
        # Move original to raw/
        dest_raw = RAW_DIR / f.name
        if not dest_raw.exists():
            shutil.move(str(f), str(dest_raw))
            moved += 1
        # Clean and write back to base
        raw_text = dest_raw.read_text(errors='ignore')
        cleaned_text = clean_text(raw_text)
        f.write_text(cleaned_text, encoding='utf-8')
        cleaned += 1
    print(f"Moved {moved} originals to raw/; cleaned {cleaned} files in place.")

if __name__ == "__main__":
    main()
