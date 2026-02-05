from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from model.data_classes.zmq_response import Response


class IExampleController(ABC):
    @abstractmethod
    def example_function(self, data: Optional[Dict] = None) -> Response:
        pass
