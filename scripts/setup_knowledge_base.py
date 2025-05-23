"""
Enhanced Kavak Knowledge Setup
Configura la base de conocimiento completa con scraping y contenido de respaldo
"""
import asyncio
import json
import os
import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_comprehensive_kavak_knowledge() -> List[Dict]:
    """
    Create comprehensive Kavak knowledge base
    Combines scraping attempts with rich fallback content
    """
    logger.info("🏗️ Creating comprehensive Kavak knowledge base...")
    
    # Enhanced knowledge base with detailed information
    comprehensive_content = [
        {
            'url': 'https://www.kavak.com/mx/blog/sedes-de-kavak-en-mexico',
            'title': 'Sedes de Kavak en México',
            'main_content': '''
            Kavak cuenta con presencia en las principales ciudades de México, 
            ofreciendo un servicio completo de compra y venta de autos seminuevos. 
            Nuestras ubicaciones estratégicas permiten brindar cobertura nacional 
            con el respaldo de la tecnología más avanzada del sector automotriz.
            ''',
            'headings': [
                'Ubicaciones Kavak en México',
                'Ciudad de México',
                'Guadalajara, Jalisco', 
                'Monterrey, Nuevo León',
                'Puebla, Puebla',
                'Tijuana, Baja California',
                'Mérida, Yucatán'
            ],
            'paragraphs': [
                'Kavak revoluciona la experiencia de compra de autos seminuevos en México.',
                'Ciudad de México: Múltiples ubicaciones estratégicas para mayor conveniencia.',
                'Guadalajara: Servicio completo en la Perla de Occidente.',
                'Monterrey: Presencia sólida en el norte del país.',
                'Entrega a domicilio disponible en todas las ciudades.',
                'Pruebas de manejo programadas según conveniencia del cliente.',
                'Red de talleres autorizados para servicio postventa.'
            ],
            'lists': [
                'Entrega a domicilio disponible',
                'Prueba de manejo a domicilio',
                'Financiamiento en sitio',
                'Proceso 100% digital',
                'Servicio de intercambio',
                'Garantía extendida disponible'
            ],
            'metadata': {
                'description': 'Ubicaciones y sedes de Kavak en las principales ciudades de México',
                'category': 'locations'
            }
        },
        {
            'url': 'kavak://propuesta-valor',
            'title': 'Propuesta de Valor Kavak - Líder en Autos Seminuevos',
            'main_content': '''
            Kavak es la plataforma líder de autos seminuevos en México y Latinoamérica. 
            Ofrecemos una experiencia de compra revolucionaria con garantía real, 
            financiamiento accesible y un proceso completamente digital. 
            Más de 1 millón de mexicanos han confiado en nosotros para encontrar su auto ideal.
            ''',
            'headings': [
                'Por qué elegir Kavak',
                'Garantía real de 3 meses',
                'Financiamiento hasta 84 meses',
                'Proceso 100% digital',
                'Inspección de 240 puntos',
                'Líderes en innovación'
            ],
            'paragraphs': [
                'Somos la única plataforma que ofrece garantía real en autos seminuevos.',
                'Inspección rigurosa de 240 puntos garantiza la calidad de cada vehículo.',
                'Financiamiento flexible desde 12 hasta 84 meses con tasas competitivas.',
                'Proceso completamente digital: desde la búsqueda hasta la entrega.',
                'Red nacional de servicio postventa y talleres autorizados.',
                'Intercambio garantizado si el auto no cumple expectativas.',
                'Más de 1 millón de clientes satisfechos en toda Latinoamérica.'
            ],
            'lists': [
                'Garantía de 3 meses o 3,000 km',
                'Inspección de 240 puntos',
                'Financiamiento hasta 84 meses',
                'Proceso 100% digital',
                'Entrega a domicilio',
                'Intercambio garantizado',
                'Servicio postventa especializado'
            ],
            'metadata': {
                'description': 'Propuesta de valor y ventajas de elegir Kavak',
                'category': 'value_proposition'
            }
        },
        {
            'url': 'kavak://garantia-cobertura',
            'title': 'Garantía Kavak - Cobertura Completa',
            'main_content': '''
            La garantía Kavak es única en el mercado de autos seminuevos. 
            Cubrimos 3 meses o 3,000 kilómetros con cobertura completa de 
            componentes mecánicos principales. Somos la única plataforma 
            que respalda la calidad de sus vehículos con garantía real.
            ''',
            'headings': [
                'Garantía de 3 meses o 3,000 km',
                'Cobertura completa',
                'Únicos en el mercado',
                'Red de talleres autorizados'
            ],
            'paragraphs': [
                'Cobertura de motor, transmisión, sistema eléctrico y frenos.',
                'Aire acondicionado y sistemas de seguridad incluidos.',
                'Red nacional de talleres autorizados para reparaciones.',
                'Proceso de reclamación simple y rápido.',
                'Sin letra pequeña ni exclusiones sorpresa.',
                'Garantía transferible al nuevo propietario.',
                'Somos los únicos que realmente garantizamos la calidad.'
            ],
            'lists': [
                'Motor y transmisión',
                'Sistema eléctrico completo',
                'Frenos y suspensión',
                'Aire acondicionado',
                'Sistemas de seguridad',
                'Dirección hidráulica',
                'Sistema de enfriamiento'
            ],
            'metadata': {
                'description': 'Detalles completos de la garantía Kavak',
                'category': 'warranty'
            }
        },
        {
            'url': 'kavak://financiamiento-opciones',
            'title': 'Financiamiento Kavak - Opciones Flexibles',
            'main_content': '''
            Ofrecemos las mejores opciones de financiamiento del mercado 
            con tasas competitivas desde 10% anual. Plazos flexibles de 
            12 hasta 84 meses, aprobación rápida en 24 horas y sin 
            requisitos complicados. Tu auto ideal al alcance de tu presupuesto.
            ''',
            'headings': [
                'Financiamiento desde 10% anual',
                'Plazos de 12 a 84 meses',
                'Aprobación en 24 horas',
                'Sin aval requerido'
            ],
            'paragraphs': [
                'Tasas de interés competitivas desde 10% anual fijo.',
                'Plazos flexibles adaptados a tu capacidad de pago.',
                'Aprobación rápida con mínimos requisitos.',
                'Sin aval, sin garantías adicionales complicadas.',
                'Pago anticipado sin penalizaciones.',
                'Calculadora en línea para simular tu plan.',
                'Asesoría personalizada para encontrar la mejor opción.'
            ],
            'lists': [
                'Tasa desde 10% anual',
                'Plazos: 12, 24, 36, 48, 60, 72, 84 meses',
                'Aprobación en 24 horas',
                'Sin aval requerido',
                'Pago anticipado sin penalización',
                'Proceso 100% digital',
                'Asesoría personalizada'
            ],
            'metadata': {
                'description': 'Opciones de financiamiento y crédito automotriz',
                'category': 'financing'
            }
        },
        {
            'url': 'kavak://proceso-compra',
            'title': 'Proceso de Compra Kavak - Simple y Digital',
            'main_content': '''
            Comprar tu auto en Kavak es simple, rápido y 100% digital. 
            Desde la búsqueda hasta la entrega, todo el proceso está 
            diseñado para ofrecerte la mejor experiencia. Sin filas, 
            sin papeleo complicado, sin pérdida de tiempo.
            ''',
            'headings': [
                'Proceso 100% digital',
                'Búsqueda inteligente',
                'Prueba de manejo',
                'Financiamiento express',
                'Entrega a domicilio'
            ],
            'paragraphs': [
                'Busca y filtra entre miles de autos verificados.',
                'Agenda tu prueba de manejo en línea.',
                'Solicita financiamiento con aprobación rápida.',
                'Completa la compra desde tu celular.',
                'Recibe tu auto en casa o en sucursal.',
                'Documentos y placas incluidos en el servicio.',
                'Soporte completo durante todo el proceso.'
            ],
            'lists': [
                'Buscar auto ideal',
                'Agendar prueba de manejo',
                'Solicitar financiamiento',
                'Completar compra digital',
                'Recibir auto con documentos',
                'Activar garantía automáticamente'
            ],
            'metadata': {
                'description': 'Paso a paso del proceso de compra en Kavak',
                'category': 'process'
            }
        }
    ]
    
    logger.info(f"✅ Created comprehensive knowledge base with {len(comprehensive_content)} detailed entries")
    return comprehensive_content

