import discord
from discord.ext import commands
from discord import app_commands
from database import (
    init_db,
    increment_message,
    voice_join,
    voice_leave,
    get_message_count,
    get_message_counts_by_channel,
    get_voice_time,
)


class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        init_db()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore bots themselves
        if message.author.bot:
            return
        increment_message(message.author.id, message.channel.id)

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        # Joined a VC
        if before.channel is None and after.channel is not None:
            voice_join(member.id)
        # Left a VC
        elif before.channel is not None and after.channel is None:
            voice_leave(member.id)
        # Switched VCs
        elif before.channel and after.channel and before.channel.id != after.channel.id:
            voice_leave(member.id)
            voice_join(member.id)

    @app_commands.command(
        name="stats",
        description="Show total + per-channel message counts and voice time for a user.",
    )
    @app_commands.describe(member="The member to view stats for (defaults to yourself)")
    async def stats(
        self, interaction: discord.Interaction, member: discord.Member = None
    ):
        member = member or interaction.user

        # Fetch data
        total_msgs = get_message_count(member.id)
        per_chan = get_message_counts_by_channel(member.id)
        total_seconds = get_voice_time(member.id)
        hours, rem = divmod(total_seconds, 3600)
        minutes, seconds = divmod(rem, 60)

        # Build response
        lines = [
            f"**{member.display_name}** has sent **{total_msgs}** messages:",
            f"> **Total:** {total_msgs}",
        ]
        for chan_id, cnt in per_chan.items():
            chan = self.bot.get_channel(chan_id)
            mention = chan.mention if chan else f"<#{chan_id}>"
            lines.append(f"> **{mention}:** {cnt}")

        lines.append(f"\n**Voice time:** {hours}h {minutes}m {seconds}s")

        await interaction.response.send_message("\n".join(lines))


async def setup(bot: commands.Bot):
    await bot.add_cog(Stats(bot))
