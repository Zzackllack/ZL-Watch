import discord
from discord.ext import commands
import logging
import os
import config
import asyncio

# Enable info‑level logging so we still see Discord’s logs
logging.basicConfig(level=logging.INFO)

# (Optional) for instant command registration in one guild
GUILD_ID = os.getenv("GUILD_ID")  # set this in your .env if you want guild‑only sync

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"on_ready fired for {bot.user} (ID: {bot.user.id})")
    # 1) Load all cogs, but don’t abort on the first error
    cog_files = [
        f for f in os.listdir("./cogs") if f.endswith(".py") and f != "__init__.py"
    ]
    for filename in cog_files:
        name = filename[:-3]
        try:
            await bot.load_extension(f"cogs.{name}")
            print(f"✅ Loaded cog: {name}")
        except Exception as e:
            print(f"❌ Failed to load cog {name}: {e}")

    # 2) Sync commands
    try:
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            synced = await bot.tree.sync(guild=guild)
            print(f"🔄 Synced {len(synced)} commands to guild {GUILD_ID}")
        else:
            synced = await bot.tree.sync()
            print(f"🔄 Synced {len(synced)} global commands")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

    print("Bot is ready!")


if __name__ == "__main__":
    # Normal run
    bot.run(config.TOKEN)
