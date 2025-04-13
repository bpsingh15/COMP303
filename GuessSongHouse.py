from .myhouse import *
from .pressurePlate import *



class MyHouse_GuessSong(Map):
    def __init__(self) -> None:
        super().__init__(
            name="MyHouse GuessSong",
            description="A cozy bedroom inside the house.",
            size=(15, 15),
            entry_point=Coord(0, 0),
            background_tile_image='wood_planks'
        )

    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        objects: list[tuple[MapObject, Coord]] = []
        # Add a door to go back to the main house
        objects.append((Door('int_entrance', linked_room="My House"), Coord(9, 5)))
        music_plate = MusicPressurePlate("You stepped on the plate, a YouTube song plays!", "resources/playlists/$ome $exy $ongs 4 U.csv")
        objects.append((music_plate, Coord(12, 8)))

        return objects

