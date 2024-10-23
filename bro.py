from flask import Flask
import threading
import time
import requests
import os
import random

app = Flask(__name__)

# URL to submit the form data
url = "https://groupsor.link/data/editgroup"

# Function to generate a random IP address
def generate_random_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

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
                "desc1": "",  # Description
                "tags1": "",  # Tags
                "ip": "",  # IP will be assigned during submission
                "gname": "",
                "gcid": gcid,
                "cid": cid,
                "lid": lid,
                "tags": "",
                "gdesc": '''chciicboobo9999b'''
            })
    return groups

# Function to submit a group edit request
def edit_group(group_data):
    # Generate one random IP for both the request and group data
    group_ip = generate_random_ip()
    group_data['ip'] = group_ip  # Assign the random IP to the group data

    # Use the same IP in the request header
    headers = {'X-Forwarded-For': group_ip}
    
    try:
        response = requests.post(url, data=group_data, headers=headers)
        if response.status_code == 200:
            print(f"Group {group_data['glink']} updated successfully with IP {group_ip}!")
        else:
            print(f"Failed to update group {group_data['glink']}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error updating group {group_data['glink']} with IP {group_ip}: {e}")

# Function to process groups concurrently
def edit_groups_concurrently(groups):
    for group_data in groups:
        # Every group submission will have a new IP that is consistent between the request and data
        threading.Thread(target=edit_group, args=(group_data,)).start()

# Function to handle the main logic
def run_group_updater():
    while True:
        try:
            file_path = os.getenv('GROUP_DATA_FILE', 'gpid_results.txt')  # Default to 'gpid_results.txt'
            groups = read_group_data(file_path)
            edit_groups_concurrently(groups)
            time.sleep(10)  # Wait for 10 seconds before the next iteration
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

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
