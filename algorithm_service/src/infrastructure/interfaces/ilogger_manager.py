from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from model.data_classes.zmq_response import Response


class ILoggerManager(ABC):

    @abstractmethod
    def log(self, log_name: str, msg: str, level: Any) -> None:
        pass
