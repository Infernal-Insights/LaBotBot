
import discord
import os
from dotenv import load_dotenv
from redis_db import add_priority_link

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_NOTIFY_CHANNEL_ID"))

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Discord Bot is online as {client.user}")

@client.event
async def on_message(message):
    if message.channel.id != CHANNEL_ID or message.author == client.user:
        return

    if message.content.startswith("https://www.popmart.com/us/products/"):
        add_priority_link(message.content, score=100)
        await message.channel.send(f"🔗 Added to priority: {message.content}")
    elif message.content == "!status":
        await message.channel.send("🤖 Bot is running and listening.")
    elif message.content == "!clear":
        await message.channel.send("⚠️ Clear command not implemented yet.")
    else:
        await message.channel.send("❓ Unknown command.")

client.run(TOKEN)
