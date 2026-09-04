import discord
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["h"])
    async def help_command(self, ctx, category: str = None):
        # General Help Menu Overview
        if not category:
            embed = discord.Embed(
                title="📖 Bot Command Categories",
                description="Use `.help <category>` to view commands in a specific section!\n\n"
                            "📂 **Categories Available:**\n"
                            "• `economy` - Money, banking, shop, gathering & leaderboard\n"
                            "• `roleplay` - Social interactions, romance & expressions\n"
                            "• `quotes` - Motivational or funny quote features\n"
                            "• `welcome` - Automated member greeting system",
                color=discord.Color.blurple()
            )
            embed.set_footer(text="Type .help [category] for detailed command lists.")
            return await ctx.send(embed=embed)

        cat = category.lower()

        # Category: Economy
        if cat in ["economy", "eco", "money"]:
            embed = discord.Embed(
                title="💰 Economy & Adventure Commands",
                description="Manage your wealth, buy gear, and gather resources.",
                color=discord.Color.gold()
            )
            embed.add_field(name="Financials", value="`.bal` - Check wallet/bank\n`.work` - Earn initial cash\n`.deposit <amt>` - Save money\n`.withdraw <amt>` - Take money out\n`.leaderboard` - Top players", inline=False)
            embed.add_field(name="Adventure & Shop", value="`.shop` - Browse gear\n`.buy <item>` - Purchase items\n`.inventory` - Check gear\n`.hunt` / `.mine` / `.fish` - Gather resources", inline=False)
            return await ctx.send(embed=embed)

        # Category: Roleplay
        elif cat in ["roleplay", "rp", "social"]:
            embed = discord.Embed(
                title="✨ Roleplay & Social Commands",
                description="Interact with other members in your server.",
                color=discord.Color.pink()
            )
            embed.add_field(name="Affection & Social", value="`.hug`, `.kiss`, `.pat`, `.cuddle`, `.poke`, `.tickle`, `.highfive`, `.handshake`, `.fistbump` `.fuck`", inline=False)
            embed.add_field(name="Actions & Banter", value="`.slap`, `.punch`, `.kick`, `.roast`, `.simp`, `.flirt`, `.kill`", inline=False)
            embed.add_field(name="Expressions", value="`.wave`, `.salute`, `.blush`, `.cry`, `.dance`, `.sleep`, `.shrug`, `.facepalm`", inline=False)
            return await ctx.send(embed=embed)

        # Category: Quotes
        elif cat in ["quote", "quotes"]:
            embed = discord.Embed(
                title="💬 Quote Commands",
                description="Fetch or display quotes.",
                color=discord.Color.green()
            )
            embed.add_field(name="Commands", value="Use your quote command prefix to generate random quotes across the server.", inline=False)
            return await ctx.send(embed=embed)

        # Category: Welcome
        elif cat in ["welcome", "welcomes"]:
            embed = discord.Embed(
                title="👋 Welcome System",
                description="Automated features for greeting new members.",
                color=discord.Color.blue()
            )
            embed.add_field(name="Status", value="Runs automatically on member join events (requires server members intent).", inline=False)
            return await ctx.send(embed=embed)

        else:
            await ctx.send("❌ Unknown category! Choose from `economy`, `roleplay`, `quotes`, or `welcome`.")

async def setup(bot):
    await bot.add_cog(HelpCog(bot))