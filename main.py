import discord
from discord.ext import commands
import asyncio
import aiohttp
import json
import time
import random
import string
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, BooleanVar
from datetime import datetime, timedelta
import requests

# ====================================
# إعدادات الأداة
# ====================================
TOKEN = os.getenv('TOKEN')  # التوكن من متغيرات البيئة
PREFIX = "+"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, self_bot=True, intents=intents, help_command=None)

# ====================================
# المتغيرات العامة
# ====================================
activity_start_time = None
activity_timer_running = False
spam_active = False
spam_words = []
spam_speed = 1
kep_active = False
kep_target = None
kep_words = []
kep_speed = 1
send_tasks = {}
reaction_active = False
reaction_channels = []
reaction_servers = []
voice_connection = None
text_leveling_channel = None
nuke_active = False
clone_options = {}

# ====================================
# كلاس واجهة النسخ
# ====================================
class CloneGUI:
    def __init__(self, source_name, target_name):
        self.source_name = source_name
        self.target_name = target_name
        self.result = None
        self.create_window()
    
    def create_window(self):
        self.root = tk.Tk()
        self.root.title("Clone Server Options")
        self.root.geometry("400x500")
        self.root.configure(bg='#2c2f33')
        
        title = tk.Label(self.root, text="خيارات نسخ السيرفر", 
                        font=('Arial', 16, 'bold'), bg='#2c2f33', fg='white')
        title.pack(pady=20)
        
        info_frame = tk.Frame(self.root, bg='#23272a')
        info_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(info_frame, text=f"من: {self.source_name}", 
                bg='#23272a', fg='#7289da').pack()
        tk.Label(info_frame, text=f"إلى: {self.target_name}", 
                bg='#23272a', fg='#7289da').pack()
        
        options_frame = tk.Frame(self.root, bg='#2c2f33')
        options_frame.pack(pady=20)
        
        self.channels_var = BooleanVar(value=True)
        self.roles_var = BooleanVar(value=True)
        self.emojis_var = BooleanVar(value=True)
        self.categories_var = BooleanVar(value=True)
        self.all_var = BooleanVar(value=False)
        
        ttk.Checkbutton(options_frame, text="نسخ الرومات", 
                       variable=self.channels_var).pack(anchor='w', pady=5)
        ttk.Checkbutton(options_frame, text="نسخ الرتب", 
                       variable=self.roles_var).pack(anchor='w', pady=5)
        ttk.Checkbutton(options_frame, text="نسخ الإيموجي", 
                       variable=self.emojis_var).pack(anchor='w', pady=5)
        ttk.Checkbutton(options_frame, text="نسخ الكاتجوري", 
                       variable=self.categories_var).pack(anchor='w', pady=5)
        ttk.Checkbutton(options_frame, text="نسخ الكل", 
                       variable=self.all_var, command=self.toggle_all).pack(anchor='w', pady=5)
        
        btn_frame = tk.Frame(self.root, bg='#2c2f33')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="بدء النسخ", command=self.start_clone,
                 bg='#43b581', fg='white', padx=20, font=('Arial', 12)).pack()
        
        self.root.mainloop()
    
    def toggle_all(self):
        if self.all_var.get():
            self.channels_var.set(True)
            self.roles_var.set(True)
            self.emojis_var.set(True)
            self.categories_var.set(True)
        else:
            self.channels_var.set(False)
            self.roles_var.set(False)
            self.emojis_var.set(False)
            self.categories_var.set(False)
    
    def start_clone(self):
        self.result = {
            'channels': self.channels_var.get(),
            'roles': self.roles_var.get(),
            'emojis': self.emojis_var.get(),
            'categories': self.categories_var.get()
        }
        self.root.quit()
        self.root.destroy()

# ====================================
# دوال مساعدة
# ====================================
def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

