import discord
from discord.ext import commands
import sqlite3

class LevelingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        self.conn = sqlite3.connect('leveling.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                xp INTEGER,
                level INTEGER
            )
        ''')
        self.conn.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        MAX_LEVEL = 100  # Set your maximum level cap here

        user_id = message.author.id
        self.cursor.execute('SELECT xp, level FROM users WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()

        if result is None:
            self.cursor.execute('INSERT INTO users (user_id, xp, level) VALUES (?, ?, ?)', (user_id, 10, 1))
            self.conn.commit()
        else:
            xp, level = result

            # Stop giving XP if the user has reached the cap
            if level >= MAX_LEVEL:
                return

            xp += 10
            
            if xp >= 100 * level:
                level += 1
                xp = 0
                await message.channel.send(f'GG {message.author.mention}, you leveled up to level {level}!')

            self.cursor.execute('UPDATE users SET xp = ?, level = ? WHERE user_id = ?', (xp, level, user_id))
            self.conn.commit()

async def setup(bot):
    await bot.add_cog(LevelingCog(bot))