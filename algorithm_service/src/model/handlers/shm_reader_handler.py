import cv2
import os
import logging
import time
import struct
import mmap
import numpy as np
from infrastructure.interfaces.handlers.ishm_reader_handler import IShmReaderHandler
from infrastructure.factories.logger_factory import LoggerFactory
from globals.consts.const_strings import ConstStrings
from globals.consts.logger_messages import LoggerMessages


class ShmReaderHandler(IShmReaderHandler):
    def __init__(self, video_id: int, width: int = 1280, height: int = 720):
        self._video_id = video_id
        self._width = width
        self._height = height
        self._shm_path = f"/dev/shm/video{video_id}.avi"
        self._cap = None
        self._logger = LoggerFactory.get_logger_manager()
        self._last_read_time = 0
        self._min_frame_interval = 0.033  # ~30 FPS

    def start(self) -> None:
        # Wait for shared memory file to be created
        max_wait = 10
        waited = 0
        while not os.path.exists(self._shm_path) and waited < max_wait:
            self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                             f"Waiting for shared memory file: {self._shm_path}")
            time.sleep(1)
            waited += 1
        
        if not os.path.exists(self._shm_path):
            raise FileNotFoundError(f"Shared memory file not found: {self._shm_path}")
        
        self._cap = cv2.VideoCapture(self._shm_path)
        
        if not self._cap.isOpened():
            raise ValueError(f"Cannot open shared memory video: {self._shm_path}")
        
        self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                         f"Opened shared memory reader for video {self._video_id}")

    def read_frame(self) -> np.ndarray:
        if not self._cap or not self._cap.isOpened():
            return None
        
        # Throttle reading to avoid excessive CPU
        current_time = time.time()
        time_since_last = current_time - self._last_read_time
        if time_since_last < self._min_frame_interval:
            time.sleep(self._min_frame_interval - time_since_last)
        
        ret, frame = self._cap.read()
        self._last_read_time = time.time()
        
        return frame if ret else None

    def release(self) -> None:
        if self._cap and self._cap.isOpened():
            self._cap.release()
