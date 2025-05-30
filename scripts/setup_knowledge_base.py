"""
Enhanced Kavak Knowledge Setup
"""

import json
import os
import logging
from typing import Dict, List, Any
import datetime
import uuid

import chromadb
from chromadb.utils import embedding_functions
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config import settings
from scrape_kavak import (
    KavakWebScraper,
)  # Assuming this is in the same directory or PYTHONPATH

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _combine_text_fields(item: Dict) -> str:
    """Combines relevant text fields from a knowledge item for embedding."""
    parts = []
    if main_content := item.get("main_content", "").strip():
        parts.append(main_content)

    if headings := item.get("headings"):
        for h in headings:
            if h_text := str(h).strip():
                parts.append(f"\n## {h_text}")

    if paragraphs := item.get("paragraphs"):
        for p in paragraphs:
            if p_text := str(p).strip():
                parts.append(f"\n\n{p_text}")

    if lists := item.get("lists"):
        for l_item in lists:
            if l_text := str(l_item).strip():
                parts.append(f"\n- {l_text}")

    return "\n".join(parts).strip()


def _ensure_metadata_types(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Ensures all metadata values are ChromaDB compatible types (str, int, float, bool)."""
    compatible_metadata = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)):
            compatible_metadata[key] = value
        elif isinstance(value, (list, dict, tuple)):
            compatible_metadata[key] = json.dumps(
                value
            )  # Serialize complex types to JSON strings
        else:
            compatible_metadata[key] = str(value)
    return compatible_metadata


def create_comprehensive_kavak_knowledge() -> List[Dict]:
    """
    Create comprehensive Kavak knowledge base
    Combines scraping attempts with rich fallback content
    """
    logger.info("Creating comprehensive Kavak fallback knowledge content...")
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    fallback_notice = (
        "⚠️ IMPORTANTE: Esta es información de respaldo. "
        "No se pudo obtener la información más reciente del sitio web de Kavak. "
        f"Última actualización: {current_date}"
    )

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
            ],
            "paragraphs": [
                "Kavak revoluciona la experiencia de compra de autos seminuevos en México.",
                "Ciudad de México: Múltiples ubicaciones estratégicas para mayor conveniencia.",
            ],
            "lists": [
                "Entrega a domicilio disponible",
                "Prueba de manejo a domicilio",
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
    3. Combines text fields, chunks them, and populates ChromaDB.
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
            logger.warning("Insufficient content scraped. Using fallback.")
            knowledge_entries = create_comprehensive_kavak_knowledge()
    except Exception as scraping_error:
        logger.warning(f"Scraping failed: {scraping_error}. Using fallback content.")
        knowledge_entries = create_comprehensive_kavak_knowledge()

    try:
        with open(knowledge_data_json_path, "w", encoding="utf-8") as f:
            json.dump(knowledge_entries, f, ensure_ascii=False, indent=2)
        logger.info(f"Raw knowledge data saved to {knowledge_data_json_path}")
    except Exception as e:
        logger.error(f"Error saving raw knowledge data to JSON: {e}")

    if not knowledge_entries:
        logger.error("No knowledge entries to load. Aborting.")
        return

    logger.info("Setting up ChromaDB...")
    try:
        client = chromadb.HttpClient(
            host=settings.chroma.CHROMA_HOST, port=settings.chroma.CHROMA_PORT
        )
        client.heartbeat()  # Test connection
        logger.info(
            f"Connected to ChromaDB server at http://{settings.chroma.CHROMA_HOST}:{settings.chroma.CHROMA_PORT}"
        )
    except Exception as http_error:
        logger.error(
            f"Failed to connect to ChromaDB HTTP server: {http_error}. Ensure it's running."
        )
        # Fallback to persistent client if HTTP fails
        chroma_persist_dir = settings.chroma.CHROMA_PERSIST_DIRECTORY
        os.makedirs(chroma_persist_dir, exist_ok=True)
        client = chromadb.PersistentClient(path=chroma_persist_dir)
        logger.info(
            f"Using persistent ChromaDB at: {os.path.abspath(chroma_persist_dir)}"
        )

    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=settings.chroma.EMBEDDING_MODEL_NAME
    )
    logger.info(f"Embedding model: {settings.chroma.EMBEDDING_MODEL_NAME}")

    collection_name = settings.chroma.CHROMA_COLLECTION_NAME
    try:
        if any(c.name == collection_name for c in client.list_collections()):
            logger.warning(
                f"Collection '{collection_name}' exists. Deleting for fresh build."
            )
            client.delete_collection(name=collection_name)
        collection = client.create_collection(
            name=collection_name,
            embedding_function=embedding_func,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"Collection '{collection_name}' created/recreated.")
    except Exception as e:
        logger.error(
            f"Error managing collection '{collection_name}': {e}", exc_info=True
        )
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )

    all_chunk_docs = []
    all_chunk_metadatas = []
    all_chunk_ids = []

    logger.info(
        f"Processing {len(knowledge_entries)} entries for chunking and embedding..."
    )
    for i, item in enumerate(knowledge_entries):
        combined_text = _combine_text_fields(item)
        if not combined_text:
            logger.warning(
                f"Skipping entry {i + 1} ('{item.get('title', 'N/A')}') due to empty combined text."
            )
            continue

        chunks = text_splitter.split_text(combined_text)
        original_doc_id = item.get("id", str(uuid.uuid4()))

        for chunk_idx, chunk_text in enumerate(chunks):
            chunk_id = f"doc_{original_doc_id}_chunk_{chunk_idx}"

            chunk_metadata = item.get("metadata", {}).copy()
            chunk_metadata["original_title"] = item.get("title", "N/A")
            chunk_metadata["original_url"] = item.get("url", "N/A")
            chunk_metadata["original_doc_id"] = original_doc_id
            chunk_metadata["chunk_number"] = chunk_idx + 1
            chunk_metadata["total_chunks_in_doc"] = len(chunks)

            all_chunk_docs.append(chunk_text)
            all_chunk_metadatas.append(_ensure_metadata_types(chunk_metadata))
            all_chunk_ids.append(chunk_id)

    if all_chunk_docs:
        logger.info(
            f"Adding {len(all_chunk_docs)} text chunks to ChromaDB collection '{collection_name}'..."
        )
        # Using large list, but can use batch_size if needed.
        collection.add(
            documents=all_chunk_docs, metadatas=all_chunk_metadatas, ids=all_chunk_ids
        )
        logger.info(f"Successfully added {collection.count()} chunks to ChromaDB.")
    else:
        logger.warning("No valid text chunks to add to ChromaDB.")

    final_count = collection.count()
    logger.info(
        f"ChromaDB collection '{collection_name}' now contains {final_count} chunks."
    )
    if final_count == 0 and len(knowledge_entries) > 0:
        logger.error(
            "CRITICAL: Entries were available, but 0 chunks loaded! Check processing."
        )
    elif final_count > 0:
        logger.info("Kavak knowledge base (chunked) successfully populated!")
    else:
        logger.warning(
            "ChromaDB collection is empty. This might be expected if no source data was found or processed into chunks."
        )


if __name__ == "__main__":
    logger.info("Executing Kavak Knowledge Base Setup Script (with chunking)...")
    setup_kavak_knowledge_base()
    logger.info("Kavak Knowledge Base Setup Script finished.")
