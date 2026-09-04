import discord
from discord.ext import commands

class AnnouncementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="broadcast", aliases=["broadcast"])
    async def broadcast(self, ctx, channel: discord.TextChannel, *, message: str):
        """Sends a message to a specific server channel. Only the bot creator can use this."""
        
        # Replace with your actual numeric Discord user ID
        CREATOR_ID = 1521196096465010719 
        
        if ctx.author.id != CREATOR_ID:
            await ctx.send("You do not have permission to use this command.", delete_after=5)
            return

        try:
            await channel.send(message)
            await ctx.send(f"Successfully sent your message to {channel.mention}!", delete_after=5)
            await ctx.message.delete()
        except discord.Forbidden:
            await ctx.send("I don't have permission to send messages in that channel.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(AnnouncementCog(bot))