async def update_activity_timer():
    global activity_start_time, activity_timer_running
    while activity_timer_running:
        if activity_start_time:
            elapsed = int(time.time() - activity_start_time)
            # تحديث الحالة مع الوقت
            await asyncio.sleep(1)

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
# قائمة المساعدة
# ====================================
@bot.command(name='help', aliases=['مساعدة'])
async def help_command(ctx):
    help_text = f"""```ansi
[1;36m====================================[0m
[1;33m** اوامر المستخدمين (+)**
[1;36m====================================[0m

[1;32m>> الحالات:[0m
{PREFIX}playing <نص> <اسم_الصورة>
{PREFIX}streaming <رابط> <نص>
{PREFIX}watching <نص>
{PREFIX}competing <نص>
{PREFIX}listening <نص>
{PREFIX}stopact
[1;35m⏱️ عداد الوقت يظهر مع الحالة[0m

[1;32m>> Copy Server :[0m
{PREFIX}clone <ايدي_المصدر> <ايدي_الهدف>
(واجهة GUI مع خيارات متعددة)

[1;32m>> فويس:[0m
{PREFIX}voice <channelID>
{PREFIX}stopvoice

[1;32m>> تيكست:[0m
{PREFIX}text <channelID>
{PREFIX}stoptext

[1;32m>> اوتو ريأكشن:[0m
{PREFIX}reaction channel <channelID>
{PREFIX}reaction server <serverID>
{PREFIX}reaction on
{PREFIX}reaction off
{PREFIX}stopreaction

[1;32m>> ارسال:[0m
{PREFIX}send <channelID> <وقت_بالثواني> <رسالة>
{PREFIX}stopsend

[1;32m>> Spam:[0m
{PREFIX}addword <كلمة>
{PREFIX}removeword <كلمة>
{PREFIX}spam
{PREFIX}stopspam
{PREFIX}speed <رقم>

[1;32m>> Kep:[0m
{PREFIX}kep @المنشن
{PREFIX}addw <كلمة>
{PREFIX}ad
{PREFIX}dele <كلمة>
{PREFIX}stopkep
{PREFIX}speedk <رقم>

[1;32m>> Nuke:[0m
{PREFIX}account <serverID> <عدد> <اسم>
{PREFIX}bot <token> <serverID> <عدد> <كلمة>
{PREFIX}stopnuke

[1;32m>> Clear:[0m
{PREFIX}friend
{PREFIX}server
{PREFIX}dm
{PREFIX}all
{PREFIX}stopdestroy
```"""
    await ctx.send(help_text)

# ====================================
# أوامر الحالات
# ====================================
@bot.command(name='playing')
async def playing(ctx, *, text):
    global activity_start_time, activity_timer_running
    activity_start_time = time.time()
    activity_timer_running = True
    
    await bot.change_presence(activity=discord.Game(name=text))
    asyncio.create_task(update_activity_timer())
    
    embed = discord.Embed(
        title="✅ تم تغيير الحالة",
        description=f"الحالة: Playing **{text}**\n⏱️ بدأ العداد",
        color=0x00ff00
    )
    await ctx.send(embed=embed)

@bot.command(name='streaming')
async def streaming(ctx, url, *, text):
    global activity_start_time, activity_timer_running
    activity_start_time = time.time()
    activity_timer_running = True
    
    await bot.change_presence(activity=discord.Streaming(name=text, url=url))
    asyncio.create_task(update_activity_timer())
    
    embed = discord.Embed(
        title="✅ تم تغيير الحالة",
        description=f"الحالة: Streaming **{text}**\n⏱️ بدأ العداد",
        color=0x9146ff
    )
    await ctx.send(embed=embed)

@bot.command(name='watching')
async def watching(ctx, *, text):
    global activity_start_time, activity_timer_running
    activity_start_time = time.time()
    activity_timer_running = True
    
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=text))
    asyncio.create_task(update_activity_timer())
    
    embed = discord.Embed(
        title="✅ تم تغيير الحالة",
        description=f"الحالة: Watching **{text}**\n⏱️ بدأ العداد",
        color=0x00ff00
    )
    await ctx.send(embed=embed)

