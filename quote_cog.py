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
            display_name = ref_msg.author.display_name
            username = str(ref_msg.author.name)
            avatar_url = ref_msg.author.avatar.url if ref_msg.author.avatar else ref_msg.author.default_avatar.url
        elif text:
            display_name = ctx.author.display_name
            username = str(ctx.author.name)
            avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        else:
            await ctx.send("Please provide some text or reply to a message with `.quo`!")
            return

        # Sleek dark aesthetic background (900x450 pixels)
        base = Image.new("RGBA", (900, 450), color=(18, 18, 22, 255))
        draw = ImageDraw.Draw(base)

        # Download and crop avatar into a smooth circle
        async with aiohttp.ClientSession() as session:
            async with session.get(str(avatar_url)) as resp:
                if resp.status == 200:
                    avatar_bytes = await resp.read()
                    avatar_image = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
                    avatar_image = avatar_image.resize((100, 100), Image.Resampling.LANCZOS)
                    
                    # Create circular mask
                    mask = Image.new("L", (100, 100), 0)
                    mask_draw = ImageDraw.Draw(mask)
                    mask_draw.ellipse((0, 0, 100, 100), fill=255)
                    
                    # Paste circular avatar onto the card
                    base.paste(avatar_image, (60, 60), mask)

        # Load fonts safely (using your bundled ttf files)
        try:
            quote_font = ImageFont.truetype("arial.ttf", 32)
            name_font = ImageFont.truetype("arialbd.ttf", 22)
            handle_font = ImageFont.truetype("arial.ttf", 16)
        except IOError:
            quote_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            handle_font = ImageFont.load_default()

        # Draw display name and username next to the avatar
        draw.text((180, 75), display_name, fill="white", font=name_font)
        draw.text((180, 105), f"@{username}", fill=(140, 140, 150, 255), font=handle_font)

        # Draw aesthetic quote text below
        draw.text((60, 195), "“", fill=(220, 220, 220, 255), font=quote_font)
        draw.text((95, 200), text, fill="white", font=quote_font)

        # Save and send
        buffer = io.BytesIO()
        base.save(buffer, format="PNG")
        buffer.seek(0)

        file = discord.File(fp=buffer, filename="quote.png")
        await ctx.send(file=file)

async def setup(bot):
    await bot.add_cog(QuoteCog(bot))