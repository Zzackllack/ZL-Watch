import sqlite3
import discord
from discord.ext import commands
from discord import app_commands
from database import (
    DB_PATH,
    get_message_count,
    get_message_counts_by_channel,
    get_voice_time,
    get_voice_times_by_channel,
)


def _format_duration(sec: int) -> str:
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m}m {s}s"


class Compare(commands.Cog):
    """Compare two users' message and voice stats side-by-side."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="compare",
        description="Compare two members' total messages and voice time.",
    )
    @app_commands.describe(
        user1="First member to compare", user2="Second member to compare"
    )
    async def compare(
        self,
        interaction: discord.Interaction,
        user1: discord.Member,
        user2: discord.Member,
    ):
        await interaction.response.defer(thinking=True)

        # Fetch totals
        msgs1 = get_message_count(user1.id)
        msgs2 = get_message_count(user2.id)
        voice1 = get_voice_time(user1.id)
        voice2 = get_voice_time(user2.id)

        # Fetch top channel for each by messages
        per_msgs1 = get_message_counts_by_channel(user1.id)
        per_msgs2 = get_message_counts_by_channel(user2.id)
        top_msg_chan1 = max(per_msgs1.items(), key=lambda x: x[1], default=(None, 0))
        top_msg_chan2 = max(per_msgs2.items(), key=lambda x: x[1], default=(None, 0))

        # Fetch top channel for each by voice
        per_voice1 = get_voice_times_by_channel(user1.id)
        per_voice2 = get_voice_times_by_channel(user2.id)
        top_voice_chan1 = max(per_voice1.items(), key=lambda x: x[1], default=(None, 0))
        top_voice_chan2 = max(per_voice2.items(), key=lambda x: x[1], default=(None, 0))

        # Helper to mention channels
        def mention_chan(cid):
            if cid:
                ch = self.bot.get_channel(cid)
                return ch.mention if ch else f"<#{cid}>"
            return "N/A"

        # Build comparison embed
        embed = discord.Embed(
            title=f"⚖️ Comparing {user1.display_name} vs. {user2.display_name}",
            color=discord.Color.blurple(),
            timestamp=discord.utils.utcnow(),
        )

        # Messages comparison
        msgs_field = (
            f"**Total:** {msgs1:,} vs {msgs2:,}\n"
            f"**Top Channel:** {mention_chan(top_msg_chan1[0])} ({top_msg_chan1[1]}) vs "
            f"{mention_chan(top_msg_chan2[0])} ({top_msg_chan2[1]})"
        )
        embed.add_field(name="💬 Messages", value=msgs_field, inline=False)

        # Voice comparison
        voice_field = (
            f"**Total:** {_format_duration(voice1)} vs {_format_duration(voice2)}\n"
            f"**Top Channel:** {mention_chan(top_voice_chan1[0])} "
            f"({_format_duration(top_voice_chan1[1])}) vs "
            f"{mention_chan(top_voice_chan2[0])} "
            f"({_format_duration(top_voice_chan2[1])})"
        )
        embed.add_field(name="🔊 Voice Time", value=voice_field, inline=False)

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Compare(bot))
