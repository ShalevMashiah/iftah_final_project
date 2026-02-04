import threading
from typing import Callable, Dict, List

from infrastructure.interfaces.ievent_manager import IEventManager


class EventManager(IEventManager):
    def __init__(self) -> None:
        self._listeners: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()

    def register_event(self, event_name: str, listener: Callable) -> None:
        with self._lock:
            if event_name not in self._listeners:
                self._listeners[event_name] = []
            self._listeners[event_name].append(listener)

    def emit(self, event_name: str, *args, **kwargs) -> None:
        with self._lock:
            listeners = list(self._listeners.get(event_name, []))  # Copy
        for listener in listeners:
            listener(*args, **kwargs)
