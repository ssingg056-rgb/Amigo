import os
import psycopg2
from discord.ext import commands

class LevelingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def get_connection(self):
        # This fetches the DATABASE_URL key you set up in Render
        return psycopg2.connect(os.getenv("DATABASE_URL"))

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Creates the leveling table if it doesn't already exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leveling (
                user_id BIGINT PRIMARY KEY,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user_id = message.author.id
        
        conn = self.get_connection()
        cursor = conn.cursor()

        # Fetch user's current data
        cursor.execute("SELECT xp, level FROM leveling WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()

        MAX_LEVEL = 100  # Sets a cap for the leveling system

        if result is None:
            # Insert user if they don't exist yet
            cursor.execute("INSERT INTO leveling (user_id, xp, level) VALUES (%s, %s, %s)", (user_id, 15, 1))
            conn.commit()
        else:
            xp, level = result
            
            # Check if the user has already reached the maximum level cap
            if level >= MAX_LEVEL:
                cursor.close()
                conn.close()
                return

            xp += 15  # Add XP per message
            needed_xp = level * 100  # Formula for leveling up

            if xp >= needed_xp:
                level += 1
                xp = 0
                # Optional: Send a level-up notification to the channel
                # await message.channel.send(f"Congrats {message.author.mention}, you leveled up to level {level}!")

            # Update database with new stats
            cursor.execute("UPDATE leveling SET xp = %s, level = %s WHERE user_id = %s", (xp, level, user_id))
            conn.commit()

        cursor.close()
        conn.close()

async def setup(bot):
    await bot.add_cog(LevelingCog(bot))