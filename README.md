# LaBotBot

## Droplet setup

Use `scripts/setup_droplet.sh` on a fresh Ubuntu system to install dependencies and prepare the environment.

```bash
bash scripts/setup_droplet.sh
```

The script installs required system packages, clones (or updates) this repository, sets up a Python virtual environment, installs `requirements.txt`, and installs Playwright's Chromium browser.

Create a `.env` file in the repository root containing the following variables:

```
POP_USERNAME=
POP_PASSWORD=
DISCORD_BOT_TOKEN=
DISCORD_NOTIFY_CHANNEL_ID=
MONGODB_URI=
```
