# multiplayer/music_manager.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class Observer(ABC):
    @abstractmethod
    def update(self, data: Dict[str, Any]) -> None:
        """Called when MusicManager has new data to push."""
        pass

class MusicManager:
    # use Optional[...] for the singleton instance
    _instance: Optional["MusicManager"] = None

    def __init__(self):
        if MusicManager._instance is not None:
            raise Exception("MusicManager is a singleton!")
        self.vote_counts: Dict[str, int] = {}
        self.observers: List[Observer] = []
        MusicManager._instance = self

    @staticmethod
    def get_instance() -> "MusicManager":
        if MusicManager._instance is None:
            MusicManager()
        # now _instance is guaranteed to be a MusicManager
        return MusicManager._instance  # type: ignore

    def add_observer(self, observer: Observer) -> None:
        self.observers.append(observer)

    def remove_observer(self, observer: Observer) -> None:
        self.observers.remove(observer)

    def notify_all(self, data: Dict[str, Any]) -> None:
        for obs in self.observers:
            obs.update(data)

    def cast_vote(self, song: str) -> None:
        self.vote_counts[song] = self.vote_counts.get(song, 0) + 1
        self.notify_all({
            "type": "vote",
            "song": song,
            "votes": self.vote_counts[song]
        })

    def get_vote_counts(self) -> Dict[str, int]:
        return dict(self.vote_counts)
