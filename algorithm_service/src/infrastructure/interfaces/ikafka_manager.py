from abc import ABC, abstractmethod
from typing import Callable


class IKafkaManager(ABC):
    @abstractmethod
    def send_message(self, topic: str, msg: str) -> None:
        pass

    @abstractmethod
    def start_consuming(self, topic: str, callback: Callable) -> None:
        pass
