"""
Kavak Website Scraper
Extrae información del sitio web de Kavak para la base de conocimiento del agente
"""
import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KavakWebScraper:
    """
    Scraper for Kavak website content
    Extrae contenido del sitio web de Kavak para crear base de conocimiento
    """
    
    def __init__(self):
        self.base_url = "https://www.kavak.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.scraped_content = []
        
    def scrape_kavak_knowledge(self) -> List[Dict]:
        """
        Scrape Kavak website for knowledge base content
        
        Returns:
            List of content dictionaries with structured information
        """
        
        # URLs to scrape for Kavak information
        urls_to_scrape = [
            "https://www.kavak.com/mx/blog/sedes-de-kavak-en-mexico",  # Provided URL
        ]
        
        logger.info("🌐 Starting Kavak website scraping...")
        
        for url in urls_to_scrape:
            try:
                logger.info(f"📄 Scraping: {url}")
                content = self.scrape_single_page(url)
                if content:
                    self.scraped_content.append(content)
                    logger.info(f"✅ Successfully scraped: {content['title'][:50]}...")
                else:
                    logger.warning(f"⚠️ No content extracted from: {url}")
                
                # Be respectful to the server
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Error scraping {url}: {e}")
                # Continue with other URLs even if one fails
                continue
        
        logger.info(f"🎉 Scraping completed. Extracted content from {len(self.scraped_content)} pages")
        return self.scraped_content
    
    def scrape_single_page(self, url: str) -> Optional[Dict]:
        """
        Scrape content from a single page
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary with structured content or None if failed
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'iframe', 'noscript']):
                element.decompose()
            
            # Extract structured content
            content = {
                'url': url,
                'title': self.extract_title(soup),
                'main_content': self.extract_main_content(soup),
                'headings': self.extract_headings(soup),
                'paragraphs': self.extract_paragraphs(soup),
                'lists': self.extract_lists(soup),
                'metadata': self.extract_metadata(soup)
            }
            
            return content
            
        except requests.RequestException as e:
            logger.error(f"Network error scraping {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            return None
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Fallback to h1
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return "Sin título"
    
    def extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content text"""
        # Try to find main content area
        main_selectors = [
            'main',
            'article', 
            '.content',
            '.main-content',
            '.post-content',
            '.entry-content',
            '#content'
        ]
        
        for selector in main_selectors:
            main_element = soup.select_one(selector)
            if main_element:
                return main_element.get_text(separator=' ', strip=True)
        
        # Fallback to body content
        body = soup.find('body')
        if body:
            return body.get_text(separator=' ', strip=True)
        
        return soup.get_text(separator=' ', strip=True)
    
    def extract_headings(self, soup: BeautifulSoup) -> List[str]:
        """Extract all headings (h1-h6)"""
        headings = []
        for level in range(1, 7):
            for heading in soup.find_all(f'h{level}'):
                text = heading.get_text().strip()
                if text and len(text) > 3:  # Filter out very short headings
                    headings.append(text)
        return headings
    
    def extract_paragraphs(self, soup: BeautifulSoup) -> List[str]:
        """Extract paragraph content"""
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if text and len(text) > 20:  # Filter out very short paragraphs
                paragraphs.append(text)
        return paragraphs
    
    def extract_lists(self, soup: BeautifulSoup) -> List[str]:
        """Extract list items"""
        lists = []
        for ul in soup.find_all(['ul', 'ol']):
            items = [li.get_text().strip() for li in ul.find_all('li')]
            if items:
                lists.extend(items)
        return lists
    
    def extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract metadata from the page"""
        metadata = {}
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata['description'] = meta_desc.get('content', '')
        
        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            metadata['keywords'] = meta_keywords.get('content', '')
        
        # Open Graph data
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title:
            metadata['og_title'] = og_title.get('content', '')
        
        return metadata
    
    def save_content(self, filename: str = 'data/kavak_knowledge.json') -> None:
        """
        Save scraped content to JSON file
        
        Args:
            filename: Output filename
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_content, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Saved {len(self.scraped_content)} pages to {filename}")
            
        except Exception as e:
            logger.error(f"❌ Error saving content: {e}")
    
    def create_fallback_content(self) -> List[Dict]:
        """
        Create fallback content if scraping fails
        Based on known Kavak information
        """
        logger.info("📋 Creating fallback Kavak knowledge base...")
        
        fallback_content = [
            {
                'url': 'fallback://kavak-value-proposition',
                'title': 'Propuesta de Valor de Kavak',
                'main_content': '''
                Kavak es la plataforma líder de autos seminuevos en México y Latinoamérica. 
                Ofrecemos una experiencia de compra 100% digital con garantía real y 
                financiamiento accesible. Nuestro proceso incluye inspección de 240 puntos, 
                garantía de 3 meses o 3,000 km, y financiamiento hasta 84 meses.
                ''',
                'headings': [
                    'Kavak - Plataforma Líder de Autos Seminuevos',
                    'Garantía Real',
                    'Financiamiento Accesible',
                    'Proceso 100% Digital'
                ],
                'paragraphs': [
                    'Kavak revoluciona la compra y venta de autos seminuevos en México.',
                    'Ofrecemos garantía de 3 meses o 3,000 kilómetros en todos nuestros vehículos.',
                    'Financiamiento disponible hasta 84 meses con tasas competitivas.',
                    'Proceso completamente digital desde la búsqueda hasta la entrega.'
                ],
                'metadata': {'source': 'fallback', 'category': 'value_proposition'}
            },
            {
                'url': 'fallback://kavak-locations',
                'title': 'Sedes de Kavak en México',
                'main_content': '''
                Kavak cuenta con presencia en las principales ciudades de México incluyendo
                Ciudad de México, Guadalajara, Monterrey, Puebla, Tijuana y Mérida.
                Ofrecemos entrega a domicilio y servicio de prueba de manejo.
                ''',
                'headings': [
                    'Ubicaciones Kavak en México',
                    'Ciudad de México',
                    'Guadalajara',
                    'Monterrey'
                ],
                'paragraphs': [
                    'Kavak tiene presencia en las principales ciudades mexicanas.',
                    'Multiple ubicaciones en Ciudad de México para mayor conveniencia.',
                    'Servicio de entrega a domicilio disponible.',
                    'Pruebas de manejo programadas en ubicación del cliente.'
                ],
                'metadata': {'source': 'fallback', 'category': 'locations'}
            },
            {
                'url': 'fallback://kavak-warranty',
                'title': 'Garantía Kavak',
                'main_content': '''
                Todos los autos Kavak incluyen garantía de 3 meses o 3,000 kilómetros.
                Cobertura incluye motor, transmisión, sistema eléctrico, frenos y aire acondicionado.
                Somos la única plataforma que ofrece garantía real en autos seminuevos.
                ''',
                'headings': [
                    'Garantía de 3 Meses o 3,000 KM',
                    'Cobertura Completa',
                    'Única en el Mercado'
                ],
                'paragraphs': [
                    'Garantía de 3 meses o 3,000 kilómetros lo que ocurra primero.',
                    'Cobertura de motor, transmisión, sistema eléctrico y frenos.',
                    'Somos la única plataforma con garantía real en seminuevos.',
                    'Red de talleres autorizados en todo México.'
                ],
                'metadata': {'source': 'fallback', 'category': 'warranty'}
            }
        ]
        
        return fallback_content

