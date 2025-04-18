import aiosqlite

DB_PATH = "stats.db"

async def init_db():
    """
    Initialize the SQLite database and create necessary tables.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            '''
            CREATE TABLE IF NOT EXISTS message_counts (
                user_id TEXT PRIMARY KEY,
                count INTEGER NOT NULL
            )
            '''
        )
        await db.execute(
            '''
            CREATE TABLE IF NOT EXISTS join_counts (
                user_id TEXT PRIMARY KEY,
                count INTEGER NOT NULL
            )
            '''
        )
        await db.commit()

async def increment_message(user_id: str):
    """
    Increment the message count for a user.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            '''
            INSERT INTO message_counts (user_id, count)
            VALUES (?, 1)
            ON CONFLICT(user_id) DO UPDATE SET count = count + 1
            ''',
            (user_id,)
        )
        await db.commit()

async def increment_join(user_id: str):
    """
    Increment the join count for a user.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            '''
            INSERT INTO join_counts (user_id, count)
            VALUES (?, 1)
            ON CONFLICT(user_id) DO UPDATE SET count = count + 1
            ''',
            (user_id,)
        )
        await db.commit()

async def get_stats(user_id: str):
    """
    Retrieve message and join counts for a user.
    Returns a tuple (message_count, join_count).
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT count FROM message_counts WHERE user_id = ?', (user_id,)
        )
        row = await cursor.fetchone()
        msg_count = row[0] if row else 0

        cursor = await db.execute(
            'SELECT count FROM join_counts WHERE user_id = ?', (user_id,)
        )
        row = await cursor.fetchone()
        join_count = row[0] if row else 0

        return msg_count, join_count