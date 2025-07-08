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
   MAX_ITEMS=6
   MONGODB_USERNAME=db_username
   MONGODB_PASSWORD=db_password
   MONGODB_CLUSTER=cluster0.ecntfwt.mongodb.net
   MONGODB_DATABASE=popmart
   DASHBOARD_USER=admin
   DASHBOARD_PASS=secret
   ```
   Replace the values with your own credentials. The MongoDB connection string is built automatically using these variables.
4. Ensure Redis and MongoDB are running and accessible. If using Atlas, whitelist your VM's IP address.

## Running

The usual workflow is:

1. Run the scraper to collect product data:
   ```bash
   python scraper.py
   ```
2. Optionally run the Discord listener if you want to add links via Discord:
   ```bash
   python discord_listener.py
   ```
3. Run the buyer bot to attempt purchases:
   ```bash
   python buyer_bot.py
   ```

Each script loads the `.env` file for configuration. If `DISCORD_BOT_TOKEN` and
`DISCORD_NOTIFY_CHANNEL_ID` are not set, the buyer bot prints notifications to
stdout instead of sending them to Discord.
The buyer bot also logs its actions to `buyer_bot.log` for later review.

To run everything automatically, use the `run_all.py` helper:

```bash
python run_all.py
```

This script launches the dashboard in a background process, runs the scraper,
then runs the buyer bot. It repeats this cycle every hour by default. Set the
`RUN_INTERVAL` environment variable (in seconds) to change the interval.
## Dashboard

Run `python dashboard.py` to start a simple status page on `http://localhost:8000`.
The page refreshes automatically every 10 seconds and lists the priority links
that the buyer bot will attempt to purchase. JSON APIs are also available at
`/api/priority` and `/api/products`.
If you set `DASHBOARD_USER` and `DASHBOARD_PASS` in your `.env` file, the page
will require HTTP Basic authentication. The dashboard binds to `127.0.0.1` by
default. To expose it remotely, set `DASHBOARD_HOST` and `DASHBOARD_PORT` in
your environment, e.g. `DASHBOARD_HOST=64.225.91.160`. For secure remote
access, consider tunneling the port over SSH instead of exposing it directly.
## Scheduling

The scripts can be scheduled with cron. While logged in as `labot`, add entries using `crontab -e`:

```cron
# Automatically start everything at boot
@reboot cd /LaBotBot && /LaBotBot/.venv/bin/python run_all.py >> /var/log/labotbot.log 2>&1

# If you prefer separate jobs, schedule them like this:
0 * * * * cd /LaBotBot && /LaBotBot/.venv/bin/python scraper.py >> /var/log/scraper.log 2>&1
*/10 * * * * cd /LaBotBot && /LaBotBot/.venv/bin/python buyer_bot.py >> /var/log/buyer.log 2>&1
```

## Troubleshooting

If the `playwright` command is missing after a reboot, reactivate the virtual
environment:

```bash
source .venv/bin/activate
```

Then reinstall dependencies and browsers if needed:

```bash
pip install -r requirements.txt
playwright install
```

