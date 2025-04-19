import sqlite3
import discord
from discord.ext import commands
from discord import app_commands
from database import DB_PATH


class StatsAll(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="statsall",
        description="Show server‑wide stats: total messages, top text & voice channels.",
    )
    async def statsall(self, interaction: discord.Interaction):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Total messages (all users)
        c.execute("SELECT SUM(count) FROM message_counts;")
        total_msgs = c.fetchone()[0] or 0

        # Top text channel (from aggregated table)
        c.execute(
            """
            SELECT channel_id, count
              FROM channel_message_counts
          ORDER BY count DESC
             LIMIT 1;
        """
        )
        row = c.fetchone()
        if row:
            top_text_id, top_text_count = row
        else:
            top_text_id, top_text_count = None, 0

        # Total voice time (all users)
        c.execute("SELECT SUM(duration) FROM voice_times;")
        total_voice_secs = c.fetchone()[0] or 0

        # Top voice channel (from aggregated table)
        c.execute(
            """
            SELECT channel_id, duration
              FROM channel_voice_times
          ORDER BY duration DESC
             LIMIT 1;
        """
        )
        row = c.fetchone()
        if row:
            top_voice_id, top_voice_secs = row
        else:
            top_voice_id, top_voice_secs = None, 0

        conn.close()

        def fmt(sec: int) -> str:
            h, rem = divmod(sec, 3600)
            m, s = divmod(rem, 60)
            return f"{h}h {m}m {s}s"

        embed = discord.Embed(
            title="🌐 Server‑wide Stats",
            color=discord.Color.blurple(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(
            name="💬 Total Messages", value=f"**{total_msgs:,}**", inline=False
        )

        if top_text_id:
            chan = self.bot.get_channel(top_text_id)
            mention = chan.mention if chan else f"<#{top_text_id}>"
            embed.add_field(
                name="🏆 Top Text Channel",
                value=f"{mention} — **{top_text_count:,}** messages",
                inline=False,
            )
        else:
            embed.add_field(name="🏆 Top Text Channel", value="No data", inline=False)

        embed.add_field(
            name="🔊 Total Voice Time",
            value=f"**{fmt(total_voice_secs)}**",
            inline=False,
        )

        if top_voice_id:
            chan = self.bot.get_channel(top_voice_id)
            mention = chan.mention if chan else f"<#{top_voice_id}>"
            embed.add_field(
                name="🏅 Top Voice Channel",
                value=f"{mention} — **{fmt(top_voice_secs)}**",
                inline=False,
            )
        else:
            embed.add_field(name="🏅 Top Voice Channel", value="No data", inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(StatsAll(bot))