@bot.command(name='competing')
async def competing(ctx, *, text):
    global activity_start_time, activity_timer_running
    activity_start_time = time.time()
    activity_timer_running = True
    
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name=text))
    asyncio.create_task(update_activity_timer())
    
    embed = discord.Embed(
        title="✅ تم تغيير الحالة",
        description=f"الحالة: Competing in **{text}**\n⏱️ بدأ العداد",
        color=0x00ff00
    )
    await ctx.send(embed=embed)

@bot.command(name='listening')
async def listening(ctx, *, text):
    global activity_start_time, activity_timer_running
    activity_start_time = time.time()
    activity_timer_running = True
    
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=text))
    asyncio.create_task(update_activity_timer())
    
    embed = discord.Embed(
        title="✅ تم تغيير الحالة",
        description=f"الحالة: Listening to **{text}**\n⏱️ بدأ العداد",
        color=0x00ff00
    )
    await ctx.send(embed=embed)

@bot.command(name='stopact')
async def stopact(ctx):
    global activity_timer_running, activity_start_time
    activity_timer_running = False
    activity_start_time = None
    await bot.change_presence(activity=None)
    
    embed = discord.Embed(
        title="⏹️ تم إيقاف الحالة",
        description="تم إزالة الحالة وإيقاف العداد",
        color=0xff0000
    )
    await ctx.send(embed=embed)

# ====================================
# أوامر النسخ
# ====================================
@bot.command(name='clone')
async def clone_server(ctx, source_id: int, target_id: int):
    try:
        source_guild = bot.get_guild(source_id)
        target_guild = bot.get_guild(target_id)
        
        if not source_guild or not target_guild:
            await ctx.send("❌ لم يتم العثور على أحد السيرفرات")
            return
        
        # فتح واجهة GUI
        gui = CloneGUI(source_guild.name, target_guild.name)
        
        if not gui.result:
            await ctx.send("❌ تم إلغاء عملية النسخ")
            return
        
        await ctx.send("🔄 جاري نسخ السيرفر...")
        
        # نسخ الرتب
        if gui.result['roles']:
            roles = {}
            for role in reversed(source_guild.roles):
                if role.name != "@everyone":
                    try:
                        new_role = await target_guild.create_role(
                            name=role.name,
                            color=role.color,
                            hoist=role.hoist,
                            mentionable=role.mentionable,
                            permissions=role.permissions
                        )
                        roles[role] = new_role
                        await asyncio.sleep(0.5)
                    except:
                        pass
        
        # نسخ الكاتجوري والرومات
        if gui.result['categories'] or gui.result['channels']:
            for category in source_guild.categories:
                if gui.result['categories']:
                    try:
                        new_category = await target_guild.create_category(
                            name=category.name,
                            position=category.position
                        )
                        
                        # نسخ الرومات داخل الكاتجوري
                        if gui.result['channels']:
                            for channel in category.channels:
                                if isinstance(channel, discord.TextChannel):
                                    await target_guild.create_text_channel(
                                        name=channel.name,
                                        category=new_category,
                                        topic=channel.topic,
                                        nsfw=channel.nsfw,
                                        slowmode_delay=channel.slowmode_delay
                                    )
                                elif isinstance(channel, discord.VoiceChannel):
                                    await target_guild.create_voice_channel(
                                        name=channel.name,
                                        category=new_category,
                                        bitrate=channel.bitrate,
                                        user_limit=channel.user_limit
                                    )
                                await asyncio.sleep(0.5)
                    except Exception as e:
                        print(f"Error copying category: {e}")
        
        # نسخ الإيموجي
        if gui.result['emojis']:
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
        
        embed = discord.Embed(
            title="✅ تم نسخ السيرفر بنجاح",
            description=f"من: {source_guild.name}\nإلى: {target_guild.name}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ حدث خطأ: {str(e)}")

