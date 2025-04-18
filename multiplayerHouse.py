from .myhouse import *
from .pressurePlate import *
from .multiplayer.music_manager import *
from .multiplayer.vote_observer import *
from .multiplayer.vote_command import *


class MyHouse_Multiplayer(Map):
    def __init__(self) -> None:
        super().__init__(
            name="MyHouse Multiplayer",
            description="The kitchen, with all its cooking tools.",
            size=(15, 15),
            entry_point=Coord(0, 0),
            background_tile_image='wood_planks'
        )

    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        objects: list[tuple[MapObject, Coord]] = []
        objects.append((Door('int_entrance', linked_room="Paul House"), Coord(9, 5)))

        computer = CustomComputer(
            image_name="computer",
            menu_name="Select an option",
            menu_options={}
        )

        # Register Observer once
        manager = MusicManager.get_instance()
        main_menu_options: dict[str, MenuCommand] = {
            "Vote for Song": VoteForSongCommand(
                csv_path=os.path.join("resources", "playlists", "$ome $exy $ongs 4 U.csv")
            )
        }

        computer.set_menu_options(main_menu_options)
        objects.append((computer, Coord(10, 7)))
        return objects