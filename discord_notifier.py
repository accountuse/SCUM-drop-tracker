import requests
import threading
import time
import os
from typing import Optional
from requests.models import Response


DISCORD_WEBHOOK_URL: Optional[str] = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_AUTHOR_NAME: str = os.getenv("DISCORD_AUTHOR_NAME", "SCUM Server")
DISCORD_AUTHOR_ICON: Optional[str] = os.getenv("DISCORD_AUTHOR_ICON")


class DiscordNotifier:
    """
    Class for sending messages to Discord via webhook.

    Attributes:
        webhook_url (Optional[str]): Discord webhook URL.
        username (str): Name displayed as message author.
        avatar_url (Optional[str]): URL of the author's avatar.
        lock (threading.Lock): Lock for thread-safe sending.
    """

    def __init__(
        self,
        webhook_url: Optional[str] = DISCORD_WEBHOOK_URL,
        username: str = DISCORD_AUTHOR_NAME,
        avatar_url: Optional[str] = DISCORD_AUTHOR_ICON,
    ) -> None:
        """
        Initialize DiscordNotifier instance.

        Args:
            webhook_url (Optional[str]): Discord webhook URL.
            username (str): Name displayed as message author.
            avatar_url (Optional[str]): URL of the author's avatar.
        """
        self.webhook_url = webhook_url
        self.username = username
        self.avatar_url = avatar_url
        self.lock = threading.Lock()

    def send_message(self, message: str) -> Response:
        """
        Send a message to Discord channel using webhook.

        Args:
            message (str): The message content to send.

        Returns:
            Response: HTTP response from the Discord server.
        """
        with self.lock:
            data = {
                "username": self.username,
                "avatar_url": self.avatar_url,
                "embeds": [
                    {
                        "author": {
                            "name": self.username,
                            "icon_url": self.avatar_url,
                        },
                        "description": message,
                        "color": 3447003,
                    }
                ],
            }
            response = requests.post(self.webhook_url, json=data)
            time.sleep(0.5)  # Sleep to avoid rate limits
            return response