# ====================================
# أوامر الفويس
# ====================================
@bot.command(name='voice')
async def voice_join(ctx, channel_id: int):
    global voice_connection
    try:
        channel = bot.get_channel(channel_id)
        if channel and isinstance(channel, discord.VoiceChannel):
            voice_connection = await channel.connect()
            await ctx.send(f"✅ تم الانضمام إلى روم: {channel.name}")
        else:
            await ctx.send("❌ لم يتم العثور على الروم الصوتي")
    except Exception as e:
        await ctx.send(f"❌ حدث خطأ: {str(e)}")

@bot.command(name='stopvoice')
async def voice_leave(ctx):
    global voice_connection
    try:
        if voice_connection:
            await voice_connection.disconnect()
            voice_connection = None
            await ctx.send("✅ تم الخروج من الروم الصوتي")
        else:
            await ctx.send("❌ لست في روم صوتي")
    except Exception as e:
        await ctx.send(f"❌ حدث خطأ: {str(e)}")

# ====================================
# أوامر رفع مستوى التكست
# ====================================
@bot.command(name='text')
async def text_level(ctx, channel_id: int):
    global text_leveling_channel
    try:
        channel = bot.get_channel(channel_id)
        if channel and isinstance(channel, discord.TextChannel):
            text_leveling_channel = channel
            await ctx.send(f"✅ بدأ رفع المستوى في روم: {channel.name}")
            
            # إرسال رسائل لرفع المستوى
            while text_leveling_channel:
                try:
                    await channel.send(f"Leveling up... {random.randint(1000, 9999)}")
                    await asyncio.sleep(random.uniform(3, 7))
                except:
                    break
        else:
            await ctx.send("❌ لم يتم العثور على الروم النصي")
    except Exception as e:
        await ctx.send(f"❌ حدث خطأ: {str(e)}")

@bot.command(name='stoptext')
async def stop_text(ctx):
    global text_leveling_channel
    text_leveling_channel = None
    await ctx.send("✅ تم إيقاف رفع المستوى")

# ====================================
# أوامر الريأكشن التلقائي
# ====================================
@bot.command(name='reaction')
async def reaction_command(ctx, action=None, target_id: int = None):
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
        await ctx.send("⏸️ تم إيقاف الريأكشن التلقائي")
    
    elif action == 'stop':
        reaction_active = False
        reaction_channels.clear()
        reaction_servers.clear()
        await ctx.send("⏹️ تم إيقاف وحذف جميع إعدادات الريأكشن")
    
    else:
        await ctx.send("❌ استخدام خاطئ: +reaction [channel/server/on/off/stop] [id]")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if reaction_active:
        if message.channel.id in reaction_channels or message.guild.id in reaction_servers:
            try:
                await message.add_reaction("👍")
                await asyncio.sleep(0.5)
                await message.add_reaction("❤️")
            except:
                pass
    
    await bot.process_commands(message)

# ====================================
# أوامر الإرسال المجدول
# ====================================
@bot.command(name='send')
async def scheduled_send(ctx, channel_id: int, interval: int, *, message_text):
    channel = bot.get_channel(channel_id)
    if not channel:
        await ctx.send("❌ لم يتم العثور على الروم")
        return
    
    task_id = f"{channel_id}_{int(time.time())}"
    
    async def send_loop():
        while task_id in send_tasks:
            try:
                await channel.send(message_text)
                await asyncio.sleep(interval)
            except:
                break
    
    send_tasks[task_id] = asyncio.create_task(send_loop())
    await ctx.send(f"✅ بدأ الإرسال المجدول كل {interval} ثانية")

@bot.command(name='stopsend')
async def stop_scheduled_send(ctx):
    for task_id, task in send_tasks.items():
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
    await ctx.send(f"✅ تم تغيير سرعة السبام إلى {speed} ثانية")

# ====================================
# أوامر الكيب (Ghost Ping)
# ====================================

