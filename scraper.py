
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
import json
from urllib.request import urlopen

def hash_id(text):
    return hashlib.md5(text.encode()).hexdigest()

def check_mongo_connection():
    load_dotenv()
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("MONGODB_URI is not set.")
        return False
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

    page = 1
    scraped = 0
    while scraped < min_items:
        data_url = f"https://cdn-global.popmart.com/shop_productoncollection-11-1-{page}-us-en.json"
        with urlopen(data_url) as resp:
            collection_data = json.load(resp)

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
                scraped += 1
                time.sleep(0.1)

            except Exception as e:
                print(f"Error processing product {item.get('id')}: {e}")

        if scraped >= min_items:
            break

        # end for item

        page += 1

    print(f"Scraped {scraped} products")

    try:
        sync_from_redis_to_mongo()
    except Exception as e:
        print(f"Mongo sync failed: {e}")
    print("Scrape and sync complete.")

if __name__ == "__main__":
    check_mongo_connection()
    scrape()
