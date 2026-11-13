import discord
from discord.ext import commands, tasks
import datetime
import os
import asyncio
import random
from aiohttp import web

async def handle(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Ваш ID канала
CHANNEL_ID = 1570716369664745573

# 5 случайных фраз для проверки тишины
SILENCE_PHRASES = [
    "Что молчим? Чего не пишем?",
    "Эй, пятница на дворе! Куда все пропали?",
    "Тишина в эфире... Давайте оживлять чат!",
    "Ау! Есть кто живой? Делитесь новостями!",
    "Чего притихли? Кто первый напишет сообщение?"
]

last_message_time = datetime.datetime.utcnow()
silence_notified = False

@bot.event
async def on_ready():
    global last_message_time
    last_message_time = datetime.datetime.utcnow()
    print(f"Бот {bot.user} запущен!")
    
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("🟢 Бот успешно запущен и работает!")
    
    # Запускаем фоновые задачи, если они еще не запущены
    if not check_schedule.is_running():
        check_schedule.start()
    if not check_silence.is_running():
        check_silence.start()

@bot.event
async def on_message(message):
    global last_message_time, silence_notified
    
    if message.author.bot or message.channel.id != CHANNEL_ID:
        return

    last_message_time = datetime.datetime.utcnow()
    silence_notified = False
    
    await bot.process_commands(message)

# Проверяем расписание КАЖДУЮ МИНУТУ, чтобы закрывать/открывать вовремя
@tasks.loop(minutes=1)
async def check_schedule():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return

    # Получаем точное время по Москве (UTC+3)
    now_msk = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    current_weekday = now_msk.weekday()  # 4 — это пятница
    
    role = channel.guild.default_role
    overwrite = channel.overwrites_for(role)

    # Если сегодня пятница (по МСК)
    if current_weekday == 4:
        if overwrite.send_messages is not True:
            overwrite.send_messages = True
            await channel.set_permissions(role, overwrite=overwrite)
            await channel.send("📢 Канал открыт! Наступила пятница, можете писать сообщения.")
    else:
        # Во все остальные дни недели канал закрыт
        if overwrite.send_messages is not False:
            overwrite.send_messages = False
            await channel.set_permissions(role, overwrite=overwrite)

@tasks.loop(minutes=5)
async def check_silence():
    global silence_notified
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return

    now_msk = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    if now_msk.weekday() != 4:
        return

    time_passed = (datetime.datetime.utcnow() - last_message_time).total_seconds()
    if time_passed >= 3600 and not silence_notified:
        phrase = random.choice(SILENCE_PHRASES)
        await channel.send(phrase)
        silence_notified = True

async def main():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("Ошибка: Токен не найден!")
        return
    await web_server()
    await bot.start(token)

asyncio.run(main())
