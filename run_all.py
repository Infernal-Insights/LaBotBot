import os
import time
from multiprocessing import Process

from dashboard import run as run_dashboard
from scraper import scrape
from buyer_bot import run as run_buyer


def start_dashboard():
    host = os.getenv("DASHBOARD_HOST", "127.0.0.1")
    port = int(os.getenv("DASHBOARD_PORT", "8000"))
    try:
        run_dashboard(host=host, port=port)
    except OSError as exc:
        if exc.errno in (99, 98):
            print(
                f"Failed to bind to {host}:{port}, starting on 0.0.0.0 instead"
            )
            run_dashboard(host="0.0.0.0", port=port)
        else:
            raise


def main():
    interval = int(os.getenv("RUN_INTERVAL", "3600"))
    dash_proc = Process(target=start_dashboard, daemon=True)
    dash_proc.start()
    while True:
        scrape()
        run_buyer()
        time.sleep(interval)


if __name__ == "__main__":
    main()
