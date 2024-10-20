from flask import Flask
import threading
import time
import requests
import os

app = Flask(__name__)

# URL to submit the form data
url = "https://groupsor.link/data/editgroup"

# Function to read group data from a text file
def read_group_data(file_path):
    groups = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            glink, group_id, code, gcid, cid, lid = line.strip().split(',')
            groups.append({
                "glink": glink,
                "id": group_id,
                "code": code,
                "gname": "Kavach",
                "gcid": gcid,
                "cid": cid,
                "lid": lid,
                "tags": "",
                "gdesc": '''<strong><font color="#FF1493" size="4">Aʟʟ Tʏᴘᴇ Vɪᴅᴇᴏs🥵🤤ʟɪɴᴋ👇</font><br><br><font color="blue" size="3">👉🏻 https://dub.sh/xxcvideo 👈</font></strong><br><br>Cᴏᴘʏ ᴀɴᴅ ᴏᴘᴇɴ ᴀʙᴏᴠᴇ URL ɪɴ Bʀᴏᴡsᴇʀ ᴛᴏ ᴡᴀᴛᴄʜ ᴠɪᴅᴇᴏs'''
            })
    return groups

# Function to submit a group edit request
def edit_group(group_data):
    try:
        response = requests.post(url, data=group_data)
        if response.status_code == 200:
            print(f"Group {group_data['glink']} updated successfully!")
        else:
            print(f"Failed to update group {group_data['glink']}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error updating group {group_data['glink']}: {e}")

# Function to process groups concurrently
def edit_groups_concurrently(groups):
    for group_data in groups:
        threading.Thread(target=edit_group, args=(group_data,)).start()

# Function to handle the main logic
def run_group_updater():
    while True:
        try:
            file_path = os.getenv('GROUP_DATA_FILE', 'gpid_results.txt')  # Default to 'gpids.txt'
            groups = read_group_data(file_path)
            edit_groups_concurrently(groups)
            time.sleep(1)  # Wait for 10 seconds before the next iteration
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(900)

# Flask route to keep the web service alive
@app.route('/')
def home():
    return "Service is running!"

if __name__ == "__main__":
    # Start the background thread for the group updater
    updater_thread = threading.Thread(target=run_group_updater)
    updater_thread.start()

    # Start the Flask web server
    app.run(host='0.0.0.0', port=5000)
