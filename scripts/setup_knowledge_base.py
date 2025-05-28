"""
Enhanced Kavak Knowledge Setup
"""

import json
import os
import logging
from typing import Dict, List
import datetime

import chromadb
from chromadb.utils import embedding_functions
from src.config import settings
from scrape_kavak import KavakWebScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_comprehensive_kavak_knowledge() -> List[Dict]:
    """
    Create comprehensive Kavak knowledge base
    Combines scraping attempts with rich fallback content
    """
    logger.info("Creating comprehensive Kavak fallback knowledge content...")

    # Add timestamp and source information
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    fallback_notice = (
        "⚠️ IMPORTANTE: Esta es información de respaldo. "
        "No se pudo obtener la información más reciente del sitio web de Kavak. "
        f"Última actualización: {current_date}"
    )

    # Enhanced knowledge base with detailed information
    comprehensive_content = [
        {
            "url": "kavak-fallback://sedes-mexico",
            "title": "Sedes de Kavak en México (Datos de Respaldo)",
            "main_content": f"""
            {fallback_notice}

            Kavak cuenta con presencia en las principales ciudades de México,
            ofreciendo un servicio completo de compra y venta de autos seminuevos.
            Nuestras ubicaciones estratégicas permiten brindar cobertura nacional
            con el respaldo de la tecnología más avanzada del sector automotriz.

            Nota: Esta información podría no estar actualizada.
            Por favor verifica en el sitio web oficial de Kavak para la información más reciente.
            """,
            "headings": [
                "Ubicaciones Kavak en México (Datos de Respaldo)",
                "Ciudad de México",
                "Guadalajara, Jalisco",
                "Monterrey, Nuevo León",
                "Puebla, Puebla",
                "Tijuana, Baja California",
                "Mérida, Yucatán",
                "Nota Importante",
            ],
            "paragraphs": [
                "Kavak revoluciona la experiencia de compra de autos seminuevos en México.",
                "Ciudad de México: Múltiples ubicaciones estratégicas para mayor conveniencia.",
                "Guadalajara: Servicio completo en la Perla de Occidente.",
                "Monterrey: Presencia sólida en el norte del país.",
                "Entrega a domicilio disponible en todas las ciudades.",
                "Pruebas de manejo programadas según conveniencia del cliente.",
                "Red de talleres autorizados para servicio postventa.",
                "Nota: Esta información es de respaldo y podría no estar actualizada.",
            ],
            "lists": [
                "Entrega a domicilio disponible",
                "Prueba de manejo a domicilio",
                "Financiamiento en sitio",
                "Proceso 100% digital",
                "Servicio de intercambio",
                "Garantía extendida disponible",
            ],
            "metadata": {
                "description": "Ubicaciones y sedes de Kavak en las principales ciudades de México (Datos de respaldo)",
                "category": "locations",
                "source": "fallback_content",
                "last_updated": current_date,
                "is_fallback": True,
                "version": "1.0.0",
                "disclaimer": "Esta información es de respaldo y podría no estar actualizada. Verificar en el sitio oficial de Kavak para información actualizada.",
            },
        }
    ]

    logger.info(
        f"Created FALLBACK knowledge content with {len(comprehensive_content)} entries. "
        f"Last updated: {current_date}"
    )
    return comprehensive_content


