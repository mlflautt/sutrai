# Sutrai — System Architecture

This document describes the organizational structure and architectural principles of the Sutrai archive and creative system.

---

## Repository Structure

```
Sutrai/
├── 📚 Archive/                     # LOCAL-FIRST SOURCE LIBRARY
├── 📖 Stories/                     # EXTRACTED NARRATIVE UNITS
├── 🎬 Projects/                    # ACTIVE ADAPTATION PROJECTS
├── 🎨 Creative/                    # GENERATED CREATIVE ASSETS
├── 🤖 Agents/                      # AGENTIC WORKFLOW DEFINITIONS
├── 🔬 Research/                    # RESEARCH OUTPUTS
├── ⚙️ System/                      # REPOSITORY MANAGEMENT
└── 📄 Docs/                        # Top-level documentation
```

### 📚 Archive/

The local-first source library contains primary texts, translations, commentaries, folklore collections, scholarly works, and related material.

- **texts/** — Primary source texts organized by category (sacred, mythology, folklore, philosophical, poetry)
- **translations/** — Multiple translations for comparison, organized by source or language
- **commentaries/** — Scholarly commentaries and exegesis
- **motifs/** — Cross-cultural motif index, aligned with Thompson Motif-Index where applicable
- **references/** — Bibliographic and reference works (encyclopedias, dictionaries, atlases)

### 📖 Stories/

Extracted narrative units that are addressable as reusable research objects and potential film nuclei.

- **by-source/** — Stories organized by parent text (e.g., `by-source/bible/genesis/the-flood.md`)
- **by-theme/** — Cross-cultural thematic index (e.g., `by-theme/flood.md`)
- **by-motif/** — Motif-based relationships (e.g., `by-motif/the-flood-hero.md`)

Each story file uses YAML frontmatter for structured metadata and markdown for the narrative text.

### 🎬 Projects/

Active adaptation projects, each containing:

- `project.yaml` — Project metadata and status
- `interpretation.md` — Developed interpretation
- `visual-bible.md` — Visual direction and references
- `storyboard.md` — Shot-by-shot storyboard
- `shot-manifest.yaml` — Generated shot specifications
- `audio-plan.md` — Voice, music, SFX plan
- `edit/` — Edit assembly files
- `exports/` — Final rendered outputs

A template is available in `Projects/_template/`.

### 🎨 Creative/

Generated creative assets organized by type:

- **concept-art/** — Concept art by project
- **storyboards/** — Storyboard panels
- **animations/** — Animated sequences
- **audio/** — Voice (ElevenLabs/TTS), music, SFX
- **edits/** — NLE project files

### 🤖 Agents/

Agentic workflow definitions, including:

- **skills/** — Reusable agent skills organized by function (archive, research, creative, production, quality)
- **pipelines/** — End-to-end pipeline definitions (text-acquisition, story-extraction, etc.)
- **configs/** — Agent configuration templates (curator, researcher, visual-artist, editor)

### 🔬 Research/

Research outputs generated during adaptation development:

- **context/** — Cultural/historical context documents
- **comparisons/** — Cross-cultural comparisons
- **interpretations/** — Developed interpretations
- **bibliographies/** — Project-specific bibliographies

### ⚙️ System/

Repository management infrastructure:

- **schemas/** — Data schemas (story, project, source, motif)
- **indexes/** — Master indexes and catalogs
- **docs/** — Repository documentation
- **scripts/** — Utility scripts (validate, index-builder, migrate)

---

## Data Schemas

All data entities in Sutrai follow defined schemas:

| Schema | File | Description |
|--------|------|-------------|
| Story | `System/schemas/story.schema.yaml` | Extracted narrative unit |
| Project | `System/schemas/project.schema.yaml` | Adaptation project |
| Source | `System/schemas/source.schema.yaml` | Source text in archive |
| Motif | `System/schemas/motif.schema.yaml` | Motif index entry |

---

## Agentic Workflows

### Pipeline: Text Acquisition

Downloads and catalogs public domain sacred texts from trusted sources (Sacred Texts, Project Gutenberg, Internet Archive, Wikisource).

**Agent roles:** curator

**Steps:**
1. Search for texts across configured sources
2. Verify public domain status
3. Download in multiple formats (PDF, TXP, EPUB)
4. Extract bibliographic metadata
5. Add to source index
6. Generate source summary

### Pipeline: Story Extraction

Segments source texts into addressable narrative units with full metadata.

**Agent roles:** curator + researcher

**Steps:**
1. Load source text from archive
2. Identify narrative units (chapters, episodes, parables)
3. Extract each unit with context windows
4. Auto-tag with themes, motifs, characters, symbols
5. Build cross-cultural relationships
6. Update story and motif indexes

### Pipeline: Research

Gathers cultural context, finds connections, and develops interpretations.

**Agent roles:** researcher

**Steps:**
1. Research cultural/historical context of the story
2. Find related motifs across traditions
3. Compare translations
4. Trace sources and scholarly interpretations
5. Write developed interpretation

### Pipeline: Adaptation Development

Creates visual direction, storyboards, and shot manifests.

**Agent roles:** visual-artist

**Steps:**
1. Develop adaptation approach grounded in interpretation
2. Create visual bible
3. Build storyboard
4. Generate shot manifest

### Pipeline: Media Production

Generates concept art, animations, audio, and assembles edits.

**Agent roles:** visual-artist + editor

**Steps:**
1. Generate concept art
2. Generate animations
3. Generate voice (ElevenLabs)
4. Generate music
5. Assemble edit

---

## Naming Conventions

- **IDs:** lowercase, hyphenated, no special characters (e.g., `bible-genesis-flood`)
- **File names:** match the ID with appropriate extension (e.g., `the-flood.md`)
- **Directories:** lowercase, hyphenated (e.g., `by-source/bible/genesis/`)
- **Dates:** ISO 8601 format (`YYYY-MM-DD`)
- **Versions:** semantic versioning (`v1.0.0`)

---

## Git Sync Protocol

This repository uses GitHub for version control, with selective syncing to avoid uploading large media assets.

**Synced to GitHub:**
- All `.md`, `.yaml`, `.yml`, `.json`, `.txt` files
- All code and scripts
- Documentation
- Schemas and indexes
- Project metadata

**NOT synced to GitHub (gitignored):**
- Large media files (`.mp4`, `.mp3`, `.png`, `.jpg`, `.webp`, `.bmp`)
- Archive text files (`.pdf`, `.epub`, `.docx`)
- Generated creative assets
- Edit project files (`.drp`, `.fcp`, `.prproj`)
- Database files (`.db`, `.sqlite`, `.sqlite3`)
- Cache and temporary files
- Environment files (`.env`)

Large media assets are managed through alternative backup strategies (Google Drive, rclone, local backup).

---

## Contributing

See `System/docs/CONTRIBUTING.md` for contribution guidelines.

---

## License

This project and its documentation are licensed under [LICENSE]. Individual source texts retain their original licenses. Generated assets are marked with appropriate provenance.
