from urllib.parse import urljoin, urlparse
import re


def is_valid_url(url):
    """
    Valida se a URL é válida
    
    Args:
        url: URL para validar
        
    Returns:
        bool: True se válida, False caso contrário
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def normalize_url(url):
    """
    Normaliza a URL
    
    Args:
        url: URL para normalizar
        
    Returns:
        str: URL normalizada
    """
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url


def extract_domain(url):
    """
    Extrai o domínio da URL
    
    Args:
        url: URL para extrair domínio
        
    Returns:
        str: Domínio extraído
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None


def clean_text(text):
    """
    Remove espaços extra e normaliza texto
    
    Args:
        text: Texto para limpar
        
    Returns:
        str: Texto limpo
    """
    if not text:
        return None
    # Remove espaços em branco múltiplos
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def make_absolute_url(base_url, relative_url):
    """
    Converte URL relativa em absoluta
    
    Args:
        base_url: URL base
        relative_url: URL relativa
        
    Returns:
        str: URL absoluta
    """
    try:
        return urljoin(base_url, relative_url)
    except Exception:
        return relative_url