def setup_kavak_knowledge_base():
    """
    Complete setup of Kavak knowledge base:
    1. Fetches data (scraped or fallback).
    2. Saves raw data to a JSON file (for reference/backup).
    3. Populates ChromaDB with this data.
    """
    logger.info("Starting Kavak Knowledge Base Setup...")

    knowledge_data_json_path = "data/kavak_knowledge.json"
    os.makedirs(os.path.dirname(knowledge_data_json_path), exist_ok=True)

    knowledge_entries: List[Dict] = []

    try:
        logger.info("Attempting to scrape live Kavak content...")
        scraper = KavakWebScraper()
        scraped_content = scraper.scrape_kavak_knowledge()

        if scraped_content and len(scraped_content) >= 1:
            logger.info(f"Successfully scraped {len(scraped_content)} pages.")
            knowledge_entries = scraped_content
        else:
            logger.warning(
                "Insufficient content scraped or scraper returned empty. Proceeding with fallback."
            )
            raise Exception("Insufficient content from scraper")

    except Exception as scraping_error:
        logger.warning(
            f"Scraping failed: {scraping_error}. Using comprehensive fallback content."
        )
        knowledge_entries = create_comprehensive_kavak_knowledge()

    # Save the obtained knowledge entries to a JSON file for reference
    try:
        with open(knowledge_data_json_path, "w", encoding="utf-8") as f:
            json.dump(knowledge_entries, f, ensure_ascii=False, indent=2)
        logger.info(f"Raw knowledge data saved to {knowledge_data_json_path}")
    except Exception as e:
        logger.error(f"Error saving raw knowledge data to JSON: {e}")

    if not knowledge_entries:
        logger.error(
            "No knowledge entries (neither scraped nor fallback) to load into ChromaDB. Aborting."
        )
        return

    logger.info("Setting up ChromaDB...")
    try:
        # First try to connect to ChromaDB via HTTP
        try:
            logger.info(
                f"Attempting to connect to ChromaDB at http://{settings.chroma.CHROMA_HOST}:{settings.chroma.CHROMA_PORT}"
            )
            client = chromadb.HttpClient(
                host=settings.chroma.CHROMA_HOST,
                port=settings.chroma.CHROMA_PORT
            )
            logger.info("Successfully connected to ChromaDB via HTTP")
        except Exception as http_error:
            logger.warning(
                f"Failed to connect to ChromaDB via HTTP: {http_error}. Falling back to persistent client."
            )
            # Fall back to persistent client
            chroma_persist_dir = settings.chroma.CHROMA_PERSIST_DIRECTORY
            os.makedirs(chroma_persist_dir, exist_ok=True)
            logger.info(
                f"Using persistent ChromaDB at: {os.path.abspath(chroma_persist_dir)}"
            )
            client = chromadb.PersistentClient(path=chroma_persist_dir)
            logger.info("ChromaDB persistent client initialized.")

        embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=settings.chroma.EMBEDDING_MODEL_NAME
        )
        logger.info(
            f"Embedding function initialized with model: {settings.chroma.EMBEDDING_MODEL_NAME}"
        )

        collection_name = settings.chroma.CHROMA_COLLECTION_NAME
        logger.info(f"Target collection: {collection_name}")

        # Delete collection if it exists to ensure a clean rebuild
        try:
            logger.info(f"Checking if collection '{collection_name}' exists...")
            existing_collections = client.list_collections()
            if any(c.name == collection_name for c in existing_collections):
                logger.warning(
                    f"Collection '{collection_name}' already exists. Deleting for a fresh build."
                )
                client.delete_collection(name=collection_name)
                logger.info(f"Collection '{collection_name}' deleted.")
            else:
                logger.info(
                    f"Collection '{collection_name}' does not exist. Will be created."
                )
        except Exception as e:
            logger.error(
                f"Error managing existing collection '{collection_name}': {e}. Attempting to create."
            )

        # Define collection metadata with useful information
        collection_metadata = {
            "hnsw:space": "cosine",
            "name": "Kavak Knowledge Base",
            "description": "Knowledge base containing Kavak's product and service information",
            "source": "kavak_knowledge_source.json",
            "embedding_model": embedding_func.__class__.__name__,
            "content_type": "product_info,faq,service_info"
        }

        collection = client.create_collection(
            name=collection_name,
            embedding_function=embedding_func,
            metadata=collection_metadata
        )
        logger.info(f"Collection '{collection_name}' created/recreated successfully.")

        documents_to_add = []
        metadatas_to_add = []
        ids_to_add = []

        logger.info(f"Processing {len(knowledge_entries)} entries for ChromaDB...")
        for i, item in enumerate(knowledge_entries):
            doc_text = item.get("main_content", "")
            if not doc_text.strip():
                logger.warning(
                    f"Skipping entry {i + 1} ('{item.get('title', 'N/A')}') due to empty main_content."
                )
                continue

            doc_metadata = item.get(
                "metadata", {}
            ).copy()  # Start with existing metadata
            doc_metadata["source_url"] = item.get("url", "N/A")
            doc_metadata["title"] = item.get("title", "N/A")
            # Ensure all metadata values are valid types for ChromaDB (str, int, float, bool)
            for key, value in doc_metadata.items():
                if not isinstance(value, (str, int, float, bool)):
                    doc_metadata[key] = str(value)

            doc_id = f"doc_{i + 1}"

            documents_to_add.append(doc_text)
            metadatas_to_add.append(doc_metadata)
            ids_to_add.append(doc_id)

        if documents_to_add:
            logger.info(
                f"Adding {len(documents_to_add)} documents to ChromaDB collection '{collection_name}'..."
            )
            collection.add(
                documents=documents_to_add, metadatas=metadatas_to_add, ids=ids_to_add
            )
            logger.info(
                f"Successfully added {collection.count()} documents to ChromaDB."
            )
        else:
            logger.warning(
                "No valid documents to add to ChromaDB after processing entries."
            )

        # Verification
        final_count = collection.count()
        logger.info(
            f"ChromaDB collection '{collection_name}' now contains {final_count} documents."
        )
        if final_count == 0 and len(knowledge_entries) > 0:
            logger.error(
                "CRITICAL: Knowledge entries were available, but 0 documents were loaded into ChromaDB!"
            )
        elif final_count > 0:
            logger.info("Kavak knowledge base successfully populated into ChromaDB!")
        else:
            logger.warning(
                "ChromaDB collection is empty. This might be expected if no source data was found."
            )

    except Exception as e:
        logger.error(f"An error occurred during ChromaDB setup: {e}", exc_info=True)
        logger.error("Kavak knowledge base setup FAILED.")


if __name__ == "__main__":
    logger.info("Executing Kavak Knowledge Base Setup Script...")
    setup_kavak_knowledge_base()
    logger.info("Kavak Knowledge Base Setup Script finished.")
