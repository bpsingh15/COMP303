from .music_manager import Observer
from typing import Any, Dict

class VoteDisplayObserver(Observer):
    def update(self, data: Dict[str, Any]) -> None:
        if data["type"] == "vote":
            print(f"VOTE UPDATE: '{data['song']}' now has {data['votes']} votes!")
