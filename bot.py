import discord
from discord.ext import commands
import os
import logging
import asyncio
from dotenv import load_dotenv
from discord import app_commands, Interaction

# --- Basic Logging Setup ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s:%(name)s: %(message)s"
)
log = logging.getLogger("ZL-Watch")

# --- Environment Variables ---
load_dotenv()
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
                if filename.endswith(".py") and not filename.startswith("_"):
                    self.initial_extensions.append(f"cogs.{filename[:-3]}")
            log.info(f"Found potential extensions: {self.initial_extensions}")
        except Exception as e:
            log.error(f"Error listing cogs directory: {e}", exc_info=True)

    async def setup_hook(self):
        log.info("--- Starting Cog Loading ---")
        loaded = []
        for ext in self.initial_extensions:
            try:
                await self.load_extension(ext)
                log.info(f"Loaded extension: {ext}")
                loaded.append(ext)
            except Exception:
                log.error(f"Failed to load extension {ext}", exc_info=True)
        log.info(
            f"--- Finished Cog Loading ({len(loaded)}/{len(self.initial_extensions)}) ---"
        )

        # Sync slash commands
        if loaded:
            if GUILD_ID:
                guild_obj = discord.Object(id=GUILD_ID)
                log.info(f"Syncing slash commands to guild {GUILD_ID}...")
                try:
                    synced = await self.tree.sync(guild=guild_obj)
                    log.info(f"Synced {len(synced)} commands to guild {GUILD_ID}")
                except Exception:
                    log.error("Error syncing commands to guild", exc_info=True)
            else:
                log.info("Syncing slash commands globally...")
                try:
                    synced = await self.tree.sync()
                    log.info(f"Synced {len(synced)} global commands")
                except Exception:
                    log.error("Error syncing global commands", exc_info=True)

    async def on_ready(self):
        log.info(f"Logged in as {self.user} (ID: {self.user.id})")
        log.info(f"Connected to {len(self.guilds)} guilds.")
        log.info("Bot is ready and operational.\n" + "-" * 40)

    async def on_application_command(self, interaction: Interaction):
        # Called at start of slash command dispatch
        cmd = interaction.data.get("name")
        log.info(
            f"🔹 Received /{cmd} from {interaction.user} (ID: {interaction.user.id}) "
            f"in guild {interaction.guild} (ID: {interaction.guild.id}) "
            f"channel {interaction.channel} (ID: {interaction.channel.id})"
        )

    async def on_app_command_completion(
        self, interaction: Interaction, command: app_commands.Command
    ):
        log.info(
            f"✅ Completed /{command.name} for {interaction.user} "
            f"in guild {interaction.guild.id}, channel {interaction.channel.id}"
        )

    async def on_app_command_error(self, interaction: Interaction, error: Exception):
        cmd = interaction.data.get("name")
        log.error(f"❌ Error in /{cmd}", exc_info=True)
        # Try to inform the user
        try:
            await interaction.response.send_message(
                "⚠️ An unexpected error occurred. The developers have been notified.",
                ephemeral=True,
            )
        except Exception:
            pass  # if even that fails, ignore

    async def on_command(self, ctx: commands.Context):
        # Prefix command start
        log.info(
            f"🔸 Received prefix command {ctx.command} from {ctx.author} "
            f"in {ctx.guild}/{ctx.channel}"
        )

    async def on_command_completion(self, ctx: commands.Context):
        log.info(f"✅ Prefix command {ctx.command} completed for {ctx.author}")

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        log.error(f"❌ Error in prefix command {ctx.command}", exc_info=True)
        try:
            await ctx.send("⚠️ Something went wrong executing that command.")
        except Exception:
            pass


# --- Bot Instantiation and Run ---
bot = MyBot()

if __name__ == "__main__":
    if not TOKEN:
        log.critical("DISCORD_TOKEN not set; cannot start bot.")
        exit(1)
    log.info("Starting bot...")
    try:
        bot.run(TOKEN, log_handler=None)
    except discord.LoginFailure:
        log.critical("Login failed: Invalid token.")
    except Exception:
        log.critical("Fatal error running bot.", exc_info=True)
