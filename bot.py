import discord
from discord.ext import commands, tasks
import datetime
import os
import asyncio
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
CHANNEL_ID = 1570718048854474792  # Замените на ID вашего канала

@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен!")
    if not check_day.is_running():
        check_day.start()

@tasks.loop(minutes=30)
async def check_day():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return

    now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)  # +3 для МСК
    current_weekday = now.weekday()  # 4 — это пятница
    role = channel.guild.default_role
    overwrite = channel.overwrites_for(role)

    if current_weekday == 4:
        if overwrite.send_messages is not True:
            overwrite.send_messages = True
            await channel.set_permissions(role, overwrite=overwrite)
            await channel.send("📢 Канал открыт! Сегодня пятница, можете писать сообщения.")
    else:
        if overwrite.send_messages is not False:
            overwrite.send_messages = False
            await channel.set_permissions(role, overwrite=overwrite)

async def main():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("Ошибка: Токен не найден!")
        return
    await web_server()
    await bot.start(token)

asyncio.run(main())
