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
        
        # Default values
        display_name = ctx.author.display_name
        username = str(ctx.author.name)
        avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        attached_image_url = None

        if target_message:
            display_name = target_message.author.display_name
            username = str(target_message.author.name)
            avatar_url = target_message.author.avatar.url if target_message.author.avatar else target_message.author.default_avatar.url
            
            if not text:
                text = target_message.content
                
            # Check for image attachment in the quoted message
            if target_message.attachments:
                for attachment in target_message.attachments:
                    if attachment.content_type and "image" in attachment.content_type:
                        attached_image_url = attachment.url
                        break

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

        # 1. Process author's avatar into the left circle with a drop shadow
        avatar_size = 280
        async with aiohttp.ClientSession() as session:
            async with session.get(str(avatar_url)) as resp:
                if resp.status == 200:
                    avatar_bytes = await resp.read()
                    avatar_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
                    avatar_img = avatar_img.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
                    
                    mask = Image.new("L", (avatar_size, avatar_size), 0)
                    mask_draw = ImageDraw.Draw(mask)
                    mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
                    
                    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                    shadow_draw = ImageDraw.Draw(shadow)
                    shadow_x, shadow_y = 80, 110
                    shadow_draw.ellipse((shadow_x + 8, shadow_y + 12, shadow_x + avatar_size + 8, shadow_y + avatar_size + 12), fill=(0, 0, 0, 90))
                    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
                    base.paste(shadow, (0, 0), shadow)
                    base.paste(avatar_img, (shadow_x, shadow_y), mask)

        author_text = f"— {display_name} (@{username})"
        author_bbox = draw.textbbox((0, 0), author_text, font=author_font)
        author_width = author_bbox[2] - author_bbox[0]
        right_section_center = 700

        # 2. Handle Right Side Content (Image Attachment vs Text)
        if attached_image_url:
            # Download and paste the quoted image on the right side
            async with aiohttp.ClientSession() as session:
                async with session.get(str(attached_image_url)) as resp:
                    if resp.status == 200:
                        img_bytes = await resp.read()
                        quoted_img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
                        
                        # Resize to fit nicely on the right side (max width 420, max height 280)
                        quoted_img.thumbnail((420, 280), Image.Resampling.LANCZOS)
                        qi_width, qi_height = quoted_img.size
                        
                        qi_x = right_section_center - (qi_width / 2)
                        qi_y = (height - qi_height - 40) / 2 - 10
                        
                        # Optional subtle shadow for the quoted image
                        img_shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                        img_shadow_draw = ImageDraw.Draw(img_shadow)
                        img_shadow_draw.rectangle((qi_x + 4, qi_y + 6, qi_x + qi_width + 4, qi_y + qi_height + 6), fill=(0, 0, 0, 70))
                        img_shadow = img_shadow.filter(ImageFilter.GaussianBlur(8))
                        base.paste(img_shadow, (0, 0), img_shadow)
                        
                        base.paste(quoted_img, (int(qi_x), int(qi_y)), quoted_img)
                        
                        # Place author text below the quoted image
                        author_x = right_section_center - (author_width / 2)
                        draw.text((author_x, qi_y + qi_height + 15), author_text, fill=(75, 75, 75, 255), font=author_font)
        elif text:
            # Standard text quote wrapping and rendering
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

            formatted_lines = []
            for i, line in enumerate(lines):
                if i == 0:
                    line = f'“{line}'
                if i == len(lines) - 1:
                    line = f'{line}”'
                formatted_lines.append(line)

            line_height = 46
            total_text_height = len(formatted_lines) * line_height
            total_block_height = total_text_height + 25 + 25
            start_y = (height - total_block_height) / 2 - 15

            current_y = start_y
            for line in formatted_lines:
                bbox = draw.textbbox((0, 0), line, font=quote_font)
                line_width = bbox[2] - bbox[0]
                line_x = right_section_center - (line_width / 2)
                
                draw.text((line_x, current_y), line, fill=(35, 35, 35, 255), font=quote_font)
                current_y += line_height

            current_y += 10
            author_x = right_section_center - (author_width / 2)
            draw.text((author_x, current_y), author_text, fill=(75, 75, 75, 255), font=author_font)
        else:
            author_x = right_section_center - (author_width / 2)
            draw.text((author_x, height / 2 - 10), author_text, fill=(75, 75, 75, 255), font=author_font)

        # Save and send output image
        buffer = io.BytesIO()
        base.save(buffer, format="PNG")
        buffer.seek(0)

        file = discord.File(fp=buffer, filename="quote.png")
        await ctx.send(file=file)

async def setup(bot):
    await bot.add_cog(QuoteCog(bot))