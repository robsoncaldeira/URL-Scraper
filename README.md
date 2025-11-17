# URL Scraper

Um web scraper robusto e eficiente para extrair dados de URLs com suporte a múltiplos modos de operação, crawling com profundidade, respeito a `robots.txt` e persistência em SQLite.

## Características

- ✅ **3 Modos de operação**: Seed (URLs manuais), Keywords (descoberta via Bing), Hybrid (combinado)
- ✅ **Crawling inteligente**: Seguir links até profundidade configurável com delay entre requisições
- ✅ **Respeito a robots.txt**: Verificação automática antes de cada requisição
- ✅ **Persistência em SQLite**: Armazenamento com deduplicação automática por URL
- ✅ **Exportação de dados**: JSON e consultas via CLI
- ✅ **Extração rica**: Títulos, descrições, links, imagens, headings, conteúdo
- ✅ **Tratamento robusto**: Retry strategy, timeout, logging detalhado
- ✅ **Testes unitários**: 9 testes com cobertura completa
- ✅ **CI/CD automático**: GitHub Actions com Python 3.10
- ✅ **Scripts de automação**: PowerShell e Batch para fácil execução

## Instalação

```bash
# Clone o repositório
git clone https://github.com/robsoncaldeira/URL-Scraper.git
cd URL-Scraper

# Crie um virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instale dependências
pip install -r requirements.txt
```

## Uso Rápido

### 1️⃣ Modo Seed (URLs manuais)

Crie `urls.txt`:
```
https://www.python.org
https://github.com
https://stackoverflow.com
```

Execute:
```bash
python cli.py --mode seed --urls urls.txt --delay 2 --output results.json

# Ou com SQLite:
python cli.py --mode seed --urls urls.txt --db sqlite --output scraper_results.json
```

### 2️⃣ Modo com Crawling (URLs + Seguir links)

```bash
# Raspar URLs iniciais e seguir links até profundidade 1
python cli.py --mode seed --urls urls.txt --follow-depth 1 --delay 2 --output results.json

# Com SQLite (recomendado para grandes volumes):
python cli.py --mode seed --urls urls.txt --follow-depth 1 --db sqlite --output results.json
```

### 3️⃣ Modo Keywords (com Bing API - opcional)

Crie `keywords.txt`:
```
python programming
web scraping
github repositories
```

Configure a chave de API:
```powershell
$env:BING_API_KEY = "sua_chave_aqui"
```

Execute:
```bash
python cli.py --mode keywords --keywords keywords.txt --use-bing --db sqlite --output results.json
```

### 🤖 Automação com Scripts

**PowerShell (recomendado):**
```powershell
# Seed mode
.\run_scraper.ps1 -Mode seed -Delay 2

# Com profundidade 1
.\run_scraper.ps1 -Mode seed -FollowDepth 1 -Delay 2

# Com keywords e Bing
.\run_scraper.ps1 -Mode hybrid -UseBing -Delay 2
```

**Batch (Windows):**
```batch
run_scraper.bat seed
run_scraper.bat hybrid 1 2.0
```

## Consultar Dados (SQLite)

Após salvar em banco de dados, use `query_db.py`:

```bash
# Ver estatísticas
python query_db.py --db scraper_results.db --stats

# Listar URLs únicas
python query_db.py --db scraper_results.db --list-urls

# Listar resultados (tabela formatada)
python query_db.py --db scraper_results.db --list-results --limit 50

# Filtrar por intervalo de datas
python query_db.py --db scraper_results.db --by-date 2025-11-01 2025-11-30

# Exportar para JSON
python query_db.py --db scraper_results.db --export results_completo.json

# Limpar resultados com mais de 30 dias
python query_db.py --db scraper_results.db --clear-old 30
```

## Estrutura do Projeto

```
URL-Scraper/
├── scraper.py              # Classe principal do scraper
├── config.py               # Configurações
├── logger.py               # Setup de logging
├── utils.py                # Funções utilitárias
├── db.py                   # Persistência SQLite
├── cli.py                  # Interface de linha de comando
├── query_db.py             # Ferramenta de consulta de dados
├── requirements.txt        # Dependências Python
├── .env.example            # Exemplo de variáveis de ambiente
├── urls.txt                # URLs seed (exemplo)
├── keywords.txt            # Keywords para descoberta (exemplo)
├── run_scraper.ps1         # Automação PowerShell
├── run_scraper.bat         # Automação Batch
├── .github/workflows/
│   └── ci.yml              # Pipeline CI/CD (GitHub Actions)
├── tests/
│   ├── __init__.py
│   └── test_scraper.py     # Suite de testes (9 testes)
└── README.md               # Este arquivo
```

## Testes

```bash
# Rodar todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=. --cov-report=html

# Teste específico
pytest tests/test_scraper.py::TestURLScraper -v
```

**Status atual:** ✅ 9/9 testes passando

## Variáveis de Ambiente

Crie `.env` baseado em `.env.example`:

