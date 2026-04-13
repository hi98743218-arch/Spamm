import discord
from discord.ext import commands
import asyncio
import random
import os
import time

# --- الإعدادات العامة ---
# ضع التوكنات هنا مفصولة بفاصلة (Token1,Token2,Token3)
TOKENS_RAW = os.getenv("TOKEN") 
PREFIX = "+"

class MySelfBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix=PREFIX, self_bot=True, help_command=None, *args, **kwargs)
        # إعدادات مستقلة لكل حساب
        self.spam_words = []
        self.spam_speed = 0.5
        self.stop_flags = {}
        self.start_time = time.time()

    async def on_ready(self):
        print(f'✅ متصل الآن: {self.user.name} ({self.user.id})')

    def setup_commands(self):
        # --- أمر المساعدة ---
        @self.command()
        async def help(ctx):
            help_msg = f"""**📋 أوامر الحساب: {self.user.name}**
💫 **الحالات:** `playing`, `streaming`, `watching`, `competing`, `listening`, `stopact`
🧬 **كلون:** `clone <sourceID> <targetID>`
🎙 **الفويس:** `voice <ID>`, `stopvoice`
📝 **التيكست:** `text <ID>`, `stoptext`
🔄 **الرياكشن:** `reaction <on/off>`, `stopreaction`
📨 **الإرسال:** `send <ID> <time> <msg>`, `stopsend`
🔧 **الكيب:** `addkep`, `kep @user`, `stopkep`, `ad`, `dele`, `speed`
💣 **التدمير:** `account`, `bot`, `stopnuke`
🔥 **التنظيف:** `friend`, `server`, `dm`, `all`, `stopdestroy`"""
            await ctx.send(help_msg)

        # --- الحالات مع عداد وقت ---
        @self.command()
        async def streaming(ctx, *, text):
            await self.change_presence(activity=discord.Streaming(name=text, url="https://www.twitch.tv/discord", start=self.start_time))
            await ctx.send(f"✅ {self.user.name}: Streaming {text}")

        @self.command()
        async def playing(ctx, *, text):
            await self.change_presence(activity=discord.Game(name=text, start=self.start_time))
            await ctx.send(f"✅ {self.user.name}: Playing {text}")

        @self.command()
        async def stopact(ctx):
            await self.change_presence(activity=None)
            await ctx.send("✅ Activity stopped.")

        # --- نظام الكيب والسبام الفردي ---
        @self.command()
        async def addkep(ctx, *, word):
            self.spam_words.append(word)
            await ctx.send(f"➕ Added: {word}")

        @self.command()
        async def ad(ctx):
            await ctx.send(f"📝 Words: {', '.join(self.spam_words) if self.spam_words else 'None'}")

        @self.command()
        async def speed(ctx, s: float):
            self.spam_speed = s
            await ctx.send(f"⚡ Speed set to: {s}")

        @self.command()
        async def kep(ctx, user: discord.Member):
            self.stop_flags["kep"] = False
            while not self.stop_flags.get("kep"):
                word = random.choice(self.spam_words) if self.spam_words else "Spamming..."
                await ctx.send(f"{user.mention} {word}")
                await asyncio.sleep(self.spam_speed)

        @self.command()
        async def stopkep(ctx):
            self.stop_flags["kep"] = True
            await ctx.send("✅ Stopped.")

        # --- الفويس (دخول تلقائي) ---
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

        # --- التدمير بأقصى سرعة (Nuke) ---
        @self.command()
        async def account(ctx, s_id: int, count: int, name: str, *, msg):
            guild = self.get_guild(s_id)
            if not guild: return
            self.stop_flags[f"nuke_{s_id}"] = False
            for c in guild.channels: 
                try: await c.delete()
                except: pass
            for i in range(count):
                if self.stop_flags.get(f"nuke_{s_id}"): break
                ch = await guild.create_text_channel(name)
                asyncio.create_task(self.nuke_spam(ch, msg))

    async def nuke_spam(self, ch, msg):
        while True:
            try: await ch.send(msg)
            except: break

# --- تشغيل الحسابات بشكل متوازي ---
async def start_account(token):
    bot = MySelfBot()
    bot.setup_commands()
    try:
        await bot.start(token)
    except Exception as e:
        print(f"❌ Error with token {token[:10]}: {e}")

async def main():
    if not TOKENS_RAW:
        print("❌ No tokens found! Please add them in Railway/Host Variables.")
        return
    tokens = [t.strip() for t in TOKENS_RAW.split(',')]
    await asyncio.gather(*[start_account(token) for token in tokens])

if __name__ == "__main__":
    asyncio.run(main())
