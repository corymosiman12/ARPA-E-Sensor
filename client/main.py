import my_photo
import json

# Where will everything be running?
base_path = "~/client"

# Store IP addresses of the raspberry pi servers in servers.conf
with open("servers.conf", "r") as f:
    servers = json.load(f)

