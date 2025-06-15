from playwright.sync_api import sync_playwright
from redis_db import get_priority_links
from dotenv import load_dotenv
from utils import try_to_buy
import discord
import asyncio
import time
import os

load_dotenv()
USERNAME = os.getenv("POP_USERNAME")
PASSWORD = os.getenv("POP_PASSWORD")
CHANNEL_ID = int(os.getenv("DISCORD_NOTIFY_CHANNEL_ID"))
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

MAX_ITEMS = 6

def notify_discord(message):
    async def send():
        client = discord.Client(intents=discord.Intents.default())
        await client.login(DISCORD_TOKEN)
        channel = await client.fetch_channel(CHANNEL_ID)
        await channel.send(message)
        await client.close()
    asyncio.run(send())

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        links = get_priority_links()
        count = 0

        for link in links:
            if count >= MAX_ITEMS:
                break
            try_to_buy(page, link)
            notify_discord(f"✅ Purchased: {link}")
            count += 1

        browser.close()

if __name__ == "__main__":
    run()
