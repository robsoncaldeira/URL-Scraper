"""
SQLite database module for URL Scraper.
Handles storage, retrieval, and deduplication of scrape results.
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from logger import get_logger

logger = get_logger(__name__)


class Database:
    """SQLite database handler for scrape results."""

    def __init__(self, db_path: str = "scraper_results.db"):
        """Initialize database connection and create schema if needed."""
        self.db_path = db_path
        self.conn = None
        self._init_db()

    def _init_db(self):
        """Create database connection and initialize schema."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Return rows as dicts
            cursor = self.conn.cursor()

            # Create URLs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    url_hash TEXT UNIQUE NOT NULL,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create scrape_results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scrape_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url_id INTEGER NOT NULL,
                    title TEXT,
                    description TEXT,
                    content TEXT,
                    links INTEGER DEFAULT 0,
                    images INTEGER DEFAULT 0,
                    headings INTEGER DEFAULT 0,
                    status_code INTEGER,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    raw_data TEXT,
                    FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE
                )
            """)

            # Create index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_scrape_results_url_id 
                ON scrape_results (url_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_scrape_results_scraped_at 
                ON scrape_results (scraped_at)
            """)

            self.conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    def _compute_url_hash(self, url: str) -> str:
        """Compute SHA256 hash of URL."""
        return hashlib.sha256(url.encode()).hexdigest()

    def insert_result(self, scrape_data: Dict) -> Optional[int]:
        """
        Insert scrape result into database.
        Returns the ID of the inserted result or None if URL already exists.
        """
        url = scrape_data.get("url")
        if not url:
            logger.warning("Skipping result with no URL")
            return None

        url_hash = self._compute_url_hash(url)

        try:
            cursor = self.conn.cursor()

            # Try to insert URL (or get existing ID if duplicate)
            cursor.execute("""
                INSERT OR IGNORE INTO urls (url, url_hash) 
                VALUES (?, ?)
            """, (url, url_hash))

            # Get URL ID (either just inserted or existing)
            cursor.execute("SELECT id FROM urls WHERE url = ?", (url,))
            url_id = cursor.fetchone()[0]

            # Update last_seen timestamp if URL was already in DB
            cursor.execute("""
                UPDATE urls SET last_seen = CURRENT_TIMESTAMP WHERE id = ?
            """, (url_id,))

            # Insert scrape result
            result_id = cursor.execute("""
                INSERT INTO scrape_results 
                (url_id, title, description, content, links, images, headings, status_code, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                url_id,
                scrape_data.get("title"),
                scrape_data.get("description"),
                scrape_data.get("content", "")[:1000],  # Store first 1000 chars
                len(scrape_data.get("links", [])),
                len(scrape_data.get("images", [])),
                len(scrape_data.get("headings", [])),
                scrape_data.get("status_code"),
                json.dumps(scrape_data)  # Store full data as JSON
            )).lastrowid

            self.conn.commit()
            logger.debug(f"Inserted result {result_id} for URL {url}")
            return result_id

        except sqlite3.IntegrityError:
            logger.debug(f"URL already exists in database: {url}")
            return None
        except sqlite3.Error as e:
            logger.error(f"Failed to insert result: {e}")
            return None

    def insert_batch(self, scrape_results: List[Dict]) -> int:
        """Insert multiple results and return count of successful inserts."""
        count = 0
        for result in scrape_results:
            if self.insert_result(result):
                count += 1
        return count

    def get_all_results(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all scrape results with pagination."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    u.url,
                    sr.title,
                    sr.description,
                    sr.status_code,
                    sr.scraped_at,
                    sr.links,
                    sr.images,
                    sr.headings
                FROM scrape_results sr
                JOIN urls u ON sr.url_id = u.id
                ORDER BY sr.scraped_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))

            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve results: {e}")
            return []

    def get_unique_urls(self) -> List[str]:
        """Get all unique URLs in database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT url FROM urls ORDER BY first_seen DESC")
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve URLs: {e}")
            return []

    def get_url_count(self) -> int:
        """Get total count of unique URLs in database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM urls")
            return cursor.fetchone()[0]
        except sqlite3.Error as e:
            logger.error(f"Failed to get URL count: {e}")
            return 0

    def get_result_count(self) -> int:
        """Get total count of scrape results in database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM scrape_results")
            return cursor.fetchone()[0]
        except sqlite3.Error as e:
            logger.error(f"Failed to get result count: {e}")
            return 0

    def get_results_by_date(self, start_date: str, end_date: str) -> List[Dict]:
        """Get results scraped between two dates (YYYY-MM-DD format)."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    u.url,
                    sr.title,
                    sr.scraped_at
                FROM scrape_results sr
                JOIN urls u ON sr.url_id = u.id
                WHERE DATE(sr.scraped_at) BETWEEN ? AND ?
                ORDER BY sr.scraped_at DESC
            """, (start_date, end_date))

            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve results by date: {e}")
            return []

    def get_statistics(self) -> Dict:
        """Get database statistics."""
        try:
            cursor = self.conn.cursor()

            # Count URLs and results
            cursor.execute("SELECT COUNT(*) FROM urls")
            url_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM scrape_results")
            result_count = cursor.fetchone()[0]

            # Average links per page
            cursor.execute("SELECT AVG(links) FROM scrape_results")
            avg_links = cursor.fetchone()[0] or 0

            # Average images per page
            cursor.execute("SELECT AVG(images) FROM scrape_results")
            avg_images = cursor.fetchone()[0] or 0

            # Success rate (status 200)
            cursor.execute("SELECT COUNT(*) FROM scrape_results WHERE status_code = 200")
            success_count = cursor.fetchone()[0]

            success_rate = (success_count / result_count * 100) if result_count > 0 else 0

            return {
                "unique_urls": url_count,
                "total_results": result_count,
                "avg_links_per_page": round(avg_links, 2),
                "avg_images_per_page": round(avg_images, 2),
                "success_rate": f"{success_rate:.1f}%",
                "db_path": self.db_path
            }
        except sqlite3.Error as e:
            logger.error(f"Failed to compute statistics: {e}")
            return {}

    def export_to_json(self, output_path: str, limit: int = 0) -> bool:
        """Export all results to JSON file."""
        try:
            cursor = self.conn.cursor()

            query = """
                SELECT 
                    u.url,
                    sr.title,
                    sr.description,
                    sr.content,
                    sr.links,
                    sr.images,
                    sr.headings,
                    sr.status_code,
                    sr.scraped_at,
                    sr.raw_data
                FROM scrape_results sr
                JOIN urls u ON sr.url_id = u.id
                ORDER BY sr.scraped_at DESC
            """

            if limit > 0:
                query += f" LIMIT {limit}"

            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]

            # Convert raw_data from string to dict
            for result in results:
                if result["raw_data"]:
                    result["raw_data"] = json.loads(result["raw_data"])

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"Exported {len(results)} results to {output_path}")
            return True
        except (sqlite3.Error, IOError) as e:
            logger.error(f"Failed to export to JSON: {e}")
            return False

    def clear_old_results(self, days: int = 30) -> int:
        """Delete results older than X days. Returns number of deleted results."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                DELETE FROM scrape_results 
                WHERE scraped_at < datetime('now', ? || ' days')
            """, (f"-{days}",))

            self.conn.commit()
            deleted = cursor.rowcount
            logger.info(f"Deleted {deleted} results older than {days} days")
            return deleted
        except sqlite3.Error as e:
            logger.error(f"Failed to clear old results: {e}")
            return 0

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
