from .myhouse import *
from .pressurePlate import *


class MyHouse_GuessSong(Map):
    """
    A map representing a cozy bedroom where players can trigger a music pressure plate
    that plays a random YouTube song.

    Used for testing or enjoying surprise song playback in a single-player setting.
    """

    def __init__(self) -> None:
        """
        Initializes the GuessSong room map with background, size, and entry point.

        Preconditions:
            - Coord(0, 0) must be a valid coordinate.
            - 'wood_planks' must be a valid background tile.
        """
        super().__init__(
            name="MyHouse GuessSong",
            description="A cozy bedroom inside the house.",
            size=(15, 15),
            entry_point=Coord(0, 0),
            background_tile_image='wood_planks'
        )

    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        """
        Returns the list of interactive map objects including a door and a music pressure plate.

        Returns:
            list[tuple[MapObject, Coord]]: A list of (object, coordinate) tuples.

        Preconditions:
            - The playlist file path provided to MusicPressurePlate must exist and be valid.
        """
        objects: list[tuple[MapObject, Coord]] = []

        # Add a door back to the main house
        objects.append((Door('int_entrance', linked_room="Paul House"), Coord(9, 5)))

        # Add a pressure plate that plays a random song
        music_plate = MusicPressurePlate(
            "You stepped on the plate, a YouTube song plays!",
            "resources/playlists/$ome $exy $ongs 4 U.csv"
        )
        objects.append((music_plate, Coord(12, 8)))

        return objects
