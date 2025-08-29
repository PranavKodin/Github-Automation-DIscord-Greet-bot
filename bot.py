import os
import yaml
import discord
from datetime import datetime, timezone

# ---- Load config ----
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Pick automation2 from YAML
automation2 = next((a for a in config["automations"] if a["name"] == "automation2"), None)
if not automation2:
    raise RuntimeError('config.yaml must contain automations with name "automation2".')

CHANNEL_IDS = [int(cid) for cid in automation2["channel_ids"]]  # multiple channels
MESSAGE = automation2["message"]

# ---- Token from env (support either name) ----
TOKEN = os.getenv("RIYA_TOKEN") or os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError(
        "Discord bot token not found. Set a GitHub Actions secret and pass it via env.\n"
        "Options:\n"
        "  • In workflow env:  RIYA_TOKEN: ${{ secrets.RIYA_TOKEN }}\n"
        "  • Or:               DISCORD_TOKEN: ${{ secrets.DISCORD_TOKEN }}\n"
    )

# ---- Intents ----
intents = discord.Intents.default()

class Client(discord.Client):
    async def on_ready(self):
        print(f"✅ Logged in as {self.user} (id={self.user.id})")

        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        for cid in CHANNEL_IDS:
            try:
                channel = self.get_channel(cid)
                if channel is None:
                    channel = await self.fetch_channel(cid)

                await channel.send(f"{MESSAGE}\n\nSir pranav uth gaye hai aur tum chutiyo ko\n_GOOD MORNING_ \nkehna chahte hai")
                print(f"✅ Message sent to channel {cid}")
            except Exception as e:
                print(f"❌ Failed to send message to channel {cid}: {e}")

        await self.close()  # end the job once all messages are sent

client = Client(intents=intents)
client.run(TOKEN)
