import discord
from discord.ext import commands, tasks
import datetime
import os

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_ID = 123456789012345678  # Укажите ID вашего канала

@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен и готов к работе!")
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

# Бот берет токен из защищенной переменной окружения Render
token = os.environ.get("DISCORD_TOKEN")
bot.run(token)
