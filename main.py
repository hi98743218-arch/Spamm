import discord
from discord.ext import commands
import asyncio
import time
import random
import os
import sys

# ====================================
# إعدادات الأداة
# ====================================
TOKEN = os.getenv('TOKEN')
PREFIX = "+"

bot = commands.Bot(command_prefix=PREFIX, self_bot=True, intents=discord.Intents.all())
bot.remove_command('help')

# ====================================
# المتغيرات العامة
# ====================================
activity_start_time = None
spam_active = False
spam_words = []
spam_speed = 1
kep_active = False
kep_target = None
kep_words = []
kep_speed = 1
reaction_active = False
reaction_channels = []
reaction_servers = []
voice_client = None
text_spam_channel = None
send_tasks = {}
nuke_active = False

# ====================================
# حدث جاهزية البوت
# ====================================
@bot.event
async def on_ready():
    print(f"""
╔════════════════════════════════════════╗
║     تم تسجيل الدخول بنجاح!              ║
║     الحساب: {bot.user.name}            
║     الآيدي: {bot.user.id}              
║     البريفكس: {PREFIX}                 
╚════════════════════════════════════════╝
    """)

# ====================================
# أمر المساعدة
# ====================================
@bot.command(name='help', aliases=['مساعدة'])
async def help_command(ctx):
    help_text = f"""```
====================================
** اوامر المستخدمين (+)**
====================================

>> الحالات:
{PREFIX}playing <نص>
{PREFIX}streaming <رابط> <نص>
{PREFIX}watching <نص>
{PREFIX}competing <نص>
{PREFIX}listening <نص>
{PREFIX}stopact

>> Copy Server :
{PREFIX}clone <ايدي_المصدر> <ايدي_الهدف> <خيار>
الخيارات: all, channels, roles, emojis, categories

>> فويس:
{PREFIX}voice <channelID>
{PREFIX}stopvoice

>> تيكست:
{PREFIX}text <channelID>
{PREFIX}stoptext

>> اوتو ريأكشن:
{PREFIX}reaction channel <channelID>
{PREFIX}reaction server <serverID>
{PREFIX}reaction on
{PREFIX}reaction off

>> ارسال:
{PREFIX}send <channelID> <وقت> <رسالة>
{PREFIX}stopsend

>> Spam:
{PREFIX}addword <كلمة>
{PREFIX}removeword <كلمة>
{PREFIX}spam
{PREFIX}stopspam
{PREFIX}speed <رقم>

>> Kep:
{PREFIX}kep @المنشن
{PREFIX}addw <كلمة>
{PREFIX}ad
{PREFIX}dele <كلمة>
{PREFIX}stopkep
{PREFIX}speedk <رقم>

>> Nuke:
{PREFIX}account <serverID> <عدد> <اسم>
{PREFIX}bot <token> <serverID> <عدد> <كلمة>
{PREFIX}stopnuke

>> Clear:
{PREFIX}friend
{PREFIX}server
{PREFIX}dm
{PREFIX}all
```"""
    await ctx.send(help_text)

# ====================================
# أوامر الحالات
# ====================================
@bot.command(name='playing')
async def playing(ctx, *, text):
    global activity_start_time
    activity_start_time = time.time()
    await bot.change_presence(activity=discord.Game(name=text))
    await ctx.send(f"✅ تم تغيير الحالة إلى: Playing **{text}**")

@bot.command(name='streaming')
async def streaming(ctx, url, *, text):
    global activity_start_time
    activity_start_time = time.time()
    await bot.change_presence(activity=discord.Streaming(name=text, url=url))
    await ctx.send(f"✅ تم تغيير الحالة إلى: Streaming **{text}**")

@bot.command(name='watching')
async def watching(ctx, *, text):
    global activity_start_time
    activity_start_time = time.time()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=text))
    await ctx.send(f"✅ تم تغيير الحالة إلى: Watching **{text}**")

