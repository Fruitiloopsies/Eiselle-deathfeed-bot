import requests
import json

API_URL = "https://api.lusternia.com/gamefeed.json"
DATA_FILE = "gamefeed_history.json"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1344011185481056286/0qUgo3x3PQ8_0lOlTa5wt_Gw-CDS_Wgi527-OEM4SJ9-CL4LgzXPN_t_YsggmQwCv49V"  # Replace this

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

def process_and_send_updates(new_data):
    try:
        # Load existing data if available
        try:
            with open(DATA_FILE, "r") as f:
                history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            history = []

        # Filter only "DEA" events
        existing_ids = {entry.get("id") for entry in history}
        new_deaths = [entry for entry in new_data if entry.get("type") == "DEA" and entry.get("id") not in existing_ids]

        if new_deaths:
            for death in new_deaths:
                send_to_discord(death)  # Send each death to Discord
                history.append(death)  # Save it to history

            # Save back to file
            with open(DATA_FILE, "w") as f:
                json.dump(history, f, indent=4)

            print(f"Sent {len(new_deaths)} new player deaths to Discord.")

    except Exception as e:
        print(f"Error processing data: {e}")

def send_to_discord(death_entry):
    """Send a formatted death event to Discord"""
    message = f"💀 **{death_entry['caption']}**\n{death_entry['description']}\n📅 {death_entry['date']}"
    
    payload = {
        "content": message
    }

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
