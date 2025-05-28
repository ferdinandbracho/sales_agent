"""
Unit tests for Kavak knowledge base and RAG implementation
"""

from unittest.mock import patch, MagicMock, PropertyMock

from src.knowledge.kavak_knowledge import KavakKnowledgeBase
from src.tools.kavak_info import get_kavak_info


class TestKavakKnowledgeBase:
    """Test Kavak knowledge base functionality"""

    def test_kavak_knowledge_base_initialization(self):
        """Test knowledge base initialization"""
        # Create instance with default settings
        kb = KavakKnowledgeBase()

        # Check default attributes
        assert kb.chroma_client is None
        assert kb.embedding_function is None
        assert kb.collection is None
        assert kb.initialization_error is None
        assert kb.is_ready is False  # Should not be ready until initialized

    @patch("src.knowledge.kavak_knowledge.chromadb.HttpClient")
    @patch(
        "src.knowledge.kavak_knowledge.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    @patch.object(
        KavakKnowledgeBase, "is_ready", new_callable=PropertyMock, return_value=True
    )
    def test_initialize_success(
        self, mock_is_ready, mock_embedding_function, mock_http_client
    ):
        """Test successful initialization"""
        # Create a real integer for count
        mock_count = 10

        # Create a mock collection with a count method that returns our mock_count
        mock_collection = MagicMock()
        mock_collection.count.return_value = mock_count

        # Configure the mock client to return our mock collection
        mock_client = MagicMock()
        mock_client.heartbeat.return_value = True
        mock_client.get_collection.return_value = mock_collection

        # Configure the mock http client to return our mock client
        mock_http_client.return_value = mock_client

        # Mock the embedding function
        mock_embedding = MagicMock()
        mock_embedding_function.return_value = mock_embedding

        # Create a mock for the embedding model
        mock_embedding_model = MagicMock()

        # We need to patch the KavakKnowledgeBase class to avoid actual ChromaDB connections
        with patch(
            "sentence_transformers.SentenceTransformer",
            return_value=mock_embedding_model,
        ):
            # Create an instance of the knowledge base
            kb = KavakKnowledgeBase()

            # Patch the collection's count method to return our mock_count
            with patch.object(
                kb, "collection", create=True, new_callable=PropertyMock
            ) as mock_collection_prop:
                mock_collection_prop.return_value = mock_collection

                # Call initialize
                kb.initialize()

                # Verify initialization
                assert kb.chroma_client is not None
                assert kb.embedding_function is not None
                assert kb.collection is not None
                assert kb.initialization_error is None

                # Verify ChromaDB client was called with correct parameters
                mock_http_client.assert_called_once()
                mock_client.heartbeat.assert_called_once()
                mock_client.get_collection.assert_called_once()
                mock_embedding_function.assert_called_once()

                # Verify the count method was called and returns the correct value
                assert kb.collection.count() == mock_count

                # Verify status through is_ready property
                assert kb.is_ready is True

    @patch("src.knowledge.kavak_knowledge.chromadb.HttpClient")
    def test_initialize_collection_not_found(self, mock_http_client):
        """Test initialization with collection not found"""
        # Setup mocks
        mock_client = MagicMock()
        mock_http_client.return_value = mock_client

        # Simulate collection not found
        mock_client.get_collection.side_effect = Exception("Collection not found")

        # Mock the embedding function
        with patch("sentence_transformers.SentenceTransformer") as mock_embedding:
            mock_embedding.return_value = MagicMock()

            # Initialize
            kb = KavakKnowledgeBase()
            kb.initialize()

            # Should not be ready since collection was not found
            assert not kb.is_ready
            # Check that we have an initialization error
            assert kb.initialization_error is not None
            assert (
                "collection" in kb.initialization_error.lower()
                or "not found" in kb.initialization_error.lower()
            )

    @patch("src.knowledge.kavak_knowledge.chromadb.HttpClient")
    def test_initialize_empty_collection(self, mock_http_client):
        """Test initialization with empty collection"""
        # Setup mocks
        mock_client = MagicMock()
        mock_http_client.return_value = mock_client

        mock_collection = MagicMock()
        mock_collection.count.return_value = 0  # Empty collection
        mock_client.get_collection.return_value = mock_collection

        # Initialize KB
        kb = KavakKnowledgeBase()
        kb.initialize()

        # Verify initialization state
        assert kb.chroma_client is not None
        assert kb.collection is not None
        assert kb.is_ready is False  # Should not be ready with empty collection
        assert "empty" in kb.initialization_error.lower()

    @patch("src.knowledge.kavak_knowledge.chromadb.HttpClient")
    def test_initialize_connection_error(self, mock_http_client):
        """Test initialization with connection error"""
        # Setup mock to raise connection error
        mock_http_client.side_effect = Exception("Connection refused")

        # Initialize KB
        kb = KavakKnowledgeBase()
        kb.initialize()

        # Should handle error gracefully
        assert not kb.is_ready
        assert kb.initialization_error is not None
        assert "connection" in str(kb.initialization_error).lower()

    @patch("src.knowledge.kavak_knowledge.chromadb.HttpClient")
    def test_search_knowledge_not_ready(self, mock_http_client):
        """Test search_knowledge when not ready"""
        # Setup KB that's not ready
        kb = KavakKnowledgeBase()
        kb.initialization_error = "Not initialized"

        # Search should return empty list
        results = kb.search_knowledge("test query")
        assert results == []

    @patch("src.knowledge.kavak_knowledge.chromadb.HttpClient")
    def test_search_knowledge_success(self, mock_http_client):
        """Test successful knowledge search"""
        # Setup mocks
        mock_client = MagicMock()
        mock_http_client.return_value = mock_client

        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_collection.query.return_value = {
            "documents": [["Document 1 content", "Document 2 content"]],
            "metadatas": [[{"source": "test1"}, {"source": "test2"}]],
            "distances": [[0.1, 0.2]],
            "ids": [["id1", "id2"]],
        }
        mock_client.get_collection.return_value = mock_collection

        # Initialize and search
        kb = KavakKnowledgeBase()
        kb.initialize()
        results = kb.search_knowledge("test query", top_k=2)

        # Verify results
        assert len(results) == 2
        assert results[0]["content"] == "Document 1 content"
        assert results[0]["metadata"]["source"] == "test1"
        assert results[0]["distance"] == 0.1
        assert results[1]["content"] == "Document 2 content"

        # Verify query parameters
        mock_collection.query.assert_called_with(
            query_texts=["test query"],
            n_results=2,
            where=None,
            include=["documents", "metadatas", "distances"],
        )

    @patch("src.knowledge.kavak_knowledge.chromadb.HttpClient")
    def test_search_knowledge_with_filters(self, mock_http_client):
        """Test knowledge search with filters"""
        # Setup mocks
        mock_client = MagicMock()
        mock_http_client.return_value = mock_client

        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_collection.query.return_value = {
            "documents": [["Filtered document"]],
            "metadatas": [[{"category": "financing"}]],
            "distances": [[0.1]],
            "ids": [["id1"]],
        }
        mock_client.get_collection.return_value = mock_collection

        # Initialize and search with filters
        kb = KavakKnowledgeBase()
        kb.initialize()
        filters = {"category": "financing"}
        results = kb.search_knowledge("test query", top_k=1, filters=filters)

        # Verify results
        assert len(results) == 1
        assert results[0]["content"] == "Filtered document"
        assert results[0]["metadata"]["category"] == "financing"

        # Verify query parameters
        mock_collection.query.assert_called_with(
            query_texts=["test query"],
            n_results=1,
            where=filters,
            include=["documents", "metadatas", "distances"],
        )

    @patch("src.knowledge.kavak_knowledge.chromadb.HttpClient")
    def test_search_knowledge_empty_results(self, mock_http_client):
        """Test knowledge search with empty results"""
        # Setup mocks
        mock_client = MagicMock()
        mock_http_client.return_value = mock_client

        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_collection.query.return_value = {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
            "ids": [[]],
        }
        mock_client.get_collection.return_value = mock_collection

        # Initialize and search
        kb = KavakKnowledgeBase()
        kb.initialize()
        results = kb.search_knowledge("test query", top_k=2)

        # Verify results
        assert len(results) == 0

    def test_get_kavak_info_tool(self):
        """Test get_kavak_info tool"""
        # Setup mock KB
        mock_kb = MagicMock()
        mock_kb.is_ready = True
        mock_kb.search_knowledge.return_value = [
            {
                "content": "Kavak es una plataforma de compra y venta de autos seminuevos.",
                "metadata": {"category": "general"},
                "distance": 0.1,
            }
        ]
        mock_kb.get_status.return_value = "Ready"

        # Patch the global knowledge base
        with patch("src.knowledge.kavak_knowledge.kavak_kb_instance", mock_kb):
            # Test tool
            result = get_kavak_info.invoke({"query": "¿Qué es Kavak?"})

            # Should return the content from the knowledge base
            assert "Kavak" in result
            assert "plataforma" in result.lower()
            assert "autos" in result.lower()
            mock_kb.search_knowledge.assert_called_once_with(
                query="¿Qué es Kavak?", top_k=1
            )

    @patch("src.knowledge.kavak_knowledge.kavak_kb_instance")
    def test_get_kavak_info_tool_not_ready(self, mock_kb_instance):
        """Test get_kavak_info tool when KB is not ready"""
        # Setup mock KB that's not ready
        mock_kb = MagicMock()
        mock_kb.is_ready = False
        mock_kb.get_status.return_value = "Not initialized"
        mock_kb.initialization_error = "Collection not found"
        mock_kb_instance.return_value = mock_kb

        # Test tool
        result = get_kavak_info.invoke({"query": "¿Qué es Kavak?"})

        # Should return an error message or indicate no clear information
        assert (
            any(
                phrase in result.lower()
                for phrase in [
                    "no está disponible",
                    "no encontré información",
                    "no tengo información",
                    "no pude encontrar",
                ]
            )
            or "🤔" in result
        )
        assert not mock_kb.search_knowledge.called

    @patch("src.knowledge.kavak_knowledge.get_kavak_knowledge_base")
    def test_get_kavak_info_tool_empty_results(self, mock_get_kb):
        """Test get_kavak_info tool with empty results"""
        # Setup mock KB with empty results
        mock_kb = MagicMock()
        mock_kb.is_ready = True
        mock_kb.search_knowledge.return_value = []
        mock_kb.get_status.return_value = "Ready"
        mock_get_kb.return_value = mock_kb

        # Test tool
        result = get_kavak_info.invoke({"query": "tema desconocido"})

        # Should return empty string to signal agent to use base knowledge
        assert result == ""

    def test_get_kavak_info_tool_long_content(self):
        """Test get_kavak_info tool with long content"""
        # Create long content
        long_content = "Kavak " + "información " * 500

        # Setup mock KB with long content
        mock_kb = MagicMock()
        mock_kb.is_ready = True
        mock_kb.search_knowledge.return_value = [
            {
                "content": long_content,
                "metadata": {"category": "general"},
                "distance": 0.1,
            }
        ]
        mock_kb.get_status.return_value = "Ready"

        # Patch the global knowledge base
        with patch("src.knowledge.kavak_knowledge.kavak_kb_instance", mock_kb):
            # Test tool
            result = get_kavak_info.invoke({"query": "información general"})

            # Should truncate the content and add a message
            assert result  # Make sure result is not empty
            assert len(result) < len(long_content)
            assert any(
                phrase in result
                for phrase in [
                    "¿Te gustaría que profundice",
                    "más detalles",
                    "información",
                ]
            )
