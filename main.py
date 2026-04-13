import discord
from discord.ext import commands
import asyncio
import random
import os
import time

# --- الإعدادات ---
# يمكنك وضع توكن الحساب الأساسي هنا مباشرة بين القوسين
PRIMARY_TOKEN = "ضع_التوكن_هنا_إذا_أردت" 

# جلب باقي التوكنات من Railway (إذا وجدت)
TOKENS_RAW = os.getenv("TOKEN")
PREFIX = "+"

class MultiAccountBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix=PREFIX, self_bot=True, help_command=None, *args, **kwargs)
        self.spam_words = []
        self.spam_speed = 0.5
        self.kep_speed = 0.4
        self.stop_flags = {}
        self.start_time = int(time.time())

    async def on_ready(self):
        print(f'✅ Connected: {self.user.name}')

    def setup_account_commands(self):
        # --- >> أمر الهيلب (مطابق لطلبك بالسنتي) << ---
        @self.command()
        async def help(ctx):
            help_text = """**====================================**
** اوامر المستخدمين (+)**
**====================================**

**>> الحالات:**
+playing <نص> <اسم_الصورة>
+streaming <رابط> <نص>
+watching <نص>
+competing <نص>
+listening <نص>
+stopact

**>> كلون:**
+clone <sourceID> <targetID>

**>> فويس:**
+voice <channelID>
+stopvoice

**>> تيكت:**
+text <channelID>
+stoptext

**>> رياكشن:**
+reaction channel <channelID>
+reaction server <serverID>
+reaction on
+reaction off
+stopreaction

**>>ارسال:**
+send <channelID> <وقت> <رسالة>
+stopsend

**>> Spam:**
+addword <كلمة>
+removeword <كلمة>
+spam
+stopspam
+speed

**>> Kep:**
+kep @شخص
+stopkep
+speedk

**>> Nuke:**
+account <serverID> <عدد> <كلمة>
+bot <token> <serverID> <عدد> <كلمة>
+stopnuke

**>> Clear:**
+friend
+server
+dm
+all
+stopdestroy"""
            await ctx.send(help_text)

        # --- >> الحالات مع دعم الصور << ---
        @self.command()
        async def playing(ctx, text, image_name=None):
            activity = discord.Game(name=text, start=self.start_time)
            # إذا وضعت اسم صورة مسجلة في الـ Assets الخاصة بـ Application
            if image_name:
                activity = discord.Activity(
                    type=discord.ActivityType.playing,
                    name=text,
                    assets={'large_image': image_name, 'large_text': 'Vexy Bot'},
                    timestamps={'start': self.start_time}
                )
            await self.change_presence(activity=activity)
            await ctx.send(f"🎮 {self.user.name}: Playing **{text}**")

        @self.command()
        async def streaming(ctx, url, *, text):
            await self.change_presence(activity=discord.Streaming(name=text, url=url, start=self.start_time))
            await ctx.send(f"🟣 {self.user.name}: Streaming **{text}**")

        @self.command()
        async def stopact(ctx):
            await self.change_presence(activity=None)
            await ctx.send("✅ Status stopped.")

        # --- >> باقي الأوامر (Spam, Kep, Nuke, Clear) بنفس المنطق السابق << ---
        @self.command()
        async def addword(ctx, *, word):
            self.spam_words.append(word)
            await ctx.send(f"➕ Added: `{word}`")

        @self.command()
        async def spam(ctx):
            self.stop_flags["spam"] = False
            while not self.stop_flags.get("spam"):
                if self.spam_words: await ctx.send(random.choice(self.spam_words))
                await asyncio.sleep(self.spam_speed)

        @self.command()
        async def stopspam(ctx):
            self.stop_flags["spam"] = True
            await ctx.send("🛑 Spam stopped.")

        @self.command()
        async def kep(ctx, user: discord.Member):
            self.stop_flags["kep"] = False
            while not self.stop_flags.get("kep"):
                msg = random.choice(self.spam_words) if self.spam_words else ".."
                await ctx.send(f"{user.mention} {msg}")
                await asyncio.sleep(self.kep_speed)

        @self.command()
        async def stopkep(ctx):
            self.stop_flags["kep"] = True
            await ctx.send("🛑 Kep stopped.")

        @self.command()
        async def voice(ctx, channel_id: int):
            self.stop_flags["voice"] = False
            channel = self.get_channel(channel_id)
            while not self.stop_flags.get("voice"):
                if not ctx.voice_client:
                    try: await channel.connect()
                    except: pass
                await asyncio.sleep(5)

        @self.command()
        async def stopvoice(ctx):
            self.stop_flags["voice"] = True
            if ctx.voice_client: await ctx.voice_client.disconnect()

# --- دالة التشغيل ---
async def start_acc(token):
    if not token or token == "ضع_التوكن_هنا_إذا_أردت": return
    client = MultiAccountBot()
    client.setup_account_commands()
    try: await client.start(token)
    except: print(f"❌ Failed to start token: {token[:10]}...")

async def main():
    all_tokens = []
    # إضافة التوكن الأساسي من الكود
    if PRIMARY_TOKEN and PRIMARY_TOKEN != "ضع_التوكن_هنا_إذا_أردت":
        all_tokens.append(PRIMARY_TOKEN)
    
    # إضافة التوكنات من Variables
    if TOKENS_RAW:
        all_tokens.extend([t.strip() for t in TOKENS_RAW.split(',')])
    
    if not all_tokens:
        print("❌ No tokens provided!")
        return

    await asyncio.gather(*[start_acc(token) for token in all_tokens])

if __name__ == "__main__":
    asyncio.run(main())
                
