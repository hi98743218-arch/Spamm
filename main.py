import discord
from discord.ext import commands
import asyncio
import random
import os
import time

# --- الإعدادات ---
# يمكنك وضع توكن الحساب الأساسي هنا مباشرة
PRIMARY_TOKEN = "ضع_التوكن_هنا" 
TOKENS_RAW = os.getenv("TOKEN")
PREFIX = "+"

class MultiAccountBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix=PREFIX, self_bot=True, help_command=None, *args, **kwargs)
        # إعدادات مستقلة لكل توكن
        self.spam_words = []
        self.spam_speed = 0.5
        self.kep_speed = 0.4
        self.stop_flags = {}
        self.reaction_settings = {"state": False, "target": None, "type": None}
        self.start_time = int(time.time())

    async def on_ready(self):
        print(f'✅ المتصل الآن: {self.user.name}')

    # نظام الرياكشن التلقائي
    async def on_message(self, message):
        if self.reaction_settings["state"]:
            # إذا كان الرياكشن مفعل لسيرفر أو روم محدد
            should_react = False
            if self.reaction_settings["type"] == "channel" and message.channel.id == self.reaction_settings["target"]:
                should_react = True
            elif self.reaction_settings["type"] == "server" and message.guild and message.guild.id == self.reaction_settings["target"]:
                should_react = True
            
            if should_react and message.author.id != self.user.id:
                try: await message.add_reaction("⭐") # يمكنك تغيير الايموجي هنا
                except: pass

        await self.process_commands(message)

    def setup_account_commands(self):
        # --- >> الهيلب بظبط كما طلبت << ---
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

        # --- الحالات ---
        @self.command()
        async def streaming(ctx, url, *, text):
            await self.change_presence(activity=discord.Streaming(name=text, url=url, start=self.start_time))
            await ctx.send(f"🟣 Streaming: {text}")

        @self.command()
        async def stopact(ctx):
            await self.change_presence(activity=None)
            await ctx.send("✅ Status stopped.")

        # --- الرياكشن ---
        @self.command()
        async def reaction(ctx, mode, target_id: int = None):
            if mode == "channel":
                self.reaction_settings["type"] = "channel"
                self.reaction_settings["target"] = target_id or ctx.channel.id
            elif mode == "server":
                self.reaction_settings["type"] = "server"
                self.reaction_settings["target"] = target_id or ctx.guild.id
            elif mode == "on": self.reaction_settings["state"] = True
            elif mode == "off": self.reaction_settings["state"] = False
            await ctx.send(f"🔄 Reaction set: {mode}")

        # --- إخفاء الخاص (dm) ---
        @self.command()
        async def dm(ctx):
            await ctx.send("🧹 جاري إخفاء المحادثات الخاصة...")
            for channel in self.private_channels:
                try: 
                    await channel.close() # يقوم بإغلاق المحادثة (إخفائها)
                    await asyncio.sleep(0.3)
                except: continue
            await ctx.send("✅ تم إخفاء جميع محادثات الخاص.")

        # --- السبام والكيب ---
        @self.command()
        async def addword(ctx, *, word):
            self.spam_words.append(word)
            await ctx.send(f"➕ Added: {word}")

        @self.command()
        async def kep(ctx, user: discord.Member):
            self.stop_flags["kep"] = False
            while not self.stop_flags.get("kep"):
                word = random.choice(self.spam_words) if self.spam_words else "..."
                await ctx.send(f"{user.mention} {word}")
                await asyncio.sleep(self.kep_speed)

        # --- التيكست (XP) ---
        @self.command()
        async def text(ctx, channel_id: int):
            self.stop_flags["text"] = False
            channel = self.get_channel(channel_id)
            while not self.stop_flags.get("text"):
                await channel.send(f"XP Boost {random.randint(100,999)}")
                await asyncio.sleep(60)

        # --- إرسال مجدول ---
        @self.command()
        async def send(ctx, channel_id: int, delay: int, *, msg):
            self.stop_flags["send"] = False
            channel = self.get_channel(channel_id)
            while not self.stop_flags.get("send"):
                await channel.send(msg)
                await asyncio.sleep(delay)

        # --- توقيف عام ---
        @self.command()
        async def stopact(ctx): await self.change_presence(activity=None)
        @self.command()
        async def stopkep(ctx): self.stop_flags["kep"] = True
        @self.command()
        async def stoptext(ctx): self.stop_flags["text"] = True
        @self.command()
        async def stopsend(ctx): self.stop_flags["send"] = True

# --- تشغيل الحسابات ---
async def start_acc(token):
    if not token or "ضع" in token: return
    client = MultiAccountBot()
    client.setup_account_commands()
    try: await client.start(token)
    except Exception as e: print(f"❌ Error: {e}")

async def main():
    all_tokens = []
    if PRIMARY_TOKEN and "ضع" not in PRIMARY_TOKEN: all_tokens.append(PRIMARY_TOKEN)
    if TOKENS_RAW: all_tokens.extend([t.strip() for t in TOKENS_RAW.split(',')])
    await asyncio.gather(*[start_acc(token) for token in all_tokens])

if __name__ == "__main__":
    asyncio.run(main())
