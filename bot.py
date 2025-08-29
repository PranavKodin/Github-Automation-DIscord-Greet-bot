import discord
import yaml
import os
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Load automation settings
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

automations = config["automations"]

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()

async def send_automation_message(channel_id, message):
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(message)
    else:
        print(f"Channel {channel_id} not found!")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    for auto in automations:
        if auto["name"] == "automation2":
            hour, minute = map(int, auto["time"].split(":"))
            scheduler.add_job(
                send_automation_message,
                "cron",
                hour=hour,
                minute=minute,
                args=[auto["channel_id"], auto["message"]],
            )
    scheduler.start()

TOKEN = os.getenv("RIYA_TOKEN")
bot.run(TOKEN)
