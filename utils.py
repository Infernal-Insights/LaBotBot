def try_to_buy(page, link):
    from dotenv import load_dotenv
    import os
    import time

    load_dotenv()
    USERNAME = os.getenv("POP_USERNAME")
    PASSWORD = os.getenv("POP_PASSWORD")

    login_url = "https://www.popmart.com/us/user/login?redirect=%2Faccount"
    page.goto(login_url, wait_until="domcontentloaded", timeout=60000)

    # Dismiss privacy policy overlay if it appears
    try:
        page.locator("div.policy_acceptBtn__ZNU71").click(timeout=5000)
    except Exception:
        pass

    page.wait_for_selector("input#email", timeout=60000)
    page.fill("input#email", USERNAME)
    page.locator("button:has-text('CONTINUE')").click()

    page.wait_for_selector("input#password", timeout=60000)
    page.fill("input#password", PASSWORD)
    page.locator("button[type='submit']").click()
    page.wait_for_load_state("domcontentloaded")

    page.goto(link, wait_until="networkidle", timeout=120000)
    print(f"Watching {link} for stock...")
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
    time.sleep(3)
    return price_value


def get_price(page, link):
    page.goto(link, wait_until="networkidle", timeout=120000)
    try:
        page.wait_for_selector(".product__price", timeout=120000)
        price = page.text_content(".product__price")
    except Exception as e:
        print(f"Failed to get price from {link}: {e}")
        return 0.0
    return float(price.strip().replace("$", "")) if price else 0.0
