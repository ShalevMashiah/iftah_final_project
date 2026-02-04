from abc import ABC, abstractmethod
from typing import Any, Dict


class IConfigManager(ABC):
    @abstractmethod
    def get(self, *path: str) -> Any:
        pass

    @abstractmethod
    def set(self, *path: str, value: Any) -> None:
        pass

    @abstractmethod
    def exists(self, *path: str) -> bool:
        pass

    @abstractmethod
    def get_all(self) -> Dict[str, Any]:
        pass
