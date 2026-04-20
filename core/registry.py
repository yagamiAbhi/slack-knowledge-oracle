import logging

logger = logging.getLogger(__name__)


class ProviderRegistry:
    _llms = {}
    _embedders = {}
    _vector_stores = {}
    _loaders = {}

    # --- LLM Registration ---
    @classmethod
    def register_llm(cls, name: str):
        def wrapper(llm_class):
            cls._llms[name] = llm_class
            logger.debug("Registered LLM provider '%s' -> %s", name, llm_class.__name__)
            return llm_class
        return wrapper

    @classmethod
    def get_llm(cls, name: str):
        if name not in cls._llms:
            logger.error("LLM provider '%s' is not registered", name)
            raise ValueError(f"LLM Provider '{name}' is not registered.")
        logger.debug("Resolved LLM provider '%s' -> %s", name, cls._llms[name].__name__)
        return cls._llms[name]

    # --- Embedder Registration ---
    @classmethod
    def register_embedder(cls, name: str):
        def wrapper(embedder_class):
            cls._embedders[name] = embedder_class
            logger.debug("Registered embedder '%s' -> %s", name, embedder_class.__name__)
            return embedder_class
        return wrapper

    @classmethod
    def get_embedder(cls, name: str):
        if name not in cls._embedders:
            logger.error("Embedder '%s' is not registered", name)
            raise ValueError(f"Embedder '{name}' is not registered.")
        logger.debug("Resolved embedder '%s' -> %s", name, cls._embedders[name].__name__)
        return cls._embedders[name]

    # --- Vector Store Registration ---
    @classmethod
    def register_vector_store(cls, name: str):
        def wrapper(vs_class):
            cls._vector_stores[name] = vs_class
            logger.debug("Registered vector store '%s' -> %s", name, vs_class.__name__)
            return vs_class
        return wrapper

    @classmethod
    def get_vector_store(cls, name: str):
        if name not in cls._vector_stores:
            logger.error("Vector store '%s' is not registered", name)
            raise ValueError(f"Vector Store '{name}' is not registered.")
        logger.debug("Resolved vector store '%s' -> %s", name, cls._vector_stores[name].__name__)
        return cls._vector_stores[name]

    # --- Document Loader Registration ---
    @classmethod
    def register_loader(cls, name: str):
        def wrapper(loader_class):
            cls._loaders[name] = loader_class
            logger.debug("Registered loader '%s' -> %s", name, loader_class.__name__)
            return loader_class
        return wrapper

    @classmethod
    def get_loader(cls, name: str):
        if name not in cls._loaders:
            logger.error("Loader '%s' is not registered", name)
            raise ValueError(f"Loader '{name}' is not registered.")
        logger.debug("Resolved loader '%s' -> %s", name, cls._loaders[name].__name__)
        return cls._loaders[name]
