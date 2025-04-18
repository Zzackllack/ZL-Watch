import discord
from discord.ext import commands
from database import increment_message

class MessageTracker(commands.Cog):
    """
    Tracks the number of messages each user sends.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages from bots
        if message.author.bot:
            return
        # Increment the message count
        await increment_message(str(message.author.id))

        # Process other commands if any
        await self.bot.process_commands(message)

def setup(bot: commands.Bot):
    bot.add_cog(MessageTracker(bot))