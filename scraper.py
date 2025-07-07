
from playwright.sync_api import sync_playwright
from redis_db import save_product
from sync_to_mongo import sync_from_redis_to_mongo
from dotenv import load_dotenv
import pymongo
import datetime
import hashlib
import time
import os
import sys

def hash_id(text):
    return hashlib.md5(text.encode()).hexdigest()

def check_mongo_connection():
    load_dotenv()
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("MONGODB_URI is not set.")
        sys.exit(1)
    try:
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
        db = client["popmart"]
        test_col = db["connection_test"]
        doc = {"_id": "connection_test", "ts": datetime.datetime.utcnow()}
        test_col.insert_one(doc)
        test_col.delete_one({"_id": "connection_test"})
        client.close()
        print("MongoDB connection check: SUCCESS")
    except Exception as e:
        print(f"MongoDB connection check FAILED: {e}")
        sys.exit(1)

def scrape():
    print("Starting scrape for The Monsters collection ...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.popmart.com/us/collection/11")
        page.wait_for_load_state("networkidle")

        links = page.eval_on_selector_all(
            "a.product-card-link[href*='/us/product/']",
            "els => els.map(el => el.href)"
        )
        print(f"Found {len(links)} product pages")

        for link in links:
            try:
                page.goto(link)
                name = page.text_content("h1.product__title").strip()
                print(f"Scraping: {name} -> {link}")
                price = float(page.text_content(".product__price").strip().replace("$", ""))
                description = page.text_content(".product__description").strip()
                image = page.get_attribute(".product__media img", "src")
                in_stock = not page.query_selector("button.product__button[name='add']:disabled")

                pid = hash_id(link)
                save_product(pid, {
                    "name": name,
                    "url": link,
                    "price": price,
                    "description": description,
                    "image": image,
                    "in_stock": int(in_stock),
                    "priority_score": 0,
                    "is_priority": 0,
                    "source": "scraped",
                    "last_checked": datetime.datetime.utcnow().isoformat()
                })
                time.sleep(0.5)

            except Exception as e:
                print(f"Error scraping product: {link} — {e}")

        browser.close()
        sync_from_redis_to_mongo()
        print("Scrape and sync complete.")

if __name__ == "__main__":
    check_mongo_connection()
    scrape()
