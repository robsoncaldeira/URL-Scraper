import pytest
import sys
from pathlib import Path

# Adicionar o diretório pai ao path para importações
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper import URLScraper
from config import Config
from utils import is_valid_url, clean_text, normalize_url


class TestConfig:
    """Testes para a classe Config"""
    
    def test_config_defaults(self):
        """Testa configurações padrão"""
        config = Config()
        assert config.TIMEOUT == 10
        assert config.MAX_RETRIES == 3
        assert config.USER_AGENT is not None
    
    def test_config_custom(self):
        """Testa configurações personalizadas"""
        config = Config(timeout=15, max_retries=5)
        assert config.TIMEOUT == 15
        assert config.MAX_RETRIES == 5
    
    def test_default_headers(self):
        """Testa headers padrão"""
        config = Config()
        assert 'User-Agent' in config.DEFAULT_HEADERS
        assert 'Accept' in config.DEFAULT_HEADERS


class TestURLScraper:
    """Testes para a classe URLScraper"""
    
    def test_scraper_init(self):
        """Testa inicialização do scraper"""
        scraper = URLScraper()
        assert scraper.session is not None
        assert scraper.config is not None
        scraper.close()
    
    def test_scraper_with_custom_config(self):
        """Testa scraper com configuração customizada"""
        config = Config(timeout=20)
        scraper = URLScraper(config)
        assert scraper.config.TIMEOUT == 20
        scraper.close()


class TestUtilFunctions:
    """Testes para funções utilitárias"""
    
    def test_is_valid_url_valid(self):
        """Testa validação de URL válida"""
        assert is_valid_url('https://example.com') is True
        assert is_valid_url('http://google.com') is True
    
    def test_is_valid_url_invalid(self):
        """Testa validação de URL inválida"""
        assert is_valid_url('not a url') is False
        assert is_valid_url('') is False
        assert is_valid_url('example.com') is False
    
    def test_clean_text(self):
        """Testa limpeza de texto"""
        assert clean_text('Hello   World') == 'Hello World'
        assert clean_text('  spaces  ') == 'spaces'
        assert clean_text('') is None
    
    def test_normalize_url(self):
        """Testa normalização de URL"""
        assert normalize_url('example.com').startswith('https://')
        assert normalize_url('https://example.com') == 'https://example.com'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
