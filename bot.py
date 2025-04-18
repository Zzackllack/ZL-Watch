import os
import asyncio
import discord
from discord.ext import commands
import config
import logging

# Define intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


async def main():
    # Dynamically load all cogs in the cogs/ folder (awaiting each)
    cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")
    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
    # Start the bot
    await bot.start(config.TOKEN)


if __name__ == "__main__":
    # asyncio.run will set up the loop and call main()
    asyncio.run(main())
