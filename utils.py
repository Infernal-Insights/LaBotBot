def try_to_buy(page, link):
    from dotenv import load_dotenv
    import os
    import time
    load_dotenv()
    USERNAME = os.getenv("POP_USERNAME")
    PASSWORD = os.getenv("POP_PASSWORD")

    page.goto("https://www.popmart.com/account/login")
    page.fill("input[name='customer[email]']", USERNAME)
    page.fill("input[name='customer[password]']", PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")

    page.goto(link)
    print(f"Watching {link} for stock...")
    price = page.text_content(".product__price")
    price_value = float(price.strip().replace("$", "")) if price else 0.0
    page.wait_for_selector("button.product__button[name='add']:not([disabled])", timeout=0)
    page.click("button.product__button[name='add']")
    page.goto("https://www.popmart.com/cart")
    page.click("button[name='checkout']")
    time.sleep(3)
    return price_value


def get_price(page, link):
    page.goto(link)
    price = page.text_content(".product__price")
    return float(price.strip().replace("$", "")) if price else 0.0
