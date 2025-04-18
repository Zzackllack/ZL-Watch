import os

# Your bot token should be in the DISCORD_TOKEN env var
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("DISCORD_TOKEN environment variable not set.")