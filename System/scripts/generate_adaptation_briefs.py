#!/usr/bin/env python3
"""
Generate adaptation briefs for promoted stories.

Creates structured creative briefs in Stories/adaptation-briefs/ that drive
the audiovisual pipeline (image generation, video, audio, etc.).

Each brief includes:
- Narrative arc summary (beginning/middle/end)
- Key characters with visual descriptors
- Key scenes/beats for visualization
- Cultural/aesthetic reference tags
- Suggested medium (animation, illustration, audio drama, etc.)
- Duration estimate
- Mood/tone palette
"""

import re
import yaml
from pathlib import Path

PROMOTED_DIR = Path(r"G:\My Drive\AI\Sutrai\Stories\by-source\ia\promoted")
BRIEF_DIR = Path(r"G:\My Drive\AI\Sutrai\Stories\adaptation-briefs")
INDEX_PATH = Path(r"G:\My Drive\AI\Sutrai\System\indexes\adaptation-briefs.yaml")

BRIEF_DIR.mkdir(parents=True, exist_ok=True)

# Culture → aesthetic mapping for visual generation prompts
CULTURE_AESTHETICS = {
    'Tsimshian': {
        'visual_style': 'Pacific Northwest Indigenous formline art, cedar textures, ovoid/U-shape motifs, black/red/blue palette',
        'medium': 'illustrated scroll, animated formline sequences',
        'color_palette': ['#1a1a1a', '#c41e3a', '#004b87', '#d4a574', '#8b7355'],
        'cultural_notes': 'Respect clan ownership of stories; Raven as transformer/trickster; potlatch context',
    },
    'Pawnee': {
        'visual_style': 'Great Plains ledger art style, hide painting aesthetic, geometric borders, earth pigments',
        'medium': 'animated ledger drawings, illustrated narrative',
        'color_palette': ['#8b4513', '#daa520', '#228b22', '#dc143c', '#fff8dc'],
        'cultural_notes': 'Star knowledge, Morning Star/Evening Star, sacred bundles, ceremonial context',
    },
    'Chinook': {
        'visual_style': 'Pacific Northwest Coast formline, cedar plank house interior, trade jargon cultural context',
        'medium': 'animated formline, illustrated narrative scroll',
        'color_palette': ['#1a1a1a', '#c41e3a', '#004b87', '#d4a574', '#8b7355'],
        'cultural_notes': 'Chinook Jargon trade language, Columbia River cultures, transformer myths',
    },
    'Chinese': {
        'visual_style': 'Classical Chinese ink wash (shui-mo), gongbi detail, silk scroll format, seal script calligraphy',
        'medium': 'animated scroll painting, ink animation',
        'color_palette': ['#0d0d0d', '#c8a951', '#8b0000', '#006400', '#f5f5dc'],
        'cultural_notes': 'Daoist/Buddhist/Confucian layers; Eight Immortals, Dragon Kings, Jade Emperor',
    },
    'Celtic': {
        'visual_style': 'Insular illumination (Book of Kells), knotwork borders, zoomorphic interlace, vellum texture',
        'medium': 'illuminated manuscript animation, Celtic metalwork aesthetic',
        'color_palette': ['#1a1a2e', '#0f3460', '#e94560', '#f0d653', '#a8c8d0'],
        'cultural_notes': 'Otherworld (Tir na Nog), geasa, shapeshifting, heroic cycles (Ulster, Fenian)',
    },
    'African': {
        'visual_style': 'West African textile patterns (adinkra, bogolan), wood sculpture aesthetic, vibrant contrasts',
        'medium': 'shadow puppetry, animated textile patterns, oral storytelling visualization',
        'color_palette': ['#1a1a1a', '#ff6b00', '#ffd700', '#004d00', '#8b0000'],
        'cultural_notes': 'Anansi trickster cycles, sky god Nyame, communal oral tradition, proverbs',
    },
    'Greek': {
        'visual_style': 'Classical red-figure/black-figure vase painting, marble sculpture, architectural orders',
        'medium': 'animated vase painting, marble relief sequences',
        'color_palette': ['#e8c58d', '#1a1a1a', '#c0392b', '#ffffff', '#4a4a4a'],
        'cultural_notes': 'Olympian pantheon, heroic myth cycles, fate (moira), hubris/nemesis',
    },
    'Armenian': {
        'visual_style': 'Armenian manuscript illumination, khachkar cross-stones, birds/angels, floral marginalia',
        'medium': 'illuminated manuscript animation, stone carving sequences',
        'color_palette': ['#1a1a2e', '#c0392b', '#f39c12', '#27ae60', '#8e44ad'],
        'cultural_notes': 'Pre-Christian pagan roots, Christian synthesis, Mount Ararat, Vahagn/Astghik',
    },
    'Norse/Icelandic': {
        'visual_style': 'Viking Age art styles (Borre, Jelling, Mammen, Ringerike, Urnes), runic inscription',
        'medium': 'runestone animation, wood carving, metalwork aesthetic',
        'color_palette': ['#1a1a1a', '#8b0000', '#daa520', '#4a4a4a', '#f5f5dc'],
        'cultural_notes': 'Yggdrasil, Ragnarok, nine worlds, runic magic, skaldic poetry',
    },
    'Slavic': {
        'visual_style': 'Lubok folk prints, Byzantine icon influence, floral borders, vibrant folk palette',
        'medium': 'lubok animation, folk art illustration',
        'color_palette': ['#e74c3c', '#f39c12', '#27ae60', '#2980b9', '#8e44ad'],
        'cultural_notes': 'Baba Yaga, domovoi, rusalki, Perun/Veles duality, calendar rituals',
    },
    'Indian': {
        'visual_style': 'Indian miniature painting (Mughal/Rajput/Pahari), temple sculpture, Sanskrit manuscript',
        'medium': 'miniature painting animation, temple relief sequences',
        'color_palette': ['#8b0000', '#ffd700', '#006400', '#4b0082', '#fff8dc'],
        'cultural_notes': 'Hindu epics (Mahabharata/Ramayana), Puranic cycles, Buddhist/Jain traditions',
    },
    'Vedic': {
        'visual_style': 'Vedic fire altar geometry, ancient Sanskrit manuscript, ritual implements',
        'medium': 'ritual animation, geometric sacred diagram sequences',
        'color_palette': ['#daa520', '#ff4500', '#fff8dc', '#8b4513', '#2f4f4f'],
        'cultural_notes': 'Rigvedic hymns, fire sacrifice (yajna), devas/asuras, rta cosmic order',
    },
    'Persian': {
        'visual_style': 'Persian miniature painting, illuminated manuscripts (Shahnameh), geometric arabesque',
        'medium': 'miniature painting animation, manuscript illumination sequences',
        'color_palette': ['#004d40', '#bf360c', '#ffd600', '#311b92', '#fafafa'],
        'cultural_notes': 'Zoroastrian duality, Shahnameh epic, Sufi poetry, pre-Islamic/Iranian synthesis',
    },
    'Japanese': {
        'visual_style': 'Ukiyo-e woodblock, yamato-e narrative scrolls, sumi-e ink, gold leaf accents',
        'medium': 'emaki scroll animation, woodblock print sequences',
        'color_palette': ['#1a1a1a', '#e63946', '#f1faee', '#a8dadc', '#457b9d'],
        'cultural_notes': 'Kami, yokai, Buddhist/Shinto syncretism, mono no aware',
    },
    'Comparative': {
        'visual_style': 'Academic diagram style, comparative mythology charts, archetypal pattern visualization',
        'medium': 'animated infographic, scholarly illustration',
        'color_palette': ['#2c3e50', '#34495e', '#7f8c8d', '#bdc3c7', '#ecf0f1'],
        'cultural_notes': 'Cross-cultural motif analysis, Frazer/Jung/Campbell comparative frameworks',
    },
}

