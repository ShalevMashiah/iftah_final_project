import os
import threading
import time
import logging
from typing import List, Dict

from infrastructure.interfaces.managers.ivideo_manager import IVideoManager
from infrastructure.factories.handler_factory import HandlerFactory
from infrastructure.factories.logger_factory import LoggerFactory
from globals.consts.const_strings import ConstStrings
from globals.consts.logger_messages import LoggerMessages


class VideoManager(IVideoManager):
    def __init__(self, videos_config: List[Dict]) -> None:
        self._videos_config = videos_config
        self._handlers = []
        self._num_videos = len(videos_config)
        self._process_video_threads = []
        self._running = True
        self._logger = LoggerFactory.get_logger_manager()
        
        # Clean up shared memory files 
        self._remove_shared_memory_files()
        
        # Initialize video handlers 
        self._init_video_handlers()

    def start(self) -> None:
        for i in range(self._num_videos):
            thread = threading.Thread(
                target=self._process_frames_for_video, args=(i,)
            )
            self._process_video_threads.append(thread)
            thread.start()
        
        self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                         LoggerMessages.VIDEO_STREAMS_STARTED.format(self._num_videos))
        
        # Keep running
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        self._running = False
        
        for handler in self._handlers:
            handler.release()
        
        for thread in self._process_video_threads:
            thread.join()
        
        self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                         LoggerMessages.VIDEO_MANAGER_STOPPED)

    def _init_video_handlers(self) -> None:
        for video in self._videos_config:
            video_id = video.get("video_id")
            video_path = video.get("video_path")
            
            # Create handler using factory (SAME pattern as example)
            video_handler = HandlerFactory.create_video_stream_handler(
                video_id, video_path
            )
            self._handlers.append(video_handler)
            video_handler.start()

    def _process_frames_for_video(self, video_index: int) -> None:
        handler = self._handlers[video_index]
        
        while self._running:
            frame = handler.read_frame()
            if frame is None:
                continue
            
            # In the example, they process with algorithm here
            # For you, just write directly to shared memory
            handler.write_frame(frame)

    def _remove_shared_memory_files(self) -> None:
        file_prefixes = ["cam", "shmpipe"]
        shm_path = ConstStrings.SHARED_MEMORY_PATH
        
        if not os.path.exists(shm_path):
            return
        
        files = [f for f in os.listdir(shm_path) if any(
            f.startswith(prefix) for prefix in file_prefixes)]
        
        for file in files:
            try:
                os.remove(os.path.join(shm_path, file))
                self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                                 LoggerMessages.SHM_FILE_REMOVED.format(file))
            except Exception as e:
                self._logger.log(ConstStrings.LOG_NAME_ERROR,
                                 LoggerMessages.SHM_FILE_REMOVAL_FAILED.format(file, e), level=logging.ERROR)