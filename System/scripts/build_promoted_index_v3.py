#!/usr/bin/env python3
"""
Build promoted stories index from the v3 promoted directory.
"""

import yaml
from pathlib import Path

PROMOTED_DIR = Path(r"G:\My Drive\AI\Sutrai\Stories\by-source\ia\promoted_v3")
INDEX_PATH = Path(r"G:\My Drive\AI\Sutrai\System\indexes\promoted-stories-v3.yaml")

def main():
    stories = []
    
    for md_file in sorted(PROMOTED_DIR.glob("*.md")):
        content = md_file.read_text(encoding='utf-8', errors='ignore')
        
        # Parse YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                if frontmatter:
                    stories.append(frontmatter)
    
    print(f"Indexed {len(stories)} promoted stories")
    
    # Sort by source, then by story ID
    stories.sort(key=lambda s: (s.get('source', ''), s.get('id', '')))
    
    # Group by source for summary
    by_source = {}
    by_culture = {}
    by_type = {}
    
    for s in stories:
        src = s.get('source', 'unknown')
        cult = s.get('culture', 'Unknown')
        stype = s.get('story_type', 'legend')
        
        by_source[src] = by_source.get(src, 0) + 1
        by_culture[cult] = by_culture.get(cult, 0) + 1
        by_type[stype] = by_type.get(stype, 0) + 1
    
    print(f"\nBy source:")
    for src, count in sorted(by_source.items(), key=lambda x: -x[1]):
        print(f"  {src}: {count}")
    
    print(f"\nBy culture:")
    for cult, count in sorted(by_culture.items(), key=lambda x: -x[1]):
        print(f"  {cult}: {count}")
    
    print(f"\nBy story type:")
    for stype, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {stype}: {count}")
    
    # Write index
    index = {
        'version': '3',
        'total_stories': len(stories),
        'generated_from': 'narrative_segment_v3.py + promote_narratives_v3.py',
        'by_source': by_source,
        'by_culture': by_culture,
        'by_story_type': by_type,
        'stories': stories,
    }
    
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(index, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"\nIndex written to: {INDEX_PATH}")


if __name__ == "__main__":
    main()