def main():
    """Main function to run the scraper"""
    scraper = KavakWebScraper()
    
    try:
        # Attempt to scrape live content
        content = scraper.scrape_kavak_knowledge()
        
        # If scraping failed or returned minimal content, use fallback
        if len(content) < 2:
            logger.warning("⚠️ Limited content scraped, adding fallback content...")
            fallback_content = scraper.create_fallback_content()
            content.extend(fallback_content)
            scraper.scraped_content = content
        
        # Save the content
        scraper.save_content()
        
        # Print summary
        print("\n📊 SCRAPING SUMMARY:")
        print("=" * 50)
        for item in content:
            print(f"✅ {item['title']}")
            print(f"   URL: {item['url']}")
            print(f"   Content length: {len(item['main_content'])} characters")
            print()
        
        print(f"🎉 Successfully created Kavak knowledge base with {len(content)} entries!")
        print("💾 Content saved to: data/kavak_knowledge.json")
        
    except Exception as e:
        logger.error(f"❌ Scraping failed: {e}")
        
        # Create fallback content as last resort
        logger.info("🔄 Creating fallback knowledge base...")
        fallback_content = scraper.create_fallback_content()
        scraper.scraped_content = fallback_content
        scraper.save_content()
        
        print("⚠️ Used fallback content due to scraping issues")
        print("💾 Fallback knowledge base saved to: data/kavak_knowledge.json")

if __name__ == "__main__":
    main()
