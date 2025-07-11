import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def publish_event(message: str, channel: str = "bot_events") -> None:
    """Publish a one-off message to the given Redis pubsub channel."""
    try:
        r.publish(channel, message)
    except Exception:
        # Ignore Redis errors so callers don't fail if Redis is down
        pass

def get_pubsub(channel: str = "bot_events"):
    """Return a PubSub instance subscribed to the given channel."""
    pubsub = r.pubsub()
    pubsub.subscribe(channel)
    return pubsub

def save_product(pid, data):
    r.hset(f"product:{pid}", mapping=data)
    r.zadd("product_ids", {pid: 0})
    r.expire(f"product:{pid}", 43200)

def get_all_products():
    ids = r.zrange("product_ids", 0, -1)
    return [r.hgetall(f"product:{i}") for i in ids]

def get_eligible_products(max_price=30.0, max_items=6):
    return [p for p in get_all_products() if p.get('in_stock') == '1' and float(p.get('price', 0)) <= max_price][:max_items]

def get_priority_links():
    return r.zrevrange("priority_products", 0, -1)

def add_priority_link(link, score=100):
    r.zadd("priority_products", {link: score})
