# Contributing to Sutrai

Welcome! This document outlines how to contribute to the Sutrai archive and creative system.

## Table of Contents

- [Getting Started](#getting-started)
- [Archive Contributions](#archive-contributions)
- [Story Extraction](#story-extraction)
- [Project Development](#project-development)
- [Code Standards](#code-standards)
- [Git Workflow](#git-workflow)

---

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/mlflautt/sutrai.git`
3. Install dependencies: `pip install -r requirements.txt` (when available)
4. Read the [README.md](README.md) and [ARCHITECTURE.md](System/docs/ARCHITECTURE.md)

---

## Archive Contributions

### Adding a New Source Text

1. **Find a text** from a free, public domain source
2. **Download the text** using the appropriate method:
   - Project Gutenberg: Direct TXT download
   - Sacred Texts: HTML page (may be rate-limited)
   - ctext.org: Chinese Text Project API
   - Internet Archive: Full API
3. **Convert to clean TXT** using pandoc or pdftotext
4. **Verify integrity** - check for completeness and encoding
5. **Create metadata** - write a `source.yaml` file
6. **Update the index** - add to `System/indexes/source-index.yaml`
7. **Commit** (metadata only, large text files are gitignored)

### Source Metadata Format

```yaml
id: unique-source-id
title: Full Title of the Text
category: sacred|mythology|folklore|philosophical|poetry
tradition: Religious/Cultural Tradition
original_language: Original Language
author: Author Name
date_composed: 'YYYY'
date_acquired: 'YYYY-MM-DD'
source_url: https://example.com/source
license: Public Domain
copyright_status: public_domain
file_formats:
  - txt
file_paths:
  txt: Archive/texts/sacred/tradition/filename.txt
quality_rating: high|medium|low
notes: |
  Brief description of the text, its significance,
  and any notable features.
word_count: 50000
```

### Quality Standards

- **High quality:** Complete text, clean encoding, verified against original
- **Medium quality:** Minor gaps or encoding issues, still usable
- **Low quality:** Significant issues, needs improvement

### Source Priority

Priority sources for ingestion:

1. **Project Gutenberg** - Direct TXT, no auth, 70,000+ texts
2. **Sacred Texts** - 1,700+ religious/mythology texts (rate-limited)
3. **ctext.org** - Classical Chinese texts with API
4. **Internet Archive** - Millions of texts (may be overloaded)
5. **Wikisource** - Multi-language religious texts

---

## Story Extraction

### Extracting a Story from a Source

1. **Read the source text** to identify narrative units
2. **Create the story file** following the story schema
3. **Write YAML frontmatter** with proper metadata
4. **Copy the narrative text** (clean of headers/formatting)
5. **Add adaptation notes** at the end
6. **Update indexes:**
   - `System/indexes/story-index.yaml`
   - `Stories/by-theme/<theme>.md`
   - `Stories/by-motif/<motif>.md`

### Story File Format

```markdown
---
id: unique-story-id
title: Story Title
source:
  name: Source Name
  tradition: Tradition
  original_language: Language
  source_text: path/to/source.txt
  translation: Translation Info
  reference: Chapter/Section reference
extracted_units:
  - id: unit-1
    text: "Opening line..."
    reference: "Chapter 1"
themes:
  - theme-1
  - theme-2
motifs:
  - motif-1
  - motif-2
related_stories:
  - other-story-id
cultural_context:
  - context-1
adaptation_status: not_started
adaptation_notes: >
  Notes about adaptation potential.
---

# Story Title

[Full story text, cleaned and formatted]

---

*Adaptation notes: [Notes]*
```

---

## Project Development

### Creating a New Adaptation Project

1. Copy `Projects/_template/` to `Projects/<project-id>/`
2. Fill in `project.yaml` with project metadata
3. Write `interpretation.md` with your adaptation approach
4. Create visual assets in the `edit/` directory
5. Document progress in `project.yaml`

### Project Lifecycle

1. **draft** - Initial concept and research
2. **research** - Gathering context and references
3. **development** - Creating visual bible and storyboard
4. **production** - Generating assets and assembling
5. **review** - Quality checking and revision
6. **complete** - Finished and exported

---

## Code Standards

### Python Scripts

- Follow PEP 8
- Use type hints where possible
- Document functions with docstrings
- Keep functions focused and small

### YAML Files

- Use 2-space indentation
- Quote strings containing colons
- Use literal block scalars (`|`) for multi-line text
- Keep IDs lowercase with hyphens

### File Naming

- Use lowercase with hyphens
- Keep names descriptive but short
- Use `.yaml` for metadata (not `.yml`)
- Use `.txt` for plain text (not `.text`)

---

## Git Workflow

### Branching

- `main` - Stable, working archive
- `develop` - Development branch (optional)
- Feature branches: `feature/description`

### Commits

- Use descriptive commit messages
- Reference issues when applicable
- Keep commits focused and atomic

### What to Commit

**Commit:**
- `.md`, `.yaml`, `.json` files
- Scripts and code
- Documentation
- Directory structure (with `.gitkeep`)

**Don't Commit:**
- Large text files (>1MB)
- Media files (images, audio, video)
- Edit project files
- Environment files
- Cache/temp files

### Pull Requests

1. Describe what was added and why
2. Reference any related issues
3. Ensure all metadata is complete
4. Verify no large files are included

---

## Questions?

Open an issue or reach out to the maintainers.

---

*Last updated: 2026-08-17*
