import os
import sqlite3
from datetime import datetime

# Ensure the DB lives next to this file
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "stats.db")

# Connect (or create) the SQLite database file
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()


def init_db():
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS message_counts (
        user_id INTEGER PRIMARY KEY,
        count INTEGER NOT NULL
    )"""
    )
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS active_voice (
        user_id INTEGER PRIMARY KEY,
        join_time TEXT NOT NULL
    )"""
    )
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS voice_times (
        user_id INTEGER NOT NULL,
        duration INTEGER NOT NULL
    )"""
    )
    conn.commit()


def increment_message(user_id: int):
    c.execute("SELECT count FROM message_counts WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if row:
        c.execute(
            "UPDATE message_counts SET count = count + 1 WHERE user_id = ?", (user_id,)
        )
    else:
        c.execute(
            "INSERT INTO message_counts (user_id, count) VALUES (?, 1)", (user_id,)
        )
    conn.commit()


def voice_join(user_id: int):
    now = datetime.utcnow().isoformat()
    c.execute(
        "INSERT OR REPLACE INTO active_voice (user_id, join_time) VALUES (?, ?)",
        (user_id, now),
    )
    conn.commit()


def voice_leave(user_id: int) -> int:
    c.execute("SELECT join_time FROM active_voice WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        return 0
    join_time = datetime.fromisoformat(row[0])
    duration = int((datetime.utcnow() - join_time).total_seconds())
    c.execute("DELETE FROM active_voice WHERE user_id = ?", (user_id,))
    c.execute(
        "INSERT INTO voice_times (user_id, duration) VALUES (?, ?)", (user_id, duration)
    )
    conn.commit()
    return duration


def get_message_count(user_id: int) -> int:
    c.execute("SELECT count FROM message_counts WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    return row[0] if row else 0


def get_voice_time(user_id: int) -> int:
    c.execute("SELECT SUM(duration) FROM voice_times WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    return row[0] or 0
