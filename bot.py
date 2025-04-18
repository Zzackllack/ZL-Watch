import discord
from discord.ext import commands
import logging
import os
import config

# Enable discord.py's INFO‑level logging
logging.basicConfig(level=logging.INFO)

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    # Dynamically load all cogs in the cogs/ folder
    try:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and filename != "__init__.py":
                await bot.load_extension(f"cogs.{filename[:-3]}")
        # Sync all slash commands
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands!")
    except Exception as e:
        print(f"Error loading cogs or syncing commands: {e}")
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


# Run the bot
bot.run(config.TOKEN)