@bot.command(name='competing')
async def competing(ctx, *, text):
    global activity_start_time
    activity_start_time = time.time()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name=text))
    await ctx.send(f"✅ تم تغيير الحالة إلى: Competing in **{text}**")

@bot.command(name='listening')
async def listening(ctx, *, text):
    global activity_start_time
    activity_start_time = time.time()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=text))
    await ctx.send(f"✅ تم تغيير الحالة إلى: Listening to **{text}**")

@bot.command(name='stopact')
async def stopact(ctx):
    global activity_start_time
    activity_start_time = None
    await bot.change_presence(activity=None)
    await ctx.send("✅ تم إزالة الحالة")

# ====================================
# أمر نسخ السيرفر
# ====================================
@bot.command(name='clone')
async def clone_server(ctx, source_id: int, target_id: int, option: str = "all"):
    try:
        source_guild = bot.get_guild(source_id)
        target_guild = bot.get_guild(target_id)
        
        if not source_guild or not target_guild:
            await ctx.send("❌ لم يتم العثور على أحد السيرفرات")
            return
        
        await ctx.send(f"🔄 جاري نسخ السيرفر مع خيار: {option}...")
        
        # نسخ الرتب
        if option in ["all", "roles"]:
            for role in reversed(source_guild.roles):
                if role.name != "@everyone":
                    try:
                        await target_guild.create_role(
                            name=role.name,
                            color=role.color,
                            hoist=role.hoist,
                            mentionable=role.mentionable,
                            permissions=role.permissions
                        )
                        await asyncio.sleep(0.5)
                    except:
                        pass
        
        # نسخ الكاتجوري والرومات
        if option in ["all", "categories", "channels"]:
            for category in source_guild.categories:
                if option in ["all", "categories"]:
                    try:
                        new_category = await target_guild.create_category(
                            name=category.name,
                            position=category.position
                        )
                        
                        if option in ["all", "channels"]:
                            for channel in category.channels:
                                if isinstance(channel, discord.TextChannel):
                                    await target_guild.create_text_channel(
                                        name=channel.name,
                                        category=new_category
                                    )
                                elif isinstance(channel, discord.VoiceChannel):
                                    await target_guild.create_voice_channel(
                                        name=channel.name,
                                        category=new_category
                                    )
                                await asyncio.sleep(0.5)
                    except:
                        pass
        
        # نسخ الإيموجي
        if option in ["all", "emojis"]:
            for emoji in source_guild.emojis:
                try:
                    emoji_data = await emoji.read()
                    await target_guild.create_custom_emoji(
                        name=emoji.name,
                        image=emoji_data
                    )
                    await asyncio.sleep(1)
                except:
                    pass
        
        await ctx.send(f"✅ تم نسخ السيرفر بنجاح")
        
    except Exception as e:
        await ctx.send(f"❌ حدث خطأ: {str(e)}")

# ====================================
# أوامر الفويس
# ====================================
@bot.command(name='voice')
async def voice_join(ctx, channel_id: int):
    global voice_client
    
    if voice_client:
        await ctx.send("❌ أنت بالفعل في روم صوتي")
        return
    
    channel = bot.get_channel(channel_id)
    if not channel or not isinstance(channel, discord.VoiceChannel):
        await ctx.send("❌ لم يتم العثور على الروم الصوتي")
        return
    
    try:
        voice_client = await channel.connect()
        await ctx.send(f"✅ تم الدخول إلى الروم: {channel.name}")
    except Exception as e:
        await ctx.send(f"❌ فشل الدخول: {str(e)}")

@bot.command(name='stopvoice')
async def voice_leave(ctx):
    global voice_client
    
    if voice_client:
        await voice_client.disconnect()
        voice_client = None
        await ctx.send("✅ تم الخروج من الروم الصوتي")
    else:
        await ctx.send("❌ لست في روم صوتي")

