import requests
import json
import os
import subprocess

API_URL = "https://api.lusternia.com/gamefeed.json"
DATA_FILE = "gamefeed_history.json"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1344011185481056286/0qUgo3x3PQ8_0lOlTa5wt_Gw-CDS_Wgi527-OEM4SJ9-CL4LgzXPN_t_YsggmQwCv49V"  # Replace this

# Ensure history is updated
def pull_latest_history():
    if os.path.exists(DATA_FILE):
        try:
            subprocess.run(["git", "pull"], check=True)
            print("Pulled latest gamefeed history.")
        except subprocess.CalledProcessError:
            print("Error pulling latest history from GitHub.")

# Save history and push it to GitHub
def save_and_push_history(history):
    with open(DATA_FILE, "w") as f:
        json.dump(history, f, indent=4)

    try:
        subprocess.run(["git", "add", DATA_FILE], check=True)
        subprocess.run(["git", "commit", "-m", "Updated gamefeed history"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Successfully updated gamefeed history.")
    except subprocess.CalledProcessError:
        print("Error pushing updated history to GitHub.")

# Fetch and process data
def fetch_gamefeed():
    pull_latest_history()
    response = requests.get(API_URL)
    if response.status_code == 200:
        process_and_send_updates(response.json())

def process_and_send_updates(new_data):
    try:
        with open(DATA_FILE, "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    existing_ids = {entry.get("id") for entry in history}
    new_deaths = [entry for entry in new_data if entry.get("type") == "DEA" and entry.get("id") not in existing_ids]

    if new_deaths:
        for death in new_deaths:
            send_to_discord(death)
            history.append(death)

        save_and_push_history(history)
    else:
        print("No new deaths found.")

def send_to_discord(death_entry):
    message = f"💀 **{death_entry['caption']}**\n{death_entry['description']}\n📅 {death_entry['date']}"
    requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

fetch_gamefeed()
