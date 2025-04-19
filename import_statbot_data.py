# import_statbot_data.py

import sqlite3
import csv
from database import DB_PATH, init_db

# Paths to your exported CSVs
USER_MSG_CSV = "top-members-by-messages-all-time-no-bots.csv"
CHAN_MSG_CSV = "top-channels-by-messages-all-time.csv"
USER_VOICE_CSV = "top-members-by-voice-time-in-hours-no-bots-all-time.csv"
CHAN_VOICE_CSV = "top-voice-channels-by-voice-time-in-hours-all-time.csv"


def to_seconds(hours_str: str) -> int:
    # e.g. "12.5" → 12.5 hours → 45000 seconds
    return int(float(hours_str) * 3600)


def main():
    # Ensure tables exist (incl. the new aggregated ones)
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1) Import user message counts
    with open(USER_MSG_CSV, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            user_id = int(row[2])
            count = int(row[3])
            c.execute(
                "INSERT OR REPLACE INTO message_counts (user_id, count) VALUES (?, ?)",
                (user_id, count),
            )

    # 2) Import channel message counts
    with open(CHAN_MSG_CSV, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            channel_id = int(row[2])
            count = int(row[3])
            c.execute(
                "INSERT OR REPLACE INTO channel_message_counts (channel_id, count) VALUES (?, ?)",
                (channel_id, count),
            )

    # 3) Import user voice totals (all voice_times with channel_id = 0)
    with open(USER_VOICE_CSV, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            user_id = int(row[2])
            hours = row[3]
            secs = to_seconds(hours)
            c.execute(
                "INSERT INTO voice_times (user_id, channel_id, duration) VALUES (?, ?, ?)",
                (user_id, 0, secs),
            )

    # 4) Import channel voice totals
    with open(CHAN_VOICE_CSV, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            channel_id = int(row[2])
            hours = row[3]
            secs = to_seconds(hours)
            c.execute(
                "INSERT OR REPLACE INTO channel_voice_times (channel_id, duration) VALUES (?, ?)",
                (channel_id, secs),
            )

    conn.commit()
    conn.close()
    print("✅ Import complete.")


if __name__ == "__main__":
    main()
