from abc import ABC, abstractmethod
from numpy import ndarray


class IShmReaderHandler(ABC):
    @abstractmethod
    def read_frame(self) -> ndarray:
        pass
    
    @abstractmethod
    def start(self) -> None:
        pass
    
    @abstractmethod
    def release(self) -> None:
        pass
