import os
from dotenv import load_dotenv

load_dotenv()

LOG_PATH = os.getenv("LOG_PATH")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
SERVER_PROCESS_NAME = os.getenv("SERVER_PROCESS_NAME")
SERVER_CONFIG_PATH = os.getenv("SERVER_CONFIG_PATH")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "10"))
