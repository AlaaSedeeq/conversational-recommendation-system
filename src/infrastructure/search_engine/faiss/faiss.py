import re
import os
import warnings
import numpy as np
from typing import Optional, List, Tuple

from langchain_openai import OpenAIEmbeddings
# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from langchain_community.vectorstores.faiss import FAISS

from src.common.logger import logger
from src.common.config import ConfigBase, load_config

from src.utils.tools import read_dialogue, read_user_data, read_jsonl, read_json, get_conversation_by_id
from src.infrastructure.search_engine.base import SimilaritySearchEngine
from ..types import SearchEngineResponse

class FAISS_Search(SimilaritySearchEngine):
    def __init__(
            self,
        config: Optional[ConfigBase] = None,
        encoder = None,
        **kwargs
        ) -> None:
        """
        Initialize FAISS Search engine
        
        Args:
            config: Configuration object, if None will load from default path
            encoder: Embedding encoder, if None will use OpenAIEmbeddings
            **kwargs: Additional arguments
        """

        if config is None:
            config = load_config()
            
        super().__init__(config, encoder, **kwargs)
        
        self.logger = logger
        self.data = None
        self.vectorstore = None
        self.embeddings_loaded = False
        self.top_k = config.similarity_search.top_k

    def load_embeddings(self) -> bool:
        if os.path.exists(self.config.embeddings.vectordb_path):
            self.vectorstore = FAISS.load_local(
                self.config.embeddings.vectordb_path, 
                self.encoder, 
                allow_dangerous_deserialization=True)
            self.embeddings_loaded = True
            return True
        else:
            self.logger.error(f"Embeddings not found: {self.config.embeddings.vectordb_path}")
            return self.embed_data()

    def _read_data(self) -> List[Document]:
        
        path = self.config.data.conversations
        docs = read_dialogue(path)
        
        pattern = r"(\d+)\n\n((?:User:.*?\n\nAgent:.*?(?:\n\n|$))+)"
        matches = re.findall(pattern, docs, re.DOTALL)

        documents = []
        for match in matches:
            dialogue_number = match[0]
            dialogue_content = match[1].strip()
            metadata = {"dialogue_number": dialogue_number}
            documents.append(Document(page_content=dialogue_content, metadata=metadata))

        return documents

    def embed_data(self) -> bool:
        try:
            self.logger.info("Reading the data")
            docs = self._read_data()
            self.logger.info("Embedding the data")
            self.vectorstore = FAISS.from_documents(docs, self.encoder)
            self.embeddings_loaded = True
            self.logger.info("Saving the embeddings")
            self.save_embeddings()
            return True

        except Exception as e:
            self.logger.error(f"Failed to embed data: {e}")
            return False
            
    # def rerank(self, query: str, docs: List[Tuple[Document, np.float64]]):
    #     import os        
    #     if "COHERE_API_KEY" in os.environ:
        
    def save_embeddings(self) -> None:
        if self.vectorstore:
            self.vectorstore.save_local(self.config.embeddings.vectordb_path)
            self.logger.info("Embeddings saved locally.")
        else:
            self.logger.error("No vectorstore to save embeddings from.")

    def search(
        self, 
        query: str, 
        filter_neg: bool = True, 
    ) -> SearchEngineResponse:

        if not self.embeddings_loaded:
            if not self.load_embeddings():
                return SearchEngineResponse(status=False, response=[])

        query = query.strip()
        self.logger.info(f"Searching for: {query[:100]} ...")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                docs = self.vectorstore.similarity_search_with_relevance_scores(query, k=self.top_k)
                docs = sorted(docs, key=lambda x: x[1], reverse=True)
                
                if filter_neg:
                    Hscore = docs[0][1]
                    if Hscore < 0.0:
                        self.logger.info("No similar items found in the item list for item `{}`.".format(query))
                        return SearchEngineResponse(status=True, response=[])
                    qdocs = [d for d in docs if d[1] >= 0.0]
                # if rerank:
                #     docs = self.rerank(query, docs)
                # else:
                #     docs = [d for d in docs if d[1] >= self.config.min_similarity_thr]
                #     qdocs = sorted(docs, key=lambda x: x[1], reverse=True)

                return SearchEngineResponse(status=True, response=qdocs)

            except Exception as e:
                self.logger.error(f"Similarity search error: \n{e}")
                return SearchEngineResponse(status=False, response=[])