@bot.command(name='kep')
async def kep_target(ctx, user: discord.User):
    global kep_target, kep_active
    kep_target = user
    kep_active = True
    
    embed = discord.Embed(
        title="✅ بدأ الكيب",
        description=f"المستهدف: {user.mention}",
        color=0x00ff00
    )
    await ctx.send(embed=embed)
    
    while kep_active:
        for word in kep_words if kep_words else ["."]:
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
    embed = discord.Embed(
        title="✅ تمت الإضافة",
        description=f"الكلمة: {word}",
        color=0x00ff00
    )
    await ctx.send(embed=embed)

@bot.command(name='ad')
async def list_kep_words(ctx):
    if kep_words:
        words_list = "\n".join([f"• {w}" for w in kep_words])
        embed = discord.Embed(
            title="📝 قائمة الكلمات",
            description=words_list,
            color=0x3498db
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="📝 قائمة الكلمات",
            description="لا توجد كلمات مضافة",
            color=0xff0000
        )
        await ctx.send(embed=embed)

@bot.command(name='dele')
async def delete_kep_word(ctx, *, word):
    if word in kep_words:
        kep_words.remove(word)
        embed = discord.Embed(
            title="✅ تم الحذف",
            description=f"الكلمة: {word}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ خطأ",
            description="الكلمة غير موجودة في القائمة",
            color=0xff0000
        )
        await ctx.send(embed=embed)

@bot.command(name='stopkep')
async def stop_kep(ctx):
    global kep_active, kep_target
    kep_active = False
    kep_target = None
    embed = discord.Embed(
        title="⏹️ تم الإيقاف",
        description="تم إيقاف الكيب",
        color=0xff0000
    )
    await ctx.send(embed=embed)

@bot.command(name='speedk')
async def set_kep_speed(ctx, speed: float):
    global kep_speed
    kep_speed = speed
    embed = discord.Embed(
        title="⚡ تم تغيير السرعة",
        description=f"السرعة الجديدة: {speed} ثانية",
        color=0x00ff00
    )
    await ctx.send(embed=embed)

# ====================================
# أوامر التدمير (Nuke)
# ====================================

