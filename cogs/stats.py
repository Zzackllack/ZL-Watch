import discord
from discord.ext import commands
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
        # ignore bots
        if message.author.bot:
            return
        increment_message(message.author.id, message.channel.id)
        await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        # joined a VC
        if before.channel is None and after.channel is not None:
            voice_join(member.id)
        # left a VC
        elif before.channel is not None and after.channel is None:
            voice_leave(member.id)
        # switched VCs
        elif before.channel and after.channel and before.channel.id != after.channel.id:
            voice_leave(member.id)
            voice_join(member.id)

    @commands.command(name="stats")
    async def stats(self, ctx: commands.Context, member: discord.Member = None):
        """Show message counts (total + per channel) and total voice time."""
        member = member or ctx.author

        # Messages
        total_msgs = get_message_count(member.id)
        per_chan = get_message_counts_by_channel(member.id)

        # Voice
        total_seconds = get_voice_time(member.id)
        hours, rem = divmod(total_seconds, 3600)
        minutes, seconds = divmod(rem, 60)

        lines = [
            f"**{member.display_name}** has sent **{total_msgs}** messages:",
            f"> **Total:** {total_msgs}",
        ]
        for chan_id, cnt in per_chan.items():
            chan = self.bot.get_channel(chan_id)
            mention = chan.mention if chan else f"<#{chan_id}>"
            lines.append(f"> **{mention}:** {cnt}")

        lines.append(f"\n**Voice time:** {hours}h {minutes}m {seconds}s")

        await ctx.send("\n".join(lines))


async def setup(bot: commands.Bot):
    await bot.add_cog(Stats(bot))
