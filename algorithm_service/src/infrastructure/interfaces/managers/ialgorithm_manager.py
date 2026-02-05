from abc import ABC, abstractmethod


class IAlgorithmManager(ABC):
    @abstractmethod
    def start(self) -> None:
        pass
    
    @abstractmethod
    def stop(self) -> None:
        pass
