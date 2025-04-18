import os
import csv
import random
from .imports import *

from typing import TYPE_CHECKING, Optional, Any, Dict, cast, List
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    from Player import HumanPlayer


# ============================================================
# CUSTOM COMPUTER 
# ============================================================

class CustomComputer(UtilityObject, SelectionInterface):
    """
    A custom computer object that players can interact with to select from a menu of commands.
    Supports paginated options and scroll navigation.
    """

    def __init__(
        self,
        image_name: str = 'computer',
        menu_name: str = 'Select an option',
        menu_options: dict[str, MenuCommand] = {}
    ) -> None:
        """
        Initializes the CustomComputer with menu options and scroll settings.

        Parameters:
            image_name (str): The image to use for the computer object.
            menu_name (str): Title shown in the menu interface.
            menu_options (dict): A dictionary mapping option names to commands.

        Preconditions:
            - image_name must be a valid sprite/image asset.
            - menu_name must be a non-empty string.
            - menu_options must be a dictionary of string: MenuCommand
        """
        assert isinstance(menu_name, str) and menu_name.strip(), "menu_name must be a non-empty string"
        assert isinstance(menu_options, dict), "menu_options must be a dictionary"

        super().__init__(image_name, passable=False)
        self.__menu_name: str = menu_name
        self.__menu_options: dict[str, MenuCommand] = {}
        self.set_menu_options(menu_options)

        self.__scroll_index: int = 0  # Start index for visible options
        self.__page_size: int = 5     # Number of options per page

    def set_menu_options(self, menu_options: dict[str, MenuCommand]):
        """
        Set or update the computer's menu options and reset the scroll.

        Parameters:
            menu_options (dict): New mapping of option labels to commands.

        Preconditions:
            - menu_options must be a dictionary with string keys and MenuCommand values.
        """
        assert isinstance(menu_options, dict), "menu_options must be a dictionary"
        self.__menu_options = menu_options
        self.__scroll_index = 0  # Reset scroll to top when menu is updated

    def get_menu_options(self) -> dict[str, MenuCommand]:
        """
        Get the current menu options.

        Returns:
            dict[str, MenuCommand]: The current menu option mappings.
        """
        return self.__menu_options

    def player_interacted(self, player: "HumanPlayer") -> list[Message]:
        """
        Triggered when a player interacts with the computer.

        Parameters:
            player (HumanPlayer): The player who interacted.

        Returns:
            list[Message]: Menu message displaying current options.

        Preconditions:
            - player must be a valid HumanPlayer object.
        """
        assert player is not None, "player cannot be None"

        player.set_current_menu(self)
        options_list = list(self.__menu_options.keys())
        visible_options = options_list[self.__scroll_index : self.__scroll_index + self.__page_size]

        # Insert scroll items if needed.
        if self.__scroll_index > 0:
            visible_options.insert(0, "Scroll Up")
        if self.__scroll_index + self.__page_size < len(options_list):
            visible_options.append("Scroll Down")

        return [MenuMessage(self, player, self.__menu_name, visible_options)]

    def select_option(self, player: "HumanPlayer", option: str) -> list[Message]:
        """
        Handle the player's selection from the menu.

        Parameters:
            player (HumanPlayer): The player making the selection.
            option (str): The selected menu option.

        Returns:
            list[Message]: Result of the command or menu update.

        Preconditions:
            - option must be a string and either match a key in __menu_options or be a scroll control.
        """
        assert isinstance(option, str), "option must be a string"
        assert player is not None, "player cannot be None"

        options_list = list(self.__menu_options.keys())

        if option == "Scroll Down":
            self.__scroll_index = min(
                self.__scroll_index + self.__page_size,
                max(0, len(options_list) - self.__page_size)
            )
            return self.player_interacted(player)

        elif option == "Scroll Up":
            self.__scroll_index = max(0, self.__scroll_index - self.__page_size)
            return self.player_interacted(player)

        if option in self.__menu_options:
            cmd = self.__menu_options[option]
            return cmd.execute(player.get_current_room(), player)

        # Invalid selection, return no action
        return []
