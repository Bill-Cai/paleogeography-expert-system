from .retriever import SearchAPIRetriever, SearchDBRetriever
from langchain.retrievers import (
    ContextualCompressionRetriever,
)
from langchain.retrievers.document_compressors import (
    DocumentCompressorPipeline,
    EmbeddingsFilter,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter

# used in _get_contextual_retriever
DB_MODE = "DB-MODE"
SEARCH_API_MODE = "SEARCH-API-MODE"


class ContextCompressor:
    def __init__(self, documents, embeddings, max_results=5, **kwargs):
        self.max_results = max_results
        self.documents = documents
        self.kwargs = kwargs
        self.embeddings = embeddings

    def _get_contextual_retriever(self, mode=SEARCH_API_MODE):
        # https://python.langchain.com/docs/modules/data_connection/retrievers/contextual_compression/
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        relevance_filter = EmbeddingsFilter(embeddings=self.embeddings, similarity_threshold=0.78)
        pipeline_compressor = DocumentCompressorPipeline(
            transformers=[splitter, relevance_filter]
        )
        if mode == SEARCH_API_MODE:
            base_retriever = SearchAPIRetriever(
                pages=self.documents
            )
        elif mode == DB_MODE:
            base_retriever = SearchDBRetriever(
                pages=self.documents
            )
        else:
            raise ValueError(f"Invalid mode: {mode}")

        contextual_retriever = ContextualCompressionRetriever(
            base_compressor=pipeline_compressor, base_retriever=base_retriever
        )
        return contextual_retriever

    def _pretty_print_docs(self, docs, top_n):
        return f"\n".join(f"Source: {d.metadata.get('source')}\n"
                          f"Title: {d.metadata.get('title')}\n"
                          f"Content: {d.page_content}\n"
                          for i, d in enumerate(docs) if i < top_n)

    def get_context(self, query, max_results=5, mode=SEARCH_API_MODE):
        compressed_docs = self._get_contextual_retriever(mode=mode)
        relevant_docs = compressed_docs.get_relevant_documents(query)
        return self._pretty_print_docs(relevant_docs, max_results)
