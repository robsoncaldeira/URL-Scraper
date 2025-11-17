"""
Query tool for SQLite database results.

Usage examples:
python query_db.py --stats
python query_db.py --list-urls
python query_db.py --list-results --limit 20
python query_db.py --export results.json
python query_db.py --by-date 2025-11-01 2025-11-30
"""

import argparse
from db import Database
from datetime import datetime


def print_stats(db: Database):
    """Print database statistics."""
    stats = db.get_statistics()
    print("\n" + "="*50)
    print("📊 SCRAPER DATABASE STATISTICS")
    print("="*50)
    for key, value in stats.items():
        print(f"{key:<25}: {value}")
    print("="*50 + "\n")


def print_urls(db: Database):
    """Print all unique URLs."""
    urls = db.get_unique_urls()
    print(f"\n📌 Total unique URLs: {len(urls)}\n")
    for i, url in enumerate(urls, 1):
        print(f"{i:3}. {url}")
    print()


def print_results(db: Database, limit: int = 50):
    """Print all results."""
    results = db.get_all_results(limit=limit)
    print(f"\n📄 Showing {len(results)} results (most recent first):\n")
    print(f"{'#':<4} {'URL':<50} {'Title':<30} {'Status':<8} {'Date':<19}")
    print("-" * 120)
    for i, r in enumerate(results, 1):
        url = r['url'][:45] + "..." if len(r['url']) > 45 else r['url']
        title = (r['title'] or "")[:25] + "..." if r['title'] and len(r['title']) > 25 else (r['title'] or "")
        status = r['status_code']
        date = r['scraped_at'][:19]
        print(f"{i:<4} {url:<50} {title:<30} {status:<8} {date:<19}")
    print()


def print_by_date(db: Database, start_date: str, end_date: str):
    """Print results by date range."""
    results = db.get_results_by_date(start_date, end_date)
    print(f"\n📅 Results from {start_date} to {end_date}: {len(results)} results\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. [{r['scraped_at'][:19]}] {r['title']}")
        print(f"   URL: {r['url']}\n")


def export_json(db: Database, output_path: str, limit: int = 0):
    """Export results to JSON."""
    if db.export_to_json(output_path, limit=limit):
        print(f"✅ Exported to {output_path}")
    else:
        print(f"❌ Failed to export to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Query URL Scraper database')
    parser.add_argument('--db', default='scraper_results.db', help='Path to SQLite database')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    parser.add_argument('--list-urls', action='store_true', help='List all unique URLs')
    parser.add_argument('--list-results', action='store_true', help='List all results')
    parser.add_argument('--limit', type=int, default=50, help='Limit results (for --list-results)')
    parser.add_argument('--export', help='Export results to JSON file')
    parser.add_argument('--by-date', nargs=2, metavar=('START', 'END'), help='Show results by date range (YYYY-MM-DD)')
    parser.add_argument('--clear-old', type=int, metavar='DAYS', help='Delete results older than N days')

    args = parser.parse_args()

    if not any([args.stats, args.list_urls, args.list_results, args.export, args.by_date, args.clear_old]):
        print("Use --help to see available options")
        return

    with Database(args.db) as db:
        if args.stats:
            print_stats(db)

        if args.list_urls:
            print_urls(db)

        if args.list_results:
            print_results(db, limit=args.limit)

        if args.export:
            export_json(db, args.export)

        if args.by_date:
            print_by_date(db, args.by_date[0], args.by_date[1])

        if args.clear_old:
            deleted = db.clear_old_results(days=args.clear_old)
            print(f"✅ Deleted {deleted} results older than {args.clear_old} days")


if __name__ == '__main__':
    main()