```env
# Scraper Configuration
SCRAPER_TIMEOUT=10
SCRAPER_MAX_RETRIES=3
SCRAPER_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
LOG_LEVEL=INFO

# Bing Web Search API (opcional)
BING_API_KEY=sua_chave_aqui

# Database
DB_PATH=scraper_results.db
```

## Banco de Dados (SQLite)

### Schema

**Tabela `urls`:**
- `id` (PRIMARY KEY)
- `url` (UNIQUE)
- `url_hash` (SHA256 para deduplicação)
- `first_seen` (timestamp)
- `last_seen` (timestamp)

**Tabela `scrape_results`:**
- `id` (PRIMARY KEY)
- `url_id` (FOREIGN KEY)
- `title`, `description`, `content`
- `links`, `images`, `headings` (contadores)
- `status_code`
- `raw_data` (JSON completo)
- `scraped_at` (timestamp)

### Deduplicação

URLs são automaticamente deduplicas por hash SHA256. Se uma URL for raspada novamente:
- A entrada em `urls` é atualizada com `last_seen`
- Um novo registro é criado em `scrape_results`
- Não cria duplicatas em `urls`

## Argumentos do CLI

```
python cli.py [OPTIONS]

Options:
  --mode {seed,keywords,hybrid}    Modo de operação (default: seed)
  --urls FILE                       Arquivo com URLs (uma por linha)
  --keywords FILE                  Arquivo com keywords (uma por linha)
  --use-bing                        Usar Bing Web Search API para descoberta
  --top N                          Top N resultados por keyword (default: 5)
  --follow-depth N                 Profundidade de crawling (default: 0)
  --delay SECONDS                  Delay entre requisições (default: 1.0)
  --db {json,sqlite}              Formato de saída (default: json)
  --output PATH                    Arquivo de saída (default: scraping_results.json)
  --max-links N                    Max links por página (default: 10)
```

## Exemplos Completos

### Exemplo 1: Raspar com deduplicação

```bash
# Primeira execução
python cli.py --mode seed --urls urls.txt --db sqlite

# Segunda execução (mesmo arquivo)
# → Detecta URLs duplicadas, não duplica no banco
python cli.py --mode seed --urls urls.txt --db sqlite

# Ver estatísticas
python query_db.py --stats
# Output:
# unique_urls: 4
# total_results: 8 (com duplicatas de execuções)
# success_rate: 100%
```

### Exemplo 2: Crawling com profundidade

```bash
# Raspar seed URLs + seguir 1 nível de profundidade
python cli.py --mode seed --urls urls.txt --follow-depth 1 --delay 2 --db sqlite

# Ver quantas URLs foram descobertas
python query_db.py --list-urls
```

### Exemplo 3: Automação agendada (Windows Task Scheduler)

1. Abra Task Scheduler
2. Create Basic Task → "Web Scraper Daily"
3. Trigger: Diário às 8:00 AM
4. Action: 
   - Program: `C:\path\to\project\.venv\Scripts\python.exe`
   - Arguments: `cli.py --mode seed --urls urls.txt --db sqlite --delay 2`
   - Start in: `C:\path\to\project`

Ou use o PowerShell script:
```powershell
$scriptPath = "C:\path\to\run_scraper.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 8:00am
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File $scriptPath -Mode seed"
Register-ScheduledTask -TaskName "URLScraper" -Trigger $trigger -Action $action -Description "Daily URL scraping"
```

## Tratamento de Erros

| Erro | Causa | Solução |
|------|-------|---------|
| `BING_API_KEY not set` | Falta chave de API Bing | Configure em `.env` ou `$env:BING_API_KEY` |
| `Mode seed/hybrid requires --urls` | URLs não fornecidas | Use `--urls arquivo.txt` |
| `Mode keywords/hybrid requires --keywords` | Keywords não fornecidas | Use `--keywords arquivo.txt` |
| Connection timeout | Site lento ou indisponível | Aumente `--delay` ou verifique conectividade |
| Blocked by robots.txt | Site não permite scraping | Respeite `robots.txt`, considere contato com site |

## Performance

- **2 URLs seed + follow-depth 1** → ~30 segundos (com delay de 2s)
- **SQLite deduplication** → O(1) lookups com hash
- **Parallel downloads** → Sequencial (respeitoso, delay configurável)
- **Database queries** → Indexed em `url_id` e `scraped_at`

## Desenvolvimento

### Adicionar novo extrator

Edite `scraper.py`:

```python
def _extract_custom_data(self, soup):
    """Extrator customizado"""
    return soup.find_all('custom-selector')

# No método scrape():
data['custom'] = self._extract_custom_data(soup)
```

### Rodar testes em desenvolvimento

```bash
# Watch mode (pytest-watch)
ptw -- -v

# Com coverage inline
pytest --cov=scraper tests/ -v --cov-report=term-missing
```

## Contribuindo

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Add nova-feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

MIT - Veja LICENSE file para detalhes

## Suporte

Para reportar issues ou sugerir melhorias: [GitHub Issues](https://github.com/robsoncaldeira/URL-Scraper/issues)
