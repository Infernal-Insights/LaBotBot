import os
import time
from multiprocessing import Process

from dashboard import run as run_dashboard
from scraper import scrape
from buyer_bot import run as run_buyer
import asyncio


def start_dashboard():
    host = os.getenv("DASHBOARD_HOST", "127.0.0.1")
    port = int(os.getenv("DASHBOARD_PORT", "8000"))
    run_dashboard(host=host, port=port)


def main():
    interval = int(os.getenv("RUN_INTERVAL", "3600"))
    dash_proc = Process(target=start_dashboard, daemon=True)
    dash_proc.start()
    while True:
        scrape()
        asyncio.run(run_buyer())
        time.sleep(interval)


if __name__ == "__main__":
    main()
