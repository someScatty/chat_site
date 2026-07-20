import sys
import json
import requests

if len(sys.argv) < 3:
    print("Usage: python cli.py <channel_id> <content> <user>")
    sys.exit(1)

channel = sys.argv[1]
data = sys.argv[2]
user = sys.argv[3]

response = requests.post(
    f"http://127.0.0.1:8000/channels/{channel}/send",
    json={
        "content": data,
        "author": user
    }
)

print("Status:", response.status_code)
print(response.text)