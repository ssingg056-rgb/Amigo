import sqlite3
import discord
from discord.ext import commands

# --- EXPANDED & MORE POWERFUL SHOP ITEMS ---
HUNT_ITEMS = [
    {"name": "Rusty Rifle", "price": 500, "yield_cash": 200, "resource": "Rabbit Pelt"},
    {"name": "Compound Bow", "price": 2500, "yield_cash": 800, "resource": "Wild Boar Meat"},
    {"name": "Thermal Sniper", "price": 10000, "yield_cash": 3000, "resource": "Grizzly Hide"},
    {"name": "Plasma Blaster", "price": 50000, "yield_cash": 12000, "resource": "Shadow Panther Fur"},
    {"name": "Godslayer Railgun", "price": 250000, "yield_cash": 50000, "resource": "Mythical Dragon Scale"}
]

MINE_ITEMS = [
    {"name": "Wooden Pickaxe", "price": 400, "yield_cash": 150, "resource": "Coal"},
    {"name": "Iron Pickaxe", "price": 2000, "yield_cash": 700, "resource": "Iron Ore"},
    {"name": "Diamond Drill", "price": 8500, "yield_cash": 2800, "resource": "Gold Nugget"},
    {"name": "Laser Mining Rig", "price": 40000, "yield_cash": 10000, "resource": "Raw Diamond"},
    {"name": "Quantum Antimatter Drill", "price": 200000, "yield_cash": 45000, "resource": "Cosmic Crystal"}
]

FISH_ITEMS = [
    {"name": "Wooden Fishing Rod", "price": 350, "yield_cash": 120, "resource": "Small Fish"},
    {"name": "Fiberglass Rod", "price": 1800, "yield_cash": 600, "resource": "Salmon"},
    {"name": "Deep-Sea Trawler Net", "price": 7500, "yield_cash": 2500, "resource": "Giant Squid"},
    {"name": "Sonar Sub-Submersible", "price": 35000, "yield_cash": 9000, "resource": "Golden Carp"},
    {"name": "Neptune's Trident Sub", "price": 180000, "yield_cash": 40000, "resource": "Leviathan Scale"}
]

ALL_SHOP_ITEMS = HUNT_ITEMS + MINE_ITEMS + FISH_ITEMS

# Add your Discord user ID here (and others if you want to grant them admin access)
OWNER_IDS = [1521196096465010719]

