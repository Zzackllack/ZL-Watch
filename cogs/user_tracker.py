import discord
from discord.ext import commands
from database import increment_join

class UserTracker(commands.Cog):
    """
    Tracks the number of times users join the server.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Increment the join count
        await increment_join(str(member.id))

def setup(bot: commands.Bot):
    bot.add_cog(UserTracker(bot))