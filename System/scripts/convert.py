#!/usr/bin/env python3
"""
Sutrai text conversion utilities.
Converts between formats (PDF->TXT, EPUB->TXT, HTML->TXT, DOCX->TXT).
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Ensure pandoc is on PATH
PANDOC_DIR = r"C:\Users\Mitchell\AppData\Local\Pandoc"
if os.path.isdir(PANDOC_DIR) and PANDOC_DIR not in os.environ["PATH"]:
    os.environ["PATH"] = PANDOC_DIR + os.pathsep + os.environ["PATH"]

def pdf_to_txt(src: str, dst: str) -> str:
    """Convert PDF to text using pdftotext (preserves layout)."""
    subprocess.run(["pdftotext", "-layout", src, dst], check=True)
    return dst

def epub_to_txt(src: str, dst: str) -> str:
    """Convert EPUB to text using pandoc."""
    subprocess.run([
        "pandoc", src, "-t", "plain", "--wrap=none",
        "-o", dst
    ], check=True)
    return dst

def docx_to_txt(src: str, dst: str) -> str:
    """Convert DOCX to text using pandoc."""
    subprocess.run([
        "pandoc", src, "-t", "plain", "--wrap=none",
        "-o", dst
    ], check=True)
    return dst

def html_to_txt(src: str, dst: str) -> str:
    """Convert HTML to text using pandoc."""
    subprocess.run([
        "pandoc", src, "-t", "plain", "--wrap=none",
        "-o", dst
    ], check=True)
    return dst

def any_to_txt(src: str, dst: str = None) -> str:
    """Auto-detect source format and convert to plain text."""
    src_path = Path(src)
    if dst is None:
        dst = str(src_path.with_suffix('.txt'))
    
    ext = src_path.suffix.lower()
    converters = {
        '.pdf': pdf_to_txt,
        '.epub': epub_to_txt,
        '.docx': docx_to_txt,
        '.doc': docx_to_txt,
        '.html': html_to_txt,
        '.htm': html_to_txt,
    }
    
    converter = converters.get(ext)
    if converter:
        return converter(src, dst)
    else:
        raise ValueError(f"No converter for extension: {ext}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert.py <source_file> [destination_file]")
        sys.exit(1)
    
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else None
    result = any_to_txt(src, dst)
    print(f"Converted: {result}")
