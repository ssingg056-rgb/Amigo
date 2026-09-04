import sqlite3
import random
import discord
from discord.ext import commands

# --- EXPANDED OMNIVERSAL PROGRESSIVE GEAR & RESOURCES ---
HUNT_ITEMS = [
    {"name": "Rusty Rifle", "price": 500, "yield_cash": 200, "resource": "Rabbit Pelt", "tier": "Common"},
    {"name": "Compound Bow", "price": 2500, "yield_cash": 800, "resource": "Wild Boar Meat", "tier": "Uncommon"},
    {"name": "Thermal Sniper", "price": 10000, "yield_cash": 3000, "resource": "Grizzly Hide", "tier": "Rare"},
    {"name": "Plasma Blaster", "price": 50000, "yield_cash": 12000, "resource": "Shadow Panther Fur", "tier": "Epic"},
    {"name": "Godslayer Railgun", "price": 250000, "yield_cash": 50000, "resource": "Mythical Dragon Scale", "tier": "Legendary"},
    {"name": "Universal Void Annihilator", "price": 1500000, "yield_cash": 200000, "resource": "Celestial Essence", "tier": "Universal"},
    {"name": "Omniversal Singularity Rifle", "price": 10000000, "yield_cash": 1000000, "resource": "Omni-God Core", "tier": "Omniversal"}
]

MINE_ITEMS = [
    {"name": "Wooden Pickaxe", "price": 400, "yield_cash": 150, "resource": "Coal", "tier": "Common"},
    {"name": "Iron Pickaxe", "price": 2000, "yield_cash": 700, "resource": "Iron Ore", "tier": "Uncommon"},
    {"name": "Diamond Drill", "price": 8500, "yield_cash": 2800, "resource": "Gold Nugget", "tier": "Rare"},
    {"name": "Laser Mining Rig", "price": 40000, "yield_cash": 10000, "resource": "Raw Diamond", "tier": "Epic"},
    {"name": "Quantum Antimatter Drill", "price": 200000, "yield_cash": 45000, "resource": "Cosmic Crystal", "tier": "Legendary"},
    {"name": "Supercluster Core Excavator", "price": 1200000, "yield_cash": 180000, "resource": "Stellar Shard", "tier": "Universal"},
    {"name": "Omni-Tectonic Reality Breaker", "price": 8000000, "yield_cash": 900000, "resource": "Primordial Matter", "tier": "Omniversal"}
]

FISH_ITEMS = [
    {"name": "Wooden Fishing Rod", "price": 350, "yield_cash": 120, "resource": "Small Fish", "tier": "Common"},
    {"name": "Fiberglass Rod", "price": 1800, "yield_cash": 600, "resource": "Salmon", "tier": "Uncommon"},
    {"name": "Deep-Sea Trawler Net", "price": 7500, "yield_cash": 2500, "resource": "Giant Squid", "tier": "Rare"},
    {"name": "Sonar Sub-Submersible", "price": 35000, "yield_cash": 9000, "resource": "Golden Carp", "tier": "Epic"},
    {"name": "Neptune's Trident Sub", "price": 180000, "yield_cash": 40000, "resource": "Leviathan Scale", "tier": "Legendary"},
    {"name": "Event Horizon Deep-Sub", "price": 1000000, "yield_cash": 150000, "resource": "Abyssal Singularity", "tier": "Universal"},
    {"name": "Omniversal Time-Tide Harpoon", "price": 7500000, "yield_cash": 800000, "resource": "Eternity Leviathan Tear", "tier": "Omniversal"}
]

# Sell value dictionary for resources gathered
RESOURCE_VALUES = {
    "Rabbit Pelt": 50, "Wild Boar Meat": 180, "Grizzly Hide": 700, "Shadow Panther Fur": 2800, 
    "Mythical Dragon Scale": 12000, "Celestial Essence": 60000, "Omni-God Core": 300000,
    "Coal": 40, "Iron Ore": 160, "Gold Nugget": 650, "Raw Diamond": 2500, 
    "Cosmic Crystal": 11000, "Stellar Shard": 55000, "Primordial Matter": 280000,
    "Small Fish": 35, "Salmon": 140, "Giant Squid": 600, "Golden Carp": 2200, 
    "Leviathan Scale": 10000, "Abyssal Singularity": 50000, "Eternity Leviathan Tear": 250000
}

