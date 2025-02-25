import requests
import json
import os
import subprocess

API_URL = "https://api.lusternia.com/gamefeed.json"
DATA_FILE = "gamefeed_history.json"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1344011185481056286/0qUgo3x3PQ8_0lOlTa5wt_Gw-CDS_Wgi527-OEM4SJ9-CL4LgzXPN_t_YsggmQwCv49V"  # Replace with your actual webhook URL

def fetch_gamefeed():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            new_data = response.json()
            process_and_send_updates(new_data)
        else:
            print(f"Error fetching data: {response.status_code}")
    except Exception as e:
        print(f"Request failed: {e}")

# Pull the latest history from GitHub before making changes
def pull_latest_history():
    try:
        subprocess.run(["git", "pull"], check=True)
        print("Pulled latest gamefeed history.")
    except subprocess.CalledProcessError:
        print("Error pulling latest history from GitHub.")

# Save gamefeed history and push it to GitHub
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

def process_and_send_updates(new_data):
    pull_latest_history()  # Get the latest stored history

    try:
        # Load existing data
        try:
            with open(DATA_FILE, "r") as f:
                history = json.
