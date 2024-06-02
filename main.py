import os
import json
import time
import discord
import string
import random
from discord.ext import commands

# Discord bot token
DISCORD_TOKEN = ''

# Path to the JSON data files
DATA_DIR = 'data'
WHWID_PATH = os.path.join(DATA_DIR, 'whwid.json')
BHWID_PATH = os.path.join(DATA_DIR, 'bhwid.json')
U_ORDERS_PATH = os.path.join(DATA_DIR, 'u_orders.json')
C_ORDERS_PATH = os.path.join(DATA_DIR, 'c_orders.json')
USERS_PATH = os.path.join(DATA_DIR, 'users.json')
EXPIRE_PATH = os.path.join(DATA_DIR, 'expire.json')
STATUS_PATH = os.path.join(DATA_DIR, 'status.json')

# Load JSON data at startup
def load_json_data():
    with open(WHWID_PATH, 'r') as f:
        whwid_data = json.load(f)
    with open(BHWID_PATH, 'r') as f:
        bhwid_data = json.load(f)
    with open(U_ORDERS_PATH, 'r') as f:
        u_orders_data = json.load(f)
    with open(C_ORDERS_PATH, 'r') as f:
        c_orders_data = json.load(f)
    with open(USERS_PATH, 'r') as f:
        users_data = json.load(f)
    with open(EXPIRE_PATH, 'r') as f:
        expire_data = json.load(f)
    with open(STATUS_PATH, 'r') as f:
        status_data = json.load(f)
    return {
        'whwid': whwid_data,
        'bhwid': bhwid_data,
        'u_orders': u_orders_data,
        'c_orders': c_orders_data,
        'users': users_data,
        'expire': expire_data,
        'status': status_data,
    }

data = load_json_data()

# Save JSON data to files
def save_json_data():
    with open(WHWID_PATH, 'w') as f:
        json.dump(data['whwid'], f, indent=4)
    with open(BHWID_PATH, 'w') as f:
        json.dump(data['bhwid'], f, indent=4)
    with open(U_ORDERS_PATH, 'w') as f:
        json.dump(data['u_orders'], f, indent=4)
    with open(C_ORDERS_PATH, 'w') as f:
        json.dump(data['c_orders'], f, indent=4)
    with open(USERS_PATH, 'w') as f:
        json.dump(data['users'], f, indent=4)
    with open(EXPIRE_PATH, 'w') as f:
        json.dump(data['expire'], f, indent=4)
    with open(STATUS_PATH, 'w') as f:
        json.dump(data['status'], f, indent=4)

# Generate a random string
def generate_random_string(length=8):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

class LicenseManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="check_hwid", description="🔍 Check HWID status")
    async def check_hwid(self, ctx, hwid: str, user: discord.User = None):
        embed = discord.Embed(title="🔍 HWID Status", color=0x007bff)
        if hwid in data['bhwid']:
            expiry = data['bhwid'][hwid]
            if expiry is None:
                expiry = "Permanent"
            else:
                expiry = time.ctime(expiry)
            embed.add_field(name="❌ Status", value="Blacklisted", inline=False)
            embed.add_field(name="⏰ Expiry", value=expiry, inline=False)
        elif hwid in data['whwid']:
            expiry = time.ctime(data['whwid'][hwid])
            embed.add_field(name="✅ Status", value="Whitelisted", inline=False)
            embed.add_field(name="⏰ Expiry", value=expiry, inline=False)
        else:
            embed.add_field(name="⚠️ Error", value="Hardware ID not found", inline=False)
        
        if user:
            await user.send(embed=embed)
            await ctx.respond("✅ HWID status sent to the user.", ephemeral=True)
        else:
            await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(name="verify_user", description="🕵️ Verify a user by HWID")
    async def verify_user(self, ctx, hwid: str, user: discord.User = None):
        embed = discord.Embed(title="🕵️ User Verification", color=0x007bff)
        if hwid in data['users']:
            user_info = data['users'][hwid]
            embed.add_field(name="👤 User Info", value=user_info, inline=False)
        else:
            embed.add_field(name="⚠️ Error", value="User not found", inline=False)
        
        if user:
            await user.send(embed=embed)
            await ctx.respond("✅ User verification sent to the user.", ephemeral=True)
        else:
            await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(name="register_user", description="📝 Register a new user")
    async def register_user(self, ctx, hwid: str, user: str, order: str, dm_user: discord.User = None):
        embed = discord.Embed(title="📝 User Registration", color=0x007bff)
        if order not in data['u_orders']:
            embed.add_field(name="⚠️ Error", value="You are not in the database, stop trying to cheat", inline=False)
        else:
            duration = data['u_orders'][order]
            expiry_timestamp = int(time.time()) + duration * 24 * 60 * 60

            order_data = {
                "order_id": order,
                "expiry": expiry_timestamp,
                "timestamp": int(time.time()),
                "hwid": hwid
            }
            data['c_orders'][order] = order_data
            del data['u_orders'][order]
            data['users'][hwid] = user
            data['status'][hwid] = False
            data['whwid'][hwid] = expiry_timestamp
            data['expire'][hwid] = expiry_timestamp

            save_json_data()
            embed.add_field(name="✅ Success", value="Registration successful", inline=False)
        
        if dm_user:
            await dm_user.send(embed=embed)
            await ctx.respond("✅ Registration details sent to the user.", ephemeral=True)
        else:
            await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(name="check_license", description="🔍 Check license by HWID")
    async def check_license(self, ctx, hwid: str, user: discord.User = None):
        embed = discord.Embed(title="🔍 License Check", color=0x007bff)
        if hwid not in data['whwid']:
            embed.add_field(name="⚠️ Error", value="HWID not found in whitelist", inline=False)
        elif hwid in data['bhwid']:
            expiry = data['bhwid'][hwid]
            if expiry is None:
                expiry = "Permanent"
            else:
                expiry = time.ctime(expiry)
            embed.add_field(name="❌ Status", value="Blacklisted", inline=False)
            embed.add_field(name="⏰ Expiry", value=expiry, inline=False)
        else:
            embed.add_field(name="✅ Success", value="HWID is valid and not blacklisted", inline=False)
        
        if user:
            await user.send(embed=embed)
            await ctx.respond("✅ License check details sent to the user.", ephemeral=True)
        else:
            await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(name="check_expiry", description="⏳ Check user expiry by HWID")
    async def check_user_expiry(self, ctx, hwid: str, user: discord.User = None):
        embed = discord.Embed(title="⏳ User Expiry Check", color=0x007bff)
        if hwid in data['expire']:
            expiry_timestamp = data['expire'][hwid]
            embed.add_field(name="⏰ Expiry Timestamp", value=f"```\n{expiry_timestamp}\n```", inline=False)
        else:
            embed.add_field(name="⚠️ Error", value="Hardware ID not found", inline=False)
        
        if user:
            await user.send(embed=embed)
            await ctx.respond("✅ User expiry details sent to the user.", ephemeral=True)
        else:
            await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(name="create_key", description="🔑 Create a new license key")
    async def create_license_key(self, ctx, duration: int, name: str = "", user: discord.User = None):
        embed = discord.Embed(color=0x007bff)
        if duration <= 0:
            embed.add_field(name="⚠️ Error", value="Invalid duration", inline=False)
        else:
            random_str = f"{generate_random_string()}-{generate_random_string()}-{generate_random_string()}"
            license_key = f"CYBERIOUS-{name.upper()}-{random_str}" if name else f"CYBERIOUS-{random_str}"
            data['u_orders'][license_key] = duration
            save_json_data()
            embed.add_field(name="🔑 License Key", value=f"```\n{license_key}\n```", inline=False)
            embed.add_field(name="📅 Duration", value=f"{duration} days", inline=True)
            embed.add_field(name="📆 Creation Date", value=f"{time.ctime()}", inline=True)
            embed.set_footer(text="Copy the license key above to activate your product.")
        
        if user:
            await user.send(embed=embed)
            await ctx.respond("✅ License key created and sent to the user.", ephemeral=True)
        else:
            await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(name="delete_key", description="🗑️ Delete an existing license key")
    async def delete_license_key(self, ctx, license_key: str, all: bool = False, user: discord.User = None):
        embed = discord.Embed(title="🗑️ License Key Deletion", color=0x007bff)
        hwid = None
        if license_key in data['c_orders']:
            hwid = data['c_orders'][license_key]['hwid']
            del data['c_orders'][license_key]
        if license_key in data['u_orders']:
            del data['u_orders'][license_key]

        if all and hwid:
            if hwid in data['whwid']:
                del data['whwid'][hwid]
            if hwid in data['bhwid']:
                del data['bhwid'][hwid]
            if hwid in data['users']:
                del data['users'][hwid]
            if hwid in data['expire']:
                del data['expire'][hwid]
            if hwid in data['status']:
                del data['status'][hwid]

        save_json_data()
        if hwid:
            embed.add_field(name="✅ Success", value="License key and associated data deleted successfully", inline=False)
        else:
            embed.add_field(name="✅ Success", value="License key deleted successfully", inline=False)
        
        if user:
            await user.send(embed=embed)
            await ctx.respond("✅ License key deletion details sent to the user.", ephemeral=True)
        else:
            await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(name="help", description="ℹ️ List all available commands")
    async def help(self, ctx):
        commands_list = [
            "🔍 `/check_hwid [hwid] [user]` - Check HWID status",
            "🕵️ `/verify_user [hwid] [user]` - Verify a user by HWID",
            "📝 `/register_user [hwid] [user] [order] [dm_user]` - Register a new user",
            "🔍 `/check_license [hwid] [user]` - Check license by HWID",
            "⏳ `/check_expiry [hwid] [user]` - Check user expiry by HWID",
            "🔑 `/create_key [duration] [name] [user]` - Create a new license key",
            "🗑️ `/delete_key [license_key] [all] [user]` - Delete an existing license key and associated data if 'all' is specified",
            "📜 `/list_keys` - List all available keys",
            "ℹ️ `/help` - List all available commands"
        ]
        help_message = "\n".join(commands_list)
        embed = discord.Embed(title="ℹ️ Available Commands", description=help_message, color=0x007bff)
        await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(name="list_keys", description=":scroll: List all API keys with details")
    async def list_keys(self, ctx):
        keys = list(data['u_orders'].keys())
        keys.sort()

        embeds = []
        fields = []
        for i, key in enumerate(keys):
            key_info = {"key": key, "duration": data['u_orders'][key]}
            is_active = key in data['c_orders']
            if is_active:
                order_info = data['c_orders'][key]
                key_info["hwid"] = order_info["hwid"]
                key_info["creation_date"] = time.ctime(order_info["timestamp"])
                key_info["expiry_date"] = time.ctime(order_info["expiry"])

            field_values = [
                f"```\n{key_info['key']}\n```",
                f"{key_info['duration']} days",
                f"{is_active}",
            ]
            if "hwid" in key_info:
                field_values.extend([
                    f"```\n{key_info['hwid']}\n```",
                    f"```\n{key_info['creation_date']}\n```",
                    f"```\n{key_info['expiry_date']}\n```",
                ])

            fields.append(discord.EmbedField(name=":key: Key", value=field_values[0], inline=True))
            fields.append(discord.EmbedField(name=":date: Duration", value=field_values[1], inline=True))
            fields.append(discord.EmbedField(name=":green_circle: Active", value=field_values[2], inline=True))
            if "hwid" in key_info:
                fields.append(discord.EmbedField(name=":desktop: HWID", value=field_values[3], inline=True))
                fields.append(discord.EmbedField(name=":calendar: Creation Date", value=field_values[4], inline=True))
                fields.append(discord.EmbedField(name=":alarm_clock: Expiry Date", value=field_values[5], inline=True))

            if (i + 1) % 5 == 0 or i == len(keys) - 1:
                embed = discord.Embed(title=":scroll: List of License Keys", color=0x007bff)
                embed.set_footer(text=f"Page {(i // 5) + 1} of {(len(keys) + 4) // 5}")
                embed.fields = fields
                embeds.append(embed)
                fields = []

        for embed in embeds:
            await ctx.respond(embed=embed, ephemeral=True)


bot.add_cog(LicenseManagement(bot))

bot.run(DISCORD_TOKEN)