from abc import ABC, abstractmethod


class IZmqServerManager(ABC):
    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass
