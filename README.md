# LaBotBot

Simple scripts for scraping PopMart products, listening for priority links via Discord and attempting to purchase items automatically.

## Requirements

- Python 3.10+
- Redis server running on `localhost:6379`
- MongoDB instance (local or Atlas)
- Playwright browsers

## Setup

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies and the Playwright browsers:
   ```bash
   pip install -r requirements.txt
   playwright install
   ```
3. Create a `.env` file in this directory with the following variables:
   ```ini
   POP_USERNAME=your_username
   POP_PASSWORD=your_password
   DISCORD_BOT_TOKEN=your_discord_token
   DISCORD_NOTIFY_CHANNEL_ID=1234567890
   MAX_DAILY_BUDGET=100.0
   MONGODB_URI=mongodb+srv://<db_username>:<db_password>@cluster0.ecntfwt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
   DASHBOARD_USER=admin
   DASHBOARD_PASS=secret
   ```
   Replace the values with your own credentials. When using MongoDB Atlas, paste your cluster's connection string into `MONGODB_URI`.
4. Ensure Redis and MongoDB are running and accessible. If using Atlas, whitelist your VM's IP address.

## Running

- Scraper: `python scraper.py`
- Discord listener: `python discord_listener.py`
- Buyer bot: `python buyer_bot.py`

Each script loads the `.env` file for configuration.
## Dashboard

Run `python dashboard.py` to start a simple status page on `http://localhost:8000`.
The page refreshes automatically every 10 seconds and lists the priority links
that the buyer bot will attempt to purchase. JSON APIs are also available at
`/api/priority` and `/api/products`.
If you set `DASHBOARD_USER` and `DASHBOARD_PASS` in your `.env` file, the page
will require HTTP Basic authentication. Host and port can be overridden with the
`DASHBOARD_HOST` and `DASHBOARD_PORT` environment variables. For secure remote
access, consider tunneling the port over SSH instead of exposing it directly.
## Scheduling

The scripts can be scheduled with cron. While logged in as `labot`, add entries using `crontab -e`:

```cron
# Run scraper every hour
0 * * * * cd /LaBotBot && /LaBotBot/.venv/bin/python scraper.py >> /var/log/scraper.log 2>&1

# Run buyer bot every 10 minutes
*/10 * * * * cd /LaBotBot && /LaBotBot/.venv/bin/python buyer_bot.py >> /var/log/buyer.log 2>&1
```

