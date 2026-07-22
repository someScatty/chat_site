from functools import lru_cache
import os
import requests

BASE_URL = "http://127.0.0.1:8000"


class ChatCLI:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.channel_id = None

        self.seen_messages = set()
        self.messages = []

    def headers(self):
        return {
            "Authorization": f"Bearer {self.token}"
        }

    @lru_cache()
    def get_user_data(self, id: int):
        r = requests.get(
            f"{BASE_URL}/users/{id}",
            headers=self.headers()
        )
        return r.json()

    def login(self):
        username = "moakdoge"
        password = "1234"

        r = requests.post(
            f"{BASE_URL}/api/login",
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

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def print_messages(self):
        self.clear_screen()

        for msg in self.messages:
            user_info = self.get_user_data(msg["author"])

            if msg.get("deleted"):
                content = "[message deleted]"
            else:
                content = msg["content"]

            suffix = " (edited)" if msg.get("edited") else ""

            print(
                f"[{user_info['username']}] {content}{suffix}"
            )

    def read_messages(self, refresh=False):
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

        if refresh:
            self.messages.clear()
            self.seen_messages.clear()

        for msg in data.get("messages", []):
            msg_id = msg["id"]

            if msg_id not in self.seen_messages:
                self.seen_messages.add(msg_id)
                self.messages.append(msg)

        self.print_messages()

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

    def delete_last_message(self):
        if not self.messages:
            print("No messages to delete")
            return

        msg = self.messages[-1]

        r = requests.delete(
            f"{BASE_URL}/messages/{msg['id']}/delete",
            headers=self.headers()
        )

        if not r.ok:
            print("Delete failed:", r.text)
            return

        self.read_messages(refresh=True)

    def edit_last_message(self, content):
        if not self.messages:
            print("No messages to edit")
            return

        msg = self.messages[-1]

        r = requests.patch(
            f"{BASE_URL}/messages/{msg['id']}/edit",
            headers=self.headers(),
            json={
                "content": content
            }
        )

        if not r.ok:
            print("Edit failed:", r.text)
            return

        self.read_messages(refresh=True)

    def run(self):
        self.login()
        self.get_or_create_channel()

        self.read_messages(refresh=True)

        print("\nCommands:")
        print("/quit - exit")
        print("/delete - delete last message")
        print("/edit <text> - edit last message")

        while True:
            msg = input("> ")

            if msg == "/quit":
                break

            if msg == "/delete":
                self.delete_last_message()
                continue

            if msg.startswith("/edit "):
                self.edit_last_message(msg[6:])
                continue

            if msg.strip():
                self.send_message(msg)
                self.read_messages(refresh=True)


if __name__ == "__main__":
    ChatCLI().run()