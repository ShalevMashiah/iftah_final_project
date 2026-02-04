from abc import ABC, abstractmethod
from typing import Callable


class IEventManager(ABC):
    @abstractmethod
    def register_event(self, event_name: str, listener: Callable) -> None:
        pass

    @abstractmethod
    def emit(self, event_name: str, *args, **kwargs) -> None:
        pass
