from typing import Tuple
from sector_converter import coords_to_sector


class CargoDrop:
    """
    Represents a cargo drop event in the game world.

    Attributes:
        coordinates (Tuple[float, float, float]): 3D coordinates of the drop.
        spawn_timestamp (float): Timestamp when the drop spawns.
        fall_delay (float): Delay time before the drop starts falling.
        fall_duration (float): Duration of the fall.
        selfdestruct_time (float): Time after landing before self-destruction.
        landed_timestamp (float): Calculated time when the drop lands.
        destruction_timestamp (float): Calculated time when the drop self-destructs.
        sector (str): Sector computed from the drop coordinates.
    """

    def __init__(
        self,
        coordinates: Tuple[float, float, float],
        spawn_timestamp: float,
        fall_delay: float,
        fall_duration: float,
        selfdestruct_time: float,
    ) -> None:
        """
        Initialize CargoDrop instance.

        Args:
            coordinates (Tuple[float, float, float]): 3D position of the drop.
            spawn_timestamp (float): Spawn timestamp in seconds.
            fall_delay (float): Delay before fall starts (seconds).
            fall_duration (float): Duration of fall (seconds).
            selfdestruct_time (float): Time until self-destruction after landing (seconds).
        """
        self.coordinates = coordinates
        self.spawn_timestamp = spawn_timestamp
        self.fall_delay = fall_delay
        self.fall_duration = fall_duration
        self.selfdestruct_time = selfdestruct_time

        # Calculate when the drop lands and when it will self-destruct
        self.landed_timestamp = spawn_timestamp + fall_delay + fall_duration
        self.destruction_timestamp = self.landed_timestamp + self.selfdestruct_time

        # Determine the sector based on x and y coordinates
        self.sector = coords_to_sector(coordinates[0], coordinates[1])
