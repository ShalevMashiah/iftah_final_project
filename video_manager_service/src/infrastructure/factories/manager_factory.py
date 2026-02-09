from infrastructure.interfaces.managers.ivideo_manager import IVideoManager
from model.managers.video_manager import VideoManager


class ManagerFactory:
    @staticmethod
    def create_video_manager(videos_config: list) -> IVideoManager:
        return VideoManager(videos_config)
    
    @staticmethod
    def create_all() -> None:
        # Configure your video files here
        videos_config = [
            {
                "video_id": 1,
                "video_path": "videos/video1.mp4"
            },
                        {
                "video_id": 2,
                "video_path": "videos/video2.mp4"
            },
            {
                "video_id": 3,
                "video_path": "rtsp://admin:Rd123456@192.168.2.60:556/h264"
            }
        ]
        
        video_manager = ManagerFactory.create_video_manager(videos_config)
        video_manager.start()