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
        
        # Create embed for first user
        embed1 = discord.Embed(
            title=f"📊 Stats for {user1.display_name}",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )
        embed1.set_thumbnail(url=user1.display_avatar.url)
        
        # Message info for user1
        msg_field1 = (
            f"**Total Messages:** {msgs1:,}\n"
            f"**Top Channel:** {mention_chan(top_msg_chan1[0])} ({top_msg_chan1[1]:,})"
        )
        embed1.add_field(name="💬 Message Activity", value=msg_field1, inline=False)
        
        # Voice info for user1
        voice_field1 = (
            f"**Total Time:** {_format_duration(voice1)}\n"
            f"**Top Channel:** {mention_chan(top_voice_chan1[0])} ({_format_duration(top_voice_chan1[1])})"
        )
        embed1.add_field(name="🔊 Voice Activity", value=voice_field1, inline=False)
        
        # Create embed for second user
        embed2 = discord.Embed(
            title=f"📊 Stats for {user2.display_name}",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed2.set_thumbnail(url=user2.display_avatar.url)
        
        # Message info for user2
        msg_field2 = (
            f"**Total Messages:** {msgs2:,}\n"
            f"**Top Channel:** {mention_chan(top_msg_chan2[0])} ({top_msg_chan2[1]:,})"
        )
        embed2.add_field(name="💬 Message Activity", value=msg_field2, inline=False)
        
        # Voice info for user2
        voice_field2 = (
            f"**Total Time:** {_format_duration(voice2)}\n"
            f"**Top Channel:** {mention_chan(top_voice_chan2[0])} ({_format_duration(top_voice_chan2[1])})"
        )
        embed2.add_field(name="🔊 Voice Activity", value=voice_field2, inline=False)
        
        # Create a comparison embed to show differences
        comparison = discord.Embed(
            title="⚖️ Head-to-Head Comparison",
            color=discord.Color.gold(),
            description=f"Comparing {user1.mention} vs {user2.mention}"
        )
        
        # Message difference
        msg_diff = msgs1 - msgs2
        if msg_diff > 0:
            msg_comp = f"{user1.display_name} has **{abs(msg_diff):,} more** messages than {user2.display_name}"
        elif msg_diff < 0:
            msg_comp = f"{user2.display_name} has **{abs(msg_diff):,} more** messages than {user1.display_name}"
        else:
            msg_comp = f"Both users have the same number of messages: **{msgs1:,}**"
        comparison.add_field(name="Message Comparison", value=msg_comp, inline=False)
        
        # Voice time difference
        voice_diff = voice1 - voice2
        if voice_diff > 0:
            voice_comp = f"{user1.display_name} has **{_format_duration(abs(voice_diff))} more** voice time than {user2.display_name}"
        elif voice_diff < 0:
            voice_comp = f"{user2.display_name} has **{_format_duration(abs(voice_diff))} more** voice time than {user1.display_name}"
        else:
            voice_comp = f"Both users have the same voice time: **{_format_duration(voice1)}**"
        comparison.add_field(name="Voice Time Comparison", value=voice_comp, inline=False)
        
        # Send all embeds
        await interaction.followup.send(embeds=[embed1, embed2, comparison])


async def setup(bot: commands.Bot):
    await bot.add_cog(Compare(bot))
