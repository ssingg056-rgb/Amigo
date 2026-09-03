import io
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import aiohttp

class QuoteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="quo")
    async def quo_command(self, ctx, *, text: str = None):
        if not text and ctx.message.reference and ctx.message.reference.resolved:
            ref_msg = ctx.message.reference.resolved
            text = ref_msg.content
            author_name = ref_msg.author.display_name
            avatar_url = ref_msg.author.avatar.url if ref_msg.author.avatar else ref_msg.author.default_avatar.url
        elif text:
            author_name = ctx.author.display_name
            avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        else:
            await ctx.send("Please provide some text or reply to a message with `!quo`!")
            return

        base = Image.new("RGBA", (900, 500), color=(20, 20, 20, 255))
        draw = ImageDraw.Draw(base)

        async with aiohttp.ClientSession() as session:
            async with session.get(str(avatar_url)) as resp:
                if resp.status == 200:
                    avatar_bytes = await resp.read()
                    avatar_image = Image.open(io.BytesIO(avatar_bytes)).convert("L").convert("RGBA")
                    avatar_image = avatar_image.resize((450, 500), Image.Resampling.LANCZOS)
                    base.paste(avatar_image, (0, 0))

        try:
            quote_font = ImageFont.truetype("arial.ttf", 36)
            author_font = ImageFont.truetype("arial.ttf", 22)
        except IOError:
            quote_font = ImageFont.load_default()
            author_font = ImageFont.load_default()

        draw.text((490, 100), "“", fill="white", font=quote_font)
        draw.text((490, 160), text, fill="white", font=quote_font)
        draw.text((490, 360), f"— {author_name}", fill=(180, 180, 180, 255), font=author_font)

        buffer = io.BytesIO()
        base.save(buffer, format="PNG")
        buffer.seek(0)

        file = discord.File(fp=buffer, filename="quote.png")
        await ctx.send(file=file)

async def setup(bot):
    await bot.add_cog(QuoteCog(bot))