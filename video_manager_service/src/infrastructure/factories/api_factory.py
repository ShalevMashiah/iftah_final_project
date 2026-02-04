from typing import List
from globals.consts.const_strings import ConstStrings
from infrastructure.interfaces.ikafka_manager import IKafkaManager
from infrastructure.api.controllers.example_controller import ExampleController
from infrastructure.api.routers.example_router import ExampleRouter
from infrastructure.interfaces.iapi_router import IApiRouter


class ApiFactory:
    @staticmethod
    def create_routers() -> List[IApiRouter]:
        return [
            ApiFactory.create_example_router(),
        ]

    @staticmethod
    def create_example_router() -> IApiRouter:
        example_controller = ExampleController()
        return ExampleRouter(ConstStrings.EXAMPLE_RESOURCE, example_controller)
