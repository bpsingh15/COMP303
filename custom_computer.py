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
    def __init__(
        self,
        image_name: str = 'computer',
        menu_name: str = 'Select an option',
        menu_options: dict[str, MenuCommand] = {}
    ) -> None:
        super().__init__(image_name, passable=False)
        self.__menu_name: str = menu_name
        self.__menu_options: dict[str, MenuCommand] = {}
        self.set_menu_options(menu_options)

        self.__scroll_index: int = 0  # Start index for visible options
        self.__page_size: int = 5     # Number of options per page

    def set_menu_options(self, menu_options: dict[str, MenuCommand]):
        """Allow changing the menu's options dynamically."""
        self.__menu_options = menu_options
        self.__scroll_index = 0  # Reset to top of the list whenever the menu changes

    def get_menu_options(self) -> dict[str, MenuCommand]:
        return self.__menu_options

    def player_interacted(self, player: "HumanPlayer") -> list[Message]:
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
        else:
            return []
        

