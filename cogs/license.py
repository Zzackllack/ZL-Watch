import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button

LICENSE_URL = "https://opensource.org/licenses/BSD-3-Clause"


class LicenseView(View):
    def __init__(self):
        super().__init__(timeout=None)
        # Manually add a link-style button (decorator-based @button doesn't accept url)
        self.add_item(
            Button(
                label="Full License Text",
                style=discord.ButtonStyle.link,
                url=LICENSE_URL,
            )
        )


class LicenseCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="license",
        description="Show the BSD 3‑Clause license summary and usage terms.",
    )
    async def license(self, interaction: discord.Interaction):
        """Display a summary of what you may and may not do under the BSD 3‑Clause license."""
        embed = discord.Embed(
            title="📄 BSD 3‑Clause “New” or “Revised” License",
            description=(
                "A permissive open‑source license with minimal restrictions, "
                "allowing for commercial and private use as long as conditions are met."
            ),
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(
            name="✅ Permissions",
            value=(
                "• Commercial use\n"
                "• Modification\n"
                "• Distribution\n"
                "• Private use"
            ),
            inline=False,
        )
        embed.add_field(
            name="⚠️ Conditions",
            value=(
                "• **Redistributions of source code** must retain the copyright notice, "
                "this list of conditions, and the disclaimer.\n"
                "• **Redistributions in binary form** must reproduce these in documentation "
                "and/or other materials.\n"
                "• **No endorsement**: The names of the project or contributors may not be used "
                "to endorse or promote derived products without permission."
            ),
            inline=False,
        )
        embed.add_field(
            name="🚫 Limitations",
            value=(
                "• **Liability**: The software is provided “as is”, without warranty of any kind.\n"
                "• **Warranty**: No warranties; use at your own risk."
            ),
            inline=False,
        )
        embed.set_footer(text="Click the button below to read the full license.")
        view = LicenseView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(LicenseCog(bot))