@bot.command(name='account')
async def nuke_account(ctx, server_id: int, count: int, *, name):
    global nuke_active
    guild = bot.get_guild(server_id)
    
    if not guild:
        embed = discord.Embed(
            title="❌ خطأ",
            description="لم يتم العثور على السيرفر",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    nuke_active = True
    
    embed = discord.Embed(
        title="💣 بدأ التدمير",
        description=f"السيرفر: {guild.name}\nالعدد: {count}\nالاسم: {name}",
        color=0xff5500
    )
    await ctx.send(embed=embed)
    
    try:
        # حذف جميع الرومات
        deleted_channels = 0
        for channel in guild.channels:
            if not nuke_active:
                break
            try:
                await channel.delete()
                deleted_channels += 1
                await asyncio.sleep(0.3)
            except:
                pass
        
        # حذف جميع الرتب (ما عدا @everyone)
        deleted_roles = 0
        for role in guild.roles:
            if not nuke_active or role.name == "@everyone":
                continue
            try:
                await role.delete()
                deleted_roles += 1
                await asyncio.sleep(0.3)
            except:
                pass
        
        # إنشاء رومات جديدة
        created_channels = 0
        for i in range(count):
            if not nuke_active:
                break
            try:
                await guild.create_text_channel(f"{name}-{i+1}")
                created_channels += 1
                await asyncio.sleep(0.3)
            except:
                pass
        
        # إنشاء رتب جديدة
        created_roles = 0
        for i in range(count):
            if not nuke_active:
                break
            try:
                await guild.create_role(name=f"{name}-{i+1}")
                created_roles += 1
                await asyncio.sleep(0.3)
            except:
                pass
        
        # سبام في الرومات الجديدة
        spam_count = 0
        for channel in guild.text_channels:
            if not nuke_active:
                break
            try:
                for _ in range(5):
                    await channel.send(f"@everyone {name} NUKED BY {bot.user.name}")
                    spam_count += 1
                    await asyncio.sleep(0.5)
            except:
                pass
        
        embed = discord.Embed(
            title="✅ تم التدمير بنجاح",
            description=f"الرومات المحذوفة: {deleted_channels}\nالرتب المحذوفة: {deleted_roles}\nالرومات المنشأة: {created_channels}\nالرتب المنشأة: {created_roles}\nالرسائل المرسلة: {spam_count}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ خطأ",
            description=f"حدث خطأ أثناء التدمير: {str(e)}",
            color=0xff0000
        )
        await ctx.send(embed=embed)

@bot.command(name='bot')
async def nuke_bot(ctx, bot_token: str, server_id: int, count: int, *, name):
    embed = discord.Embed(
        title="🔄 جاري التدمير",
        description="يتم التدمير باستخدام بوت خارجي...",
        color=0x3498db
    )
    await ctx.send(embed=embed)
    
    try:
        bot_client = discord.Client(intents=discord.Intents.all())
        
        @bot_client.event
        async def on_ready():
            guild = bot_client.get_guild(server_id)
            if guild:
                # حذف الرومات
                for channel in guild.channels:
                    try:
                        await channel.delete()
                        await asyncio.sleep(0.3)
                    except:
                        pass
                
                # حذف الرتب
                for role in guild.roles:
                    if role.name != "@everyone":
                        try:
                            await role.delete()
                            await asyncio.sleep(0.3)
                        except:
                            pass
                
                # إنشاء رومات جديدة
                for i in range(count):
                    try:
                        channel = await guild.create_text_channel(f"{name}-{i+1}")
                        await channel.send(f"@everyone NUKED BY BOT")
                        await asyncio.sleep(0.3)
                    except:
                        pass
                
                # إنشاء رتب جديدة
                for i in range(count):
                    try:
                        await guild.create_role(name=f"{name}-{i+1}")
                        await asyncio.sleep(0.3)
                    except:
                        pass
                
                # تغيير اسم السيرفر
                try:
                    await guild.edit(name=f"NUKED BY {name}")
                except:
                    pass
            
            await bot_client.close()
        
        await bot_client.start(bot_token)
        
        embed = discord.Embed(
            title="✅ تم التدمير",
            description="تم تدمير السيرفر بنجاح باستخدام البوت",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ خطأ",
            description=f"فشل التدمير: {str(e)}",
            color=0xff0000
        )
        await ctx.send(embed=embed)

@bot.command(name='stopnuke')
async def stop_nuke(ctx):
    global nuke_active
    nuke_active = False
    embed = discord.Embed(
        title="⏹️ تم الإيقاف",
        description="تم إيقاف عملية التدمير",
        color=0xff0000
    )
    await ctx.send(embed=embed)

# ====================================
# أوامر التنظيف (Clear)
# ====================================

@bot.command(name='friend')
async def clear_friends(ctx):
    embed = discord.Embed(
        title="🔄 جاري التنظيف",
        description="جاري حذف جميع الأصدقاء...",
        color=0x3498db
    )
    msg = await ctx.send(embed=embed)
    
    count = 0
    for friend in bot.user.friends:
        try:
            await friend.remove_friend()
            count += 1
            await asyncio.sleep(1)
        except:
            pass
    
    embed = discord.Embed(
        title="✅ تم التنظيف",
        description=f"تم حذف {count} صديق",
        color=0x00ff00
    )
    await msg.edit(embed=embed)

@bot.command(name='server')
async def leave_servers(ctx):
    embed = discord.Embed(
        title="🔄 جاري الخروج",
        description="جاري الخروج من جميع السيرفرات...",
        color=0x3498db
    )
    msg = await ctx.send(embed=embed)
    
    count = 0
    guilds_to_leave = [g for g in bot.guilds if g.owner_id != bot.user.id]
    
    for guild in guilds_to_leave:
        try:
            await guild.leave()
            count += 1
            await asyncio.sleep(1)
        except:
            pass
    
    embed = discord.Embed(
        title="✅ تم الخروج",
        description=f"تم الخروج من {count} سيرفر",
        color=0x00ff00
    )
    await msg.edit(embed=embed)

@bot.command(name='dm')
async def clear_dms(ctx):
    embed = discord.Embed(
        title="🔄 جاري الحذف",
        description="جاري حذف جميع المحادثات الخاصة...",
        color=0x3498db
    )
    msg = await ctx.send(embed=embed)
    
    count = 0
    for channel in bot.private_channels:
        if isinstance(channel, discord.DMChannel):
            try:
                # حذف جميع الرسائل في المحادثة
                async for message in channel.history(limit=1000):
                    if message.author == bot.user:
                        await message.delete()
                        await asyncio.sleep(0.3)
                count += 1
            except:
                pass
    
    embed = discord.Embed(
        title="✅ تم الحذف",
        description=f"تم تنظيف {count} محادثة",
        color=0x00ff00
    )
    await msg.edit(embed=embed)

@bot.command(name='all')
async def clear_all(ctx):
    embed = discord.Embed(
        title="🔄 جاري التنظيف الشامل",
        description="جاري تنظيف كل شيء...\n⏳ الأصدقاء\n⏳ السيرفرات\n⏳ المحادثات",
        color=0x3498db
    )
    msg = await ctx.send(embed=embed)
    
    # حذف الأصدقاء
    friend_count = 0
    for friend in bot.user.friends:
        try:
            await friend.remove_friend()
            friend_count += 1
            await asyncio.sleep(1)
        except:
            pass
    
    # الخروج من السيرفرات
    server_count = 0
    for guild in bot.guilds:
        if guild.owner_id != bot.user.id:
            try:
                await guild.leave()
                server_count += 1
                await asyncio.sleep(1)
            except:
                pass
    
    # حذف المحادثات
    dm_count = 0
    for channel in bot.private_channels:
        if isinstance(channel, discord.DMChannel):
            try:
                async for message in channel.history(limit=1000):
                    if message.author == bot.user:
                        await message.delete()
                        await asyncio.sleep(0.3)
                dm_count += 1
            except:
                pass
    
    # مغادرة السيرفرات المملوكة
    owned_count = 0
    for guild in bot.guilds:
        if guild.owner_id == bot.user.id:
            try:
                await guild.delete()
                owned_count += 1
                await asyncio.sleep(1)
            except:
                pass
    
    embed = discord.Embed(
        title="✅ تم التنظيف الشامل",
        description=f"""
        **الإحصائيات:**
        👥 الأصدقاء المحذوفين: {friend_count}
        🌐 السيرفرات المغادرة: {server_count}
        💬 المحادثات المنظفة: {dm_count}
        🗑️ السيرفرات المحذوفة: {owned_count}
        """,
        color=0x00ff00
    )
    await msg.edit(embed=embed)

@bot.command(name='stopdestroy')
async def stop_destroy(ctx):
    global nuke_active, spam_active, kep_active
    nuke_active = False
    spam_active = False
    kep_active = False
    
    embed = discord.Embed(
        title="⏹️ تم الإيقاف",
        description="تم إيقاف جميع عمليات التدمير والسبام",
        color=0xff0000
    )
    await ctx.send(embed=embed)

# ====================================
# حدث حذف الرسالة (للكيب)
# ====================================

@bot.event
async def on_message_delete(message):
    if kep_active and kep_target and message.author == bot.user:
        if kep_target.mention in message.content:
            try:
                # إعادة إرسال الرسالة المحذوفة
                await message.channel.send(message.content)
            except:
                pass

# ====================================
# معالجة الأخطاء
# ====================================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ خطأ في الاستخدام",
            description="ينقص بعض المتطلبات للأمر",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="❌ خطأ في المدخلات",
            description="تأكد من صحة المدخلات (مثال: الآيدي يجب أن يكون رقماً)",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        print(f"Error: {error}")

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
        print("❌ التوكن غير صالح أو منتهي الصلاحية")
    except Exception as e:
        print(f"❌ حدث خطأ: {str(e)}")
