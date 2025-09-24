from typing import Union


class SectorConverter:
    """
    Converts game world coordinates to sector codes based on predefined bounds.

    Attributes:
        letter_bounds (list[tuple[str, int, int]]): Boundaries for sector letters based on Y coordinate.
        number_bounds (list[tuple[int, int, int]]): Boundaries for sector numbers based on X coordinate.
    """

    def __init__(self) -> None:
        self.letter_bounds = [
            ("D", 619200, 315274),
            ("C", 315274, 10507),
            ("B", 10507, -293418),
            ("A", -293418, -598214),
            ("Z", -598214, -904205),
        ]
        self.number_bounds = [
            (4, 617516, 316116),
            (3, 316116, 11349),
            (2, 11349, -294260),
            (1, -294260, -599028),
            (0, -599028, -904205),
        ]

    def get_letter(self, y: float) -> str:
        """
        Get sector letter for a given Y coordinate.

        Args:
            y (float): Y coordinate.

        Returns:
            str: Sector letter or '?' if not found.
        """
        for letter, max_y, min_y in self.letter_bounds:
            if min_y <= y <= max_y:
                return letter
        return "?"

    def get_number(self, x: float) -> Union[int, str]:
        """
        Get sector number for a given X coordinate.

        Args:
            x (float): X coordinate.

        Returns:
            int or str: Sector number or '?' if not found.
        """
        for number, max_x, min_x in self.number_bounds:
            if min_x <= x <= max_x:
                return number
        return "?"

    def coords_to_sector(self, x: float, y: float) -> str:
        """
        Convert coordinates to sector code combining letter and number.

        Args:
            x (float): X coordinate.
            y (float): Y coordinate.

        Returns:
            str: Sector code or 'Unknown' if coordinates are out of bounds.
        """
        letter = self.get_letter(y)
        number = self.get_number(x)
        if letter == "?" or number == "?":
            return "Unknown"
        return f"{letter}{number}"


# Singleton instance for global usage
sector_converter = SectorConverter()


def coords_to_sector(x: float, y: float) -> str:
    """
    Helper function to convert coordinates to sector using sector_converter.

    Args:
        x (float): X coordinate.
        y (float): Y coordinate.

    Returns:
        str: Sector code.
    """
    return sector_converter.coords_to_sector(x, y)
