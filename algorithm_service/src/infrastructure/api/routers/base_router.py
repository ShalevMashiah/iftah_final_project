from typing import Any, Dict, Optional

from globals.consts.const_strings import ConstStrings
from globals.enums.response_status import ResponseStatus
from model.data_classes.zmq_response import Response
from infrastructure.interfaces.iapi_router import IApiRouter


class BaseRouter(IApiRouter):
    def __init__(self, resource: str) -> None:
        self._resource = resource
        self._prot_operations = {}
        self._prot_setup_operations()

    @property
    def resource(self) -> str:
        return self._resource

    def handle_operation(self, operation: str, data: Optional[Dict]) -> Response:
        if operation in self._prot_operations:
            return self._prot_operations[operation](data)
        else:
            return Response(
                status=ResponseStatus.ERROR,
                data={
                    ConstStrings.ERROR_MESSAGE: ConstStrings.UNKNOWN_OPERATION_ERROR_MESSAGE}
            )

    def _prot_setup_operations(self):
        pass