# ====================================
# أوامر التكست
# ====================================
@bot.command(name='text')
async def text_level(ctx, channel_id: int):
    global text_spam_channel
    
    channel = bot.get_channel(channel_id)
    if not channel or not isinstance(channel, discord.TextChannel):
        await ctx.send("❌ لم يتم العثور على الروم النصي")
        return
    
    text_spam_channel = channel
    await ctx.send(f"✅ بدأ رفع المستوى في: {channel.name}")
    
    while text_spam_channel:
        try:
            await channel.send(f"Level up {random.randint(1000, 9999)}")
            await asyncio.sleep(random.uniform(3, 7))
        except:
            break

@bot.command(name='stoptext')
async def stop_text(ctx):
    global text_spam_channel
    text_spam_channel = None
    await ctx.send("✅ تم إيقاف رفع المستوى")

# ====================================
# أوامر الريأكشن
# ====================================
@bot.command(name='reaction')
async def reaction_cmd(ctx, action=None, target_id: int = None):
    global reaction_active, reaction_channels, reaction_servers
    
    if action == 'channel' and target_id:
        channel = bot.get_channel(target_id)
        if channel:
            reaction_channels.append(target_id)
            await ctx.send(f"✅ تم إضافة الروم: {channel.name}")
        else:
            await ctx.send("❌ لم يتم العثور على الروم")
    
    elif action == 'server' and target_id:
        guild = bot.get_guild(target_id)
        if guild:
            reaction_servers.append(target_id)
            await ctx.send(f"✅ تم إضافة السيرفر: {guild.name}")
        else:
            await ctx.send("❌ لم يتم العثور على السيرفر")
    
    elif action == 'on':
        reaction_active = True
        await ctx.send("✅ تم تفعيل الريأكشن التلقائي")
    
    elif action == 'off':
        reaction_active = False
        await ctx.send("✅ تم إيقاف الريأكشن التلقائي")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if reaction_active:
        if message.channel.id in reaction_channels or (message.guild and message.guild.id in reaction_servers):
            try:
                await message.add_reaction("👍")
                await asyncio.sleep(0.3)
                await message.add_reaction("❤️")
            except:
                pass
    
    await bot.process_commands(message)

# ====================================
# أوامر الإرسال المجدول
# ====================================
@bot.command(name='send')
async def scheduled_send(ctx, channel_id: int, interval: int, *, msg_text):
    channel = bot.get_channel(channel_id)
    if not channel:
        await ctx.send("❌ لم يتم العثور على الروم")
        return
    
    task_id = str(channel_id)
    
    async def send_loop():
        while task_id in send_tasks:
            try:
                await channel.send(msg_text)
                await asyncio.sleep(interval)
            except:
                break
    
    send_tasks[task_id] = asyncio.create_task(send_loop())
    await ctx.send(f"✅ بدأ الإرسال المجدول كل {interval} ثانية")

@bot.command(name='stopsend')
async def stop_scheduled_send(ctx):
    for task in send_tasks.values():
        task.cancel()
    send_tasks.clear()
    await ctx.send("✅ تم إيقاف جميع الإرسالات المجدولة")

# ====================================
# أوامر السبام
# ====================================
@bot.command(name='addword')
async def add_spam_word(ctx, *, word):
    spam_words.append(word)
    await ctx.send(f"✅ تم إضافة الكلمة: {word}")

@bot.command(name='removeword')
async def remove_spam_word(ctx, *, word):
    if word in spam_words:
        spam_words.remove(word)
        await ctx.send(f"✅ تم حذف الكلمة: {word}")
    else:
        await ctx.send("❌ الكلمة غير موجودة")

@bot.command(name='spam')
async def start_spam(ctx):
    global spam_active
    if not spam_words:
        await ctx.send("❌ لا توجد كلمات، استخدم +addword أولاً")
        return
    
    spam_active = True
    await ctx.send(f"✅ بدأ السبام بـ {len(spam_words)} كلمة")
    
    while spam_active:
        for word in spam_words:
            if not spam_active:
                break
            try:
                await ctx.send(word)
                await asyncio.sleep(spam_speed)
            except:
                pass

