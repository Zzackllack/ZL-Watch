import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, button
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


class StatsView(View):
    def __init__(self, cog: commands.Cog, member: discord.Member):
        super().__init__(timeout=60)
        self.cog = cog
        self.member = member

    @button(label="🔄 Refresh", style=discord.ButtonStyle.primary)
    async def refresh_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Recompute and update the stats embed."""
        embed = self.cog.build_embed(self.cog.bot, self.member)
        await interaction.response.edit_message(embed=embed, view=self)


class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        init_db()

    def build_embed(self, bot: commands.Bot, member: discord.Member) -> discord.Embed:
        # Fetch message stats
        total_msgs = get_message_count(member.id)
        per_msgs = get_message_counts_by_channel(member.id)
        # Fetch voice stats
        total_secs = get_voice_time(member.id)
        per_voice = get_voice_times_by_channel(member.id)

        # Create embed
        embed = discord.Embed(
            title=f"📊 Stats for {member.display_name}",
            color=discord.Color.blurple(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        # Messages field
        msg_lines = [f"**Total:** {total_msgs}"]
        for chan_id, cnt in per_msgs.items():
            chan = bot.get_channel(chan_id)
            mention = chan.mention if chan else f"<#{chan_id}>"
            msg_lines.append(f"{mention}: {cnt}")
        embed.add_field(name="💬 Messages", value="\n".join(msg_lines), inline=False)

        # Voice field
        hrs, rem = divmod(total_secs, 3600)
        mins, secs = divmod(rem, 60)
        voice_lines = [f"**Total:** {hrs}h {mins}m {secs}s"]
        for chan_id, sec in per_voice.items():
            chan = bot.get_channel(chan_id)
            mention = chan.mention if chan else f"<#{chan_id}>"
            h, r = divmod(sec, 3600)
            m, s = divmod(r, 60)
            voice_lines.append(f"{mention}: {h}h {m}m {s}s")
        embed.add_field(
            name="🔊 Voice Time", value="\n".join(voice_lines), inline=False
        )

        embed.set_footer(text="Click Refresh to update these numbers")
        return embed

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
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
        # track join
        if before.channel is None and after.channel is not None:
            voice_join(member.id, after.channel.id)
        # track leave
        elif before.channel is not None and after.channel is None:
            voice_leave(member.id)
        # switching channels
        elif before.channel and after.channel and before.channel.id != after.channel.id:
            voice_leave(member.id)
            voice_join(member.id, after.channel.id)

    @app_commands.command(
        name="stats",
        description="Show fancy stats (total + per-channel) for messages & voice time.",
    )
    @app_commands.describe(member="Which member to show stats for (defaults to you)")
    async def stats(
        self, interaction: discord.Interaction, member: discord.Member = None
    ):
        member = member or interaction.user
        embed = self.build_embed(self.bot, member)
        view = StatsView(self, member)
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Stats(bot))
