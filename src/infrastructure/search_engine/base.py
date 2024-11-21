import os
from typing import Optional
from abc import ABC, abstractmethod

from src.common.logger import logger
from src.common.config import load_config, ConfigBase
from langchain_openai import OpenAIEmbeddings

from .types import SearchEngineResponse

class SimilaritySearchEngine(ABC):
    """Abstract base class for vector store functionalities."""
    
    def __init__(
        self, 
        config: Optional[ConfigBase] = None, 
        encoder = None, 
        **kwargs
        ) -> None:
        self.config = config or load_config()
        self.logger = logger
        self.encoder = encoder
        
        if encoder is None:
            self.encoder = OpenAIEmbeddings()
        else:
            self.encoder = encoder
        
        self.logger.info("Initialized SearchEngineBase!")

    @abstractmethod
    def load_embeddings(self) -> bool:
        """Abstract method for loading embeddings."""
        pass

    @abstractmethod
    def embed_data(self) -> bool:
        """Abstract method for embedding data."""
        pass

    @abstractmethod
    def save_embeddings(self) -> None:
        """Abstract method for saving embeddings."""
        pass

    @abstractmethod
    def search(self, query: str, **kwargs) -> SearchEngineResponse:
        """Abstract method for finding similar items based on input."""
        pass
