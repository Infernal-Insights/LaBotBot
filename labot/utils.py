import time
import logging
import asyncio
import hashlib


logger = logging.getLogger(__name__)


def hash_id(text: str) -> str:
    """Return a stable hash for the given text."""
    return hashlib.md5(text.encode()).hexdigest()


def login(page, username: str, password: str):
    """Log in to Popmart using the provided credentials using the sync API."""

    login_url = "https://www.popmart.com/us/user/login?redirect=%2Faccount"
    page.goto(login_url, wait_until="domcontentloaded", timeout=60000)

    # Dismiss the cookie/privacy banner if it appears. The exact class name
    # changes occasionally, so try a few variants and fall back to a text match.
    for selector in [
        "div[class*='policy_acceptBtn']",
        "div.policy_acceptBtn__ZNU71",
        "text=ACCEPT",
    ]:
        try:
            page.locator(selector).click(timeout=2000)
            page.wait_for_selector(selector, state="detached", timeout=3000)
            break
        except Exception:
            pass

    page.wait_for_selector("input#email", timeout=60000)
    page.fill("input#email", username)
    page.locator("button:has-text('CONTINUE')").click()

    page.wait_for_selector("input#password", timeout=60000)
    page.fill("input#password", password)
    page.locator("button[type='submit']").click()
    page.wait_for_load_state("networkidle")


async def async_login(page, username: str, password: str):
    """Async version of :func:`login` for Playwright's async API."""

    login_url = "https://www.popmart.com/us/user/login?redirect=%2Faccount"
    await page.goto(login_url, wait_until="domcontentloaded", timeout=60000)

    for selector in [
        "div[class*='policy_acceptBtn']",
        "div.policy_acceptBtn__ZNU71",
        "text=ACCEPT",
    ]:
        try:
            await page.locator(selector).click(timeout=2000)
            await page.wait_for_selector(selector, state="detached", timeout=3000)
            break
        except Exception:
            pass

    await page.wait_for_selector("input#email", timeout=60000)
    await page.fill("input#email", username)
    await page.locator("button:has-text('CONTINUE')").click()

    await page.wait_for_selector("input#password", timeout=60000)
    await page.fill("input#password", password)
    await page.locator("button[type='submit']").click()
    await page.wait_for_load_state("networkidle")


def try_to_buy(page, link):
    """Attempt to buy a product using the sync API."""

    try:
        page.goto(link, wait_until="networkidle", timeout=120000)
        logger.info("Watching %s for stock", link)

        page.wait_for_selector(".product__price", timeout=120000)
        price = page.text_content(".product__price")
        price_value = float(price.strip().replace("$", "")) if price else 0.0

        page.wait_for_selector(
            "button.product__button[name='add']:not([disabled]), button:has-text('ADD TO CART'):not([disabled])",
            timeout=60000,
        )
        page.locator(
            "button.product__button[name='add']:not([disabled]), button:has-text('ADD TO CART'):not([disabled])"
        ).first.click()
        page.goto(
            "https://www.popmart.com/cart", wait_until="domcontentloaded", timeout=60000
        )
        page.click("button[name='checkout']")

        success = False
        try:
            page.wait_for_selector("text=Order", timeout=10000)
            success = True
        except Exception:
            logger.warning("Checkout confirmation not detected for %s", link)
        time.sleep(3)
        return price_value, success

    except Exception as e:
        logger.error("Failed to purchase %s: %s", link, e)
        return 0.0, False


async def async_try_to_buy(page, link):
    """Async version of :func:`try_to_buy`."""

    try:
        await page.goto(link, wait_until="networkidle", timeout=120000)
        logger.info("Watching %s for stock", link)

        await page.wait_for_selector(".product__price", timeout=120000)
        price = await page.text_content(".product__price")
        price_value = float(price.strip().replace("$", "")) if price else 0.0

        await page.wait_for_selector(
            "button.product__button[name='add']:not([disabled]), button:has-text('ADD TO CART'):not([disabled])",
            timeout=60000,
        )
        await page.locator(
            "button.product__button[name='add']:not([disabled]), button:has-text('ADD TO CART'):not([disabled])"
        ).first.click()
        await page.goto(
            "https://www.popmart.com/cart", wait_until="domcontentloaded", timeout=60000
        )
        await page.click("button[name='checkout']")

        success = False
        try:
            await page.wait_for_selector("text=Order", timeout=10000)
            success = True
        except Exception:
            logger.warning("Checkout confirmation not detected for %s", link)
        await asyncio.sleep(3)
        return price_value, success

    except Exception as e:
        logger.error("Failed to purchase %s: %s", link, e)
        return 0.0, False


def get_price(page, link):
    page.goto(link, wait_until="networkidle", timeout=120000)
    try:
        page.wait_for_selector(".product__price", timeout=120000)
        price = page.text_content(".product__price")
    except Exception as e:
        logger.error("Failed to get price from %s: %s", link, e)
        return 0.0
    return float(price.strip().replace("$", "")) if price else 0.0


async def async_get_price(page, link):
    await page.goto(link, wait_until="networkidle", timeout=120000)
    try:
        await page.wait_for_selector(".product__price", timeout=120000)
        price = await page.text_content(".product__price")
    except Exception as e:
        logger.error("Failed to get price from %s: %s", link, e)
        return 0.0
    return float(price.strip().replace("$", "")) if price else 0.0
