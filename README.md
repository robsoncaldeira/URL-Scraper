# URL Scraper

Um web scraper robusto e eficiente para extrair dados de URLs.

## Características

- ✅ Scraping de múltiplas URLs
- ✅ Extração de títulos, descrições e links
- ✅ Tratamento de erros robusto
- ✅ Logging detalhado
- ✅ Suporte a variáveis de ambiente
- ✅ Testes unitários
- ✅ Cache de requisições

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

### Básico

```python
from scraper import URLScraper

scraper = URLScraper()
result = scraper.scrape('https://example.com')
print(result)
```

### Com configurações personalizadas

```python
from scraper import URLScraper
from config import Config

config = Config(timeout=15, max_retries=3)
scraper = URLScraper(config)
result = scraper.scrape('https://example.com')
```

### Scraping de múltiplas URLs

```python
from scraper import URLScraper

scraper = URLScraper()
urls = [
    'https://example.com',
    'https://google.com',
    'https://github.com'
]

for url in urls:
    result = scraper.scrape(url)
    if result:
        print(f"URL: {url}")
        print(f"Título: {result['title']}")
```

## Estrutura do Projeto

```
url-scraper/
├── scraper.py           # Classe principal do scraper
├── config.py            # Configurações
├── logger.py            # Setup de logging
├── utils.py             # Funções utilitárias
├── requirements.txt     # Dependências
├── .env.example         # Exemplo de variáveis de ambiente
├── tests/
│   ├── __init__.py
│   ├── test_scraper.py
│   └── test_utils.py
└── README.md            # Este arquivo
```

## Testes

```bash
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html
```

## Variáveis de Ambiente

Crie um arquivo `.env` baseado em `.env.example`:

```
SCRAPER_TIMEOUT=10
SCRAPER_MAX_RETRIES=3
SCRAPER_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
LOG_LEVEL=INFO
```

## Licença

MIT
