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
        target_message = None
        
        if ctx.message.reference and ctx.message.reference.resolved:
            target_message = ctx.message.reference.resolved
        
        if target_message:
            display_name = target_message.author.display_name
            username = str(target_message.author.name)
            
            # Default to author's avatar URL if no image attachment is found
            image_url = target_message.author.avatar.url if target_message.author.avatar else target_message.author.default_avatar.url
            
            # Check if the target message has an image attachment
            if target_message.attachments:
                attachment = target_message.attachments[0]
                if attachment.content_type and "image" in attachment.content_type:
                    image_url = attachment.url
                    if not text:
                        text = target_message.content or "Aesthetic"
            
            if not text:
                text = target_message.content
        else:
            display_name = ctx.author.display_name
            username = str(ctx.author.name)
            image_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            if not text:
                await ctx.send("Please provide some text or reply to a message/image with `.quo`!")
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
            quote_font = ImageFont.truetype("arialbd.ttf", 36)
            author_font = ImageFont.truetype("arial.ttf", 22)
        except IOError:
            quote_font = ImageFont.load_default()
            author_font = ImageFont.load_default()

        # Process the target image (avatar or attachment) into a circular card with a shadow
        image_size = 280
        async with aiohttp.ClientSession() as session:
            async with session.get(str(image_url)) as resp:
                if resp.status == 200:
                    img_bytes = await resp.read()
                    card_image = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
                    card_image = card_image.resize((image_size, image_size), Image.Resampling.LANCZOS)
                    
                    # Circular mask
                    mask = Image.new("L", (image_size, image_size), 0)
                    mask_draw = ImageDraw.Draw(mask)
                    mask_draw.ellipse((0, 0, image_size, image_size), fill=255)
                    
                    # Drop shadow layer
                    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                    shadow_draw = ImageDraw.Draw(shadow)
                    shadow_x, shadow_y = 80, 110
                    shadow_draw.ellipse((shadow_x + 8, shadow_y + 12, shadow_x + image_size + 8, shadow_y + image_size + 12), fill=(0, 0, 0, 90))
                    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
                    base.paste(shadow, (0, 0), shadow)

                    # Paste image
                    base.paste(card_image, (shadow_x, shadow_y), mask)

        # Intelligent text wrapping for the right side block
        max_text_width = 480
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

        # Add smart quotation marks
        formatted_lines = []
        for i, line in enumerate(lines):
            if i == 0:
                line = f'“{line}'
            if i == len(lines) - 1:
                line = f'{line}”'
            formatted_lines.append(line)

        # Vertical and horizontal alignment calculations for the right side
        line_height = 46
        total_text_height = len(formatted_lines) * line_height
        author_text = f"— {display_name} (@{username})"
        
        author_bbox = draw.textbbox((0, 0), author_text, font=author_font)
        author_width = author_bbox[2] - author_bbox[0]

        total_block_height = total_text_height + 25 + 25
        start_y = (height - total_block_height) / 2 - 15
        
        right_section_center = 700

        # Draw quote text lines centered individually
        current_y = start_y
        for line in formatted_lines:
            bbox = draw.textbbox((0, 0), line, font=quote_font)
            line_width = bbox[2] - bbox[0]
            line_x = right_section_center - (line_width / 2)
            
            draw.text((line_x, current_y), line, fill=(35, 35, 35, 255), font=quote_font)
            current_y += line_height

        # Draw author info centered underneath
        current_y += 10
        author_x = right_section_center - (author_width / 2)
        draw.text((author_x, current_y), author_text, fill=(75, 75, 75, 255), font=author_font)

        # Save and send output image
        buffer = io.BytesIO()
        base.save(buffer, format="PNG")
        buffer.seek(0)

        file = discord.File(fp=buffer, filename="quote.png")
        await ctx.send(file=file)

async def setup(bot):
    await bot.add_cog(QuoteCog(bot))