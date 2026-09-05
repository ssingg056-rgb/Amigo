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
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1
            )
        ''')
        self.conn.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        MAX_LEVEL = 100
        user_id = message.author.id

        self.cursor.execute('SELECT xp, level FROM users WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()

        if result is None:
            xp, level = 10, 1
            self.cursor.execute(
                'INSERT INTO users (user_id, xp, level) VALUES (?, ?, ?)',
                (user_id, xp, level)
            )
        else:
            xp, level = result

            if level < MAX_LEVEL:
                xp += 10

                if xp >= 100 * level:
                    level += 1
                    xp = 0
                    await message.channel.send(f'GG {message.author.mention}, you leveled up to level {level}!')

            self.cursor.execute(
                'UPDATE users SET xp = ?, level = ? WHERE user_id = ?',
                (xp, level, user_id)
            )

        self.conn.commit()
        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(LevelingCog(bot))