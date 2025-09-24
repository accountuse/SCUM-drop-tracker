import psutil
import time
from typing import Callable
from config import SERVER_PROCESS_NAME, CHECK_INTERVAL


class ServerMonitor:
    """
    Monitors the SCUM server process and triggers a callback when the server stops.

    Attributes:
        drop_disappear_callback (Callable[[], None]): Callback triggered when the server stops.
    """

    def __init__(self, drop_disappear_callback: Callable[[], None]) -> None:
        """
        Initializes the ServerMonitor with a callback.

        Args:
            drop_disappear_callback (Callable[[], None]): Function called when server stops.
        """
        self.drop_disappear_callback = drop_disappear_callback

    def is_server_running(self) -> bool:
        """
        Checks if the SCUM server process is currently running.

        Returns:
            bool: True if server process is found, False otherwise.
        """
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == SERVER_PROCESS_NAME:
                return True
        return False

    def monitor(self) -> None:
        """
        Continuously monitors the server process status.

        Calls the drop disappear callback when the server stops.
        """
        was_running = True
        while True:
            running = self.is_server_running()
            if was_running and not running:
                self.drop_disappear_callback()
            was_running = running
            time.sleep(CHECK_INTERVAL)
