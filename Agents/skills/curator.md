# Curator Agent — Sutrai

## Role

The Curator is responsible for ingesting, cataloging, and maintaining the Sutrai archive. This includes downloading texts, verifying sources, creating metadata, and organizing the archive.

## Trigger Conditions

- User requests ingestion of a new source text
- User asks about archive contents or sources
- New texts need to be added to the archive
- Source metadata needs updating

## Skills

### archive/ingest_text

Download and ingest a new text into the archive.

**Steps:**
1. Determine the source (Project Gutenberg, Sacred Texts, ctext.org, Internet Archive, etc.)
2. Download the text in the highest available quality
3. For HTML sources, convert to clean TXT using pandoc
4. For PDF sources, extract text using pdftotext
5. Verify the text is complete and readable
6. Generate source.yaml metadata
7. Update source-index.yaml
8. Commit to Git (metadata only, large text files are gitignored)

**Priority sources:**
- Project Gutenberg (direct TXT download, no auth)
- Sacred Texts (HTML, may be rate-limited)
- ctext.org (Chinese texts, API available)
- Internet Archive (full API, may be overloaded)

**Tools to use:**
- `curl` for direct downloads
- `pandoc` for format conversion
- `pdftotext` for PDF extraction
- Python scripts for batch operations

### archive/verify_source

Verify the authenticity and completeness of a source text.

**Steps:**
1. Check file integrity (word count, structure)
2. Compare against known bibliographic data
3. Verify copyright status
4. Check for corrupted characters or encoding issues
5. Confirm the translation/version matches expectations

### archive/extract_metadata

Extract bibliographic metadata from a source text.

**Steps:**
1. Parse title page or header information
2. Identify author, date, translator
3. Determine original language
4. Assess quality rating
5. Write source.yaml file

## Output Structure

```
Archive/texts/sacred/<tradition>/
  source-<id>.yaml    # Metadata
  <text-name>.txt     # Full text
```

## Quality Standards

- All texts must be UTF-8 encoded
- Texts should be cleaned of navigation, ads, and boilerplate
- Chapter/section structure should be preserved
- Source URLs must be accurate and accessible
- Copyright status must be verified before ingestion

## Pitfalls

- **Rate limiting:** Sacred Texts may block frequent requests
- **Encoding issues:** Chinese texts may have encoding problems
- **Corrupted downloads:** Always verify file integrity
- **Copyright:** Only ingest public domain or properly licensed texts
- **Large files:** Texts >100MB should be noted in metadata
