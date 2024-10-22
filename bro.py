from flask import Flask
import threading
import time
import requests
import os

app = Flask(__name__)

# URL to submit the form data
url = "https://groupsor.link/data/editgroup"

# Global variable to store dynamic IP
dynamic_ip = None

# Function to get current public IP dynamically
def fetch_dynamic_ip():
    global dynamic_ip
    while True:
        try:
            response = requests.get('http://ifconfig.me')  # External service to get the IP
            if response.status_code == 200:
                dynamic_ip = response.text.strip()  # Update dynamic_ip with fetched value
                print(f"Updated IP: {dynamic_ip}")
            else:
                print("Failed to fetch dynamic IP, using the last known IP.")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching dynamic IP: {e}")
        time.sleep(60)  # Update the IP every 60 seconds

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
                "desc1": "", # Description
                "tags1": "", # Tags
                "ip": dynamic_ip if dynamic_ip else "0.0.0.0",  # Use dynamic IP or default if not fetched yet
                "gname": "",
                "gcid": gcid,
                "cid": cid,
                "lid": lid,
                "tags": "",
                "gdesc": '''dear admin, this is just to took your attantion on some serius problem going on your platform please read my note here before you fix this again!!: https://pastebin.com/raw/wgBHjbkr'''
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
            file_path = os.getenv('GROUP_DATA_FILE', 'gpid_results.txt')  # Default to 'gpid_results.txt'
            groups = read_group_data(file_path)
            edit_groups_concurrently(groups)
            time.sleep(1)  # Wait for 10 seconds before the next iteration
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

# Flask route to keep the web service alive
@app.route('/')
def home():
    return "Service is running!"

if __name__ == "__main__":
    # Start the background thread for the dynamic IP fetcher
    ip_fetch_thread = threading.Thread(target=fetch_dynamic_ip)
    ip_fetch_thread.daemon = True  # Daemon thread to ensure it exits with the main program
    ip_fetch_thread.start()

    # Start the background thread for the group updater
    updater_thread = threading.Thread(target=run_group_updater)
    updater_thread.start()

    # Start the Flask web server
    app.run(host='0.0.0.0', port=5000)