# Implementation Plan: Embedding Pipeline Setup

**Branch**: `2-embedding-pipeline` | **Date**: 2025-12-15 | **Spec**: [link to spec](../spec.md)
**Input**: Feature specification from `/specs/2-embedding-pipeline/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create backend folder and initialize project with UV package to implement an embedding pipeline that extracts text from deployed Docusaurus URLs (https://physical-ai-book-with-rag.vercel.app/), generates embeddings using Cohere, and stores them in Qdrant with metadata. The implementation will be contained in a single main.py file with functions for URL crawling, text extraction, chunking, embedding, and vector storage.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: uv (package manager), cohere, qdrant-client, requests, beautifulsoup4
**Storage**: Qdrant vector database
**Testing**: pytest
**Target Platform**: Linux server
**Project Type**: Backend service
**Performance Goals**: Process 1000 pages per hour without exceeding API rate limits
**Constraints**: <200ms p95 for embedding generation, handle API rate limits gracefully
**Scale/Scope**: Support 10,000+ document chunks for RAG-based retrieval

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Specification-First**: ✅ Aligned - Implementation follows the detailed specification created in the previous step
- **Modular Design**: ⚠️ Partial - Single file implementation may violate modularity, but justified by requirement for single main.py file
- **AI-Assisted Development**: ✅ Aligned - Using AI to generate implementation based on specification

**Post-Design Constitution Check**:
- **Specification-First**: ✅ Aligned - All design decisions documented in research.md and data-model.md
- **Modular Design**: ⚠️ Partial - Justified by single-file requirement per user specification
- **AI-Assisted Development**: ✅ Aligned - All implementation artifacts generated with AI assistance

## Project Structure

### Documentation (this feature)

```text
specs/2-embedding-pipeline/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── pyproject.toml       # Project configuration with dependencies
├── main.py             # Single file implementation with all required functions
└── requirements.txt    # Dependencies managed by uv

tests/
└── test_main.py        # Tests for main.py functions
```

**Structure Decision**: Backend service structure chosen to align with requirement for creating a backend folder with a single main.py file containing all specified functions (get_all_urls, extract_text_from_url, chunk_text, embed, create_collection named rag_embedding, save_chunk_to_qdrant).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Modular Design - Single file | Requirement explicitly states "Only in the one file name main.py" | Would violate user's specific requirement for single-file implementation |