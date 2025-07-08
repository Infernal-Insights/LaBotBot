from playwright.async_api import async_playwright
from labot.redis_db import get_priority_links
from dotenv import load_dotenv
from labot.utils import async_try_to_buy, async_get_price, async_login
import discord
import asyncio
import logging
import os

file_handler = logging.FileHandler("buyer_bot.log")
try:
    os.chmod("buyer_bot.log", 0o600)
except OSError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        file_handler,
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

load_dotenv()
USERNAME = os.getenv("POP_USERNAME")
PASSWORD = os.getenv("POP_PASSWORD")
CHANNEL_ID = os.getenv("DISCORD_NOTIFY_CHANNEL_ID")
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DAILY_BUDGET = os.getenv("MAX_DAILY_BUDGET")
DAILY_BUDGET = float(DAILY_BUDGET) if DAILY_BUDGET else 0.0

MAX_ITEMS = int(os.getenv("MAX_ITEMS", "6"))

def notify_discord(message):
    async def send():
        client = discord.Client(intents=discord.Intents.default())
        await client.login(DISCORD_TOKEN)
        channel = await client.fetch_channel(int(CHANNEL_ID))
        await channel.send(message)
        await client.close()
    asyncio.run(send())

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            bypass_csp=True,
        )
        context.set_default_timeout(60000)
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        page = await context.new_page()

        if USERNAME and PASSWORD:
            logger.info("Logging in as %s", USERNAME)
            try:
                await async_login(page, USERNAME, PASSWORD)
            except Exception as e:
                logger.error("Login failed: %s", e)
                await browser.close()
                return
        else:
            logger.error("POP_USERNAME or POP_PASSWORD not set")
            browser.close()
            return

        links = get_priority_links()
        count = 0
        spent = 0.0

        for link in links:
            if count >= MAX_ITEMS:
                break

            price = await async_get_price(page, link)
            if DAILY_BUDGET and spent + price > DAILY_BUDGET:
                print(f"Skipping {link} — daily budget exceeded")
                continue

            price_paid, success = await async_try_to_buy(page, link)
            if success:
                spent += price_paid
                message = f"✅ Purchased: {link} for ${price_paid}"
                logger.info(message)
                if DISCORD_TOKEN and CHANNEL_ID:
                    notify_discord(message)
                else:
                    print(message)
                count += 1
            else:
                logger.warning("Failed purchase attempt for %s", link)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
