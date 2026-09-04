import discord
from discord.ext import commands

class AnnouncementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="broadcast")
    async def broadcast(self, ctx, channel: discord.TextChannel, *, message: str):
        """Sends a message to a specific server channel. Can only be used in DMs by the creator."""
        
        # 1. Ensure the command is only run in DMs
        if ctx.guild is not None:
            await ctx.send("This command can only be used in my DMs!", delete_after=5)
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass
            return

        # 2. Replace with your actual numeric Discord user ID
        CREATOR_ID = 1521196096465010719 
        
        if ctx.author.id != CREATOR_ID:
            await ctx.send("You do not have permission to use this command.", delete_after=5)
            return

        try:
            await channel.send(message)
            await ctx.send(f"Successfully sent your message to {channel.mention}!")
        except discord.Forbidden:
            await ctx.send("I don't have permission to send messages in that channel.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(AnnouncementCog(bot))