"""
Jarwin Memory System
Persists company profiles and session history using SQLite.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "jarwin_memory.db")


def _get_db():
    """Get database connection and ensure tables exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id TEXT PRIMARY KEY,
            name TEXT,
            context_json TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id TEXT,
            blueprint_json TEXT,
            chat_history_json TEXT,
            created_at TEXT,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            agent TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    return conn


def save_company(company_id: str, name: str, context: dict):
    """Save or update a company profile."""
    conn = _get_db()
    now = datetime.now().isoformat()
    conn.execute("""
        INSERT OR REPLACE INTO companies (id, name, context_json, created_at, updated_at)
        VALUES (?, ?, ?, COALESCE((SELECT created_at FROM companies WHERE id = ?), ?), ?)
    """, (company_id, name, json.dumps(context), company_id, now, now))
    conn.commit()
    conn.close()


def load_company(company_id: str) -> Optional[dict]:
    """Load a company profile."""
    conn = _get_db()
    row = conn.execute("SELECT context_json FROM companies WHERE id = ?", (company_id,)).fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None


def list_companies() -> list:
    """List all saved companies."""
    conn = _get_db()
    rows = conn.execute("SELECT id, name, updated_at FROM companies ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "updated_at": r[2]} for r in rows]


def save_session(company_id: str, blueprint: dict, chat_history: list):
    """Save a session with blueprint and chat history."""
    conn = _get_db()
    now = datetime.now().isoformat()
    conn.execute("""
        INSERT INTO sessions (company_id, blueprint_json, chat_history_json, created_at)
        VALUES (?, ?, ?, ?)
    """, (company_id, json.dumps(blueprint), json.dumps(chat_history), now))
    conn.commit()
    conn.close()


def save_chat_message(session_id: str, role: str, content: str, agent: str = ""):
    """Save a chat message."""
    conn = _get_db()
    now = datetime.now().isoformat()
    conn.execute("""
        INSERT INTO chat_messages (session_id, role, content, agent, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, role, content, agent, now))
    conn.commit()
    conn.close()


def get_chat_history(session_id: str) -> list:
    """Get chat history for a session."""
    conn = _get_db()
    rows = conn.execute(
        "SELECT role, content, agent, timestamp FROM chat_messages WHERE session_id = ? ORDER BY id",
        (session_id,)
    ).fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1], "agent": r[2], "timestamp": r[3]} for r in rows]


def get_past_sessions(company_id: str) -> list:
    """Get past sessions for a company."""
    conn = _get_db()
    rows = conn.execute(
        "SELECT id, created_at FROM sessions WHERE company_id = ? ORDER BY created_at DESC LIMIT 10",
        (company_id,)
    ).fetchall()
    conn.close()
    return [{"id": r[0], "created_at": r[1]} for r in rows]
