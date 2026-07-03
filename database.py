import sqlite3
import os

DB_PATH = "aegis.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id TEXT PRIMARY KEY,
        status TEXT,
        summary TEXT,
        recommendation TEXT,
        created_at TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evidence (
        case_id TEXT PRIMARY KEY,
        query TEXT,
        candidates TEXT,
        selected_candidate TEXT,
        sources_searched INTEGER,
        reliable_sources INTEGER,
        negative_news_found BOOLEAN,
        overall_confidence TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS followup_drafts (
        case_id TEXT PRIMARY KEY,
        trigger_reason TEXT,
        drafted_message TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS field_reconstructions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id TEXT,
        field_name TEXT,
        suggested_value TEXT,
        basis TEXT,
        confidence TEXT,
        human_confirmed BOOLEAN DEFAULT FALSE
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS synthesis_narratives (
        case_id TEXT PRIMARY KEY,
        documents_included TEXT,
        narrative TEXT
    )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
