import os
print("Files in current directory:", os.listdir("."))
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
import threading

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True  # Required to detect when members join
intents.message_content = True  # Required to read commands

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

# Flask server to bind to Render's port
app = Flask('')

@app.route('/')
def home():
    return "Bot is active and running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.start()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}!")

async def main():
    async with bot:
        await bot.load_extension("welcome_cog")
        await bot.load_extension("quote_cog")
        await bot.load_extension("economy_cog")
        await bot.load_extension("roleplay_cog")
        await bot.load_extension("help_cog")
        await bot.load_extension("leveling_cog")
        await bot.load_extension("announcement_cog")
        await bot.start(TOKEN)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())