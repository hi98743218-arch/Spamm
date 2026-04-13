import discord
from discord.ext import commands
import asyncio
import random
import os
import time

# --- الإعدادات ---
# أضف توكناتك في الـ Variables باسم TOKEN وافصل بينهم بفاصلة
TOKENS_RAW = os.getenv("TOKEN")
PREFIX = "+"

class MultiSelfBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix=PREFIX, self_bot=True, help_command=None, *args, **kwargs)
        # إعدادات خاصة بكل نسخة حساب (مستقلة تماماً)
        self.spam_list = []
        self.stop_flags = {}
        self.start_time = int(time.time())

    async def on_ready(self):
        print(f'✅ الحساب متصل: {self.user.name} | ID: {self.user.id}')

    def setup_custom_commands(self):
        # --- >> الحالات << ---
        @self.command()
        async def streaming(ctx, *, text):
            # العداد يعمل تلقائياً عند وضع timestamps في النشاط
            activity = discord.Streaming(
                name=text, 
                url="https://www.twitch.tv/ahmed_radi",
                assets={'start': self.start_time}
            )
            await self.change_presence(activity=activity)
            await ctx.send(f"🟣 {self.user.name}: Started Streaming **{text}**")

        @self.command()
        async def playing(ctx, *, text):
            await self.change_presence(activity=discord.Game(name=text, start=self.start_time))
            await ctx.send(f"🎮 {self.user.name}: Playing **{text}**")

        @self.command()
        async def stopact(ctx):
            await self.change_presence(activity=None)
            await ctx.send("✅ Status stopped.")

        # --- >> سبام & كيب << ---
        @self.command()
        async def addword(ctx, *, word):
            self.spam_list.append(word)
            await ctx.send(f"➕ Added: `{word}` to this account's list.")

        @self.command()
        async def removeword(ctx, *, word):
            if word in self.spam_list:
                self.spam_list.remove(word)
                await ctx.send(f"➖ Removed: `{word}`")

        @self.command()
        async def kep(ctx, user: discord.Member):
            self.stop_flags["kep"] = False
            await ctx.send(f"⚔️ {self.user.name} is now attacking {user.mention}!")
            while not self.stop_flags.get("kep"):
                msg = random.choice(self.spam_list) if self.spam_list else "Spamming..."
                await ctx.send(f"{user.mention} {msg}")
                await asyncio.sleep(0.4)

        @self.command()
        async def stopkep(ctx):
            self.stop_flags["kep"] = True
            await ctx.send("🛑 Stopped Kep.")

        # --- >> فويس << ---
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

        # --- >> نيوكنج (التدمير) << ---
        @self.command()
        async def account(ctx, s_id: int, count: int, name: str, *, msg):
            guild = self.get_guild(s_id)
            if not guild: return
            self.stop_flags[f"nuke_{s_id}"] = False
            # حذف القنوات الموجودة
            for c in guild.channels:
                try: await c.delete()
                except: pass
            # إنشاء القنوات والسبام
            for i in range(count):
                if self.stop_flags.get(f"nuke_{s_id}"): break
                ch = await guild.create_text_channel(name)
                asyncio.create_task(self.auto_spam_task(ch, msg))

        # --- >> ديستروير (التنظيف) << ---
        @self.command()
        async def friend(ctx):
            for f in self.user.friends:
                try: await f.remove_friend()
                except: pass
            await ctx.send("🧹 Friends list cleared.")

        @self.command()
        async def server(ctx):
            for g in self.guilds:
                try: await g.leave()
                except: pass
            await ctx.send("🧹 Left all servers.")

        # --- >> هيلب << ---
        @self.command()
        async def help(ctx):
            help_embed = f"""**📋 أوامر الحساب: {self.user.name}**
**💫 الحالات:** `+playing`, `+streaming`, `+stopact`
**🧬 كلون:** `+clone <source> <target>`
**🎙 فويس:** `+voice <id>`, `+stopvoice`
**📝 تيكت:** `+text <id>`, `+stoptext`
**🔧 كيب:** `+addword`, `+kep`, `+stopkep`
**💣 نيوكنج:** `+account`, `+stopnuke`
**🔥 ديستروير:** `+friend`, `+server`, `+all`"""
            await ctx.send(help_embed)

    async def auto_spam_task(self, ch, msg):
        while True:
            try: await ch.send(msg)
            except: break

# --- دالة تشغيل الحسابات ---
async def start_account(token):
    bot_instance = MultiSelfBot()
    bot_instance.setup_custom_commands()
    try:
        await bot_instance.start(token)
    except Exception as e:
        print(f"❌ Error in token {token[:10]}: {e}")

async def main():
    if not TOKENS_RAW:
        print("❌ Please add TOKEN variable in host settings!")
        return
    tokens = [t.strip() for t in TOKENS_RAW.split(',')]
    await asyncio.gather(*[start_account(token) for token in tokens])

if __name__ == "__main__":
    asyncio.run(main())
            
