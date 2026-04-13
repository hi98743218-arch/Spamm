import discord
from discord.ext import commands
import asyncio
import random
import os

# --- الإعدادات ---
# في Railway: أضف متغير باسم TOKEN وضع التوكنات مفصولة بفاصلة (Token1,Token2)
TOKENS_RAW = os.getenv("TOKEN")
PREFIX = "+"

class SelfBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix=PREFIX, self_bot=True, help_command=None, *args, **kwargs)
        self.stop_flags = {}
        self.spam_words = []

    async def on_ready(self):
        print(f'✅ الحساب متصل: {self.user.name} | ID: {self.user.id}')

    # --- تسجيل الأوامر داخل الكلاس لضمان استقلالية كل حساب ---
    def setup_commands(self):
        
        @self.command()
        async def help(ctx):
            help_text = f"**🤖 الحساب الحالي: {self.user.name}**\n"
            help_text += "`+streaming <نص>` | `+voice <id>` | `+text <id>`\n"
            help_text += "`+addkep <كلمة>` | `+kep <mention>` | `+stopkep`\n"
            help_text += "`+account <serverID> <count> <name> <msg>` | `+stopnuke`"
            await ctx.send(help_text)

        @self.command()
        async def streaming(self_ctx, *, text):
            url = "https://www.twitch.tv/ahmed_radi"
            await self.change_presence(activity=discord.Streaming(name=text, url=url))
            await self_ctx.send(f"🟣 {self.user.name}: Started Streaming {text}")

        # --- نظام الكيب (السبام المنفصل) ---
        @self.command()
        async def addkep(self_ctx, *, word):
            self.spam_words.append(word)
            await self_ctx.send(f"➕ {self.user.name}: Added '{word}'")

        @self.command()
        async def kep(self_ctx, user: discord.Member):
            self.stop_flags["kep"] = False
            await self_ctx.send(f"💣 {self.user.name}: Starting Spam on {user.mention}")
            while not self.stop_flags.get("kep"):
                word = random.choice(self.spam_words) if self.spam_words else "اسبام"
                await self_ctx.send(f"{user.mention} {word}")
                await asyncio.sleep(0.4) # سرعة عالية

        @self.command()
        async def stopkep(self_ctx):
            self.stop_flags["kep"] = True
            await self_ctx.send(f"🛑 {self.user.name}: Spam Stopped.")

        # --- نظام الفويس (البقاء متصلاً) ---
        @self.command()
        async def voice(self_ctx, channel_id: int):
            self.stop_flags["voice"] = False
            channel = self.get_channel(channel_id)
            while not self.stop_flags.get("voice"):
                if not self_ctx.voice_client:
                    try: await channel.connect()
                    except: pass
                await asyncio.sleep(5)

        @self.command()
        async def stopvoice(self_ctx):
            self.stop_flags["voice"] = True
            if self_ctx.voice_client: await self_ctx.voice_client.disconnect()

        # --- تدمير السيرفر (Nuke) ---
        @self.command()
        async def account(self_ctx, s_id: int, count: int, name: str, *, msg):
            guild = self.get_guild(s_id)
            if not guild: return
            self.stop_flags[f"nuke_{s_id}"] = False
            
            # حذف الرومات
            for c in guild.channels:
                try: await c.delete()
                except: pass
            
            # إنشاء رومات وسبام
            for i in range(count):
                if self.stop_flags.get(f"nuke_{s_id}"): break
                ch = await guild.create_text_channel(name)
                asyncio.create_task(self.individual_spam(ch, msg))

    async def individual_spam(self, ch, msg):
        while True:
            try: await ch.send(msg)
            except: break

# --- دالة تشغيل كل بوت بشكل منفصل ---
async def run_bot(token):
    bot = SelfBot()
    bot.setup_commands()
    try:
        await bot.start(token)
    except Exception as e:
        print(f"❌ خطأ في التوكن {token[:10]}: {e}")

# --- تشغيل المهام المتعددة ---
async def main():
    if not TOKENS_RAW:
        print("❌ لا يوجد توكنات! أضف متغير TOKEN في Railway.")
        return

    tokens = [t.strip() for t in TOKENS_RAW.split(',')]
    # تشغيل كل حساب في Task مستقلة لا تتدخل في الأخرى
    await asyncio.gather(*[run_bot(token) for token in tokens])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
        
