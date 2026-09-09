from abc import ABC, abstractmethod
from typing import List
from models.event import Event

class BaseRepository(ABC):
    """Abstract Base Class for all repository implementations."""

    @abstractmethod
    def load_events(self) -> List[Event]:
        """Abstract method to load events from a data source."""
        pass