@bot.command(name='stopspam')
async def stop_spam(ctx):
    global spam_active
    spam_active = False
    await ctx.send("✅ تم إيقاف السبام")

@bot.command(name='speed')
async def set_spam_speed(ctx, speed: float):
    global spam_speed
    spam_speed = speed
    await ctx.send(f"✅ تم تغيير السرعة إلى {speed} ثانية")

# ====================================
# أوامر الكيب
# ====================================
@bot.command(name='kep')
async def kep_cmd(ctx, user: discord.User):
    global kep_target, kep_active
    kep_target = user
    kep_active = True
    await ctx.send(f"✅ بدأ الكيب على: {user.mention}")
    
    while kep_active:
        words = kep_words if kep_words else ["."]
        for word in words:
            if not kep_active:
                break
            try:
                msg = await ctx.send(f"{user.mention} {word}")
                await msg.delete()
                await asyncio.sleep(kep_speed)
            except:
                pass

@bot.command(name='addw')
async def add_kep_word(ctx, *, word):
    kep_words.append(word)
    await ctx.send(f"✅ تم إضافة الكلمة: {word}")

@bot.command(name='ad')
async def list_kep_words(ctx):
    if kep_words:
        words = "\n".join([f"• {w}" for w in kep_words])
        await ctx.send(f"📝 الكلمات:\n{words}")
    else:
        await ctx.send("📝 لا توجد كلمات")

@bot.command(name='dele')
async def delete_kep_word(ctx, *, word):
    if word in kep_words:
        kep_words.remove(word)
        await ctx.send(f"✅ تم حذف: {word}")
    else:
        await ctx.send("❌ الكلمة غير موجودة")

@bot.command(name='stopkep')
async def stop_kep(ctx):
    global kep_active
    kep_active = False
    await ctx.send("✅ تم إيقاف الكيب")

@bot.command(name='speedk')
async def set_kep_speed(ctx, speed: float):
    global kep_speed
    kep_speed = speed
    await ctx.send(f"✅ تم تغيير السرعة إلى {speed} ثانية")

# ====================================
# أوامر التدمير
# ====================================
@bot.command(name='account')
async def nuke_account(ctx, server_id: int, count: int, *, name):
    global nuke_active
    guild = bot.get_guild(server_id)
    
    if not guild:
        await ctx.send("❌ لم يتم العثور على السيرفر")
        return
    
    nuke_active = True
    await ctx.send(f"💣 بدأ تدمير السيرفر: {guild.name}")
    
    try:
        # حذف الرومات
        for channel in guild.channels:
            if not nuke_active:
                break
            try:
                await channel.delete()
                await asyncio.sleep(0.3)
            except:
                pass
        
        # حذف الرتب
        for role in guild.roles:
            if not nuke_active or role.name == "@everyone":
                continue
            try:
                await role.delete()
                await asyncio.sleep(0.3)
            except:
                pass
        
        # إنشاء رومات جديدة
        for i in range(count):
            if not nuke_active:
                break
            try:
                ch = await guild.create_text_channel(f"{name}-{i+1}")
                await ch.send(f"@everyone NUKED BY {bot.user.name}")
                await asyncio.sleep(0.3)
            except:
                pass
        
        # إنشاء رتب جديدة
        for i in range(count):
            if not nuke_active:
                break
            try:
                await guild.create_role(name=f"{name}-{i+1}")
                await asyncio.sleep(0.3)
            except:
                pass
        
        await ctx.send("✅ تم التدمير بنجاح")
        
    except Exception as e:
        await ctx.send(f"❌ حدث خطأ: {str(e)}")

