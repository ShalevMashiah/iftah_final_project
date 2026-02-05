from typing import Dict, Optional

from globals.consts.const_strings import ConstStrings
from model.data_classes.zmq_response import Response
from infrastructure.api.routers.base_router import BaseRouter
from infrastructure.interfaces.iexample_controller import IExampleController


class ExampleRouter(BaseRouter):
    def __init__(self, resource: str, example_controller: IExampleController):
        super().__init__(resource)
        self._example_controller = example_controller
        self._prot_setup_operations()

    def _prot_setup_operations(self) -> None:
        self._prot_operations = {
            ConstStrings.EXAMPLE_OPERATION: self._example_function,
        }

    def _example_function(self, data: Optional[Dict] = None) -> Response:
        return self._example_controller.example_function(data)
