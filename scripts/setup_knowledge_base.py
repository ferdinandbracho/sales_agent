"""
Enhanced Kavak Knowledge Setup
Configura la base de conocimiento completa con scraping y contenido de respaldo
"""

import asyncio
import json
import os
import logging
from typing import Dict, List
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_comprehensive_kavak_knowledge() -> List[Dict]:
    """
    Create comprehensive Kavak knowledge base
    Combines scraping attempts with rich fallback content
    """
    logger.info("🏗️ Creating comprehensive Kavak knowledge base...")

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

    logger.warning(
        f"Created FALLBACK knowledge base with {len(comprehensive_content)} entries. "
        f"Last updated: {current_date}"
    )
    return comprehensive_content


def setup_kavak_knowledge_base():
    """
    Complete setup of Kavak knowledge base
    Configura completamente la base de conocimiento
    """
    logger.info("Setting up Kavak Knowledge Base...")

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    try:
        # Try to run the scraper first
        logger.info("Attempting to scrape live Kavak content...")

        # Import and run scraper
        import sys

        sys.path.append("scripts")

        try:
            from scrape_kavak import KavakWebScraper

            scraper = KavakWebScraper()
            scraped_content = scraper.scrape_kavak_knowledge()

            if len(scraped_content) >= 1:
                logger.info(f"Successfully scraped {len(scraped_content)} pages")
                # Save scraped content
                with open("data/kavak_knowledge.json", "w", encoding="utf-8") as f:
                    json.dump(scraped_content, f, ensure_ascii=False, indent=2)

            else:
                raise Exception("Insufficient content scraped")

        except Exception as scraping_error:
            logger.warning(f"Scraping failed: {scraping_error}")
            raise scraping_error

    except Exception as e:
        # Fallback to comprehensive content
        logger.info("Using comprehensive fallback content...")

        comprehensive_content = create_comprehensive_kavak_knowledge()

        # Save comprehensive content
        with open("data/kavak_knowledge.json", "w", encoding="utf-8") as f:
            json.dump(comprehensive_content, f, ensure_ascii=False, indent=2)

        logger.info("Comprehensive Kavak knowledge base saved")

    # Verify the knowledge base
    try:
        with open("data/kavak_knowledge.json", "r", encoding="utf-8") as f:
            content = json.load(f)

        logger.info(f"Knowledge base verified: {len(content)} entries loaded")

        # Print summary
        print("\nKAVAK KNOWLEDGE BASE SUMMARY:")
        print("=" * 50)
        for item in content:
            title = item.get("title", "Sin título")[:50]
            category = item.get("metadata", {}).get("category", "general")
            content_length = len(item.get("main_content", ""))
            print(f"{title}")
            print(f"   Category: {category}")
            print(f"   Content: {content_length} characters")
            print()

        print("Kavak knowledge base ready for RAG!")

    except Exception as e:
        logger.error(f"Error verifying knowledge base: {e}")


if __name__ == "__main__":
    setup_kavak_knowledge_base()
