import io
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageFilter
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

        # Canvas configuration (1000x500)
        width, height = 1000, 500
        base = Image.new("RGBA", (width, height))
        draw = ImageDraw.Draw(base)

        # Smooth horizontal gray gradient background
        for x in range(width):
            r = int(150 + (205 - 150) * (x / width))
            g = int(150 + (205 - 150) * (x / width))
            b = int(150 + (205 - 150) * (x / width))
            draw.line([(x, 0), (x, height)], fill=(r, g, b, 255))

        # Load fonts safely
        try:
            quote_font = ImageFont.truetype("BOD_B.TTF", 36)
            author_font = ImageFont.truetype("BOD_R.TTF", 22)
        except IOError:
            quote_font = ImageFont.load_default()
            author_font = ImageFont.load_default()

        # Process circular avatar with a soft drop shadow
        avatar_size = 280
        async with aiohttp.ClientSession() as session:
            async with session.get(str(avatar_url)) as resp:
                if resp.status == 200:
                    avatar_bytes = await resp.read()
                    avatar_image = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
                    avatar_image = avatar_image.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
                    
                    # Circular mask
                    mask = Image.new("L", (avatar_size, avatar_size), 0)
                    mask_draw = ImageDraw.Draw(mask)
                    mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
                    
                    # Drop shadow layer
                    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                    shadow_draw = ImageDraw.Draw(shadow)
                    shadow_x, shadow_y = 80, 110
                    shadow_draw.ellipse((shadow_x + 8, shadow_y + 12, shadow_x + avatar_size + 8, shadow_y + avatar_size + 12), fill=(0, 0, 0, 90))
                    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
                    base.paste(shadow, (0, 0), shadow)

                    # Paste avatar
                    base.paste(avatar_image, (shadow_x, shadow_y), mask)

        # Intelligent text wrapping for the right side block
        max_text_width = 500
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=quote_font)
            w = bbox[2] - bbox[0]
            if w <= max_text_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        # Add smart quotation marks around the full text block
        formatted_lines = []
        for i, line in enumerate(lines):
            if i == 0:
                line = f'“{line}'
            if i == len(lines) - 1:
                line = f'{line}”'
            formatted_lines.append(line)

        # Vertical alignment calculations
        line_height = 46
        total_text_height = len(formatted_lines) * line_height
        author_text = f"— {display_name} (@{username})"
        total_block_height = total_text_height + 25 + 25

        start_y = (height - total_block_height) / 2 - 15
        text_x = 400

        # Draw quote text lines
        current_y = start_y
        for line in formatted_lines:
            draw.text((text_x, current_y), line, fill=(35, 35, 35, 255), font=quote_font)
            current_y += line_height

        # Draw author info underneath
        current_y += 10
        draw.text((text_x, current_y), author_text, fill=(75, 75, 75, 255), font=author_font)

        # Save and send output image
        buffer = io.BytesIO()
        base.save(buffer, format="PNG")
        buffer.seek(0)

        file = discord.File(fp=buffer, filename="quote.png")
        await ctx.send(file=file)

async def setup(bot):
    await bot.add_cog(QuoteCog(bot))