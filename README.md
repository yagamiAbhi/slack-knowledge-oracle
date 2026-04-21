# Slack Knowledge Oracle

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-1.0.0-success.svg)](./CHANGELOG.md)

A modular Slack-native RAG assistant that ingests channel knowledge, stores embeddings in Chroma, and answers team questions inside Slack threads.

The architecture is interface-driven and provider-based, so core business logic remains decoupled from implementation choices.

## Architecture

This project separates system behavior into contracts (interfaces), application modules (business logic), and providers (concrete integrations).

```mermaid
flowchart LR
    classDef setup fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef module fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef interface fill:#f9f2f4,stroke:#c7254e,stroke-width:2px,stroke-dasharray: 5 5;
    classDef provider fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px;

    subgraph Setup ["1. Initialization"]
        direction TB
        app[app.py]:::setup
        factory[ComponentFactory]:::setup
        app --> factory
    end

    subgraph Modules ["2. Core Logic (Modules)"]
        direction TB
        ingest[IngestionService]:::module
        retrieval[RetrievalService]:::module
        gen[GenerationService]:::module
    end

    subgraph Interfaces ["3. Contracts (Interfaces)"]
        direction TB
        iLoader([BaseDocumentLoader]):::interface
        iEmbed([BaseEmbedder]):::interface
        iVector([BaseVectorStore]):::interface
        iLLM([BaseLLM]):::interface
    end

    subgraph Providers ["4. Implementations (Providers)"]
        direction TB
        slack[SlackDocumentLoader]:::provider
        oEmbed[OllamaEmbedder]:::provider
        chroma[ChromaVectorStore]:::provider
        oLLM[OllamaLLM]:::provider
    end

    factory ==>|Instantiates| ingest & retrieval & gen
    ingest ---> iLoader & iEmbed & iVector
    retrieval ---> iEmbed & iVector
    gen ---> iLLM

    iLoader -.->|Resolved to| slack
    iEmbed -.->|Resolved to| oEmbed
    iVector -.->|Resolved to| chroma
    iLLM -.->|Resolved to| oLLM
```

### End-to-End Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Operator as User/Operator
    actor Teammate as Slack User
    participant Batch as ingest_batch.py
    participant App as app.py
    participant CF as ComponentFactory
    participant Ingest as IngestionService
    participant Retrieve as RetrievalService
    participant Generate as GenerationService
    participant Loader as SlackDocumentLoader
    participant Embed as OllamaEmbedder
    participant Store as ChromaVectorStore
    participant LLM as OllamaLLM

    rect rgb(245, 245, 210)
    Note over Operator,Store: Phase 1 - Batch Ingestion (ETL)
    Operator->>Batch: Run python ingest_batch.py
    Batch->>CF: Read config + get_ingestion_service()
    CF-->>Batch: IngestionService(loader, embedder, vector_store)
    loop For each channel in config.yaml
        Batch->>Ingest: process_source(channel_id)
        Ingest->>Loader: load(channel_id)
        Loader-->>Ingest: Slack threads as Document list
        Ingest->>Embed: embed_documents(documents)
        Embed-->>Ingest: Documents with embeddings
        Ingest->>Store: upsert(embedded_docs)
        Store-->>Ingest: Upsert complete
    end
    end

    rect rgb(255, 228, 225)
    Note over Teammate,LLM: Phase 2 - Retrieval + Generation (Slack Chat)
    Teammate->>App: @bot question in Slack thread
    App->>CF: get_retrieval_service() + get_generation_service()
    CF-->>App: RetrievalService + GenerationService
    App->>Retrieve: retrieve(user_query)
    Retrieve->>Embed: embed_text(user_query)
    Embed-->>Retrieve: Query embedding
    Retrieve->>Store: search(query_embedding, top_k)
    Store-->>Retrieve: Matching context docs
    Retrieve-->>App: context_documents
    App->>Generate: answer_query(query, context, history)
    Generate->>LLM: generate(prompt, context, chat_history)
    LLM-->>Generate: Answer text
    Generate-->>App: Final response
    App-->>Teammate: Reply in same Slack thread
    end
```

## Current Features (v1.0.0)

- Slack channel ingestion with thread-aware context stitching.
- Deterministic document IDs for stable upserts.
- Metadata-rich documents with author and direct Slack message URLs.
- Local embedding and generation through Ollama.
- Local persistent vector index via Chroma.
- Dynamic provider resolution through `ProviderRegistry` decorators.
- Config-driven system behavior through `config.yaml`.
- Slack bot replies in thread to `app_mention` events.
- In-memory per-thread conversation memory for follow-up continuity.

## Directory Structure

```text
slack-knowledge-oracle/
|- app.py
|- ingest_batch.py
|- config.yaml
|- requirements.txt
|- CHANGELOG.md
|- core/
|  |- entities.py
|  |- exceptions.py
|  |- registry.py
|- interfaces/
|  |- document_loader.py
|  |- embedder.py
|  |- llm.py
|  |- vector_store.py
|- modules/
|  |- ingestion/service.py
|  |- retrieval/service.py
|  |- generation/service.py
|- providers/
|  |- __init__.py
|  |- slack/loader.py
|  |- local/ollama_embedder.py
|  |- local/ollama_llm.py
|  |- chroma/vector_store.py
|- factories/
|  |- component_factory.py
`- config/
   `- settings.py
```

## Getting Started

### 1. Prerequisites

- Python 3.9+
- Slack app credentials for bot token and app token (Socket Mode)
- Ollama running locally

Pull the default models used by `config.yaml`:

```bash
ollama pull qwen3:8b-q4_K_M
ollama pull qwen3-embedding:0.6b
```

### 2. Installation

```bash
git clone https://github.com/<your-org>/slack-knowledge-oracle.git
cd slack-knowledge-oracle
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file at project root with:

```env
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SLACK_WORKSPACE_DOMAIN=your-workspace-domain
```

### 4. Configure Ingestion Targets

Update `config.yaml` with your Slack channel IDs under:

```yaml
slack:
  target_channels:
    - "C0123456789"
```

### 5. Run Batch Ingestion

```bash
python ingest_batch.py
```

### 6. Run the Slack Bot

```bash
python app.py
```

Mention the bot in a Slack channel thread to query indexed knowledge.

## Runtime Configuration

`config.yaml` controls provider and model choices, retrieval depth, vector store settings, and logging.

Key sections:
- `models.llm`
- `models.embedder`
- `vector_store`
- `slack.target_channels`
- `retrieval.top_k`
- `logging`

## Extending the Project

To add a new provider without modifying module logic:

1. Implement the appropriate interface in `providers/<name>/...`.
2. Add the matching `@ProviderRegistry.register_*` decorator.
3. Import that provider in `providers/__init__.py`.
4. Switch configuration in `config.yaml` (where applicable).

## Notes

- Ingestion currently focuses on Slack channel data.
- Conversation memory in `app.py` is in-process memory and resets on restart.
- Advanced reranking and long-term memory backends are not yet implemented in v1.
