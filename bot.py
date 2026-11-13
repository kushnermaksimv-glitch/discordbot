import discord
from discord.ext import commands, tasks
import datetime
import os
from aiohttp import web

# Настройка веб-сервера для Render (чтобы сервис не выключался)
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
CHANNEL_ID = 123456789012345678  # ID вашего канала

@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен!")
    check_day.start()

@tasks.loop(minutes=30)
async def check_day():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return

    now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    current_weekday = now.weekday()
    role = channel.guild.default_role
    overwrite = channel.overwrites_for(role)

    if current_weekday == 4:
        if overwrite.send_messages != True:
            overwrite.send_messages = True
            await channel.set_permissions(role, overwrite=overwrite)
            await channel.send("📢 Канал открыт! Сегодня пятница, можете писать сообщения.")
    else:
        if overwrite.send_messages != False:
            overwrite.send_messages = False
            await channel.set_permissions(role, overwrite=overwrite)

# Запускаем и веб-сервер, и бота одновременно
async def main():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("Ошибка: Токен не найден!")
        return
    
    await web_server()
    await bot.start(token)

import asyncio
asyncio.run(main())
