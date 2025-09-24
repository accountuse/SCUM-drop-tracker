import configparser
import os
from typing import Tuple


def read_drop_settings(ini_path: str) -> Tuple[float, float, float]:
    """
    Reads drop-related settings from a specified INI configuration file.

    Args:
        ini_path (str): Path to the INI configuration file.

    Raises:
        FileNotFoundError: If the given INI file does not exist.
        ValueError: If the required section or keys are missing in the INI file.

    Returns:
        Tuple[float, float, float]: A tuple containing fall_delay, fall_duration, and selfdestruct_time.
    """
    if not os.path.isfile(ini_path):
        raise FileNotFoundError(f"INI file not found: {ini_path}")

    config = configparser.ConfigParser()
    config.read(ini_path)

    section = 'World'
    if section not in config:
        raise ValueError(f"Section [{section}] missing in INI file: {ini_path}")

    try:
        fall_delay = float(config.get(section, 'scum.CargoDropFallDelay'))
        fall_duration = float(config.get(section, 'scum.CargoDropFallDuration'))
        selfdestruct_time = float(config.get(section, 'scum.CargoDropSelfdestructTime'))
    except configparser.NoOptionError as e:
        raise ValueError(f"Missing required setting in section [{section}]: {e}")

    return fall_delay, fall_duration, selfdestruct_time
