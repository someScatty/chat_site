from functools import lru_cache

import requests
import time

BASE_URL = "http://127.0.0.1:8000"

class ChatCLI:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.channel_id = None
        self.seen_messages = set()

    def headers(self):
        return {
            "Authorization": f"Bearer {self.token}"
        }
    
    @lru_cache()
    def get_user_data(self, id: int):
        d=requests.get(f"{BASE_URL}/users/{id}", headers=self.headers())
        return d.json()

    def login(self):
        username = "moakdoge"
        password = "1234"

        r = requests.post(
            f"{BASE_URL}/api/login/{username}",
            json={
                "username": username,
                "password": password
            }
        )

        data = r.json()

        if not data.get("success"):
            raise Exception(data.get("error"))

        self.token = data["session_token"]
        self.user_id = data["id"]

        print(f"Logged in as {username} ({self.user_id})")

    def get_or_create_channel(self):
        r = requests.get(
            f"{BASE_URL}/channels/get",
            headers=self.headers()
        )

        data = r.json()

        channels = data.get("channels", [])

        if channels:
            self.channel_id = channels[0]
            print(f"Using channel {self.channel_id}")
            return

        print("No channels found, creating one...")

        r = requests.post(
            f"{BASE_URL}/channels/new",
            headers=self.headers(),
            json={
                "name": "cli_channel",
                "description": "Created from CLI"
            }
        )

        data = r.json()

        if not data.get("success"):
            raise Exception(data.get("error"))

        self.channel_id = data["id"]

        print(f"Created channel {self.channel_id}")

    def read_messages(self):
        r = requests.get(
            f"{BASE_URL}/channels/{self.channel_id}/read",
            headers=self.headers(),
            params={
                "limit": 50
            }
        )

        if not r.ok:
            return

        data = r.json()

        for msg in data.get("messages", []):
            # Message is a namedtuple serialized as an array
            # [content, author, timestamp, id, channel, attachments, reply]
            msg_id = msg["id"]

            if msg_id not in self.seen_messages:
                self.seen_messages.add(msg_id)
                user_info = self.get_user_data(msg["author"])
                print(
                    f"\n[{user_info["username"]}] {msg["content"]}"
                )

    def send_message(self, content):
        r = requests.post(
            f"{BASE_URL}/channels/{self.channel_id}/send",
            headers=self.headers(),
            json={
                "content": content,
                "author": self.user_id
            }
        )

        if not r.ok:
            print("Send failed:", r.text)

    def run(self):
        self.login()
        self.get_or_create_channel()

        print("Type /quit to exit")

        while True:
            self.read_messages()

            msg = input("> ")

            if msg == "/quit":
                break

            if msg.strip():
                self.send_message(msg)


if __name__ == "__main__":
    ChatCLI().run()