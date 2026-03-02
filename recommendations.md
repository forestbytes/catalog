# Project Recommendations

This document outlines recommendations for improving the Catalog project based on comprehensive codebase reviews.


## Feature Suggestions

### Add Progress Indicators

Use Click's built-in progress bar for long-running downloads:

```python
with click.progressbar(datasets, label="Downloading") as bar:
    for dataset in bar:
        # download logic
```

### Organize Data Loaders

Consider grouping loaders into a subpackage:

```text
src/catalog/
├── loaders/
│   ├── __init__.py
│   ├── base.py          # Abstract base loader
│   ├── fsgeodata.py
│   ├── gdd.py
│   └── rda.py
├── cli.py
├── core.py
├── lib.py
└── schema.py
```

## 11. LLM Integration (Current Branch)

Since the current branch (`45-feature-add-llm-interaction-to-cli-chomadb-query`) focuses on LLM integration:

### Completed

1. **RAG pattern implemented** — `ollama_chat` CLI command queries ChromaDB, builds markdown context with `USFSDocument.to_markdown()`, and sends it to Ollama via `OllamaBot.chat()`
2. **Structured query results** — `ChromaVectorDB.query()` returns `list[tuple[USFSDocument, float]]` with distance scores
3. **Distance-aware LLM context** — Relevance distance is included in the context sent to Ollama; system prompt instructs the LLM to prioritize lower-distance results
4. **Batch document loading** — `batch_load_documents()` uses real document IDs and processes in configurable batch sizes
5. **Deduplication** — `load_document_metadata()` deduplicates by document ID; standalone `dedupe_catalog()` available in `lib.py`
6. **`to_markdown()` on `USFSDocument`** — Formatting lives on the model with optional `distance` parameter; used by both CLI commands and LLM context
7. **Abstract in metadata** — `batch_load_documents()` now stores `abstract` in ChromaDB metadata so `query()` can reconstruct it
8. **Distance-aware system prompt** — `bots.py` `MESSAGE_CONTENT` instructs the LLM to prioritize lower-distance results
9. **Dead code cleanup** — Removed commented-out query method and debug snippets from `core.py`
10. **Unused global removed** — Removed `soup = BeautifulSoup()` from `lib.py`
11. **Docstrings added** — Added docstrings to `load_document_metadata`, `load_documents`, `batch_load_documents` in `core.py`
12. **Indentation fixed** — `batch_load_documents` now uses consistent 4-space indentation
13. **OllamaBot uses configured URL** — Client now uses `self.OLLAMA_BASE_URL` instead of hardcoded URL
14. **Unbound variables fixed** — `usfs.py:FSGeodataLoader.parse_metadata` now initializes all variables with defaults

### Remaining

1. ~~**Fix GDD/RDA parsers**~~ — Fixed: Added `description` field to schema
2. **Add conversation history** — Store context for follow-up questions
3. **Implement streaming** — Use Ollama's streaming API for better UX
4. **Add source citations** — Include document references in LLM responses

---

## Summary of Priority Actions

| Priority     | Action                                                  | Status  |
| ------------ | ------------------------------------------------------- | ------- |
| ~~URGENT~~   | ~~Rotate exposed API keys in `.env`~~                   | N/A     |
| Medium       | Add progress indicators                                 | Pending |
| Medium       | Add conversation history for LLM                        | Pending |
| Medium       | Implement Ollama streaming                              | Pending |
| Low          | Refactor to subpackages                                 | Pending |
| Low          | Add pre-commit hooks                                    | Done    |
| Low          | Centralize configuration                                | Done    |

---

Generated on 2026-01-26, last updated 2026-03-02

**Summary:** 37 items completed, 7 items remaining
