import sqlite3
import discord
from discord.ext import commands

HUNT_ITEMS = [
    {"name": "Rusty Rifle", "price": 500, "role": "gear", "yield": 200},
    {"name": "Compound Bow", "price": 2500, "role": "gear", "yield": 800},
    {"name": "Thermal Sniper", "price": 10000, "role": "gear", "yield": 3000},
    {"name": "Exosuit Hunter Rig", "price": 50000, "role": "gear", "yield": 12000}
]

MINE_ITEMS = [
    {"name": "Wooden Pickaxe", "price": 400, "role": "gear", "yield": 150},
    {"name": "Iron Pickaxe", "price": 2000, "role": "gear", "yield": 700},
    {"name": "Diamond Drill", "price": 8500, "role": "gear", "yield": 2800},
    {"name": "Laser Mining Rig", "price": 40000, "role": "gear", "yield": 10000}
]

FISH_ITEMS = [
    {"name": "Wooden Fishing Rod", "price": 350, "role": "gear", "yield": 120},
    {"name": "Fiberglass Rod", "price": 1800, "role": "gear", "yield": 600},
    {"name": "Deep-Sea Trawler Net", "price": 7500, "role": "gear", "yield": 2500},
    {"name": "Sonar Sub-Submersible", "price": 35000, "role": "gear", "yield": 9000}
]

ALL_SHOP_ITEMS = HUNT_ITEMS + MINE_ITEMS + FISH_ITEMS

class FullEconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        self.conn = sqlite3.connect("economy.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 500,
                bank INTEGER DEFAULT 0
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                user_id INTEGER,
                item_name TEXT,
                quantity INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, item_name)
            )
        """)
        self.conn.commit()

    def get_user(self, user_id):
        self.cursor.execute("SELECT balance, bank FROM users WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        if not row:
            self.cursor.execute("INSERT INTO users (user_id, balance, bank) VALUES (?, 500, 0)", (user_id,))
            self.conn.commit()
            return [500, 0]
        return row

    def get_best_item(self, user_id, category_items):
        for item in reversed(category_items):
            self.cursor.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_name = ?", (user_id, item["name"]))
            row = self.cursor.fetchone()
            if row and row[0] > 0:
                return item
        return category_items[0]

    @commands.command(name="economyhelp", aliases=["ehelp"])
    async def economyhelp(self, ctx):
        embed = discord.Embed(
            title="📖 Full Economy & Adventure Help Menu",
            description="Explore, gather resources, buy gear, and manage your wealth!",
            color=discord.Color.blue()
        )
        embed.add_field(name="💰 Core Financials", value="`.bal` - Check wallet & bank\n`.work` - Earn initial cash\n`.deposit <amount>` - Secure cash in bank\n`.withdraw <amount>` - Pull cash out", inline=False)
        embed.add_field(name="🏕️ Gathering & Adventure", value="`.hunt` - Hunt wildlife using your best gear\n`.mine` - Mine ores using your best pickaxe\n`.fish` - Catch fish using your best rod", inline=False)
        embed.add_field(name="🛒 Shop & Inventory", value="`.shop` - View all escalating upgrade gear\n`.buy <item name>` - Purchase items\n`.inventory` - Check your owned equipment", inline=False)
        embed.add_field(name="🛠️ Owner / Admin Commands", value="`.normalize` - Reset all data\n`.givemoney <member> <amount>` - Add money to user\n`.takemoney <member> <amount>` - Remove money from user\n`.setbalance <member> <amount>` - Set exact balance", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="balance", aliases=["bal"])
    async def balance(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        bal, bank = self.get_user(target.id)
        embed = discord.Embed(title=f"🪙 {target.display_name}'s Balance", color=discord.Color.gold())
        embed.add_field(name="Wallet", value=f"${bal:,}", inline=True)
        embed.add_field(name="Bank", value=f"${bank:,}", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="work")
    async def work(self, ctx):
        user_id = ctx.author.id
        bal, bank = self.get_user(user_id)
        earnings = 200
        self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (bal + earnings, user_id))
        self.conn.commit()
        await ctx.send(f"💼 You did a shift and earned **${earnings:,}**!")

    @commands.command(name="deposit", aliases=["dep"])
    async def deposit(self, ctx, amount: str):
        user_id = ctx.author.id
        bal, bank = self.get_user(user_id)
        
        if amount.lower() == "all":
            amt = bal
        else:
            try:
                amt = int(amount)
            except ValueError:
                return await ctx.send("❌ Please enter a valid number or 'all'.")

        if amt <= 0:
            return await ctx.send("❌ You cannot deposit zero or negative amounts.")
        if bal < amt:
            return await ctx.send(f"❌ You don't have ${amt:,} in your wallet.")

        self.cursor.execute("UPDATE users SET balance = balance - ?, bank = bank + ? WHERE user_id = ?", (amt, amt, user_id))
        self.conn.commit()
        await ctx.send(f"🏦 Successfully deposited **${amt:,}** into your bank account.")

    @commands.command(name="withdraw", aliases=["wit", "wd"])
    async def withdraw(self, ctx, amount: str):
        user_id = ctx.author.id
        bal, bank = self.get_user(user_id)
        
        if amount.lower() == "all":
            amt = bank
        else:
            try:
                amt = int(amount)
            except ValueError:
                return await ctx.send("❌ Please enter a valid number or 'all'.")

        if amt <= 0:
            return await ctx.send("❌ You cannot withdraw zero or negative amounts.")
        if bank < amt:
            return await ctx.send(f"❌ You don't have ${amt:,} in your bank.")

        self.cursor.execute("UPDATE users SET balance = balance + ?, bank = bank - ? WHERE user_id = ?", (amt, amt, user_id))
        self.conn.commit()
        await ctx.send(f"💵 Successfully withdrew **${amt:,}** from your bank account.")

    @commands.command(name="shop")
    async def shop(self, ctx):
        embed = discord.Embed(title="🛒 Full Progressive Equipment Shop", description="Items get progressively more expensive and yield higher payouts!", color=discord.Color.green())
        
        hunt_str = "\n".join([f"• **{i['name']}** - ${i['price']:,} (Yields ~${i['yield']:,})" for i in HUNT_ITEMS])
        mine_str = "\n".join([f"• **{i['name']}** - ${i['price']:,} (Yields ~${i['yield']:,})" for i in MINE_ITEMS])
        fish_str = "\n".join([f"• **{i['name']}** - ${i['price']:,} (Yields ~${i['yield']:,})" for i in FISH_ITEMS])

        embed.add_field(name="🏹 Hunting Gear", value=hunt_str, inline=False)
        embed.add_field(name="⛏️ Mining Gear", value=mine_str, inline=False)
        embed.add_field(name="🎣 Fishing Gear", value=fish_str, inline=False)
        embed.set_footer(text="Type .buy [exact item name] to purchase.")
        await ctx.send(embed=embed)

    @commands.command(name="buy")
    async def buy(self, ctx, *, item_name: str):
        user_id = ctx.author.id
        item_match = next((i for i in ALL_SHOP_ITEMS if i["name"].lower() == item_name.lower()), None)
        
        if not item_match:
            return await ctx.send("❌ That item does not exist in the shop! Check `.shop` for names.")

        bal, bank = self.get_user(user_id)
        if bal < item_match["price"]:
            return await ctx.send(f"❌ You need ${item_match['price']:,}, but you only have ${bal:,} in your wallet.")

        self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (bal - item_match["price"], user_id))
        self.cursor.execute("""
            INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, 1)
            ON CONFLICT(user_id, item_name) DO UPDATE SET quantity = quantity + 1
        """, (user_id, item_match["name"]))
        self.conn.commit()

        await ctx.send(f"✅ Successfully purchased **{item_match['name']}** for ${item_match['price']:,}!")

    @commands.command(name="inventory", aliases=["inv"])
    async def inventory(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        self.cursor.execute("SELECT item_name, quantity FROM inventory WHERE user_id = ? AND quantity > 0", (target.id,))
        rows = self.cursor.fetchall()

        embed = discord.Embed(title=f"🎒 {target.display_name}'s Inventory", color=discord.Color.purple())
        if not rows:
            embed.description = "Inventory is completely empty."
        else:
            inv_str = "\n".join([f"• {row[0]} (x{row[1]})" for row in rows])
            embed.description = inv_str
        await ctx.send(embed=embed)

    @commands.command(name="hunt")
    async def hunt(self, ctx):
        user_id = ctx.author.id
        best_gear = self.get_best_item(user_id, HUNT_ITEMS)
        reward = best_gear["yield"]
        
        bal, bank = self.get_user(user_id)
        self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (bal + reward, user_id))
        self.conn.commit()
        await ctx.send(f"🏹 Using your **{best_gear['name']}**, you went hunting and secured game worth **${reward:,}**!")

    @commands.command(name="mine")
    async def mine(self, ctx):
        user_id = ctx.author.id
        best_gear = self.get_best_item(user_id, MINE_ITEMS)
        reward = best_gear["yield"]
        
        bal, bank = self.get_user(user_id)
        self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (bal + reward, user_id))
        self.conn.commit()
        await ctx.send(f"⛏️ Using your **{best_gear['name']}**, you extracted valuable minerals worth **${reward:,}**!")

    @commands.command(name="fish")
    async def fish(self, ctx):
        user_id = ctx.author.id
        best_gear = self.get_best_item(user_id, FISH_ITEMS)
        reward = best_gear["yield"]
        
        bal, bank = self.get_user(user_id)
        self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (bal + reward, user_id))
        self.conn.commit()
        await ctx.send(f"🎣 Using your **{best_gear['name']}**, you reeled in a massive catch worth **${reward:,}**!")

    # --- FULL OWNER ADMIN COMMAND SUITE ---

    @commands.command(name="normalize")
    @commands.is_owner()
    async def normalize(self, ctx):
        self.cursor.execute("DELETE FROM users")
        self.cursor.execute("DELETE FROM inventory")
        self.conn.commit()
        await ctx.send("⚠️ **ECONOMY NORMALIZED:** All user balances and inventories have been completely wiped and reset.")

    @commands.command(name="givemoney")
    @commands.is_owner()
    async def givemoney(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("❌ Amount must be greater than zero.")
        self.get_user(member.id) # Ensure user exists
        self.cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, member.id))
        self.conn.commit()
        await ctx.send(f"✅ Added **${amount:,}** to {member.mention}'s wallet.")

    @commands.command(name="takemoney")
    @commands.is_owner()
    async def takemoney(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("❌ Amount must be greater than zero.")
        self.get_user(member.id)
        self.cursor.execute("UPDATE users SET balance = MAX(0, balance - ?) WHERE user_id = ?", (amount, member.id))
        self.conn.commit()
        await ctx.send(f"✅ Removed **${amount:,}** from {member.mention}'s wallet.")

    @commands.command(name="setbalance")
    @commands.is_owner()
    async def setbalance(self, ctx, member: discord.Member, amount: int):
        if amount < 0:
            return await ctx.send("❌ Balance cannot be negative.")
        self.get_user(member.id)
        self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (amount, member.id))
        self.conn.commit()
        await ctx.send(f"✅ Set {member.mention}'s wallet balance to **${amount:,}**.")

async def setup(bot):
    await bot.add_cog(FullEconomyCog(bot))