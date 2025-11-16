import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configurações do scraper"""
    
    # Timeout para requisições (segundos)
    TIMEOUT = int(os.getenv('SCRAPER_TIMEOUT', 10))
    
    # Número máximo de tentativas
    MAX_RETRIES = int(os.getenv('SCRAPER_MAX_RETRIES', 3))
    
    # User-Agent para as requisições
    USER_AGENT = os.getenv(
        'SCRAPER_USER_AGENT',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    
    # Nível de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Headers padrão
    DEFAULT_HEADERS = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    def __init__(self, timeout=None, max_retries=None, user_agent=None):
        """
        Inicializa configurações personalizadas
        
        Args:
            timeout: Timeout para requisições em segundos
            max_retries: Número máximo de tentativas
            user_agent: User-Agent customizado
        """
        if timeout is not None:
            self.TIMEOUT = timeout
        if max_retries is not None:
            self.MAX_RETRIES = max_retries
        if user_agent is not None:
            self.USER_AGENT = user_agent
            self.DEFAULT_HEADERS['User-Agent'] = user_agent
