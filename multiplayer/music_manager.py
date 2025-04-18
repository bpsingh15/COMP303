from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class Observer(ABC):
    """
    Abstract base class for observer components.
    Observers receive updates when MusicManager broadcasts changes.
    """

    @abstractmethod
    def update(self, data: Dict[str, Any]) -> None:
        """
        Called when the MusicManager sends an update.

        Parameters:
            data (Dict[str, Any]): A dictionary representing update information.

        Preconditions:
            - data must be a dictionary containing a "type" key.
        """
        pass


class MusicManager:
    """
    Singleton class that manages voting for songs and notifies registered observers
    whenever votes are cast or updated.
    """

    _instance: Optional["MusicManager"] = None

    def __init__(self):
        """
        Initializes the MusicManager singleton.
        Raises an exception if an instance already exists.
        """
        if MusicManager._instance is not None:
            raise Exception("MusicManager is a singleton!")

        self.vote_counts: Dict[str, int] = {}
        self.observers: List[Observer] = []
        MusicManager._instance = self

    @staticmethod
    def get_instance() -> "MusicManager":
        """
        Returns the singleton instance of MusicManager.
        If it doesn't exist, it is created.

        Returns:
            MusicManager: The singleton instance.
        """
        if MusicManager._instance is None:
            MusicManager()
        return MusicManager._instance  # type: ignore

    def add_observer(self, observer: Observer) -> None:
        """
        Registers an observer to receive updates.

        Parameters:
            observer (Observer): An object implementing the Observer interface.

        Preconditions:
            - observer must not be None.
        """
        assert observer is not None, "Observer cannot be None"
        self.observers.append(observer)

    def remove_observer(self, observer: Observer) -> None:
        """
        Removes a previously registered observer.

        Parameters:
            observer (Observer): The observer to remove.

        Preconditions:
            - observer must be in the current list of observers.
        """
        assert observer in self.observers, "Observer must be registered before removing"
        self.observers.remove(observer)

    def notify_all(self, data: Dict[str, Any]) -> None:
        """
        Notifies all observers with the provided update data.

        Parameters:
            data (Dict[str, Any]): A dictionary representing the update.

        Preconditions:
            - data must be a non-empty dictionary.
        """
        assert isinstance(data, dict) and data, "data must be a non-empty dictionary"
        for obs in self.observers:
            obs.update(data)

    def cast_vote(self, song: str) -> None:
        """
        Casts a vote for the given song and notifies observers.

        Parameters:
            song (str): The name of the song being voted for.

        Preconditions:
            - song must be a non-empty string.
        """
        assert isinstance(song, str) and song.strip(), "song must be a non-empty string"

        self.vote_counts[song] = self.vote_counts.get(song, 0) + 1
        self.notify_all({
            "type": "vote",
            "song": song,
            "votes": self.vote_counts[song]
        })

    def get_vote_counts(self) -> Dict[str, int]:
        """
        Returns a copy of the current vote counts.

        Returns:
            Dict[str, int]: A mapping from song names to vote totals.
        """
        return dict(self.vote_counts)