def is_bot_owner():
    def predicate(ctx):
        return ctx.author.id in OWNER_IDS
    return commands.check(predicate)

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

    def add_inventory(self, user_id, item_name, qty=1):
        self.cursor.execute("""
            INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, ?)
            ON CONFLICT(user_id, item_name) DO UPDATE SET quantity = quantity + ?
        """, (user_id, item_name, qty, qty))
        self.conn.commit()

    @commands.command(name="economyhelp", aliases=["ehelp"])
    async def economyhelp(self, ctx):
        embed = discord.Embed(
            title="📖 Advanced Economy & Resource Gathering Help",
            description="Gather rare resources, upgrade to powerful tier gear, and manage your wealth!",
            color=discord.Color.blue()
        )
        embed.add_field(name="💰 Core Financials", value="`.bal` - Check wallet & bank\n`.work` - Earn initial cash\n`.deposit <amount>` - Secure cash in bank\n`.withdraw <amount>` - Pull cash out\n`.leaderboard` - View richest users", inline=False)
        embed.add_field(name="🏕️ Gathering & Resources", value="`.hunt` - Hunt wildlife to get pelts/meat & cash\n`.mine` - Mine the earth to gather rare ores & cash\n`.fish` - Catch aquatic creatures & rare items", inline=False)
        embed.add_field(name="🛒 Shop & Inventory", value="`.shop` - View powerful progressive upgrade gear\n`.buy <item name>` - Purchase items/tools\n`.inventory` - Check your gathered resources & gear", inline=False)
        embed.add_field(name="🛠️ Owner Commands", value="`.normalize` - Reset economy\n`.givemoney` / `.takemoney` / `.setbalance`", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="balance", aliases=["bal"])
    async def balance(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        bal, bank = self.get_user(target.id)
        embed = discord.Embed(title=f"🪙 {target.display_name}'s Balance", color=discord.Color.gold())
        embed.add_field(name="Wallet", value=f"${bal:,}", inline=True)
        embed.add_field(name="Bank", value=f"${bank:,}", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="leaderboard", aliases=["lb", "top"])
    async def leaderboard(self, ctx):
        self.cursor.execute("SELECT user_id, (balance + bank) as total FROM users ORDER BY total DESC LIMIT 10")
        rows = self.cursor.fetchall()

        embed = discord.Embed(title="🏆 Wealth Leaderboard - Top 10", color=discord.Color.gold())
        if not rows:
            embed.description = "No users found in the economy yet."
        else:
            desc = []
            for idx, (uid, total) in enumerate(rows, start=1):
                member = ctx.guild.get_member(uid)
                name = member.display_name if member else f"User ID: {uid}"
                desc.append(f"**{idx}.** {name} — **${total:,}**")
            embed.description = "\n".join(desc)
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

        if amt <= 0 or bal < amt:
            return await ctx.send("❌ Invalid deposit amount or insufficient wallet funds.")

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

        if amt <= 0 or bank < amt:
            return await ctx.send("❌ Invalid withdrawal amount or insufficient bank funds.")

        self.cursor.execute("UPDATE users SET balance = balance + ?, bank = bank - ? WHERE user_id = ?", (amt, amt, user_id))
        self.conn.commit()
        await ctx.send(f"💵 Successfully withdrew **${amt:,}** from your bank account.")

    @commands.command(name="shop")
    async def shop(self, ctx):
        embed = discord.Embed(title="🛒 Ultimate Progressive Equipment Shop", description="Buy powerful gear to gather high-tier resources and massive cash payouts!", color=discord.Color.green())
        
        hunt_str = "\n".join([f"• **{i['name']}** — ${i['price']:,} *(Yields {i['resource']} & ~${i['yield_cash']:,})*" for i in HUNT_ITEMS])
        mine_str = "\n".join([f"• **{i['name']}** — ${i['price']:,} *(Yields {i['resource']} & ~${i['yield_cash']:,})*" for i in MINE_ITEMS])
        fish_str = "\n".join([f"• **{i['name']}** — ${i['price']:,} *(Yields {i['resource']} & ~${i['yield_cash']:,})*" for i in FISH_ITEMS])

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
            return await ctx.send("❌ That item does not exist in the shop! Check `.shop` for exact names.")

        bal, bank = self.get_user(user_id)
        if bal < item_match["price"]:
            return await ctx.send(f"❌ You need ${item_match['price']:,}, but you only have ${bal:,} in your wallet.")

        self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (bal - item_match["price"], user_id))
        self.add_inventory(user_id, item_match["name"], 1)

        await ctx.send(f"✅ Successfully purchased **{item_match['name']}** for ${item_match['price']:,}!")

    @commands.command(name="inventory", aliases=["inv"])
    async def inventory(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        self.cursor.execute("SELECT item_name, quantity FROM inventory WHERE user_id = ? AND quantity > 0", (target.id,))
        rows = self.cursor.fetchall()

        embed = discord.Embed(title=f"🎒 {target.display_name}'s Inventory & Resources", color=discord.Color.purple())
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
        reward_cash = best_gear["yield_cash"]
        resource_found = best_gear["resource"]
        
        bal, bank = self.get_user(user_id)
        self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (bal + reward_cash, user_id))
        self.add_inventory(user_id, resource_found, 1)
        
        await ctx.send(f"🏹 Using your **{best_gear['name']}**, you hunted and received **1x {resource_found}** + **${reward_cash:,}**!")

    @commands.command(name="mine")
    async def mine(self, ctx):
        user_id = ctx.author.id
        best_gear = self.get_best_item(user_id, MINE_ITEMS)
        reward_cash = best_gear["yield_cash"]
        resource_found = best_gear["resource"]
        
        bal, bank = self.get_user(user_id)
        self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (bal + reward_cash, user_id))
        self.add_inventory(user_id, resource_found, 1)
        
        await ctx.send(f"⛏️ Using your **{best_gear['name']}**, you mined and gathered **1x {resource_found}** + **${reward_cash:,}**!")

    @commands.command(name="fish")
    async def fish(self, ctx):
        user_id = ctx.author.id
        best_gear = self.get_best_item(user_id, FISH_ITEMS)
        reward_cash = best_gear["yield_cash"]
        resource_found = best_gear["resource"]
        
        bal, bank = self.get_user(user_id)
        self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (bal + reward_cash, user_id))
        self.add_inventory(user_id, resource_found, 1)
        
        await ctx.send(f"🎣 Using your **{best_gear['name']}**, you fished and reeled in **1x {resource_found}** + **${reward_cash:,}**!")

    @commands.command(name="normalize")
    @is_bot_owner()
    async def normalize(self, ctx):
        self.cursor.execute("DELETE FROM users")
        self.cursor.execute("DELETE FROM inventory")
        self.conn.commit()
        await ctx.send("⚠️ **ECONOMY NORMALIZED:** All user balances and inventories have been completely wiped and reset.")

    @commands.command(name="givemoney")
    @is_bot_owner()
    async def givemoney(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("❌ Amount must be greater than zero.")
        self.get_user(member.id)
        self.cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, member.id))
        self.conn.commit()
        await ctx.send(f"✅ Added **${amount:,}** to {member.mention}'s wallet.")

    @commands.command(name="takemoney")
    @is_bot_owner()
    async def takemoney(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("❌ Amount must be greater than zero.")
        self.get_user(member.id)
        self.cursor.execute("UPDATE users SET balance = MAX(0, balance - ?) WHERE user_id = ?", (amount, member.id))
        self.conn.commit()
        await ctx.send(f"✅ Removed **${amount:,}** from {member.mention}'s wallet.")

    @commands.command(name="setbalance")
    @is_bot_owner()
    async def setbalance(self, ctx, member: discord.Member, amount: int):
        if amount < 0:
            return await ctx.send("❌ Balance cannot be negative.")
        self.get_user(member.id)
        self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (amount, member.id))
        self.conn.commit()
        await ctx.send(f"✅ Set {member.mention}'s wallet balance to **${amount:,}**.")

async def setup(bot):
    await bot.add_cog(FullEconomyCog(bot))