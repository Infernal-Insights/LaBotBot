import time
import logging


logger = logging.getLogger(__name__)


def login(page, username: str, password: str):
    """Log in to Popmart using the provided credentials."""

    login_url = "https://www.popmart.com/us/user/login?redirect=%2Faccount"
    page.goto(login_url, wait_until="domcontentloaded", timeout=60000)

    # Dismiss privacy policy overlay if it appears
    try:
        page.locator("div.policy_acceptBtn__ZNU71").click(timeout=5000)
    except Exception:
        pass

    page.wait_for_selector("input#email", timeout=60000)
    page.fill("input#email", username)
    page.locator("button:has-text('CONTINUE')").click()

    page.wait_for_selector("input#password", timeout=60000)
    page.fill("input#password", password)
    page.locator("button[type='submit']").click()
    page.wait_for_load_state("networkidle")


def try_to_buy(page, link):
    """Attempt to buy a product. Expects the user to already be logged in."""

    try:
        page.goto(link, wait_until="networkidle", timeout=120000)
        logger.info("Watching %s for stock", link)

        page.wait_for_selector(".product__price", timeout=120000)
        price = page.text_content(".product__price")
        price_value = float(price.strip().replace("$", "")) if price else 0.0

        page.wait_for_selector(
            "button.product__button[name='add']:not([disabled])", timeout=60000
        )
        page.click("button.product__button[name='add']")
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


def get_price(page, link):
    page.goto(link, wait_until="networkidle", timeout=120000)
    try:
        page.wait_for_selector(".product__price", timeout=120000)
        price = page.text_content(".product__price")
    except Exception as e:
        logger.error("Failed to get price from %s: %s", link, e)
        return 0.0
    return float(price.strip().replace("$", "")) if price else 0.0
