
import pymongo
import redis
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
mongo_client = pymongo.MongoClient(os.getenv("MONGODB_URI"))
mongo_db = mongo_client["popmart"]
product_collection = mongo_db["products"]

product_collection.create_index("url", unique=True)
product_collection.create_index("availability.in_stock")
product_collection.create_index("priority_score")

def sync_from_redis_to_mongo():
    ids = r.zrange("product_ids", 0, -1)
    print(f"Syncing {len(ids)} products from Redis to MongoDB ...")
    for pid in ids:
        product = r.hgetall(f"product:{pid}")
        if not product:
            continue

        history_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "price": float(product.get("price", 0)),
            "in_stock": bool(int(product.get("in_stock", 0)))
        }

        product_doc = {
            "_id": pid,
            "name": product.get("name"),
            "url": product.get("url"),
            "price": float(product.get("price", 0)),
            "currency": "USD",
            "description": product.get("description", ""),
            "image_url": product.get("image", ""),
            "availability": {
                "in_stock": bool(int(product.get("in_stock", 0))),
                "last_checked": datetime.utcnow().isoformat()
            },
            "priority_score": int(product.get("priority_score", 0)),
            "is_priority": bool(int(product.get("is_priority", 0))),
            "source": product.get("source", "scraped"),
            "tags": product.get("tags", "").split(",") if product.get("tags") else []
        }

        product_collection.update_one(
            {"_id": pid},
            {"$set": product_doc, "$push": {"history": history_entry}},
            upsert=True
        )
        print(f"Synced product {pid}")

def sync_from_mongo_to_redis(limit=50):
    cursor = product_collection.find({"availability.in_stock": True, "price": {"$lte": 30}}).limit(limit)
    count = 0
    for doc in cursor:
        pid = doc["_id"]
        r.hset(f"product:{pid}", mapping={
            "name": doc.get("name"),
            "url": doc.get("url"),
            "price": doc.get("price"),
            "description": doc.get("description"),
            "image": doc.get("image_url"),
            "in_stock": int(doc.get("availability", {}).get("in_stock", 0)),
            "priority_score": doc.get("priority_score", 0),
            "is_priority": int(doc.get("is_priority", False)),
            "source": doc.get("source", "scraped"),
            "tags": ",".join(doc.get("tags", []))
        })
        r.zadd("product_ids", {pid: 0})
        r.expire(f"product:{pid}", 43200)
        count += 1
    print(f"Synced {count} products from MongoDB to Redis")
