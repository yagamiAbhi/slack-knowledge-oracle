import logging

logger = logging.getLogger(__name__)

# Importing these triggers the @ decorators so they register themselves
logger.debug("Bootstrapping provider registrations")
import providers.local.ollama_llm
import providers.local.ollama_embedder
import providers.chroma.vector_store
import providers.slack.loader
logger.debug("Provider registration bootstrap complete")
