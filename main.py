import threading
import time
import os
import sys
from datetime import datetime
from typing import Dict, Tuple
from config import SERVER_CONFIG_PATH, CHECK_INTERVAL
from drop import CargoDrop
from discord_notifier import DiscordNotifier
from log_parser import LogParser
from server_monitor import ServerMonitor
from ini_reader import read_drop_settings


LOG_PATH = os.getenv("LOG_PATH")
APP_LANGUAGE = os.getenv("APP_LANGUAGE", "ru").lower()

# Multilanguage messages dictionary
MESSAGES = {
    "ru": {
        "drop_spawned": "🗺️ Дроп **{sector}** с координатами 📍 {coords}",
        "landed": "⏳ Коснется земли в: {time} (UTC)",
        "destroyed": "💥 Будет уничтожен в: **{time}** (UTC)",
        "drop_disappeared": "🗺️ Дроп **{sector}** с координатами 📍 {coords} 🛑 исчез из-за рестарта сервера.",
    },
    "en": {
        "drop_spawned": "🗺️ Drop **{sector}** with coordinates 📍 {coords}",
        "landed": "⏳ Will land at: {time} (UTC)",
        "destroyed": "💥 Will be destroyed at: **{time}** (UTC)",
        "drop_disappeared": "🗺️ Drop **{sector}** at coordinates 📍 {coords} 🛑 disappeared due to server restart.",
    },
}


def get_text(key: str) -> str:
    """
    Retrieve localized message text by key based on app language setting.

    Args:
        key (str): Message key.

    Returns:
        str: Localized message string.
    """
    return MESSAGES.get(APP_LANGUAGE, MESSAGES["ru"]).get(key, key)


class DropManager:
    """
    Manages the lifecycle and notifications of cargo drops.

    Attributes:
        notifier (DiscordNotifier): Discord notifier instance.
        active_drops (Dict[Tuple[float, float, float], CargoDrop]): Active drops keyed by coordinates.
        lock (threading.Lock): Thread safety lock.
        fall_delay (float): Delay before drop starts falling.
        fall_duration (float): Duration of the drop fall.
        selfdestruct_time (float): Time before drop self-destructs.
    """

    def __init__(self, notifier: DiscordNotifier) -> None:
        self.notifier = notifier
        self.active_drops: Dict[Tuple[float, float, float], CargoDrop] = {}
        self.lock = threading.Lock()
        self.fall_delay, self.fall_duration, self.selfdestruct_time = read_drop_settings(SERVER_CONFIG_PATH)

    def format_drop_message(self, drop: CargoDrop) -> str:
        """
        Format the message for the given drop.

        Args:
            drop (CargoDrop): The cargo drop instance.

        Returns:
            str: Formatted message string.
        """
        coords_str = f"{drop.coordinates[0]:.3f}, {drop.coordinates[1]:.3f}, {drop.coordinates[2]:.3f}"
        landed_time = datetime.fromtimestamp(drop.landed_timestamp).strftime("%Y-%m-%d %H:%M:%S")
        destroyed_time = datetime.fromtimestamp(drop.destruction_timestamp).strftime("%Y-%m-%d %H:%M:%S")

        message = (
            f"{get_text('drop_spawned').format(sector=drop.sector, coords=coords_str)}\n"
            f"{get_text('landed').format(time=landed_time)}\n"
            f"{get_text('destroyed').format(time=destroyed_time)}"
        )
        return message

    def drop_spawned(self, coords: Tuple[float, float, float], spawn_time: float) -> None:
        """
        Callback for when a drop spawns detected by log parser.

        Args:
            coords (Tuple[float, float, float]): Drop coordinates.
            spawn_time (float): Drop spawn Unix timestamp.
        """
        new_drop = CargoDrop(
            coords,
            spawn_time,
            self.fall_delay,
            self.fall_duration,
            self.selfdestruct_time,
        )
        self.active_drops[coords] = new_drop

        message = self.format_drop_message(new_drop)
        self.notifier.send_message(message)

    def drop_disappeared(self) -> None:
        """
        Callback for when drops disappear (e.g., on server restart).

        Sends disappearing messages for all active drops and clears the list.
        """
        with self.lock:
            if self.active_drops:
                for coords in list(self.active_drops.keys()):
                    sector = self.active_drops[coords].sector
                    message = get_text('drop_disappeared').format(sector=sector, coords=coords)
                    self.notifier.send_message(message)
                self.active_drops.clear()

    def monitor_drops(self) -> None:
        """
        Dummy method to keep the monitoring thread alive.

        (Could be expanded for drop expiration checks.)
        """
        while True:
            time.sleep(CHECK_INTERVAL)


def main() -> None:
    """
    Main entry point to initialize and start monitoring SCUM drops and server events.
    """
    if not os.path.isfile(LOG_PATH):
        print(f"Log file not found: {LOG_PATH}")
        sys.exit(1)

    notifier = DiscordNotifier()
    drop_manager = DropManager(notifier)

    log_parser = LogParser(drop_manager.drop_spawned, drop_manager.drop_disappeared)
    server_monitor = ServerMonitor(drop_manager.drop_disappeared)

    threading.Thread(target=drop_manager.monitor_drops, daemon=True).start()
    threading.Thread(target=server_monitor.monitor, daemon=True).start()

    def follow(logpath: str):
        """
        Generator to follow the log file, yielding new lines as they arrive.
        Handles log rotation by reopening file if it shrinks.
        """
        with open(logpath, 'r', encoding='utf-8', errors='ignore') as f:
            f.seek(0, 2)
            last_size = os.path.getsize(logpath)
            while True:
                line = f.readline()
                if line:
                    yield line
                else:
                    time.sleep(1)
                    current_size = os.path.getsize(logpath)
                    if current_size < last_size:
                        f.close()
                        f = open(logpath, 'r', encoding='utf-8', errors='ignore')
                        last_size = current_size
                        continue
                    last_size = current_size

    for line in follow(LOG_PATH):
        log_parser.parse_line(line)


if __name__ == "__main__":
    main()
