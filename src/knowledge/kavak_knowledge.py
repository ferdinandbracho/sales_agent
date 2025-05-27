"""
Kavak Knowledge Base - RAG Implementation
Connects to a pre-populated ChromaDB instance.
"""

from typing import List, Optional, Dict

import chromadb
from chromadb.utils import embedding_functions
from chromadb.api.models.Collection import Collection

from src.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

# Global instance of the Knowledge Base
kavak_kb_instance: Optional["KavakKnowledgeBase"] = None


class KavakKnowledgeBase:
    def __init__(self):
        """Initialize the Kavak knowledge base connector."""
        self.chroma_host = settings.chroma.CHROMA_HOST
        self.chroma_port = settings.chroma.CHROMA_PORT
        self.collection_name = settings.chroma.CHROMA_COLLECTION_NAME
        self.embedding_model_name = settings.chroma.EMBEDDING_MODEL_NAME

        self.chroma_client: Optional[chromadb.ClientAPI] = None
        self.embedding_function: Optional[
            embedding_functions.SentenceTransformerEmbeddingFunction
        ] = None
        self.collection: Optional[Collection] = None
        self.initialization_error: Optional[str] = None

    def initialize(self) -> None:
        """Initialize connection to ChromaDB and get the collection."""
        logger.info(
            f"Attempting to initialize KavakKnowledgeBase for collection: '{self.collection_name}'..."
        )
        try:
            # Attempt to connect to ChromaDB service
            logger.info(
                f"Connecting to ChromaDB server at http://{self.chroma_host}:{self.chroma_port}"
            )
            self.chroma_client = chromadb.HttpClient(
                host=self.chroma_host, port=self.chroma_port
            )
            self.chroma_client.heartbeat()  # Test connection
            logger.info(
                f"Successfully connected to ChromaDB server: http://{self.chroma_host}:{self.chroma_port}"
            )

            # Initialize embedding function
            self.embedding_function = (
                embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=self.embedding_model_name
                )
            )
            logger.info(f"Using embedding model: {self.embedding_model_name}")

            # Attempt to get the collection
            try:
                logger.info(f"Attempting to get collection: '{self.collection_name}'")
                self.collection = self.chroma_client.get_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function
                )
                logger.info(f"Successfully got collection '{self.collection_name}'.")
                collection_count = self.collection.count()
                if collection_count == 0:
                    logger.warning(
                        f"Collection '{self.collection_name}' exists but is empty. RAG will be unavailable until data is added."
                    )
                else:
                    logger.info(
                        f"Collection '{self.collection_name}' contains {collection_count} documents."
                    )
            except Exception as e:  # Handles collection not found and other get_collection errors
                self.initialization_error = f"Failed to get ChromaDB collection '{self.collection_name}': {e}. This is expected if 'make setup-knowledge' has not been run. RAG will be unavailable."
                logger.warning(self.initialization_error) # Log as warning, not error
                self.collection = None  # Ensure collection is None if not found/accessible

        except Exception as e:  # Catches errors connecting to ChromaDB service itself
            self.initialization_error = (
                f"Critical error connecting to ChromaDB service: {e}"
            )
            logger.error(self.initialization_error, exc_info=True)
            self.collection = None


        # Final status log (informative only)
        if self.chroma_client:
            if self.collection and self.collection.count() > 0:
                logger.info("KavakKnowledgeBase initialized: ChromaDB service connected and collection loaded with data.")
            elif self.collection:
                logger.warning("KavakKnowledgeBase initialized: ChromaDB service connected, collection found but is EMPTY. RAG will yield no results.")
            else:
                logger.warning("KavakKnowledgeBase initialized: ChromaDB service connected, but collection NOT found or accessible. RAG will be unavailable.")
        else:
            logger.error("KavakKnowledgeBase initialization FAILED: Could not connect to ChromaDB service.")

    @property
    def is_ready(self) -> bool:
        """
        Dynamically checks if the RAG system is ready.
        Ready means:
        1. ChromaDB client is connected.
        2. Embedding function is initialized.
        3. The specified collection exists in ChromaDB.
        4. The collection contains at least one document.
        Updates self.initialization_error with the reason if not ready.
        """
        if not self.chroma_client:
            self.initialization_error = "ChromaDB client not initialized. Connection to ChromaDB service may have failed."
            return False
        if not self.embedding_function:
            self.initialization_error = "Embedding function not initialized."
            return False

        try:
            # Attempt to get the collection. This also serves as a heartbeat for the collection.
            current_collection = self.chroma_client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            self.collection = current_collection

            collection_count = self.collection.count()
            if collection_count > 0:
                self.initialization_error = None
                return True
            else:
                self.initialization_error = f"Collection '{self.collection_name}' exists but is empty."
                logger.warning(f"RAG Status: Not Ready. {self.initialization_error}")
                return False
        except chromadb.errors.NotFoundError:
            self.initialization_error = f"Collection '{self.collection_name}' does not exist."
            logger.warning(f"RAG Status: Not Ready. {self.initialization_error}")
            self.collection = None
            return False
        except Exception as e:
            # Catch other potential errors during collection access
            self.initialization_error = f"Failed to access or verify collection '{self.collection_name}': {e}"
            logger.error(f"RAG Status: Not Ready. Unexpected error: {self.initialization_error}", exc_info=True)
            self.collection = None
            return False

    def search_knowledge(
        self, query: str, top_k: int = 3, filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Search the knowledge base for relevant documents.

        Args:
            query: The user's query string.
            top_k: The number of top results to return.
            filters: Optional dictionary for metadata filtering (e.g., {"category": "financing"}).

        Returns:
            A list of dictionaries containing document content, metadata, and distance,
            or an empty list if not ready or no results.
        """
        if not self.is_ready:
            logger.error(
                f"Knowledge base search failed: {self.initialization_error or 'Unknown error'}"
            )
            return []

        try:
            logger.debug(
                f"Searching collection '{self.collection_name}' for query: '{query}', top_k={top_k}, filters={filters}"
            )
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=filters if filters else None,
                include=["documents", "metadatas", "distances"],
            )

            formatted_results = []
            if results and results.get("documents") and results.get("documents")[0]:
                for i, doc_text in enumerate(results["documents"][0]):
                    metadata = (
                        results["metadatas"][0][i]
                        if results.get("metadatas") and results["metadatas"][0]
                        else {}
                    )
                    distance = (
                        results["distances"][0][i]
                        if results.get("distances") and results["distances"][0]
                        else None
                    )
                    formatted_results.append(
                        {
                            "content": doc_text,
                            "metadata": metadata,
                            "distance": distance,
                            "title": metadata.get("title", "N/A"),
                            "source_url": metadata.get("source_url", "N/A"),
                        }
                    )
                logger.debug(
                    f"Found {len(formatted_results)} results for query: '{query}'"
                )
            else:
                logger.debug(f"No results found for query: '{query}'")
            return formatted_results

        except Exception as e:
            logger.error(
                f"Error during knowledge search for query '{query}': {e}", exc_info=True
            )
            return []


# --- Global Instance Management ---


def initialize_global_kavak_kb():
    """Initializes the global Kavak Knowledge Base instance."""
    global kavak_kb_instance
    if kavak_kb_instance is None:
        logger.info("Initializing Global Kavak Knowledge Base at startup...")
        kavak_kb_instance = KavakKnowledgeBase()
        kavak_kb_instance.initialize()
        # We just log the overall outcome of the initialization attempt.
        if kavak_kb_instance.initialization_error and not kavak_kb_instance.is_ready:
            logger.warning(
                f"Global Kavak Knowledge Base initialized, but RAG is not fully ready. Reason: {kavak_kb_instance.initialization_error}. The agent will attempt to function with limited/no RAG capabilities."
            )
        elif kavak_kb_instance.is_ready:
            logger.info(
                "Global Kavak Knowledge Base initialized and RAG is ready."
            )
        else: # Should ideally be caught, but as a fallback
             logger.warning(
                f"Global Kavak Knowledge Base initialized, but RAG is not ready. Status: {kavak_kb_instance.initialization_error or 'Unknown. Check KB logs.'}. The agent will attempt to function with limited/no RAG capabilities."
            )
    return kavak_kb_instance


def get_kavak_knowledge_base() -> KavakKnowledgeBase:
    """Get global knowledge base instance.

    Ensures that if accessed before explicit initialization (e.g. by lifespan manager),
    it attempts to initialize.
    """
    global kavak_kb_instance
    if kavak_kb_instance is None:
        logger.warning(
            "Kavak Knowledge Base accessed before global initialization. Attempting to initialize now..."
        )
        return initialize_global_kavak_kb()
    return kavak_kb_instance
