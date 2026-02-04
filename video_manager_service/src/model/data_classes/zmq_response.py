from __future__ import annotations
from dataclasses import dataclass
import json
from typing import Dict

from globals.enums.response_status import ResponseStatus
from globals.consts.const_strings import ConstStrings


@dataclass
class Response:
    def __init__(self, status: ResponseStatus, data: Dict = {}) -> None:
        self.status = status
        self.data = data

    def to_json(self) -> str:
        return json.dumps({
            ConstStrings.STATUS_IDENTIFIER: self.status.name,
            ConstStrings.DATA_IDENTIFIER: self.data
        })

    @classmethod
    def from_json(self, json_str: str) -> Response:
        json_dict = json.loads(json_str)
        status = ResponseStatus[json_dict[ConstStrings.STATUS_IDENTIFIER]]
        data = json_dict.get(ConstStrings.DATA_IDENTIFIER, {})
        return self(status=status, data=data)

    status: ResponseStatus
    data: Dict
