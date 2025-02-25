import requests
import json
import os
import subprocess

API_URL = "https://api.lusternia.com/gamefeed.json"
DATA_FILE = "gamefeed_history.json"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1344011185481056286/0qUgo3x3PQ8_0lOlTa5wt_Gw-CDS_Wgi527-OEM4SJ9-CL4LgzXPN_t_YsggmQwCv49V"  # Replace with your actual webhook

# Function to fetch the latest game feed
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

# Function to pull latest history from GitHub
def pull_latest_history():
    if os.path.exists(DATA_FILE):
        try:
            subprocess.run(["git", "pull"], check=True)
            print("Successfully pulled latest gamefeed history.")
        except subprocess.CalledProcessError:
            print("Error pulling latest history from GitHub.")
    else:
        print("No existing history file found. Creating a new one.")

# Function to save gamefeed history and push it to GitHub
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

# Function to process and send new deaths to Discord
def process_and_send_updates(new_data):
    pull_latest_history()  # Get the latest stored data

    try:
        # Load existing data if available
        try:
            with open(DATA_FILE, "r") as f:
                history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            history = []

        # Extract existing IDs to prevent duplicates
        existing_ids = {entry.get("id") for entry in history}
        new_deaths = [entry for entry in new_data if entry.get("type") == "DEA" and entry.get("id") not in existing_ids]

        if new_deaths:
            for death in new_deaths:
                send_to_discord(death)
                history.append(death)

            save_and_push_history(history)  # Save the updated history and push it

            print(f"Sent {len(new_deaths)} new player deaths to Discord.")
        else:
            print("No new deaths found.")

    except Exception as e:
        print(f"Error processing data: {e}")

# Function to send the death message to Discord
def send_to_discord(death_entry):
    message = f"💀 **{death_entry['caption']}**\n{death_entry['description']}\n📅 {death_entry['date']}"
    
    payload = {"content": message}

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("Successfully sent to Discord!")
        else:
            print(f"Failed to send to Discord. Error: {response.status_code}")
    except Exception as e:
        print(f"Error sending to Discord: {e}")

# Run the script
fetch_gamefeed()
