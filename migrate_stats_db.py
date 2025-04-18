# migrate_stats_db.py
import sqlite3

DB_PATH = "stats.db"  # adjust if your DB lives elsewhere


def column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table});")
    return any(row[1] == column for row in cursor.fetchall())


def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1) Add `channel_id` to active_voice
    if not column_exists(c, "active_voice", "channel_id"):
        print("Adding channel_id to active_voice…")
        c.execute(
            """
            ALTER TABLE active_voice
            ADD COLUMN channel_id INTEGER NOT NULL DEFAULT 0;
        """
        )

    # 2) Add `channel_id` to voice_times
    if not column_exists(c, "voice_times", "channel_id"):
        print("Adding channel_id to voice_times…")
        c.execute(
            """
            ALTER TABLE voice_times
            ADD COLUMN channel_id INTEGER NOT NULL DEFAULT 0;
        """
        )

    conn.commit()
    conn.close()
    print("Migration complete.")


if __name__ == "__main__":
    migrate()
