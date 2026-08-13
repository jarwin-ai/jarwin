"""
Jarwin Analytics
Tracks app usage — blueprints generated, industries, modes used.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "jarwin_analytics.db")


def _get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            industry TEXT,
            mode TEXT,
            details TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    return conn


def track_event(event: str, industry: str = "", mode: str = "", details: dict = None):
    """Track a usage event."""
    conn = _get_db()
    conn.execute(
        "INSERT INTO usage (event, industry, mode, details, timestamp) VALUES (?, ?, ?, ?, ?)",
        (event, industry, mode, json.dumps(details or {}), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_stats() -> dict:
    """Get usage statistics."""
    conn = _get_db()
    
    total = conn.execute("SELECT COUNT(*) FROM usage WHERE event='blueprint_generated'").fetchone()[0]
    
    today = datetime.now().strftime("%Y-%m-%d")
    today_count = conn.execute(
        "SELECT COUNT(*) FROM usage WHERE event='blueprint_generated' AND timestamp LIKE ?",
        (f"{today}%",)
    ).fetchone()[0]
    
    # Top industries
    industries = conn.execute(
        "SELECT industry, COUNT(*) as cnt FROM usage WHERE event='blueprint_generated' AND industry != '' GROUP BY industry ORDER BY cnt DESC LIMIT 5"
    ).fetchall()
    
    # Mode split
    chat_count = conn.execute("SELECT COUNT(*) FROM usage WHERE mode='chat'").fetchone()[0]
    form_count = conn.execute("SELECT COUNT(*) FROM usage WHERE mode='form'").fetchone()[0]
    
    # Last 7 days
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    weekly = conn.execute(
        "SELECT COUNT(*) FROM usage WHERE event='blueprint_generated' AND timestamp > ?",
        (week_ago,)
    ).fetchone()[0]
    
    # Total visits
    visits = conn.execute("SELECT COUNT(*) FROM usage WHERE event='page_visit'").fetchone()[0]
    
    conn.close()
    
    return {
        "total_blueprints": total,
        "today_blueprints": today_count,
        "weekly_blueprints": weekly,
        "total_visits": visits,
        "top_industries": [{"industry": r[0], "count": r[1]} for r in industries],
        "mode_split": {"chat": chat_count, "form": form_count},
    }
