# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-04-26

### Enhancements
- Added direct-message (`message` event with `channel_type == "im"`) support in `app.py` so users can query the bot in 1:1 chat, not only via `app_mention`.
- Improved DM response behavior in `app.py` with thread-aware replies, greeting/small-talk short-circuit handling, and safer session memory keys for threaded vs top-level DM conversations.
- Expanded `slack.target_channels` in `config.yaml` with an additional channel ID to ingest more workspace knowledge.

## [1.0.0] - 2026-04-22

### Added
- Core modular architecture with strict contracts in `interfaces/`, orchestration in `modules/`, and implementations in `providers/`.
- Shared `Document` entity in `core/entities.py` used across ingestion, retrieval, and generation pipelines.
- Provider Registry pattern in `core/registry.py` with decorator-based registration for loaders, embedders, vector stores, and LLMs.
- Provider bootstrap module `providers/__init__.py` to trigger safe runtime registration.
- Dependency wiring through `factories/component_factory.py` for model, vector store, retrieval, generation, and ingestion services.
- Slack ingestion pipeline via `providers/slack/loader.py` with:
  - channel history fetch,
  - thread reply stitching,
  - deterministic document IDs,
  - metadata enrichment (author, Slack URL, channel, timestamp).
- Ollama embedder provider (`providers/local/ollama_embedder.py`) for query and document embeddings.
- Ollama LLM provider (`providers/local/ollama_llm.py`) for local response generation.
- Chroma vector store provider (`providers/chroma/vector_store.py`) for persistent local vector indexing and search.
- Batch ingestion entrypoint `ingest_batch.py` to ingest configured Slack channels.
- Slack bot runtime `app.py` with Socket Mode event handling (`app_mention`) and per-thread in-memory conversation context.
- YAML-based runtime configuration in `config.yaml` for models, vector store, ingestion settings, retrieval settings, and logging.
- Centralized logging setup utility in `config/settings.py`.

### Current Scope
- This project is currently at major version `1.x`.
- Primary source type supported today: Slack channel conversations.
- Primary runtime profile supported today: local inference with Ollama + Chroma.
