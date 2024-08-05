import requests
import time
import concurrent.futures

# Fetch data from the source API
response = requests.get("https://randomuser.me/api/?results=300", timeout=100)
data = response.json()

# Extract names from the fetched data
names = [result["name"]["first"] for result in data["results"]]

# Send names to the destination API
destination_url = "http://192.168.49.2:30003/load"

# Function to send a POST request
def send_post_request(name):
    payload = {"name": name}
    start_time = time.time()
    response = requests.post(destination_url, json=payload, timeout=10)
    end_time = time.time()
    duration = end_time - start_time
    if response.status_code == 200:
        print(f"Data loaded successfully for {name} in {duration:.2f} seconds.")
    else:
        print(f"Failed to load data for {name}. Response code: {response.status_code}, Time taken: {duration:.2f} seconds.")

# Use ThreadPoolExecutor to send requests in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(send_post_request, name) for name in names]
    concurrent.futures.wait(futures)

print("Data loading completed.")
