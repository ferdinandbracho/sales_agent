"""
Kavak Knowledge Base - RAG Implementation
Integra contenido web scrapeado para respuestas informadas
"""

import json
import logging
import os
from typing import Dict, List, Optional

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class KavakKnowledgeBase:
    """
    Knowledge base that uses scraped Kavak content for RAG
    Base de conocimiento que usa contenido scrapeado para RAG
    """

    def __init__(self, knowledge_file: str = "data/kavak_knowledge.json"):
        """
        Initialize knowledge base

        Args:
            knowledge_file: Path to JSON file with scraped content
        """
        self.knowledge_file = knowledge_file
        self.embedding_model = None
        self.knowledge_chunks = []
        self.embeddings = []

        # Load knowledge base
        self.load_knowledge()

    def load_knowledge(self) -> None:
        """Load and process knowledge from JSON file"""
        try:
            if not os.path.exists(self.knowledge_file):
                logger.warning(f"Knowledge file not found: {self.knowledge_file}")
                self._create_minimal_knowledge()
                return

            with open(self.knowledge_file, "r", encoding="utf-8") as f:
                raw_content = json.load(f)

            logger.info(f"📚 Loaded {len(raw_content)} knowledge pages")

            # Process content into searchable chunks
            self.knowledge_chunks = self._create_knowledge_chunks(raw_content)

            logger.info(f"✅ Created {len(self.knowledge_chunks)} knowledge chunks")

        except Exception as e:
            logger.error(f"❌ Error loading knowledge: {e}")
            self._create_minimal_knowledge()

    def _create_knowledge_chunks(self, raw_content: List[Dict]) -> List[Dict]:
        """
        Convert raw scraped content into searchable chunks

        Args:
            raw_content: List of scraped page content

        Returns:
            List of knowledge chunks for search
        """
        chunks = []

        for page in raw_content:
            # Create chunks from different parts of the content

            # 1. Title + Description chunk
            if page.get("title"):
                title_chunk = {
                    "content": f"Título: {page['title']}",
                    "source": page.get("url", "unknown"),
                    "type": "title",
                    "category": self._categorize_content(page["title"]),
                }
                chunks.append(title_chunk)

            # 2. Main content chunks (split if too long)
            main_content = page.get("main_content", "")
            if main_content and len(main_content) > 100:
                content_chunks = self._split_content(main_content, max_length=800)
                for i, chunk_text in enumerate(content_chunks):
                    chunk = {
                        "content": chunk_text,
                        "source": page.get("url", "unknown"),
                        "type": "content",
                        "category": self._categorize_content(chunk_text),
                        "chunk_id": i,
                    }
                    chunks.append(chunk)

            # 3. Headings as separate chunks
            headings = page.get("headings", [])
            for heading in headings:
                if len(heading) > 10:  # Filter very short headings
                    heading_chunk = {
                        "content": f"Sección: {heading}",
                        "source": page.get("url", "unknown"),
                        "type": "heading",
                        "category": self._categorize_content(heading),
                    }
                    chunks.append(heading_chunk)

            # 4. Important paragraphs
            paragraphs = page.get("paragraphs", [])
            for paragraph in paragraphs:
                if len(paragraph) > 50 and len(paragraph) < 500:
                    para_chunk = {
                        "content": paragraph,
                        "source": page.get("url", "unknown"),
                        "type": "paragraph",
                        "category": self._categorize_content(paragraph),
                    }
                    chunks.append(para_chunk)

        return chunks

    def _split_content(self, content: str, max_length: int = 800) -> List[str]:
        """Split long content into smaller chunks"""
        if len(content) <= max_length:
            return [content]

        # Split by sentences first
        sentences = content.split(". ")
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk + sentence) <= max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _categorize_content(self, text: str) -> str:
        """Categorize content for better retrieval"""
        text_lower = text.lower()

        if any(
            word in text_lower
            for word in ["garantía", "garantia", "cobertura", "protección"]
        ):
            return "warranty"
        elif any(
            word in text_lower
            for word in ["financiamiento", "credito", "préstamo", "pago"]
        ):
            return "financing"
        elif any(
            word in text_lower
            for word in ["ubicación", "sede", "sucursal", "dirección"]
        ):
            return "locations"
        elif any(
            word in text_lower
            for word in ["proceso", "compra", "venta", "como funciona"]
        ):
            return "process"
        elif any(word in text_lower for word in ["ventaja", "beneficio", "diferencia"]):
            return "benefits"
        else:
            return "general"

    def search_knowledge(self, query: str, top_k: int = 3) -> List[str]:
        """
        Search knowledge base for relevant information

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of relevant content pieces
        """
        if not self.knowledge_chunks:
            return [
                "No tengo información específica sobre eso, pero en Kavak ofrecemos garantía, financiamiento y el mejor servicio."
            ]

        # Simple keyword-based search (can be enhanced with embeddings)
        query_lower = query.lower()
        scored_chunks = []

        for chunk in self.knowledge_chunks:
            score = self._calculate_relevance_score(query_lower, chunk)
            if score > 0:
                scored_chunks.append((score, chunk))

        # Sort by relevance and return top results
        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        # Extract content from top chunks
        results = []
        for score, chunk in scored_chunks[:top_k]:
            results.append(chunk["content"])

        return (
            results
            if results
            else ["Información no encontrada en la base de conocimiento."]
        )

    def _calculate_relevance_score(self, query: str, chunk: Dict) -> float:
        """Calculate relevance score between query and chunk"""
        content = chunk["content"].lower()
        score = 0.0

        # Exact phrase matching
        if query in content:
            score += 2.0

        # Word matching
        query_words = query.split()
        content_words = content.split()

        matching_words = len(set(query_words) & set(content_words))
        score += matching_words * 0.5

        # Category bonus for specific queries
        category = chunk.get("category", "general")
        if self._query_matches_category(query, category):
            score += 1.0

        # Type bonus
        chunk_type = chunk.get("type", "content")
        if chunk_type in ["title", "heading"]:
            score += 0.5

        return score

    def _query_matches_category(self, query: str, category: str) -> bool:
        """Check if query matches chunk category"""
        category_keywords = {
            "warranty": ["garantía", "garantia", "cobertura"],
            "financing": ["financiamiento", "credito", "pago", "mensualidad"],
            "locations": ["ubicación", "sede", "sucursal", "donde"],
            "process": ["proceso", "compra", "como funciona"],
            "benefits": ["ventaja", "beneficio", "por que", "diferencia"],
        }

        keywords = category_keywords.get(category, [])
        return any(keyword in query for keyword in keywords)

    def get_kavak_info(self, query: str) -> str:
        """
        Get Kavak information based on query
        Enhanced version that uses scraped content

        Args:
            query: User's question about Kavak

        Returns:
            Relevant information from knowledge base
        """
        try:
            # Search knowledge base
            relevant_chunks = self.search_knowledge(query, top_k=2)

            if (
                relevant_chunks
                and relevant_chunks[0]
                != "Información no encontrada en la base de conocimiento."
            ):
                # Combine relevant information
                response = "📋 **Información de Kavak:**\n\n"

                for i, chunk in enumerate(relevant_chunks, 1):
                    # Clean up the chunk content
                    clean_chunk = chunk.strip()
                    if not clean_chunk.endswith("."):
                        clean_chunk += "."

                    response += f"{clean_chunk}\n\n"

                response += "¿Te gustaría saber algo más específico? 😊"

                return response
            else:
                # Fallback to basic Kavak info
                return self._get_fallback_kavak_info(query)

        except Exception as e:
            logger.error(f"Error retrieving Kavak info: {e}")
            return self._get_fallback_kavak_info(query)

    def _get_fallback_kavak_info(self, query: str) -> str:
        """Fallback Kavak information when knowledge base search fails"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["garantía", "garantia", "cobertura"]):
            return """