ALL_SHOP_ITEMS = HUNT_ITEMS + MINE_ITEMS + FISH_ITEMS
OWNER_IDS = [1521196096465010719]  # Replace with your actual Discord User ID

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

    def make_progress_bar(self, current, total):
        filled = int(round(10 * current / total))
        bar = "🟩" * filled + "⬛" * (10 - filled)
        return f"[{bar}] {current}/{total} HP"

    @commands.command(name="economyhelp", aliases=["ehelp"])
    async def economyhelp(self, ctx):
        embed = discord.Embed(
            title="📖 Omniversal Economy & Gathering Help",
            description="Progress through tiers up to Omniversal gear, monitor action health bars, and sell resources!",
            color=discord.Color.blue()
        )
        embed.add_field(name="💰 Financials & Selling", value="`.bal` - Check wallet/bank\n`.work` - Quick job\n`.deposit` / `.withdraw`\n`.sell <item> <amount>` - Sell gathered items for cash", inline=False)
        embed.add_field(name="🏕️ Gathering (With Progress Bars)", value="`.hunt` - Track down game with animal health bars\n`.mine` - Extract ores with structural rock meters\n`.fish` - Reel in catches using stamina meters", inline=False)
        embed.add_field(name="🛒 Shop & Upgrades", value="`.shop` - Browse Common to Omniversal gear\n`.buy <item>` - Upgrade your tools\n`.inventory` - View items", inline=False)
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
            desc = [f"**{idx}.** <@!{uid}> — **${total:,}**" for idx, (uid, total) in enumerate(rows, start=1)]
            embed.description = "\n".join(desc)
        await ctx.send(embed=embed)

    @commands.command(name="work")
    async def work(self, ctx):
        user_id = ctx.author.id
        bal, _ = self.get_user(user_id)
        earnings = 200
        self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (bal + earnings, user_id))
        self.conn.commit()
        await ctx.send(f"💼 You worked a shift and earned **${earnings:,}**!")

    @commands.command(name="deposit", aliases=["dep"])
    async def deposit(self, ctx, amount: str):
        user_id = ctx.author.id
        bal, _ = self.get_user(user_id)
        amt = bal if amount.lower() == "all" else int(amount)
        if amt <= 0 or bal < amt:
            return await ctx.send("❌ Invalid deposit amount.")
        self.cursor.execute("UPDATE users SET balance = balance - ?, bank = bank + ? WHERE user_id = ?", (amt, amt, user_id))
        self.conn.commit()
        await ctx.send(f"🏦 Deposited **${amt:,}** into your bank.")

    @commands.command(name="withdraw", aliases=["wit", "wd"])
    async def withdraw(self, ctx, amount: str):
        user_id = ctx.author.id
        _, bank = self.get_user(user_id)
        amt = bank if amount.lower() == "all" else int(amount)
        if amt <= 0 or bank < amt:
            return await ctx.send("❌ Invalid withdrawal amount.")
        self.cursor.execute("UPDATE users SET balance = balance + ?, bank = bank - ? WHERE user_id = ?", (amt, amt, user_id))
        self.conn.commit()
        await ctx.send(f"💵 Withdrew **${amt:,}** from your bank.")

    @commands.command(name="shop")
    async def shop(self, ctx):
        embed = discord.Embed(title="🛒 Omniversal Equipment Shop", description="From Common tools all the way to Omniversal gear!", color=discord.Color.green())
        
        def format_tier(items):
            return "\n".join([f"• **{i['name']}** `[{i['tier']}]` — ${i['price']:,} \n  └ *Yields {i['resource']} (~${i['yield_cash']:,})*" for i in items])

        embed.add_field(name="🏹 Hunting Gear", value=format_tier(HUNT_ITEMS), inline=False)
        embed.add_field(name="⛏️ Mining Gear", value=format_tier(MINE_ITEMS), inline=False)
        embed.add_field(name="🎣 Fishing Gear", value=format_tier(FISH_ITEMS), inline=False)
        embed.set_footer(text="Type .buy [item name] to upgrade.")
        await ctx.send(embed=embed)

    @commands.command(name="buy")
    async def buy(self, ctx, *, item_name: str):
        user_id = ctx.author.id
        item_match = next((i for i in ALL_SHOP_ITEMS if i["name"].lower() == item_name.lower()), None)
        if not item_match:
            return await ctx.send("❌ Item not found in the shop!")
        bal, _ = self.get_user(user_id)
        if bal < item_match["price"]:
            return await ctx.send(f"❌ You need ${item_match['price']:,} to buy this.")
        self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (bal - item_match["price"], user_id))
        self.add_inventory(user_id, item_match["name"], 1)
        await ctx.send(f"✅ Successfully purchased **{item_match['name']}** for ${item_match['price']:,}!")

    @commands.command(name="sell")
    async def sell(self, ctx, amount: int, *, item_name: str):
        user_id = ctx.author.id
        if amount <= 0:
            return await ctx.send("❌ Amount must be greater than zero.")
        
        # Match inventory case-insensitively
        self.cursor.execute("SELECT item_name, quantity FROM inventory WHERE user_id = ? AND LOWER(item_name) = ?", (user_id, item_name.lower()))
        row = self.cursor.fetchone()
        if not row or row[1] < amount:
            return await ctx.send("❌ You don't have enough of that item in your inventory to sell.")
        
        actual_name = row[0]
        unit_price = RESOURCE_VALUES.get(actual_name, 20)  # Default fallback price
        total_payout = unit_price * amount

        self.cursor.execute("UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_name = ?", (amount, user_id, actual_name))
        self.cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (total_payout, user_id))
        self.conn.commit()
        await ctx.send(f"🤝 Sold **{amount}x {actual_name}** for **${total_payout:,}**!")

    @commands.command(name="inventory", aliases=["inv"])
    async def inventory(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        self.cursor.execute("SELECT item_name, quantity FROM inventory WHERE user_id = ? AND quantity > 0", (target.id,))
        rows = self.cursor.fetchall()
        embed = discord.Embed(title=f"🎒 {target.display_name}'s Inventory & Resources", color=discord.Color.purple())
        embed.description = "\n".join([f"• {r[0]} (x{r[1]})" for r in rows]) if rows else "Inventory is empty."
        await ctx.send(embed=embed)

    @commands.command(name="hunt")
    async def hunt(self, ctx):
        user_id = ctx.author.id
        best_gear = self.get_best_item(user_id, HUNT_ITEMS)
        max_hp = random.randint(50, 100)
        progress_msg = self.make_progress_bar(max_hp, max_hp)
        
        bal, _ = self.get_user(user_id)
        self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (bal + best_gear["yield_cash"], user_id))
        self.add_inventory(user_id, best_gear["resource"], 1)
        
        await ctx.send(f"🏹 **Animal Tracked ({best_gear['tier']} Tier)!** Target Health: {progress_msg}\n🎯 Using your **{best_gear['name']}**, you hunted successfully and gained **1x {best_gear['resource']}** + **${best_gear['yield_cash']:,}**!")

    @commands.command(name="mine")
    async def mine(self, ctx):
        user_id = ctx.author.id
        best_gear = self.get_best_item(user_id, MINE_ITEMS)
        max_durability = random.randint(50, 100)
        progress_msg = self.make_progress_bar(max_durability, max_durability)
        
        bal, _ = self.get_user(user_id)
        self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (bal + best_gear["yield_cash"], user_id))
        self.add_inventory(user_id, best_gear["resource"], 1)
        
        await ctx.send(f"⛏️ **Rock Deposit ({best_gear['tier']} Tier)!** Structural Integrity: {progress_msg}\n💎 Using your **{best_gear['name']}**, you mined and secured **1x {best_gear['resource']}** + **${best_gear['yield_cash']:,}**!")

    @commands.command(name="fish")
    async def fish(self, ctx):
        user_id = ctx.author.id
        best_gear = self.get_best_item(user_id, FISH_ITEMS)
        max_stamina = random.randint(50, 100)
        progress_msg = self.make_progress_bar(max_stamina, max_stamina)
        
        bal, _ = self.get_user(user_id)
        self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (bal + best_gear["yield_cash"], user_id))
        self.add_inventory(user_id, best_gear["resource"], 1)
        
        await ctx.send(f"🎣 **Catch Hooked ({best_gear['tier']} Tier)!** Fish Stamina: {progress_msg}\n🌊 Using your **{best_gear['name']}**, you reeled in **1x {best_gear['resource']}** + **${best_gear['yield_cash']:,}**!")

    @commands.command(name="normalize")
    @is_bot_owner()
    async def normalize(self, ctx):
        self.cursor.execute("DELETE FROM users")
        self.cursor.execute("DELETE FROM inventory")
        self.conn.commit()
        await ctx.send("⚠️ **ECONOMY NORMALIZED:** All stats wiped.")

    @commands.command(name="givemoney")
    @is_bot_owner()
    async def givemoney(self, ctx, member: discord.Member, amount: int):
        self.get_user(member.id)
        self.cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, member.id))
        self.conn.commit()
        await ctx.send(f"✅ Added ${amount:,} to {member.mention}.")

    @commands.command(name="takemoney")
    @is_bot_owner()
    async def takemoney(self, ctx, member: discord.Member, amount: int):
        self.get_user(member.id)
        self.cursor.execute("UPDATE users SET balance = MAX(0, balance - ?) WHERE user_id = ?", (amount, member.id))
        self.conn.commit()
        await ctx.send(f"✅ Removed ${amount:,} from {member.mention}.")

    @commands.command(name="setbalance")
    @is_bot_owner()
    async def setbalance(self, ctx, member: discord.Member, amount: int):
        self.get_user(member.id)
        self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (amount, member.id))
        self.conn.commit()
        await ctx.send(f"✅ Set {member.mention}'s wallet to ${amount:,}.")

async def setup(bot):
    await bot.add_cog(FullEconomyCog(bot))