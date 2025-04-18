import os
import asyncio
import discord
from discord.ext import commands
from database import init_db

# Configure intents
intents = discord.Intents.default()
intents.members = True
intents.messages = True

# Create bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

# Dynamically load all cogs in the cogs folder
dir_path = os.path.join(os.path.dirname(__file__), "cogs")
for filename in os.listdir(dir_path):
    if filename.endswith(".py"):
        cog_name = filename[:-3]
        bot.load_extension(f"cogs.{cog_name}")

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

if __name__ == "__main__":
    # Initialize the database before starting the bot
    asyncio.run(init_db())
    # Run the bot, ensure you set the DISCORD_TOKEN environment variable
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN environment variable not set")
    bot.run(token)