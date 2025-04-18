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
    get_voice_times_by_channel,
)


class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        init_db()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore bots
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
            voice_join(member.id, after.channel.id)
        # Left a VC
        elif before.channel is not None and after.channel is None:
            voice_leave(member.id)
        # Switched VCs
        elif before.channel and after.channel and before.channel.id != after.channel.id:
            voice_leave(member.id)
            voice_join(member.id, after.channel.id)

    @app_commands.command(
        name="stats",
        description="Show total + per-channel message counts and voice time for a user.",
    )
    @app_commands.describe(member="The member to view stats for (defaults to yourself)")
    async def stats(
        self, interaction: discord.Interaction, member: discord.Member = None
    ):
        member = member or interaction.user

        # Messages
        total_msgs = get_message_count(member.id)
        per_msgs = get_message_counts_by_channel(member.id)

        # Voice
        total_secs = get_voice_time(member.id)
        per_voice = get_voice_times_by_channel(member.id)

        # Format totals
        msg_lines = [
            f"**{member.display_name}** has sent **{total_msgs}** messages:",
            f"> **Total:** {total_msgs}",
        ]
        for chan_id, cnt in per_msgs.items():
            chan = self.bot.get_channel(chan_id)
            mention = chan.mention if chan else f"<#{chan_id}>"
            msg_lines.append(f"> **{mention}:** {cnt}")

        hrs, rem = divmod(total_secs, 3600)
        mins, secs = divmod(rem, 60)
        voice_lines = [
            f"\n**Voice time:** {hrs}h {mins}m {secs}s",
            f"> **Total:** {hrs}h {mins}m {secs}s",
        ]
        for chan_id, sec in per_voice.items():
            chan = self.bot.get_channel(chan_id)
            mention = chan.mention if chan else f"<#{chan_id}>"
            h, r = divmod(sec, 3600)
            m, s = divmod(r, 60)
            voice_lines.append(f"> **{mention}:** {h}h {m}m {s}s")

        # Send it all
        await interaction.response.send_message("\n".join(msg_lines + voice_lines))


async def setup(bot: commands.Bot):
    await bot.add_cog(Stats(bot))
