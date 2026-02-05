import os
from infrastructure.factories.infrastructure_factory import InfrastructureFactory
from globals.consts.const_strings import ConstStrings
from infrastructure.interfaces.handlers.ishm_reader_handler import IShmReaderHandler
from model.handlers.shm_reader_handler import ShmReaderHandler

class HandlerFactory:
    @staticmethod
    def create_example_handler():
        pass
    
    @staticmethod
    def create_shm_reader_handler(video_id: int, width: int = 1280, height: int = 720) -> IShmReaderHandler:
        return ShmReaderHandler(video_id, width, height)