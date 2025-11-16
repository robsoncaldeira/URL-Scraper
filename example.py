"""
Script de exemplo usando o URL Scraper
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scraper import URLScraper
from config import Config
import json


def main():
    """Função principal"""
    
    # URLs para fazer scraping
    urls = [
        'https://www.python.org',
        'https://github.com',
        'https://stackoverflow.com'
    ]
    
    # Criar scraper com configuração customizada
    config = Config(timeout=15, max_retries=3)
    scraper = URLScraper(config)
    
    results = []
    
    for url in urls:
        print(f"\n{'='*60}")
        print(f"Scraping: {url}")
        print(f"{'='*60}")
        
        result = scraper.scrape(url)
        
        if result:
            results.append(result)
            
            print(f"✓ Título: {result['title']}")
            print(f"✓ Status: {result['status_code']}")
            print(f"✓ Descrição: {result['description'][:100]}..." 
                  if result['description'] else "✗ Sem descrição")
            print(f"✓ Links encontrados: {len(result['links'])}")
            print(f"✓ Imagens encontradas: {len(result['images'])}")
            print(f"✓ H1 encontrados: {len(result['headings']['h1'])}")
        else:
            print(f"✗ Erro ao fazer scraping")
    
    # Fechar sessão
    scraper.close()
    
    # Salvar resultados em JSON
    if results:
        with open('scraping_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n{'='*60}")
        print(f"✓ Resultados salvos em 'scraping_results.json'")
        print(f"{'='*60}")


if __name__ == '__main__':
    main()
