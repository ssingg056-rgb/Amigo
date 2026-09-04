import random
import discord
from discord.ext import commands

class RoleplayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_rp(self, ctx, member, action_text, color):
        if not member:
            return await ctx.send(f"❌ You need to mention someone! Example: `.{ctx.command.name} @User`")
        
        embed = discord.Embed(
            description=f"**{ctx.author.display_name}** {action_text} **{member.display_name}**!",
            color=color
        )
        await ctx.send(embed=embed)

    # --- SOCIAL & AFFECTION ---
    @commands.command(name="hug")
    async def hug(self, ctx, member: discord.Member = None):
        await self.send_rp(ctx, member, "gives a warm hug to", discord.Color.pink())

    @commands.command(name="fuck")
    async def fuck(self, ctx, member: discord.Member = None):
        await self.send_rp(ctx, member, "fucks", discord.Color.pink())
        

    @commands.command(name="kiss")
    async def kiss(self, ctx, member: discord.Member = None):
        await self.send_rp(ctx, member, "gives a sweet kiss to", discord.Color.magenta())

    @commands.command(name="pat")
    async def pat(self, ctx, member: discord.Member = None):
        await self.send_rp(ctx, member, "gently pats the head of", discord.Color.teal())

    @commands.command(name="cuddle")
    async def cuddle(self, ctx, member: discord.Member = None):
        await self.send_rp(ctx, member, "cuddles up close to", discord.Color.purple())

    @commands.command(name="holdhands", aliases=["handhold"])
    async def holdhands(self, ctx, member: discord.Member = None):
        await self.send_rp(ctx, member, "holds hands with", discord.Color.blue())

    @commands.command(name="poke")
    async def poke(self, ctx, member: discord.Member = None):
        await self.send_rp(ctx, member, "pokes", discord.Color.gold())

    @commands.command(name="tickle")
    async def tickle(self, ctx, member: discord.Member = None):
        await self.send_rp(ctx, member, "unmercifully tickles", discord.Color.orange())

    @commands.command(name="highfive", aliases=["hf"])
    async def highfive(self, ctx, member: discord.Member = None):
        await self.send_rp(ctx, member, "gives a high-five to", discord.Color.blurple())

    @commands.command(name="handshake")
    async def handshake(self, ctx, member: discord.Member = None):
        await self.send_rp(ctx, member, "shakes hands firmly with", discord.Color.dark_gold())

    @commands.command(name="fistbump")
    async def fistbump(self, ctx, member: discord.Member = None):
        await self.send_rp(ctx, member, "shares a solid fist bump with", discord.Color.dark_purple())

    # --- EDGY / SPICY BANTER (Safe alternative) ---
    @commands.command(name="roast")
    async def roast(self, ctx, member: discord.Member = None):
        if not member:
            return await ctx.send("❌ Mention someone to roast!")
        roasts = [
            f"🔥 **{ctx.author.display_name}** completely obliterated **{member.display_name}** with facts and logic.",
            f"🔥 **{ctx.author.display_name}** told **{member.display_name}**, 'You bring everyone so much joy when you leave the room.'",
            f"🔥 **{ctx.author.display_name}** pointed out that **{member.display_name}**'s brain cell count is currently in the negatives."
        ]
        await ctx.send(embed=discord.Embed(description=random.choice(roasts), color=discord.Color.dark_orange()))

    @commands.command(name="simp")
    async def simp(self, ctx, member: discord.Member = None):
        await self.send_rp(ctx, member, "is down astronomically bad and simping hard for", discord.Color.magenta())

    @commands.command(name="flirt")
    async def flirt(self, ctx, member: discord.Member = None):
        lines = [
            f"😘 **{ctx.author.display_name}** whispers to **{member.display_name}**: 'Are you a parking ticket? Because you've got FINE written all over you.'",
            f"😏 **{ctx.author.display_name}** winks at **{member.display_name}**: 'Are you Wi-Fi? Because I'm feeling a strong connection.'"
        ]
        if not member:
            return await ctx.send("❌ Mention someone to flirt with!")
        await ctx.send(embed=discord.Embed(description=random.choice(lines), color=discord.Color.pink()))

    # --- COMBAT & AGGRESSION ---
    @commands.command(name="kill")
    async def kill(self, ctx, member: discord.Member = None):
        if not member:
            return await ctx.send("❌ Mention someone!")
        if member.id == ctx.author.id:
            return await ctx.send("🤔 You can't do that to yourself!")
        scenarios = [
            f"⚔️ **{ctx.author.display_name}** challenged **{member.display_name}** to an epic duel and won!",
            f"🍌 **{ctx.author.display_name}** dropped a tactical banana peel on **{member.display_name}**.",
            f"⚡ **{ctx.author.display_name}** zapped **{member.display_name}** with a lightning strike.",
            f"🥷 **{ctx.author.display_name}** stealthily took down **{member.display_name}**."
        ]
        await ctx.send(embed=discord.Embed(description=random.choice(scenarios), color=discord.Color.dark_red()))

    @commands.command(name="slap")
    async def slap(self, ctx, member: discord.Member = None):
        await self.send_rp(ctx, member, "slaps across the face", discord.Color.red())

    @commands.command(name="punch")
    async def punch(self, ctx, member: discord.Member = None):
        await self.send_rp(ctx, member, "lands a heavy punch on", discord.Color.dark_orange())

    @commands.command(name="kick")
    async def kick(self, ctx, member: discord.Member = None):
        await self.send_rp(ctx, member, "roundhouse kicks", discord.Color.dark_magenta())

    @commands.command(name="bite")
    async def bite(self, ctx, member: discord.Member = None):
        await self.send_rp(ctx, member, "hungrily bites", discord.Color.dark_green())

    # --- PHYSICAL MOTIONS & EXPRESSIONS ---
    @commands.command(name="wave")
    async def wave(self, ctx, member: discord.Member = None):
        await self.send_rp(ctx, member, "waves cheerfully at", discord.Color.yellow())

    @commands.command(name="salute")
    async def salute(self, ctx, member: discord.Member = None):
        await self.send_rp(ctx, member, "salutes sharply to", discord.Color.blue())

    @commands.command(name="stare")
    async def stare(self, ctx, member: discord.Member = None):
        await self.send_rp(ctx, member, "stares intensely into the soul of", discord.Color.dark_grey())

    @commands.command(name="blush")
    async def blush(self, ctx):
        await ctx.send(embed=discord.Embed(description=f"😳 **{ctx.author.display_name}** is blushing furiously!", color=discord.Color.light_gray()))

    @commands.command(name="cry")
    async def cry(self, ctx):
        await ctx.send(embed=discord.Embed(description=f"😢 **{ctx.author.display_name}** breaks down crying...", color=discord.Color.blue()))

    @commands.command(name="dance")
    async def dance(self, ctx):
        await ctx.send(embed=discord.Embed(description=f"💃 **{ctx.author.display_name}** shows off their moves and starts dancing!", color=discord.Color.purple()))

    @commands.command(name="sleep")
    async def sleep(self, ctx):
        await ctx.send(embed=discord.Embed(description=f"💤 **{ctx.author.display_name}** falls fast asleep... zzz...", color=discord.Color.dark_blue()))

async def setup(bot):
    await bot.add_cog(RoleplayCog(bot))