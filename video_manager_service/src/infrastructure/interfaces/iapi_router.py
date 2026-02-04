from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from model.data_classes.zmq_response import Response


class IApiRouter(ABC):

    @property
    @abstractmethod
    def resource(self) -> str:
        pass

    @abstractmethod
    def handle_operation(self, operation: str, data: Optional[Dict]) -> Response:
        pass
