#!/usr/bin/env python3
"""
Sutrai batch text ingestion script.
Downloads texts from Project Gutenberg and other sources,
converts them to clean TXT format, and generates metadata.
"""

import os
import sys
import json
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime

# Base directory
BASE_DIR = Path(r"G:\My Drive\AI\Sutrai\Archive\texts\sacred")

# Project Gutenberg mirror
PG_MIRROR = "https://www.gutenberg.org/cache/epub"

# Texts to download: (gutenberg_id, filename, title, author, year, category, tradition, notes)
TEXTS_TO_DOWNLOAD = [
    # Native American - Project Gutenberg
    (22072, "folk-lore-legends-na-indian", "Folk-Lore and Legends: North American Indian", "Anonymous", "1891", "folklore", "Native American", "Collection of Native American folklore tales"),
    (42390, "myths-na-indians-spence", "The Myths of the North American Indians", "Lewis Spence", "1914", "mythology", "Native American", "Scholarly account of Native American mythology"),
    (10376, "american-indian-stories", "American Indian Stories", "Zitkala-Sa", "1921", "folklore", "Native American", "Autobiographical collection by Yankton Dakota Sioux author"),
    (21620, "myth-hiawatha", "The Myth of Hiawatha", "Schoolcraft", "1856", "mythology", "Native American", "Collection of Native American myths and legends"),
    (11029, "american-hero-myths", "American Hero-Myths", "Daniel G. Brinton", "1882", "mythology", "Native American", "Pioneering scholarly study of Native American hero myths"),
    (45279, "american-indian-fairy-tales", "American Indian Fairy Tales", "W. T. Larned", "1905", "folklore", "Native American", "Collection of Native American fairy tales with illustrations"),
    (66596, "punishment-stingy", "The Punishment of the Stingy", "George Bird Grinnell", "1901", "folklore", "Native American", "Traditional Native American tales by ethnologist Grinnell"),
    (25794, "indian-legends-minnesota", "Indian Legends of Minnesota", "Mrs. Cordenio A. Severance", "1894", "folklore", "Native American", "Collection of Native American legends from Minnesota region"),
    (15888, "unwritten-literature-hopi", "The Unwritten Literature of the Hopi", "H. R. Voth", "1905", "sacred", "Native American", "Detailed study of Hopi oral literature"),
]

def download_pg_text(gutenberg_id: int, output_path: Path) -> bool:
    """Download a text from Project Gutenberg."""
    url = f"{PG_MIRROR}/{gutenberg_id}/pg{gutenberg_id}.txt"
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read()
            output_path.write_bytes(content)
            return True
    except Exception as e:
        print(f"  Error downloading {gutenberg_id}: {e}")
        return False

def create_metadata(gutenberg_id: int, filename: str, title: str, author: str,
                    year: int, category: str, tradition: str, notes: str,
                    output_dir: Path, word_count: int = 0):
    """Create a source.yaml metadata file."""
    metadata = {
        "id": f"pg-{filename}",
        "title": title,
        "category": category,
        "tradition": tradition,
        "original_language": "English",
        "author": author,
        "date_composed": year,
        "date_acquired": datetime.now().strftime("%Y-%m-%d"),
        "source_url": f"https://www.gutenberg.org/ebooks/{gutenberg_id}",
        "license": "Public Domain",
        "copyright_status": "public_domain",
        "file_formats": ["txt"],
        "file_paths": {
            "txt": f"Archive/texts/sacred/native-american/pg/{filename}.txt"
        },
        "quality_rating": "high",
        "notes": notes,
        "word_count": word_count
    }
    
    yaml_path = output_dir / f"source-pg-{filename}.yaml"
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write(f"id: {metadata['id']}\n")
        f.write(f"title: {metadata['title']}\n")
        f.write(f"category: {metadata['category']}\n")
        f.write(f"tradition: {metadata['tradition']}\n")
        f.write(f"original_language: {metadata['original_language']}\n")
        f.write(f"author: {metadata['author']}\n")
        f.write(f"date_composed: '{metadata['date_composed']}'\n")
        f.write(f"date_acquired: '{metadata['date_acquired']}'\n")
        f.write(f"source_url: {metadata['source_url']}\n")
        f.write(f"license: {metadata['license']}\n")
        f.write(f"copyright_status: {metadata['copyright_status']}\n")
        f.write(f"file_formats:\n  - txt\n")
        f.write(f"file_paths:\n  txt: {metadata['file_paths']['txt']}\n")
        f.write(f"quality_rating: {metadata['quality_rating']}\n")
        f.write(f"notes: |\n  {metadata['notes']}\n")
        f.write(f"word_count: {metadata['word_count']}\n")
    
    return yaml_path

def count_words(file_path: Path) -> int:
    """Count words in a text file."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        return len(content.split())
    except:
        return 0

def main():
    output_dir = BASE_DIR / "native-american" / "pg"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting batch download of {len(TEXTS_TO_DOWNLOAD)} texts...")
    print(f"Output directory: {output_dir}")
    
    success_count = 0
    fail_count = 0
    
    for gutenberg_id, filename, title, author, year, category, tradition, notes in TEXTS_TO_DOWNLOAD:
        print(f"\n[{gutenberg_id}] {title}")
        
        txt_path = output_dir / f"{filename}.txt"
        
        # Download if not already present
        if not txt_path.exists():
            print(f"  Downloading from Project Gutenberg...")
            if download_pg_text(gutenberg_id, txt_path):
                print(f"  Downloaded: {txt_path.stat().st_size} bytes")
            else:
                print(f"  FAILED to download")
                fail_count += 1
                continue
        else:
            print(f"  Already exists: {txt_path.stat().st_size} bytes")
        
        # Count words
        word_count = count_words(txt_path)
        
        # Create metadata
        yaml_path = create_metadata(gutenberg_id, filename, title, author, year,
                                    category, tradition, notes, output_dir, word_count)
        print(f"  Metadata: {yaml_path.name}")
        print(f"  Word count: {word_count}")
        
        success_count += 1
    
    print(f"\n{'='*50}")
    print(f"Batch complete: {success_count} succeeded, {fail_count} failed")
    print(f"Total texts: {len(TEXTS_TO_DOWNLOAD)}")

if __name__ == "__main__":
    main()
