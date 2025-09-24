import re
from datetime import datetime
from typing import Callable, Tuple


class LogParser:
    """
    Parses server log lines to detect cargo drops and server restarts.

    Attributes:
        DROP_SPAWN_PATTERN (re.Pattern): Regex pattern to match cargo drop spawn lines.
        RESTART_PATTERN (re.Pattern): Regex pattern to identify server restart or shutdown lines.
        drop_callback (Callable[[Tuple[float, float, float], float], None]): Function called on new drop with coordinates and spawn timestamp.
        restart_callback (Callable[[], None]): Function called on server restart detection.
        seen_drops (set): Set of coordinates tuples to avoid duplicate processing.
    """

    DROP_SPAWN_PATTERN = re.compile(
        r"\[(\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}:\d{3})\].*?Cargo drop spawned at:\s*(-?\d+\.\d+),\s*(-?\d+\.\d+),\s*(-?\d+\.\d+)"
    )
    RESTART_PATTERN = re.compile(r"Server is restarting|Server shutdown")

    def __init__(
        self,
        drop_callback: Callable[[Tuple[float, float, float], float], None],
        restart_callback: Callable[[], None]
    ) -> None:
        """
        Initialize LogParser.

        Args:
            drop_callback (Callable[[Tuple[float, float, float], float], None]): 
                Callback function for drops, args: coords (x,y,z) and spawn time.
            restart_callback (Callable[[], None]): Callback function for server restart events.
        """
        self.drop_callback = drop_callback
        self.restart_callback = restart_callback
        self.seen_drops = set()

    def parse_timestamp(self, timestamp_str: str) -> float:
        """
        Convert timestamp string from logs to Unix timestamp.

        Args:
            timestamp_str (str): Timestamp string like '2025.09.24-12.00.54:722'.

        Returns:
            float: Unix timestamp.
        """
        dt = datetime.strptime(timestamp_str, "%Y.%m.%d-%H.%M.%S:%f")
        return dt.timestamp()

    def parse_line(self, line: str) -> None:
        """
        Parse a single line of the log.

        Args:
            line (str): Log line text.

        Calls:
            restart_callback if server restart detected.
            drop_callback if new drop detected.
        """
        if self.RESTART_PATTERN.search(line):
            self.restart_callback()

        match = self.DROP_SPAWN_PATTERN.search(line)
        if match:
            timestamp_str = match.group(1)
            coords = (
                float(match.group(2)),
                float(match.group(3)),
                float(match.group(4)),
            )
            coords_key = tuple(round(c, 2) for c in coords)

            if coords_key not in self.seen_drops:
                self.seen_drops.add(coords_key)
                spawn_time = self.parse_timestamp(timestamp_str)
                self.drop_callback(coords, spawn_time)
