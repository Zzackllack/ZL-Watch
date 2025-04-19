import os
import sqlite3
from datetime import datetime

# Keep the DB next to this file
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "stats.db")

# Create/connect to the SQLite database
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()


def init_db():
    # Total message counts
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS message_counts (
            user_id INTEGER PRIMARY KEY,
            count INTEGER NOT NULL
        )
        """
    )
    # Per-channel message counts
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS message_channel_counts (
            user_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            count INTEGER NOT NULL,
            PRIMARY KEY (user_id, channel_id)
        )
        """
    )
    # Active voice sessions (now tracking channel)
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS active_voice (
            user_id INTEGER PRIMARY KEY,
            channel_id INTEGER NOT NULL,
            join_time TEXT NOT NULL
        )
        """
    )
    # Historical voice durations per channel
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS voice_times (
            user_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            duration INTEGER NOT NULL
        )
        """
    )
    # Aggregated messages per channel (all users)
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS channel_message_counts (
            channel_id INTEGER PRIMARY KEY,
            count INTEGER NOT NULL
        )
        """
    )
    # Aggregated voice time per channel (all users)
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS channel_voice_times (
            channel_id INTEGER PRIMARY KEY,
            duration INTEGER NOT NULL
        )
        """
    )

    conn.commit()


def increment_message(user_id: int, channel_id: int):
    # total count
    c.execute("SELECT count FROM message_counts WHERE user_id = ?", (user_id,))
    if c.fetchone():
        c.execute(
            "UPDATE message_counts SET count = count + 1 WHERE user_id = ?",
            (user_id,),
        )
    else:
        c.execute(
            "INSERT INTO message_counts (user_id, count) VALUES (?, 1)",
            (user_id,),
        )

    # per‑channel count
    c.execute(
        "SELECT count FROM message_channel_counts WHERE user_id = ? AND channel_id = ?",
        (user_id, channel_id),
    )
    if c.fetchone():
        c.execute(
            "UPDATE message_channel_counts "
            "SET count = count + 1 "
            "WHERE user_id = ? AND channel_id = ?",
            (user_id, channel_id),
        )
    else:
        c.execute(
            "INSERT INTO message_channel_counts "
            "(user_id, channel_id, count) VALUES (?, ?, 1)",
            (user_id, channel_id),
        )

    conn.commit()


def get_message_count(user_id: int) -> int:
    c.execute("SELECT count FROM message_counts WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    return row[0] if row else 0


def get_message_counts_by_channel(user_id: int) -> dict[int, int]:
    c.execute(
        "SELECT channel_id, count FROM message_channel_counts "
        "WHERE user_id = ? ORDER BY count DESC",
        (user_id,),
    )
    return {row[0]: row[1] for row in c.fetchall()}


def voice_join(user_id: int, channel_id: int):
    now = datetime.utcnow().isoformat()
    c.execute(
        "INSERT OR REPLACE INTO active_voice (user_id, channel_id, join_time) VALUES (?, ?, ?)",
        (user_id, channel_id, now),
    )
    conn.commit()


def voice_leave(user_id: int) -> int:
    c.execute(
        "SELECT channel_id, join_time FROM active_voice WHERE user_id = ?", (user_id,)
    )
    row = c.fetchone()
    if not row:
        return 0

    channel_id, join_time = row
    join_dt = datetime.fromisoformat(join_time)
    duration = int((datetime.utcnow() - join_dt).total_seconds())

    # remove active record
    c.execute("DELETE FROM active_voice WHERE user_id = ?", (user_id,))
    # log the duration per channel
    c.execute(
        "INSERT INTO voice_times (user_id, channel_id, duration) VALUES (?, ?, ?)",
        (user_id, channel_id, duration),
    )
    conn.commit()
    return duration


def get_voice_time(user_id: int) -> int:
    c.execute("SELECT SUM(duration) FROM voice_times WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    return row[0] or 0


def get_voice_times_by_channel(user_id: int) -> dict[int, int]:
    c.execute(
        "SELECT channel_id, SUM(duration) FROM voice_times "
        "WHERE user_id = ? GROUP BY channel_id ORDER BY SUM(duration) DESC",
        (user_id,),
    )
    return {row[0]: row[1] for row in c.fetchall()}
