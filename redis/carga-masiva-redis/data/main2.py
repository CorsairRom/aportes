import requests
import time
# Fetch data from the source API
response = requests.get("https://randomuser.me/api/?results=300", timeout=100)
data = response.json()

# Extract names from the fetched data
names = [result["name"]["first"] for result in data["results"]]

# Send names to the destination API
destination_url = "http://192.168.49.2:30003/load"
payload = {"name": names}  # Change "names" to "name"
response = requests.post(destination_url)

# Check the response from the destination API

for name in names:
    payload = {"name": name}
    response = requests.post(destination_url, json=payload, timeout=10)
    if response.status_code == 200:
        time.sleep(0.5)
        print("Data loaded successfully!")
    else:
        print(f"Failed to load data. Response code: {response.status_code}")
    if response.status_code == 415:
        print(f"Data loaded successfully for name: {name}")
        print(f"Data loaded successfully for name: {response.content}")
    if response.status_code != 200:
        print(f"Failed to load data for name: {name}")
