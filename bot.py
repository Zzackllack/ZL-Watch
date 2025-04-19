import discord
from discord.ext import commands
import os
import logging
import asyncio

# --- Basic Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(name)s: %(message)s')
log = logging.getLogger(__name__)

# --- Environment Variables ---
TOKEN = os.getenv("DISCORD_TOKEN")
raw_guild_id = os.getenv("GUILD_ID")
GUILD_ID = int(raw_guild_id) if raw_guild_id and raw_guild_id.isdigit() else None

# --- Intents ---
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# --- Bot Class ---
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.cogs_dir = "./cogs"
        self.initial_extensions = []
        try:
            for filename in os.listdir(self.cogs_dir):
                if filename.endswith('.py') and not filename.startswith('_'):
                    self.initial_extensions.append(f'cogs.{filename[:-3]}')
            log.info(f"Found potential extensions: {self.initial_extensions}")
        except FileNotFoundError:
            log.error(f"Cogs directory not found at: {os.path.abspath(self.cogs_dir)}")
        except Exception as e:
            log.error(f"Error listing cogs directory: {e}", exc_info=True)

    async def setup_hook(self):
        log.info("--- Starting Cog Loading ---")
        loaded_extensions = []
        for extension in self.initial_extensions:
            try:
                await self.load_extension(extension)
                log.info(f"Successfully loaded extension: {extension}")
                loaded_extensions.append(extension)
            except commands.ExtensionNotFound:
                log.error(f"Extension not found: {extension}. Check path and filename.")
            except commands.ExtensionAlreadyLoaded:
                log.warning(f"Extension already loaded: {extension}")
            except commands.NoEntryPointError:
                log.error(f"Extension {extension} has no setup() function.")
            except Exception as e:
                log.error(f"Failed to load extension {extension}.", exc_info=True)
        log.info(f"--- Finished Cog Loading. Loaded: {len(loaded_extensions)}/{len(self.initial_extensions)} ---")

        if not loaded_extensions:
            log.warning("No extensions were loaded. Skipping command sync.")
            return

        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            log.info(f"Copying global commands to guild {GUILD_ID} (if any)...")
            log.info(f"Syncing commands to guild {GUILD_ID}...")
            try:
                synced_commands = await self.tree.sync(guild=guild)
                log.info(f"Successfully synced {len(synced_commands)} commands to guild {GUILD_ID}.")
            except discord.HTTPException as e:
                log.error(f"Failed to sync commands to guild {GUILD_ID} due to HTTP error.", exc_info=True)
            except Exception as e:
                log.error(f"An unexpected error occurred during guild command sync.", exc_info=True)
        else:
            log.info("No GUILD_ID found. Syncing commands globally...")
            try:
                synced_commands = await self.tree.sync()
                log.info(f"Successfully synced {len(synced_commands)} commands globally.")
            except discord.HTTPException as e:
                log.error(f"Failed to sync commands globally due to HTTP error.", exc_info=True)
            except Exception as e:
                log.error(f"An unexpected error occurred during global command sync.", exc_info=True)

    async def on_ready(self):
        log.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        log.info(f'Connected to {len(self.guilds)} guilds.')
        log.info('Bot is ready and operational.')
        log.info('------')

# --- Bot Instantiation and Run ---
bot = MyBot()

if __name__ == "__main__":
    if TOKEN is None:
        log.critical("FATAL: DISCORD_TOKEN environment variable not set.")
    else:
        log.info("Attempting to run bot...")
        try:
            bot.run(TOKEN, log_handler=None)
        except discord.LoginFailure:
            log.critical("FATAL: Login failed - Improper token provided.")
        except discord.PrivilegedIntentsRequired:
            log.critical("FATAL: Privileged intents (like Server Members or Message Content) are required but not enabled in the Developer Portal or Intents object.")
        except Exception as e:
            log.critical("FATAL: Error running bot.", exc_info=True)
