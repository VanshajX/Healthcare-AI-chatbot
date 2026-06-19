import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "healthcare.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT NOT NULL,
            feature     TEXT NOT NULL,  -- 'faq', 'disease', 'medicine', 'report'
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS messages (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER REFERENCES conversations(id),
            role            TEXT NOT NULL,  -- 'user' or 'assistant'
            content         TEXT NOT NULL,
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS report_uploads (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      TEXT NOT NULL,
            filename        TEXT NOT NULL,
            summary         TEXT,
            uploaded_at     DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS search_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT NOT NULL,
            feature     TEXT NOT NULL,
            query       TEXT NOT NULL,
            searched_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()

def create_conversation(session_id: str, feature: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (session_id, feature) VALUES (?, ?)",
        (session_id, feature)
    )
    conv_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return conv_id

def save_message(conversation_id: int, role: str, content: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
        (conversation_id, role, content)
    )
    conn.commit()
    conn.close()

def get_conversation_messages(conversation_id: int) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content, created_at FROM messages WHERE conversation_id = ? ORDER BY created_at",
        (conversation_id,)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def save_report(session_id: str, filename: str, summary: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO report_uploads (session_id, filename, summary) VALUES (?, ?, ?)",
        (session_id, filename, summary)
    )
    conn.commit()
    conn.close()

def log_search(session_id: str, feature: str, query: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO search_history (session_id, feature, query) VALUES (?, ?, ?)",
        (session_id, feature, query)
    )
    conn.commit()
    conn.close()

def get_stats() -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as c FROM conversations")
    total_chats = cursor.fetchone()["c"]
    cursor.execute("SELECT COUNT(*) as c FROM messages WHERE role='user'")
    total_messages = cursor.fetchone()["c"]
    cursor.execute("SELECT COUNT(*) as c FROM report_uploads")
    total_reports = cursor.fetchone()["c"]
    conn.close()
    return {
        "total_chats": total_chats,
        "total_messages": total_messages,
        "total_reports": total_reports,
    }

def get_recent_history(session_id: str, limit: int = 10) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.feature, s.query, s.searched_at
        FROM search_history s
        WHERE s.session_id = ?
        ORDER BY s.searched_at DESC
        LIMIT ?
    """, (session_id, limit))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
