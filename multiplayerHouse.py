from .myhouse import *
from .pressurePlate import *
from .multiplayer.music_manager import *
from .multiplayer.vote_observer import *
from .multiplayer.vote_command import *


class MyHouse_Multiplayer(Map):
    """
    A multiplayer room map where players can vote on which song to play next.
    It features a CustomComputer terminal and uses the Observer pattern via the MusicManager.
    """

    def __init__(self) -> None:
        """
        Initializes the multiplayer room map with its layout, background, and entry point.

        Preconditions:
            - None explicitly, but assumes Coord(0, 0) and 'wood_planks' are valid.
        """
        super().__init__(
            name="MyHouse Multiplayer",
            description="The kitchen, with all its cooking tools.",
            size=(15, 15),
            entry_point=Coord(0, 0),
            background_tile_image='wood_planks'
        )

    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        """
        Returns the list of interactive map objects (e.g., doors, voting computer).

        Returns:
            list[tuple[MapObject, Coord]]: List of tuples mapping objects to coordinates.

        Preconditions:
            - The playlist file used in VoteForSongCommand must exist.
            - MusicManager singleton must be initialized before vote commands are used.
        """
        objects: list[tuple[MapObject, Coord]] = []

        # Door to return to Paul's main house
        objects.append((Door('int_entrance', linked_room="Paul House"), Coord(9, 5)))

        # Initialize interactive computer
        computer = CustomComputer(
            image_name="computer",
            menu_name="Select an option",
            menu_options={}
        )

        # Register Observer once (assumed handled internally)
        manager = MusicManager.get_instance()

        # Menu with voting command
        main_menu_options: dict[str, MenuCommand] = {
            "Vote for Song": VoteForSongCommand(
                csv_path=os.path.join("resources", "playlists", "$ome $exy $ongs 4 U.csv")
            )
        }

        # Assign the menu options to the computer
        computer.set_menu_options(main_menu_options)

        # Add computer to the map at a fixed coordinate
        objects.append((computer, Coord(10, 7)))

        return objects
