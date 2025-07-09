
import discord
import os
import asyncio
from dotenv import load_dotenv
from labot.redis_db import add_priority_link, get_pubsub

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_NOTIFY_CHANNEL_ID"))

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)
pubsub = get_pubsub()

async def forward_events():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        channel = await client.fetch_channel(CHANNEL_ID)
    while True:
        msg = pubsub.get_message()
        if msg and msg.get("type") == "message":
            content = msg["data"]
            if isinstance(content, bytes):
                content = content.decode()
            await channel.send(content)
        await asyncio.sleep(1)

@client.event
async def on_ready():
    print(f"✅ Discord Bot is online as {client.user}")
    client.loop.create_task(forward_events())

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
