import cv2
import numpy as np
import threading
import time
from typing import List, Dict
from infrastructure.interfaces.managers.ialgorithm_manager import IAlgorithmManager
from infrastructure.factories.handler_factory import HandlerFactory
from infrastructure.factories.logger_factory import LoggerFactory
from globals.consts.const_strings import ConstStrings
from globals.consts.logger_messages import LoggerMessages


class AlgorithmManager(IAlgorithmManager):
    def __init__(self, videos_config: List[Dict]) -> None:
        self._videos_config = videos_config
        self._readers = []
        self._num_videos = len(videos_config)
        self._process_threads = []
        self._running = True
        self._logger = LoggerFactory.get_logger_manager()
        
        # Initialize readers
        self._init_readers()

    def start(self) -> None:
        for i in range(self._num_videos):
            thread = threading.Thread(
                target=self._process_frames, args=(i,), daemon=True
            )
            self._process_threads.append(thread)
            thread.start()
        
        self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                         f"Started {self._num_videos} shared memory readers")
        
        # Keep running
        try:
            while self._running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        self._running = False
        
        for reader in self._readers:
            reader.release()
        
        for thread in self._process_threads:
            thread.join(timeout=1)
        
        self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                         "Algorithm manager stopped")

    def _init_readers(self) -> None:
        for video in self._videos_config:
            video_id = video.get("video_id")
            width = video.get("width", 1280)
            height = video.get("height", 720)
            
            reader = HandlerFactory.create_shm_reader_handler(video_id, width, height)
            self._readers.append(reader)
            reader.start()

    def _process_frames(self, video_index: int) -> None:
        reader = self._readers[video_index]
        frame_count = 0
        consecutive_none_count = 0
        max_none_count = 10  # Stop after 10 consecutive None frames
        
        while self._running:
            frame = reader.read_frame()
            if frame is None:
                consecutive_none_count += 1
                if consecutive_none_count >= max_none_count:
                    self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                        f"Video {video_index}: No more frames available. Total frames read: {frame_count}")
                    self._running = False  # Signal to stop instead of calling self.stop()
                    break
                time.sleep(0.1)  # Wait a bit before retrying
                continue
            
            # Reset counter when we get a valid frame
            consecutive_none_count = 0
            frame_count += 1
            
            # Log every 30 frames to verify shared memory is working
            if frame_count % 30 == 0:
                self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                    f"Video {video_index}: Read {frame_count} frames from shared memory, shape: {frame.shape}")