@bot.command(name='bot')
async def nuke_with_bot(ctx, bot_token: str, server_id: int, count: int, *, name):
    await ctx.send("🔄 جاري التدمير باستخدام البوت...")
    
    try:
        bot_client = discord.Client(intents=discord.Intents.all())
        
        @bot_client.event
        async def on_ready():
            guild = bot_client.get_guild(server_id)
            if guild:
                for channel in guild.channels:
                    try:
                        await channel.delete()
                        await asyncio.sleep(0.3)
                    except:
                        pass
                
                for role in guild.roles:
                    if role.name != "@everyone":
                        try:
                            await role.delete()
                            await asyncio.sleep(0.3)
                        except:
                            pass
                
                for i in range(count):
                    try:
                        ch = await guild.create_text_channel(f"{name}-{i+1}")
                        await ch.send("@everyone NUKED BY BOT")
                        await asyncio.sleep(0.3)
                    except:
                        pass
                
                for i in range(count):
                    try:
                        await guild.create_role(name=f"{name}-{i+1}")
                        await asyncio.sleep(0.3)
                    except:
                        pass
            
            await bot_client.close()
        
        await bot_client.start(bot_token)
        await ctx.send("✅ تم التدمير بنجاح")
        
    except Exception as e:
        await ctx.send(f"❌ فشل التدمير: {str(e)}")

@bot.command(name='stopnuke')
async def stop_nuke(ctx):
    global nuke_active
    nuke_active = False
    await ctx.send("✅ تم إيقاف التدمير")

# ====================================
# أوامر التنظيف
# ====================================
@bot.command(name='friend')
async def clear_friends(ctx):
    await ctx.send("🔄 جاري حذف الأصدقاء...")
    count = 0
    for friend in bot.user.friends:
        try:
            await friend.remove_friend()
            count += 1
            await asyncio.sleep(1)
        except:
            pass
    await ctx.send(f"✅ تم حذف {count} صديق")

@bot.command(name='server')
async def leave_servers(ctx):
    await ctx.send("🔄 جاري الخروج من السيرفرات...")
    count = 0
    for guild in bot.guilds:
        if guild.owner_id != bot.user.id:
            try:
                await guild.leave()
                count += 1
                await asyncio.sleep(1)
            except:
                pass
    await ctx.send(f"✅ تم الخروج من {count} سيرفر")

@bot.command(name='dm')
async def clear_dms(ctx):
    await ctx.send("🔄 جاري حذف المحادثات...")
    count = 0
    for channel in bot.private_channels:
        if isinstance(channel, discord.DMChannel):
            try:
                async for msg in channel.history(limit=100):
                    if msg.author == bot.user:
                        await msg.delete()
                        await asyncio.sleep(0.3)
                count += 1
            except:
                pass
    await ctx.send(f"✅ تم تنظيف {count} محادثة")

@bot.command(name='all')
async def clear_all(ctx):
    await ctx.send("🔄 جاري تنظيف كل شيء...")
    
    # حذف الأصدقاء
    fc = 0
    for friend in bot.user.friends:
        try:
            await friend.remove_friend()
            fc += 1
            await asyncio.sleep(1)
        except:
            pass
    
    # الخروج من السيرفرات
    sc = 0
    for guild in bot.guilds:
        if guild.owner_id != bot.user.id:
            try:
                await guild.leave()
                sc += 1
                await asyncio.sleep(1)
            except:
                pass
    
    # حذف المحادثات
    dc = 0
    for channel in bot.private_channels:
        if isinstance(channel, discord.DMChannel):
            try:
                async for msg in channel.history(limit=100):
                    if msg.author == bot.user:
                        await msg.delete()
                        await asyncio.sleep(0.3)
                dc += 1
            except:
                pass
    
    await ctx.send(f"✅ تم التنظيف:\n👥 أصدقاء: {fc}\n🌐 سيرفرات: {sc}\n💬 محادثات: {dc}")

# ====================================
# تشغيل البوت
# ====================================
if __name__ == "__main__":
    if not TOKEN:
        print("❌ الرجاء وضع التوكن في متغيرات البيئة TOKEN")
        sys.exit(1)
    
    try:
        print("🔄 جاري تشغيل البوت...")
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ التوكن غير صالح")
    except Exception as e:
        print(f"❌ حدث خطأ: {str(e)}")
