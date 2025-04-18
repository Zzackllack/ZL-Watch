import discord
from discord.ext import commands
from database import get_stats

class Stats(commands.Cog):
    """
    Provides commands to display tracked statistics.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='stats')
    async def stats(self, ctx: commands.Context, member: discord.Member = None):
        """
        Usage: !stats [@member]
        Displays message and join counts for the specified member or the command author.
        """
        user = member or ctx.author
        msg_count, join_count = await get_stats(str(user.id))

        embed = discord.Embed(
            title=f"Stats for {user.display_name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Messages sent", value=str(msg_count), inline=False)
        embed.add_field(name="Joins", value=str(join_count), inline=False)

        await ctx.send(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(Stats(bot))