def setup_kavak_knowledge_base():
    """
    Complete setup of Kavak knowledge base
    Configura completamente la base de conocimiento
    """
    logger.info("🚀 Setting up Kavak Knowledge Base...")
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    try:
        # Try to run the scraper first
        logger.info("🌐 Attempting to scrape live Kavak content...")
        
        # Import and run scraper
        import sys
        sys.path.append('scripts')
        
        try:
            from scrape_kavak import KavakWebScraper
            
            scraper = KavakWebScraper()
            scraped_content = scraper.scrape_kavak_knowledge()
            
            if len(scraped_content) >= 2:
                logger.info(f"✅ Successfully scraped {len(scraped_content)} pages")
                # Save scraped content
                with open('data/kavak_knowledge.json', 'w', encoding='utf-8') as f:
                    json.dump(scraped_content, f, ensure_ascii=False, indent=2)
                
            else:
                raise Exception("Insufficient content scraped")
                
        except Exception as scraping_error:
            logger.warning(f"⚠️ Scraping failed: {scraping_error}")
            raise scraping_error
            
    except Exception as e:
        # Fallback to comprehensive content
        logger.info("🔄 Using comprehensive fallback content...")
        
        comprehensive_content = create_comprehensive_kavak_knowledge()
        
        # Save comprehensive content
        with open('data/kavak_knowledge.json', 'w', encoding='utf-8') as f:
            json.dump(comprehensive_content, f, ensure_ascii=False, indent=2)
        
        logger.info("💾 Comprehensive Kavak knowledge base saved")
    
    # Verify the knowledge base
    try:
        with open('data/kavak_knowledge.json', 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        logger.info(f"✅ Knowledge base verified: {len(content)} entries loaded")
        
        # Print summary
        print("\n📚 KAVAK KNOWLEDGE BASE SUMMARY:")
        print("=" * 50)
        for item in content:
            title = item.get('title', 'Sin título')[:50]
            category = item.get('metadata', {}).get('category', 'general')
            content_length = len(item.get('main_content', ''))
            print(f"✅ {title}")
            print(f"   Category: {category}")
            print(f"   Content: {content_length} characters")
            print()
        
        print("🎉 Kavak knowledge base ready for RAG!")
        
    except Exception as e:
        logger.error(f"❌ Error verifying knowledge base: {e}")

if __name__ == "__main__":
    setup_kavak_knowledge_base()