✅ **Garantía Kavak**

🔧 Cobertura: 3 meses o 3,000 km
📋 Incluye: Motor, transmisión, sistema eléctrico, frenos y A/C
🏆 Somos la única plataforma con garantía real en seminuevos

¿Te interesa algún auto específico para explicarte más detalles? 🚗
"""
        elif any(word in query_lower for word in ["financiamiento", "credito", "pago"]):
            return """
💰 **Financiamiento Kavak**

📅 Plazos: 12 a 84 meses
📊 Tasa: Desde 10% anual
⚡ Aprobación: En 24 horas
🚫 Sin aval ni garantías adicionales

¿Quieres que calcule un plan específico? 😊
"""
        else:
            return """
🚗 **Kavak - Plataforma #1 de Autos Seminuevos**

✅ Garantía de 3 meses o 3,000 km
💰 Financiamiento hasta 84 meses
📱 Proceso 100% digital
🔍 Inspección de 240 puntos

¿En qué te puedo ayudar específicamente? 😊
"""

    def _create_minimal_knowledge(self) -> None:
        """Create minimal knowledge base if scraping failed"""
        logger.info("📝 Creating minimal knowledge base...")

        minimal_chunks = [
            {
                "content": "Kavak es la plataforma líder de autos seminuevos en México con garantía de 3 meses o 3,000 km.",
                "source": "internal",
                "type": "content",
                "category": "general",
            },
            {
                "content": "Ofrecemos financiamiento hasta 84 meses con tasa desde 10% anual y aprobación en 24 horas.",
                "source": "internal",
                "type": "content",
                "category": "financing",
            },
            {
                "content": "Garantía Kavak cubre motor, transmisión, sistema eléctrico, frenos y aire acondicionado por 3 meses.",
                "source": "internal",
                "type": "content",
                "category": "warranty",
            },
        ]

        self.knowledge_chunks = minimal_chunks


# Global knowledge base instance
kavak_kb = None


def get_kavak_knowledge_base() -> KavakKnowledgeBase:
    """Get global knowledge base instance"""
    global kavak_kb
    if kavak_kb is None:
        kavak_kb = KavakKnowledgeBase()
    return kavak_kb
