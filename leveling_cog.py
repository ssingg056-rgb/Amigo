import sqlite3
import discord
from discord.ext import commands

class LevelingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        self.conn = sqlite3.connect("economy.db") # Shares the database with your economy cog
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS leveling (
                user_id INTEGER PRIMARY KEY,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1
            )
        """)
        self.conn.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        user_id = message.author.id
        
        # Fetch or initialize user XP stats
        self.cursor.execute("SELECT xp, level FROM leveling WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        
        if not row:
            self.cursor.execute("INSERT INTO leveling (user_id, xp, level) VALUES (?, 15, 1)", (user_id,))
            self.conn.commit()
            return

        xp, level = row
        gained_xp = 15  # Fixed XP per message (or randomize if you prefer)
        new_xp = xp + gained_xp
        
        # Calculate level threshold (e.g., Level * 100 XP required to level up)
        next_level_xp = level * 100

        if new_xp >= next_level_xp:
            new_level = level + 1
            # Level-up cash bonus that scales higher the more active they are!
            cash_reward = new_level * 500 
            
            # Update leveling table and bonus cash in the users table
            self.cursor.execute("UPDATE leveling SET xp = ?, level = ? WHERE user_id = ?", (new_xp - next_level_xp, new_level, user_id))
            self.cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (cash_reward, user_id))
            self.conn.commit()
            
            await message.channel.send(f"🎉 Congrats {message.author.mention}! You leveled up to **Level {new_level}** and earned a reward of **${cash_reward:,}**!")
        else:
            self.cursor.execute("UPDATE leveling SET xp = ? WHERE user_id = ?", (new_xp, user_id))
            self.conn.commit()

    @commands.command(name="level", aliases=["lvl", "rank"])
    async def level(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        self.cursor.execute("SELECT xp, level FROM leveling WHERE user_id = ?", (target.id,))
        row = self.cursor.fetchone()
        
        if not row:
            lvl, xp = 1, 0
        else:
            xp, lvl = row

        next_goal = lvl * 100
        embed = discord.Embed(title=f"📊 {target.display_name}'s Rank & Level", color=discord.Color.blue())
        embed.add_field(name="Level", value=str(lvl), inline=True)
        embed.add_field(name="Current XP", value=f"{xp} / {next_goal}", inline=True)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LevelingCog(bot))