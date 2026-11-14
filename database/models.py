"""Data schemas and constants for SQLite storage."""

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    keywords TEXT,
    ai_provider TEXT NOT NULL,
    max_pages INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL,
    pages_crawled_count INTEGER DEFAULT 0,
    signals_count INTEGER DEFAULT 0,
    domains_count INTEGER DEFAULT 0,
    summary_note TEXT
);

CREATE TABLE IF NOT EXISTS crawled_pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    domain TEXT NOT NULL,
    title TEXT,
    crawl_time TEXT NOT NULL,
    text_content TEXT,
    word_count INTEGER DEFAULT 0,
    content_hash TEXT,
    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    page_url TEXT NOT NULL,
    category TEXT NOT NULL,
    summary TEXT NOT NULL,
    evidence TEXT NOT NULL,
    relevance_score INTEGER DEFAULT 0,
    urgency_score INTEGER DEFAULT 0,
    confidence_score INTEGER DEFAULT 0,
    reasoning TEXT,
    theme_name TEXT,
    evidence_verified INTEGER DEFAULT 1,
    extraction_method TEXT,
    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    theme_name TEXT NOT NULL,
    opportunity_score REAL DEFAULT 0.0,
    avg_relevance REAL DEFAULT 0.0,
    avg_urgency REAL DEFAULT 0.0,
    avg_confidence REAL DEFAULT 0.0,
    frequency_score REAL DEFAULT 0.0,
    recency_score REAL DEFAULT 100.0,
    source_count INTEGER DEFAULT 0,
    what_is_happening TEXT,
    who_has_problem TEXT,
    why_it_matters TEXT,
    potential_solution TEXT,
    validation_step TEXT,
    brief_json TEXT,
    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
);
"""
