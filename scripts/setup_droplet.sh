#!/usr/bin/env bash
set -euo pipefail

# This script installs system dependencies, clones or updates the LaBotBot
# repository, sets up a Python virtual environment and installs Python
# requirements. It also installs the Chromium browser for Playwright.

# Required packages
sudo apt-get update
sudo apt-get install -y git python3 python3-pip python3-venv redis-server

# Directory where the repo will live
REPO_DIR="$HOME/LaBotBot"
REPO_URL="${REPO_URL:-https://github.com/your_username/LaBotBot.git}"

if [ -d "$REPO_DIR/.git" ]; then
    echo "Updating existing repository in $REPO_DIR"
    git -C "$REPO_DIR" pull
else
    echo "Cloning repository into $REPO_DIR"
    git clone "$REPO_URL" "$REPO_DIR"
fi

cd "$REPO_DIR"

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

echo "\nSetup complete."

#------------------------------------------
# Create a .env file in the repository root
# containing values for these variables:
# POP_USERNAME
# POP_PASSWORD
# DISCORD_BOT_TOKEN
# DISCORD_NOTIFY_CHANNEL_ID
# MONGODB_URI
#------------------------------------------
