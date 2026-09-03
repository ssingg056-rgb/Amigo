import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
import threading

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True  # Required to detect when members join

bot = commands.Bot(command_prefix=".", intents=intents)

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
    await bot.load_extension("welcome_cog")
    await bot.load_extension("quote_cog")

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)