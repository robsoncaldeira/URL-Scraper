import logging
import sys
from config import Config

# Configurar o logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(getattr(logging, Config.LOG_LEVEL, logging.INFO))


def get_logger(name):
    """
    Obtém um logger configurado
    
    Args:
        name: Nome do logger
        
    Returns:
        Logger configurado
    """
    log = logging.getLogger(name)
    log.setLevel(getattr(logging, Config.LOG_LEVEL, logging.INFO))
    return log
