from abc import ABC, abstractmethod
from typing import Any, Dict


class IAlgorithm(ABC):
    @abstractmethod
    def setup(self, config: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def process(self, frame: Any) -> Any:
        pass

    @abstractmethod
    def release(self) -> None:
        pass
