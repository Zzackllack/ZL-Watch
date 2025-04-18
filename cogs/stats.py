import discord
from discord.ext import commands
from database import (
    init_db,
    increment_message,
    voice_join,
    voice_leave,
    get_message_count,
    get_voice_time,
)


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        init_db()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # ignore bots
        if message.author.bot:
            return
        increment_message(message.author.id)
        # ensure commands still work
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
        """Show messages sent and total voice time."""
        member = member or ctx.author
        msg_count = get_message_count(member.id)
        total_seconds = get_voice_time(member.id)
        hours, rem = divmod(total_seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        await ctx.send(
            f"**{member.display_name}** has sent **{msg_count}** messages "
            f"and spent **{hours}h {minutes}m {seconds}s** in voice channels."
        )


# discord.py 2.x requires an async setup function:
async def setup(bot: commands.Bot):
    await bot.add_cog(Stats(bot))
