# Sutrai

> *Sutra + AI* | Faithful, beautiful audiovisual representations of enduring sacred, religious, philosophical, and folk stories.

**Sutrai** is an experimental archive and creative system for producing faithful, beautiful audiovisual representations of enduring sacred, religious, philosophical, and folk stories.

---

## Core Mission

> Take an old story worth remembering, understand it carefully, and give it new audiovisual form.

---

## Quick Start

1. **Explore the archive:** Start with `Archive/texts/` to find source texts, or `Stories/by-source/` to browse extracted narrative units.
2. **Start a project:** Copy `Projects/_template/` to `Projects/{project-id}/` and fill in `project.yaml`.
3. **Run pipelines:** Use `Agents/pipelines/text-acquisition.yaml` to ingest new sources, or `Agents/pipelines/story-extraction.yaml` to segment texts into stories.

---

## Repository Structure

| Directory | Purpose |
|-----------|---------|
| `Archive/` | Local-first source library (texts, translations, commentaries, motifs, references) |
| `Stories/` | Extracted narrative units (by source, theme, and motif) |
| `Projects/` | Active adaptation projects (each with pipeline stages) |
| `Creative/` | Generated creative assets (concept art, storyboards, animations, audio, edits) |
| `Agents/` | Agentic workflow definitions (skills, pipelines, configs) |
| `Research/` | Research outputs (context, comparisons, interpretations, bibliographies) |
| `System/` | Repository management (schemas, indexes, docs, scripts) |
| `Docs/` | Top-level documentation |

---

## Agentic Workflows

Four agent roles power the Sutrai pipeline:

- **Curator** — Ingests, catalogs, and maintains the source archive
- **Researcher** — Develops interpretations, finds connections, gathers cultural context
- **Visual Artist** — Creates visual bibles, storyboards, shot manifests, concept art
- **Editor** — Assembles edits, coordinates audio/final output, ensures quality

Pipelines orchestrate multi-step workflows across agents:

1. **Text Acquisition** → Ingest public domain texts from trusted sources
2. **Story Extraction** → Segment texts into addressable narrative units
3. **Research** → Gather cultural context and develop interpretations
4. **Adaptation Development** → Create visual direction, storyboards, shot manifests
5. **Media Production** → Generate concept art, animations, audio
6. **Post-Production** → Assemble edits, color grade, sound mix

---

## Data Schemas

All data entities follow defined schemas in `System/schemas/`:

- `story.schema.yaml` — Extracted narrative unit
- `project.schema.yaml` — Adaptation project
- `source.schema.yaml` — Source text in archive
- `motif.schema.yaml` — Motif index entry

---

## Git Sync

This repository uses GitHub for version control. Large media assets (images, video, audio, PDFs) are **not** synced to GitHub — they are managed through alternative backup strategies (Google Drive, rclone, local backup).

See `.gitignore` for details on what is and isn't tracked.

---

## Contributing

See `System/docs/CONTRIBUTING.md` for contribution guidelines.

---

## License

This project and its documentation are licensed under [LICENSE]. Individual source texts retain their original licenses. Generated assets are marked with appropriate provenance.
