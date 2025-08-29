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

CHANNEL_ID = int(automation2["channel_id"])
MESSAGE = automation2["message"]

# ---- Token from env (support either name) ----
TOKEN = os.getenv("RIYA_TOKEN") or os.getenv("DISCORD_TOKEN")
if not TOKEN:
    # Fail clearly (no token leak)
    raise RuntimeError(
        "Discord bot token not found. Set a GitHub Actions secret and pass it via env.\n"
        "Options:\n"
        "  • In workflow env:  RIYA_TOKEN: ${{ secrets.RIYA_TOKEN }}  and read os.getenv('RIYA_TOKEN')\n"
        "  • Or:               DISCORD_TOKEN: ${{ secrets.DISCORD_TOKEN }} and read os.getenv('DISCORD_TOKEN')\n"
    )

# ---- Intents ----
intents = discord.Intents.default()  # enough to send a message by channel ID
# (Message Content Intent is not required to send messages)

class Client(discord.Client):
    async def on_ready(self):
        print(f"✅ Logged in as {self.user} (id={self.user.id})")
        # Try cache, then API fetch
        channel = self.get_channel(CHANNEL_ID)
        if channel is None:
            try:
                channel = await self.fetch_channel(CHANNEL_ID)
            except Exception as e:
                print(f"❌ Could not fetch channel {CHANNEL_ID}: {e}")
                await self.close()
                return

        # Send with a small proof-of-run timestamp
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        try:
            await channel.send(f"{MESSAGE}\n\n_(Run at: {ts})_")
            print("✅ Message sent, shutting down.")
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
        finally:
            await self.close()  # end the job

client = Client(intents=intents)
client.run(TOKEN)
