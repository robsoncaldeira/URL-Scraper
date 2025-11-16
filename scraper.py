import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from logger import get_logger
from config import Config
from utils import is_valid_url, clean_text, make_absolute_url


class URLScraper:
    """Classe principal para web scraping"""
    
    def __init__(self, config=None):
        """
        Inicializa o scraper
        
        Args:
            config: Objeto de configuração (Config)
        """
        self.config = config or Config()
        self.logger = get_logger(__name__)
        self.session = self._create_session()
    
    def _create_session(self):
        """
        Cria uma sessão com retry automático
        
        Returns:
            requests.Session: Sessão configurada
        """
        session = requests.Session()
        
        # Configurar retry strategy
        # `method_whitelist` foi depreciado em urllib3; usar `allowed_methods`.
        # Usar frozenset para compatibilidade com versões que esperam um set.
        retry_strategy = Retry(
            total=self.config.MAX_RETRIES,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset(["HEAD", "GET", "OPTIONS"]),
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def scrape(self, url):
        """
        Faz scraping de uma URL
        
        Args:
            url: URL para fazer scraping
            
        Returns:
            dict: Dados extraídos da página
        """
        # Validar URL
        if not is_valid_url(url):
            self.logger.error(f"URL inválida: {url}")
            return None
        
        try:
            self.logger.info(f"Iniciando scraping de: {url}")
            
            # Fazer requisição
            response = self.session.get(
                url,
                headers=self.config.DEFAULT_HEADERS,
                timeout=self.config.TIMEOUT
            )
            response.raise_for_status()
            
            # Parser HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair dados
            data = {
                'url': url,
                'status_code': response.status_code,
                'title': self._extract_title(soup),
                'description': self._extract_description(soup),
                'links': self._extract_links(soup, url),
                'images': self._extract_images(soup),
                'headings': self._extract_headings(soup),
                'content': self._extract_content(soup)
            }
            
            self.logger.info(f"Scraping concluído com sucesso: {url}")
            return data
            
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout ao acessar {url}")
            return None
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Erro de conexão ao acessar {url}")
            return None
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"Erro HTTP {response.status_code} para {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Erro ao fazer scraping de {url}: {e}")
            return None
    
    def _extract_title(self, soup):
        """Extrai o título da página"""
        title_tag = soup.find('title')
        if title_tag:
            return clean_text(title_tag.get_text())
        
        h1_tag = soup.find('h1')
        if h1_tag:
            return clean_text(h1_tag.get_text())
        
        return None
    
    def _extract_description(self, soup):
        """Extrai a descrição da página"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return clean_text(meta_desc.get('content'))
        
        # Tentar open graph
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return clean_text(og_desc.get('content'))
        
        return None
    
    def _extract_links(self, soup, base_url, limit=20):
        """
        Extrai links da página
        
        Args:
            soup: BeautifulSoup object
            base_url: URL base para converter links relativos
            limit: Limite de links a extrair
            
        Returns:
            list: Lista de links únicos
        """
        links = set()
        for link in soup.find_all('a', href=True)[:limit]:
            href = link.get('href')
            if href:
                absolute_url = make_absolute_url(base_url, href)
                if is_valid_url(absolute_url):
                    links.add(absolute_url)
        
        return list(links)
    
    def _extract_images(self, soup, limit=10):
        """
        Extrai imagens da página
        
        Args:
            soup: BeautifulSoup object
            limit: Limite de imagens a extrair
            
        Returns:
            list: Lista de URLs de imagens
        """
        images = []
        for img in soup.find_all('img')[:limit]:
            src = img.get('src')
            alt = img.get('alt', '')
            if src:
                images.append({
                    'src': src,
                    'alt': clean_text(alt) or 'Sem descrição'
                })
        
        return images
    
    def _extract_headings(self, soup):
        """
        Extrai headings da página
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            dict: Headings organizados por nível
        """
        headings = {
            'h1': [],
            'h2': [],
            'h3': []
        }
        
        for level in headings.keys():
            for tag in soup.find_all(level):
                text = clean_text(tag.get_text())
                if text:
                    headings[level].append(text)
        
        return headings
    
    def _extract_content(self, soup):
        """
        Extrai conteúdo principal da página
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            str: Conteúdo extraído
        """
        # Remover scripts e styles
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Tentar encontrar artigo principal
        main_content = soup.find('main') or soup.find('article')
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            text = main_content.get_text()
            return clean_text(text)[:500]  # Primeiros 500 caracteres
        
        return None
    
    def close(self):
        """Fecha a sessão"""
        self.session.close()
        self.logger.info("Sessão fechada")
