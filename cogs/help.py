# cogs/help.py

import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, button

REPO_URL = "https://github.com/zzackllack/ZL-Watch.git"


class HelpView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    def embed_setup(self) -> discord.Embed:
        embed = discord.Embed(
            title="🚀 Setup",
            description=(
                f"1. **Clone the repository**\n"
                f"`git clone {REPO_URL}`\n\n"
                "2. **Install dependencies**\n"
                "`pip install -r requirements.txt`\n\n"
                "3. **Configure your token**\n"
                "Set the `DISCORD_TOKEN` env var:\n"
                "```bash\n"
                'export DISCORD_TOKEN="your-token-here"\n'
                "```\n\n"
                "4. **Run the bot**\n"
                "`python bot.py`"
            ),
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Stats Bot Setup Instructions")
        return embed

    def embed_troubleshoot(self) -> discord.Embed:
        embed = discord.Embed(
            title="🛠️ Troubleshooting",
            description=(
                "- **Slash commands not appearing?**\n"
                "  • Make sure you invited the bot with the `applications.commands` scope.\n"
                "  • Restart the bot to sync.\n\n"
                "- **Missing intents errors?**\n"
                "  • Enable **Message Content** and **Voice State** intents in the Discord Developer Portal and in your code.\n\n"
                "- **Database issues?**\n"
                "  • Ensure `stats.db` is writable and located next to `database.py`.\n\n"
                "- **Other errors?**\n"
                "  • Check your console for tracebacks."
            ),
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Troubleshooting Tips")
        return embed

    def embed_credits(self) -> discord.Embed:
        embed = discord.Embed(
            title="🤝 Credits",
            description="This bot was developed by **Zacklack**.",
            color=discord.Color.purple(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Thanks for using Stats Bot!")
        return embed

    def embed_license(self) -> discord.Embed:
        embed = discord.Embed(
            title="📄 License",
            description="[BSD 3‑Clause “New” or “Revised” License]"
            "(https://opensource.org/licenses/BSD-3-Clause)",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Licensed under BSD 3‑Clause")
        return embed

    @button(label="Setup", style=discord.ButtonStyle.green, custom_id="help:setup")
    async def setup_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.edit_message(embed=self.embed_setup(), view=self)

    @button(
        label="Troubleshoot",
        style=discord.ButtonStyle.secondary,
        custom_id="help:troubleshoot",
    )
    async def troubleshoot_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=self.embed_troubleshoot(), view=self
        )

    @button(
        label="Credits", style=discord.ButtonStyle.primary, custom_id="help:credits"
    )
    async def credits_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.edit_message(embed=self.embed_credits(), view=self)

    # Changed from Link to Primary, so we can handle clicks
    @button(
        label="License", style=discord.ButtonStyle.primary, custom_id="help:license"
    )
    async def license_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.edit_message(embed=self.embed_license(), view=self)


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="help",
        description="Show setup guide, troubleshooting, credits, and license.",
    )
    async def help(self, interaction: discord.Interaction):
        """Display help menu with buttons to navigate sections."""
        view = HelpView(self.bot)
        embed = view.embed_setup()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
