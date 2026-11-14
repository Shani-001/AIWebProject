import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from config import settings
from database.models import CREATE_TABLES_SQL

logger = logging.getLogger(__name__)


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Returns an active SQLite connection configured with Row factory and foreign keys enabled.
    """
    path = db_path or settings.DATABASE_PATH
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[Path] = None):
    """
    Initializes the SQLite database tables.
    """
    with get_connection(db_path) as conn:
        conn.executescript(CREATE_TABLES_SQL)
        conn.commit()
    logger.info("Database initialized successfully.")


def create_session(
    topic: str,
    keywords: Optional[str],
    ai_provider: str,
    max_pages: int,
    created_at: str,
    status: str = "running",
    db_path: Optional[Path] = None
) -> int:
    """
    Creates a new research session and returns its ID.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO sessions (topic, keywords, ai_provider, max_pages, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (topic, keywords or "", ai_provider, max_pages, created_at, status)
        )
        conn.commit()
        return cursor.lastrowid


def update_session_summary(
    session_id: int,
    status: str,
    pages_count: int,
    signals_count: int,
    domains_count: int,
    summary_note: str,
    db_path: Optional[Path] = None
):
    """
    Updates completion stats for a session.
    """
    with get_connection(db_path) as conn:
        conn.execute(
            """
            UPDATE sessions
            SET status = ?, pages_crawled_count = ?, signals_count = ?, domains_count = ?, summary_note = ?
            WHERE id = ?
            """,
            (status, pages_count, signals_count, domains_count, summary_note, session_id)
        )
        conn.commit()


def save_crawled_pages(session_id: int, pages: List[Dict[str, Any]], db_path: Optional[Path] = None):
    """
    Saves a batch of crawled pages.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT INTO crawled_pages (session_id, url, domain, title, crawl_time, text_content, word_count, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    session_id,
                    p.get("url", ""),
                    p.get("domain", ""),
                    p.get("title", ""),
                    p.get("crawl_time", ""),
                    p.get("text_content", ""),
                    p.get("word_count", 0),
                    p.get("content_hash", "")
                )
                for p in pages
            ]
        )
        conn.commit()


def save_signals(session_id: int, signals: List[Dict[str, Any]], db_path: Optional[Path] = None):
    """
    Saves extracted signals into the database.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT INTO signals (
                session_id, page_url, category, summary, evidence,
                relevance_score, urgency_score, confidence_score,
                reasoning, theme_name, evidence_verified, extraction_method
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    session_id,
                    s.get("source_url", ""),
                    s.get("category", "Irrelevant Content"),
                    s.get("summary", ""),
                    s.get("evidence", ""),
                    int(s.get("relevance_score", 0)),
                    int(s.get("urgency_score", 0)),
                    int(s.get("confidence_score", 0)),
                    s.get("reasoning", ""),
                    s.get("theme_name", ""),
                    1 if s.get("evidence_verified", True) else 0,
                    s.get("extraction_method", "LLM")
                )
                for s in signals
            ]
        )
        conn.commit()


def save_opportunities(session_id: int, briefs: List[Dict[str, Any]], db_path: Optional[Path] = None):
    """
    Saves ranked opportunity briefs.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT INTO opportunities (
                session_id, title, theme_name, opportunity_score,
                avg_relevance, avg_urgency, avg_confidence,
                frequency_score, recency_score, source_count,
                what_is_happening, who_has_problem, why_it_matters,
                potential_solution, validation_step, brief_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    session_id,
                    b.get("title", ""),
                    b.get("theme_name", ""),
                    float(b.get("opportunity_score", 0.0)),
                    float(b.get("avg_relevance", 0.0)),
                    float(b.get("avg_urgency", 0.0)),
                    float(b.get("avg_confidence", 0.0)),
                    float(b.get("frequency_score", 0.0)),
                    float(b.get("recency_score", 100.0)),
                    int(b.get("source_count", 0)),
                    b.get("what_is_happening", ""),
                    b.get("who_has_problem", ""),
                    b.get("why_it_matters", ""),
                    b.get("potential_solution", ""),
                    b.get("validation_step", ""),
                    json.dumps(b)
                )
                for b in briefs
            ]
        )
        conn.commit()


def get_all_sessions(db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Retrieves all research sessions ordered by latest first.
    """
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM sessions ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]


def get_session_by_id(session_id: int, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieves a single session by id.
    """
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        return dict(row) if row else None


def get_signals_for_session(session_id: int, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Retrieves all signals for a session.
    """
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM signals WHERE session_id = ? ORDER BY relevance_score DESC", (session_id,)).fetchall()
        return [dict(r) for r in rows]


def get_opportunities_for_session(session_id: int, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Retrieves opportunity briefs for a session.
    """
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM opportunities WHERE session_id = ? ORDER BY opportunity_score DESC", (session_id,)).fetchall()
        res = []
        for r in rows:
            d = dict(r)
            if d.get("brief_json"):
                try:
                    d["brief_json"] = json.loads(d["brief_json"])
                except Exception:
                    pass
            res.append(d)
        return res


def get_pages_for_session(session_id: int, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Retrieves crawled pages for a session.
    """
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT id, session_id, url, domain, title, crawl_time, word_count, content_hash FROM crawled_pages WHERE session_id = ?", (session_id,)).fetchall()
        return [dict(r) for r in rows]


def delete_session(session_id: int, db_path: Optional[Path] = None) -> bool:
    """
    Deletes a session and cascades deletes for crawled pages, signals, opportunities.
    """
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()
        return True


def get_global_metrics(db_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Retrieves global overview metrics across all research sessions.
    """
    with get_connection(db_path) as conn:
        sessions_count = conn.execute("SELECT COUNT(*) FROM sessions WHERE status = 'completed'").fetchone()[0]
        pages_count = conn.execute("SELECT COUNT(*) FROM crawled_pages").fetchone()[0]
        signals_count = conn.execute("SELECT COUNT(*) FROM signals WHERE category != 'Irrelevant Content'").fetchone()[0]
        opportunities_count = conn.execute("SELECT COUNT(*) FROM opportunities").fetchone()[0]
        domains_count = conn.execute("SELECT COUNT(DISTINCT domain) FROM crawled_pages").fetchone()[0]

        return {
            "sessions_count": sessions_count,
            "pages_count": pages_count,
            "signals_count": signals_count,
            "opportunities_count": opportunities_count,
            "domains_count": domains_count
        }
