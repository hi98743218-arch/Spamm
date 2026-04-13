import discord
from discord.ext import commands
import asyncio
import random
import os

# --- الإعدادات ---
# Railway سيقرأ التوكن من خانة Variables التي ستضيفها هناك باسم TOKEN
TOKEN = os.getenv("TOKEN") 
PREFIX = "+"

# متغيرات النظام
STOP_FLAGS = {}
spam_words = []

class MySelfBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=PREFIX, self_bot=True, help_command=None)

    async def on_ready(self):
        print(f'------\nLogged in as: {self.user.name}\nID: {self.user.id}\n------')

bot = MySelfBot()

# --- أوامر المساعدة ---
@bot.command()
async def help(ctx):
    help_text = """
**📋 أوامر المستخدم (+):**
**💫 الحالات:** `playing`, `streaming`, `watching`, `competing`, `listening`, `stopact`
**🧬 كلون:** `clone <sourceID> <targetID>`
**🎙 الفويس:** `voice <channelID>`, `stopvoice`
**📝 التيكست:** `text <channelID>`, `stoptext`
**📨 الإرسال:** `send <channelID> <time> <message>`, `stopsend`
**🔧 الكيب:** `addkep`, `kep @user`, `stopkep`, `ad`, `dele`
**💣 التدمير:** `account <serverID> <count> <name> <msg>`, `stopnuke`
**🔥 التنظيف:** `friend`, `server`, `stopdestroy`
    """
    await ctx.send(help_text)

# --- أوامر الحالات (Presence) ---
@bot.command()
async def streaming(ctx, *, text):
    url = "https://www.twitch.tv/ahmed_radi"
    await bot.change_presence(activity=discord.Streaming(name=text, url=url))
    await ctx.send(f"✅ Streaming: {text}")

@bot.command()
async def stopact(ctx):
    await bot.change_presence(activity=None)
    await ctx.send("✅ Activity stopped.")

# --- أوامر الفويس (Auto-Reconnect) ---
@bot.command()
async def voice(ctx, channel_id: int):
    STOP_FLAGS["voice"] = False
    channel = bot.get_channel(channel_id)
    await ctx.send(f"🎙 Joining {channel.name}...")
    while not STOP_FLAGS.get("voice"):
        if not ctx.voice_clients:
            try: await channel.connect()
            except: pass
        await asyncio.sleep(5)

@bot.command()
async def stopvoice(ctx):
    STOP_FLAGS["voice"] = True
    for vc in bot.voice_clients: await vc.disconnect()
    await ctx.send("✅ Voice stopped.")

# --- نظام الكلون (Server Clone) ---
@bot.command()
async def clone(ctx, source_id: int, target_id: int):
    s_guild = bot.get_guild(source_id)
    t_guild = bot.get_guild(target_id)
    await ctx.send("🔄 Cleaning and Clowning...")
    for c in t_guild.channels: await c.delete()
    for cat in s_guild.categories:
        new_cat = await t_guild.create_category(name=cat.name)
        for ch in cat.channels:
            if isinstance(ch, discord.TextChannel): await new_cat.create_text_channel(name=ch.name)
            elif isinstance(ch, discord.VoiceChannel): await new_cat.create_voice_channel(name=ch.name)
    await ctx.send("✅ Done.")

# --- نظام الكيب (Kep System) ---
@bot.command()
async def addkep(ctx, *, word):
    spam_words.append(word)
    await ctx.send(f"➕ Added: {word}")

@bot.command()
async def kep(ctx, user: discord.Member):
    STOP_FLAGS["kep"] = False
    while not STOP_FLAGS.get("kep"):
        word = random.choice(spam_words) if spam_words else "Spam"
        await ctx.send(f"{user.mention} {word}")
        await asyncio.sleep(0.4)

@bot.command()
async def stopkep(ctx):
    STOP_FLAGS["kep"] = True
    await ctx.send("✅ Kep stopped.")

# --- أوامر التدمير (Nuke) ---
@bot.command()
async def account(ctx, s_id: int, count: int, name: str, *, msg):
    guild = bot.get_guild(s_id)
    STOP_FLAGS[f"nuke_{s_id}"] = False
    for c in guild.channels: await c.delete()
    for i in range(count):
        if STOP_FLAGS.get(f"nuke_{s_id}"): break
        ch = await guild.create_text_channel(name)
        asyncio.create_task(spam_task(ch, msg))

async def spam_task(ch, msg):
    while True:
        try: await ch.send(msg)
        except: break

# --- أوامر التنظيف ---
@bot.command()
async def friend(ctx):
    for f in bot.user.friends: await f.remove_friend()
    await ctx.send("✅ Friends deleted.")

@bot.command()
async def server(ctx):
    for g in bot.guilds: await g.leave()
    await ctx.send("✅ Left all servers.")

# تشغيل البوت
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ Error: No TOKEN found in Environment Variables!")
  
