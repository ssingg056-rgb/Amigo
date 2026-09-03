import io
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import aiohttp

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Replace with your actual welcome channel ID
        self.WELCOME_CHANNEL_ID = 1543928907307417651

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = self.bot.get_channel(self.WELCOME_CHANNEL_ID)
        if not channel:
            return

        # 1. Create a blank dark-grey background image (900x450 pixels)
        base = Image.new("RGBA", (900, 450), color=(40, 40, 40, 255))
        draw = ImageDraw.Draw(base)

        # 2. Download and process the user's avatar into a circle
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        async with aiohttp.ClientSession() as session:
            async with session.get(str(avatar_url)) as resp:
                if resp.status == 200:
                    avatar_bytes = await resp.read()
                    avatar_image = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")

                    # Resize avatar to 260x260 pixels
                    avatar_image = avatar_image.resize((260, 260), Image.Resampling.LANCZOS)

                    # Create a circular mask for the avatar
                    mask = Image.new("L", (260, 260), 0)
                    mask_draw = ImageDraw.Draw(mask)
                    mask_draw.ellipse((0, 0, 260, 260), fill=255)

                    # Paste avatar onto base image at coordinates (x=90, y=95)
                    base.paste(avatar_image, (90, 95), mask)

        # 3. Load font safely (make sure to include your font file in your project repo!)
        try:
            title_font = ImageFont.truetype("arial.ttf", 40)
            sub_font = ImageFont.truetype("arial.ttf", 26)
        except IOError:
            title_font = ImageFont.load_default()
            sub_font = ImageFont.load_default()

        # Format text, keeping special character fonts intact
        safe_name = member.display_name
        welcome_text = f"Welcome to our server !\n{safe_name}!"
        member_count_text = f" You're our {member.guild.member_count}th Member!"

        # Draw text onto the image
        draw.text((380, 100), welcome_text, fill="white", font=title_font)
        draw.text((380, 280), member_count_text, fill=(180, 180, 180, 255), font=sub_font)

        # 4. Save to byte buffer
        buffer = io.BytesIO()
        base.save(buffer, format="PNG")
        buffer.seek(0)

        file = discord.File(fp=buffer, filename="welcome.png")

        # 5. Send both the text message mentioning the user and the image file
        text_message = f"Welcome to our server, {member.mention}!"
        await channel.send(content=text_message, file=file)

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))