DEFAULT_AESTHETIC = {
    'visual_style': 'Atmospheric illustration, dreamlike narrative art, textured paper, muted palette',
    'medium': 'illustrated storybook animation, atmospheric sequences',
    'color_palette': ['#2c2c2c', '#8b7355', '#a0522d', '#2f4f4f', '#f5f5dc'],
    'cultural_notes': 'Universal mythic motifs, archetypal patterns',
}


def extract_narrative_arc(text, max_chars=3000):
    """Extract beginning/middle/end from story text."""
    # Clean text
    clean = re.sub(r'\s+', ' ', text).strip()
    clean = clean[:max_chars]
    
    # Split into thirds
    third = len(clean) // 3
    beginning = clean[:third].strip()
    middle = clean[third:2*third].strip()
    end = clean[2*third:].strip()
    
    return {
        'beginning': beginning[:500] + '...' if len(beginning) > 500 else beginning,
        'middle': middle[:500] + '...' if len(middle) > 500 else middle,
        'end': end[:500] + '...' if len(end) > 500 else end,
    }


def extract_key_characters(text):
    """Extract potential character names from story text."""
    # Look for capitalized names (simplified)
    names = set(re.findall(r'\b[A-Z][a-z\']{2,}\b', text))
    # Filter common words
    common = {'The', 'And', 'But', 'For', 'With', 'His', 'Her', 'Was', 'She', 'He', 'They', 'Them', 'Their', 'There', 'Then', 'When', 'Who', 'What', 'Where', 'Which', 'While', 'After', 'Before', 'Once', 'Upon', 'Time', 'Long', 'Ago', 'Far', 'Away', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten'}
    names = [n for n in names if n not in common and len(n) > 2]
    # Return top 5 most frequent
    freq = {}
    for n in names:
        freq[n] = freq.get(n, 0) + 1
    return sorted(freq.keys(), key=lambda x: -freq[x])[:5]


def extract_key_scenes(text, max_scenes=5):
    """Extract visualizable scene beats from text."""
    sentences = re.split(r'[.!?]+', text)
    scenes = []
    visual_keywords = ['saw', 'looked', 'appeared', 'transformed', 'became', 'rose', 'fell', 'flew', 'swam', 'climbed', 'entered', 'found', 'met', 'fought', 'killed', 'born', 'died', 'married', 'gave', 'took', 'made', 'built', 'created', 'destroyed', 'changed', 'turned', 'grew', 'shrank', 'shone', 'glowed', 'burned', 'froze', 'storm', 'flood', 'fire', 'light', 'dark', 'sun', 'moon', 'star', 'tree', 'river', 'mountain', 'cave', 'house', 'village', 'city', 'palace', 'temple', 'altar', 'sacred', 'magic', 'spell', 'curse', 'blessing', 'dream', 'vision', 'spirit', 'god', 'goddess', 'demon', 'monster', 'dragon', 'serpent', 'bird', 'animal', 'wolf', 'bear', 'eagle', 'raven', 'fox', 'coyote', 'spider', 'snake']
    
    for s in sentences:
        s = s.strip()
        if len(s) < 30 or len(s) > 200:
            continue
        s_lower = s.lower()
        if any(kw in s_lower for kw in visual_keywords):
            scenes.append(s[:180])
            if len(scenes) >= max_scenes:
                break
    return scenes


def suggest_medium(length, culture):
    """Suggest production medium based on story length and culture."""
    if length < 2000:
        return 'short_animation_30s'
    elif length < 5000:
        return 'animation_1min'
    elif length < 15000:
        return 'animation_3min'
    else:
        return 'animation_series'


def estimate_duration(length):
    """Estimate production duration in seconds."""
    # Rough: 150 words per minute spoken, ~10s per visual beat
    words = len(length.split()) if isinstance(length, str) else length
    return max(30, min(300, words // 25))


def main():
    files = sorted(PROMOTED_DIR.glob("*.md"))
    print(f"Generating adaptation briefs for {len(files)} promoted stories...")
    
    brief_index = []
    
    for f in files:
        text = f.read_text(encoding='utf-8', errors='ignore')
        
        # Parse frontmatter
        fm_match = re.match(r'^---\n(.*?)\n---', text, re.S)
        if not fm_match:
            continue
        fm = yaml.safe_load(fm_match.group(1))
        
        story_id = fm.get('id', f.stem)
        title = fm.get('title', 'Untitled')
        source = fm.get('source', 'unknown')
        culture = fm.get('culture', 'Unknown')
        story_type = fm.get('story_type', 'myth')
        length = fm.get('length', 0)
        
        # Get story body (after frontmatter)
        body = text[fm_match.end():].strip()
        
        # Extract narrative arc
        arc = extract_narrative_arc(body)
        
        # Extract characters and scenes
        characters = extract_key_characters(body)
        scenes = extract_key_scenes(body)
        
        # Get cultural aesthetic
        aesthetic = CULTURE_AESTHETICS.get(culture, DEFAULT_AESTHETIC)
        
        # Determine medium and duration
        medium = suggest_medium(length, culture)
        duration = estimate_duration(body)
        
        # Build brief
        brief = {
            'story_id': story_id,
            'title': title,
            'source': source,
            'culture': culture,
            'story_type': story_type,
            'narrative_arc': arc,
            'key_characters': characters,
            'key_scenes': scenes,
            'visual_style': aesthetic['visual_style'],
            'suggested_medium': medium,
            'estimated_duration_seconds': duration,
            'color_palette': aesthetic['color_palette'],
            'cultural_notes': aesthetic['cultural_notes'],
            'production_status': 'brief_generated',
            'tags': [culture.lower(), story_type, medium],
        }
        
        # Write brief file
        brief_path = BRIEF_DIR / f"{story_id}.yaml"
        with open(brief_path, 'w', encoding='utf-8') as out:
            yaml.dump(brief, out, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        brief_index.append({
            'story_id': story_id,
            'title': title,
            'culture': culture,
            'story_type': story_type,
            'medium': medium,
            'duration': duration,
            'file': f"Stories/adaptation-briefs/{story_id}.yaml",
        })
    
    # Write index
    with open(INDEX_PATH, 'w', encoding='utf-8') as out:
        yaml.dump({'briefs': brief_index}, out, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"Generated {len(brief_index)} adaptation briefs in {BRIEF_DIR}")
    print(f"Index written to {INDEX_PATH}")


if __name__ == "__main__":
    main()