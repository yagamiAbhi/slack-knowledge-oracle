import logging
import yaml
from dotenv import load_dotenv

import providers # <-- This imports the __init__.py we just made, triggering the decorators!
from core.registry import ProviderRegistry

# Core Services
from modules.ingestion.service import IngestionService
from modules.retrieval.service import RetrievalService
from modules.generation.service import GenerationService

logger = logging.getLogger(__name__)


class ComponentFactory:
    def __init__(self, config_path: str = "config.yaml"):
        load_dotenv()
        logger.debug("Loaded environment variables from .env (if present)")
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        logger.debug("Loaded configuration from %s", config_path)
            
        # Dynamically instantiate the Vector Store based on config string
        vs_config = self.config["vector_store"]
        logger.debug("Resolving vector store provider: %s", vs_config["provider"])
        VSClass = ProviderRegistry.get_vector_store(vs_config["provider"])
        logger.debug("Resolved vector store class: %s", VSClass.__name__)
        
        # We pass the specific kwargs Chroma needs. (In V3, kwargs management can be further abstracted)
        if vs_config["provider"] == "chroma":
            self._vector_store = VSClass(
                collection_name=vs_config.get("collection_name", "local_knowledge"),
                persist_directory=vs_config.get("persist_directory", "./chroma_db")
            )
        else:
            self._vector_store = VSClass() # For memory store fallback
        logger.info("Vector store initialized: %s", vs_config["provider"])

    def get_ingestion_service(self) -> IngestionService:
        # Dynamically get the loader (Assuming "txt" for now, can be read from config later)
        LoaderClass = ProviderRegistry.get_loader("txt")
        logger.debug("Resolved document loader class: %s", LoaderClass.__name__)
        loader = LoaderClass()
        
        # Dynamically get the embedder
        embedder_config = self.config["models"]["embedder"]
        logger.debug("Resolving embedder provider: %s", embedder_config["provider"])
        EmbedderClass = ProviderRegistry.get_embedder(embedder_config["provider"])
        logger.debug("Resolved embedder class: %s", EmbedderClass.__name__)
        embedder = EmbedderClass(model_name=embedder_config["model_name"])

        chunk_size = self.config["ingestion"].get("chunk_size", 1000)
        logger.debug(
            "Building IngestionService (loader=%s, embedder=%s, chunk_size=%d)",
            LoaderClass.__name__,
            EmbedderClass.__name__,
            chunk_size,
        )

        return IngestionService(
            loader=loader,
            embedder=embedder,
            vector_store=self._vector_store,
            chunk_size=chunk_size
        )

    def get_retrieval_service(self) -> RetrievalService:
        embedder_config = self.config["models"]["embedder"]
        logger.debug("Resolving embedder provider for retrieval: %s", embedder_config["provider"])
        EmbedderClass = ProviderRegistry.get_embedder(embedder_config["provider"])
        logger.debug("Resolved retrieval embedder class: %s", EmbedderClass.__name__)
        embedder = EmbedderClass(model_name=embedder_config["model_name"])
        
        top_k = self.config["retrieval"].get("top_k", 5)
        logger.debug(
            "Building RetrievalService (embedder=%s, top_k=%d)",
            EmbedderClass.__name__,
            top_k,
        )

        return RetrievalService(
            embedder=embedder,
            vector_store=self._vector_store,
            top_k=top_k
        )

    def get_generation_service(self) -> GenerationService:
        llm_config = self.config["models"]["llm"]
        logger.debug("Resolving llm provider: %s", llm_config["provider"])
        
        # 1. Ask registry for class
        LLMClass = ProviderRegistry.get_llm(llm_config["provider"])
        logger.debug("Resolved llm class: %s", LLMClass.__name__)
        
        # 2. Instantiate it
        llm = LLMClass(
            model_name=llm_config["model_name"],
            temperature=llm_config["temperature"]
        )
        logger.debug(
            "Building GenerationService (llm=%s, model=%s, temperature=%s)",
            LLMClass.__name__,
            llm_config["model_name"],
            llm_config["temperature"],
        )

        return GenerationService(llm=llm)
