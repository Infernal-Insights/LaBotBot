from labot.redis_db import save_product, r, publish_event
from labot.sync_to_mongo import sync_from_redis_to_mongo, _build_mongo_uri
from dotenv import load_dotenv
import pymongo
import datetime
import time
import os
import sys
import json
from urllib.request import urlopen
from urllib.error import URLError
from labot.utils import hash_id

def fetch_json_with_retry(url, retries=3, delay=2):
    """Fetch JSON data from ``url`` with basic retry logic."""
    for attempt in range(1, retries + 1):
        try:
            with urlopen(url) as resp:
                return json.load(resp)
        except URLError as e:
            print(f"Error fetching {url}: {e}. Retry {attempt}/{retries}")
            if attempt == retries:
                raise
            time.sleep(delay)

def check_mongo_connection():
    load_dotenv()
    try:
        uri = _build_mongo_uri()
    except RuntimeError as e:
        print(e)
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
        return True
    except Exception as e:
        print(f"MongoDB connection check FAILED: {e}")
        return False

def scrape(min_items=50):
    """Scrape Popmart products and store them in Redis."""
    print("Starting scrape for The Monsters collection ...")
    publish_event("Scraper started")

    page = 1
    scraped = 0
    while scraped < min_items:
        data_url = f"https://cdn-global.popmart.com/shop_productoncollection-11-1-{page}-us-en.json"
        try:
            collection_data = fetch_json_with_retry(data_url)
        except Exception:
            print("Giving up on fetching page", page)
            break

        products = collection_data.get("productData", [])
        if not products:
            break

        print(f"Page {page}: found {len(products)} products")

        for item in products:
            try:
                link = f"https://www.popmart.com/us/products/{item['id']}"
                name = item.get("title", "")
                description = item.get("subTitle", "")
                price = 0.0
                if item.get("skus"):
                    price = item["skus"][0].get("price", 0) / 100.0
                    in_stock = item["skus"][0].get("stock", {}).get("onlineStock", 0) > 0
                else:
                    in_stock = False
                image = item.get("bannerImages", [""])[0]

                pid = hash_id(link)
                existed = r.exists(f"product:{pid}")
                prev_stock = r.hget(f"product:{pid}", "in_stock") if existed else None
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
                if not existed:
                    publish_event(f"New product: {name} - {link}")
                elif prev_stock == '0' and in_stock:
                    publish_event(f"Back in stock: {name} - {link}")
                scraped += 1
                time.sleep(0.1)

            except Exception as e:
                print(f"Error processing product {item.get('id')}: {e}")

        if scraped >= min_items:
            break

        # end for item

        page += 1

    print(f"Scraped {scraped} products")
    publish_event(f"Scraped {scraped} products")

    try:
        sync_from_redis_to_mongo()
    except Exception as e:
        print(f"Mongo sync failed: {e}")
    print("Scrape and sync complete.")
    publish_event("Scrape and sync complete")

if __name__ == "__main__":
    check_mongo_connection()
    scrape()
