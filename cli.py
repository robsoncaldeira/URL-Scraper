"""
CLI runner for the URL Scraper.

Modes:
- seed: read URLs from a file and scrape them
- keywords: read keywords from a file, convert to URLs via Bing Web Search API (requires `BING_API_KEY` in env), then scrape
- hybrid: keywords -> seeds -> follow links up to `--follow-depth`

Outputs results to a JSON file (default `scraping_results.json`).

Usage examples:
python cli.py --mode seed --urls urls.txt --output out.json --delay 1
python cli.py --mode hybrid --keywords keywords.txt --follow-depth 1 --output out.json --use-bing

If `--use-bing` is set you must provide `BING_API_KEY` in the environment (or in a .env file).
"""

import argparse
import json
import time
import os
from collections import deque
from urllib.parse import urlparse
import urllib.robotparser as robotparser
from typing import List, Set

from scraper import URLScraper
from utils import normalize_url
from db import Database

BING_SEARCH_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"


def read_lines(path: str) -> List[str]:
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def discover_with_bing(keywords: List[str], top: int = 5):
    """Discover URLs using Bing Web Search API. Requires BING_API_KEY in env."""
    key = os.getenv('BING_API_KEY')
    if not key:
        raise RuntimeError('BING_API_KEY not set in environment. Cannot use Bing discovery.')

    import requests

    headers = {'Ocp-Apim-Subscription-Key': key}
    urls = []
    for kw in keywords:
        params = {'q': kw, 'count': top}
        resp = requests.get(BING_SEARCH_ENDPOINT, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # Extract webPages.value[*].url
        web = data.get('webPages', {}).get('value', [])
        for item in web:
            u = item.get('url')
            if u:
                urls.append(u)
    return urls


def can_fetch_url(url: str, user_agent='*') -> bool:
    """Check robots.txt for the site and return whether we can fetch the URL."""
    try:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        rp = robotparser.RobotFileParser()
        rp.set_url(base + '/robots.txt')
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        # If robots can't be parsed, be conservative and allow
        return True


def crawl(seeds: List[str], scraper: URLScraper, follow_depth: int = 0, delay: float = 1.0, max_links_per_page: int = 10):
    """Crawl seeds and optionally follow links up to `follow_depth`.

    Returns list of scraped results.
    """
    results = []
    seen: Set[str] = set()
    queue = deque()
    for s in seeds:
        queue.append((s, 0))

    while queue:
        url, depth = queue.popleft()
        url = normalize_url(url)
        if url in seen:
            continue
        seen.add(url)

        # robots.txt check
        if not can_fetch_url(url):
            scraper.logger.info(f"Blocked by robots.txt: {url}")
            continue

        data = scraper.scrape(url)
        if data:
            results.append(data)
            # Follow links if depth < follow_depth
            if depth < follow_depth:
                for link in data.get('links', [])[:max_links_per_page]:
                    if link not in seen:
                        queue.append((link, depth + 1))
        time.sleep(delay)
    return results


def save_results(results: List[dict], out_path: str, db_mode: bool = False):
    """Save results to JSON file and/or SQLite database."""
    if db_mode:
        # Save to SQLite
        with Database(out_path.replace('.json', '.db')) as db:
            inserted = db.insert_batch(results)
            print(f"Saved {inserted} unique results to {out_path.replace('.json', '.db')}")
    else:
        # Save to JSON
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(results)} results to {out_path}")


def main():
    parser = argparse.ArgumentParser(description='URL Scraper CLI')
    parser.add_argument('--mode', choices=['seed', 'keywords', 'hybrid'], default='seed')
    parser.add_argument('--urls', help='Path to file with URLs (one per line)')
    parser.add_argument('--keywords', help='Path to file with keywords (one per line)')
    parser.add_argument('--use-bing', action='store_true', help='Use Bing Web Search API for keyword discovery (requires BING_API_KEY)')
    parser.add_argument('--top', type=int, default=5, help='Top results per keyword when using search API')
    parser.add_argument('--follow-depth', type=int, default=0, help='Depth to follow links (0 = no follow)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests in seconds')
    parser.add_argument('--output', default='scraping_results.json', help='Output JSON file')
    parser.add_argument('--db', choices=['json', 'sqlite'], default='json', help='Output format: json or sqlite')
    parser.add_argument('--max-links', type=int, default=10, help='Max links followed per page')

    args = parser.parse_args()

    scraper = URLScraper()

    seeds = []
    if args.mode in ('seed', 'hybrid'):
        if not args.urls:
            raise SystemExit('Mode seed/hybrid requires --urls path')
        seeds = read_lines(args.urls)

    if args.mode in ('keywords', 'hybrid'):
        if not args.keywords:
            raise SystemExit('Mode keywords/hybrid requires --keywords path')
        keywords = read_lines(args.keywords)
        if args.use_bing:
            discovered = discover_with_bing(keywords, top=args.top)
            # Extend seeds
            seeds.extend(discovered)
        else:
            print('No discovery method selected (use --use-bing to enable Bing discovery). Using only provided seed URLs if any.')

    # Deduplicate seeds
    seeds = list(dict.fromkeys([normalize_url(s) for s in seeds]))

    results = crawl(seeds, scraper, follow_depth=args.follow_depth, delay=args.delay, max_links_per_page=args.max_links)

    save_results(results, args.output, db_mode=(args.db == 'sqlite'))


if __name__ == '__main__':
    main()
