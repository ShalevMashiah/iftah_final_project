from src.infrastructure.interfaces.handlers.ivideo_stream_handler import IVideoStreamHandler
from src.models.handlers.video_stream_handler import VideoStreamHandler


class HandlerFactory:
    @staticmethod
    def create_video_stream_handler(video_id: int, video_path: str) -> IVideoStreamHandler:
        return VideoStreamHandler(video_id, video_path)