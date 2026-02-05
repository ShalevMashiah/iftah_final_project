from __future__ import annotations
from dataclasses import dataclass
import json
from typing import Dict

from globals.consts.const_strings import ConstStrings


@dataclass
class Request:
    def __init__(self, resource: str, operation: str, data: Dict = {}) -> None:
        self.resource = resource
        self.operation = operation
        self.data = data

    def to_json(self) -> str:
        return json.dumps({
            ConstStrings.RESOURCE_IDENTIFIER: self.resource,
            ConstStrings.OPERATION_IDENTIFIER: self.operation,
            ConstStrings.DATA_IDENTIFIER: self.data
        })

    @classmethod
    def from_json(self, json_str: str) -> Request:
        request = json.loads(json_str)
        return self(resource=request[ConstStrings.RESOURCE_IDENTIFIER],
                    operation=request[ConstStrings.OPERATION_IDENTIFIER],
                    data=request.get(ConstStrings.DATA_IDENTIFIER, {}))

    resource: str
    operation: str
    data: Dict
