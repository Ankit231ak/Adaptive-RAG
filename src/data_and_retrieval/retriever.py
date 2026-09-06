"""
Retriever component for document fetching.
Owner: Member B (Data & Retrieval - Ankit)
"""
from typing import List
from src.data_and_retrieval.corpus import Corpus, Document


class Retriever:
    """Retriever class serving document passages for a query."""
    def __init__(self, corpus: Corpus):
        self.corpus = corpus

    def retrieve(self, query: str, context_doc_ids: List[str], top_k: int = 5) -> List[Document]:
        docs = [self.corpus.get_document(did) for did in context_doc_ids if self.corpus.get_document(did) is not None]
        return docs[:top_k]
