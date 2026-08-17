# Project Template

Copy this directory to create a new adaptation project.

## Structure

```
{project-id}/
├── project.yaml               # Project metadata & status
├── interpretation.md          # Developed interpretation
├── visual-bible.md            # Visual direction & references
├── storyboard.md              # Shot-by-shot storyboard
├── shot-manifest.yaml         # Generated shot specifications
├── audio-plan.md              # Voice, music, SFX plan
├── research/                  # Research outputs for this project
├── edit/                      # Edit assembly files (gitignored)
└── exports/                   # Final rendered outputs (gitignored)
```

## project.yaml

```yaml
# Project metadata
id: {project-id}
title: {Human-readable title}
source_story: {story-id}
status: draft
created_date: {YYYY-MM-DD}
last_updated: {YYYY-MM-DD}

# Pipeline
pipeline_version: v1.0.0

# Creative direction
adaptation_approach: >
  {Brief description of the creative approach}
target_duration: {e.g., 5m, 10m, 30s}
target_platforms:
  - youtube
  - instagram
  - tiktok

# Fidelity
fidelity_notes: >
  {Notes on how this adaptation maintains fidelity to the source}
```

## Project Lifecycle

1. **Draft** — Project created, source story identified
2. **Research** — Cultural context, related motifs, interpretations gathered
3. **Development** — Visual bible, storyboard, shot manifest created
4. **Pre-production** — Audio plan, concept art, voice generation
5. **Production** — Animation, video, and audio generation
6. **Post-production** — Editing, color grading, sound mixing
7. **Complete** — Final output delivered
