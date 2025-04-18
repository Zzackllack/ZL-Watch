import sqlite3
import discord
from discord.ext import commands
from discord import app_commands
from database import DB_PATH


class Top(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="top",
        description="Display the server’s top users by message count and voice time.",
    )
    async def top(self, interaction: discord.Interaction):
        # Open DB connection
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Top 5 message senders
        c.execute(
            "SELECT user_id, count FROM message_counts " "ORDER BY count DESC LIMIT 5;"
        )
        msg_rows = c.fetchall()

        # Top 5 voice-time users
        c.execute(
            "SELECT user_id, SUM(duration) AS total "
            "FROM voice_times GROUP BY user_id "
            "ORDER BY total DESC LIMIT 5;"
        )
        voice_rows = c.fetchall()

        conn.close()

        # Build embed
        embed = discord.Embed(
            title="🏆 Top Users Leaderboard",
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow(),
        )

        # Format top message senders
        if msg_rows:
            lines = []
            for i, (user_id, cnt) in enumerate(msg_rows, start=1):
                member = interaction.guild.get_member(user_id)
                name = member.display_name if member else f"<@{user_id}>"
                lines.append(f"**{i}. {name}** — {cnt} messages")
            embed.add_field(
                name="💬 Top Messages", value="\n".join(lines), inline=False
            )
        else:
            embed.add_field(
                name="💬 Top Messages", value="No message data available.", inline=False
            )

        # Format top voice-time users
        if voice_rows:
            lines = []
            for i, (user_id, total_sec) in enumerate(voice_rows, start=1):
                member = interaction.guild.get_member(user_id)
                name = member.display_name if member else f"<@{user_id}>"
                h, rem = divmod(total_sec, 3600)
                m, s = divmod(rem, 60)
                lines.append(f"**{i}. {name}** — {h}h {m}m {s}s")
            embed.add_field(
                name="🔊 Top Voice Time", value="\n".join(lines), inline=False
            )
        else:
            embed.add_field(
                name="🔊 Top Voice Time",
                value="No voice-time data available.",
                inline=False,
            )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Top(bot))
