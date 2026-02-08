import cv2
import os
import logging
import time
from numpy import ndarray
from infrastructure.interfaces.handlers.ivideo_stream_handler import IVideoStreamHandler
from infrastructure.factories.logger_factory import LoggerFactory
from globals.consts.const_strings import ConstStrings
from globals.consts.consts import Consts
from globals.consts.logger_messages import LoggerMessages


class VideoStreamHandler(IVideoStreamHandler):
    def __init__(self, video_id: int, video_path: str):
        self._video_id = video_id
        self._video_path = video_path
        self._frame_width = Consts.ALGO_FRAME_WIDTH
        self._frame_height = Consts.ALGO_FRAME_HEIGHT
        self._frame_rate = Consts.ALGO_FRAME_RATE
        self._cap = None
        self._writer = None
        self._logger = LoggerFactory.get_logger_manager()

    def read_frame(self) -> ndarray:
        ret, frame = self._cap.read()
        return frame if ret else None

    def write_frame(self, frame: ndarray) -> None:
        if frame is None:
            return
        
        # Resize to target dimensions
        resized = cv2.resize(frame, (self._frame_width, self._frame_height))

        if self._writer and self._writer.isOpened():
            self._writer.write(resized)
            # Pace writes to approximate the configured frame rate
            time.sleep(1.0 / max(1.0, float(self._frame_rate)))
        else:
            self._logger.log(ConstStrings.LOG_NAME_ERROR,
                             LoggerMessages.WRITER_NOT_OPENED.format(self._video_id), level=logging.ERROR)

    def release(self) -> None:
        if self._cap and self._cap.isOpened():
            self._cap.release()
        if self._writer and self._writer.isOpened():
            self._writer.release()

    def start(self) -> None:
        self._init_capture()
        self._init_writer()

    def _init_capture(self) -> None:
        self._cap = cv2.VideoCapture(self._video_path)
        
        if not self._cap.isOpened():
            self._logger.log(ConstStrings.LOG_NAME_ERROR,
                             f"Cannot open video file: {self._video_path}", level=logging.ERROR)
            raise ValueError(f"Cannot open video file: {self._video_path}")
        
        self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                         LoggerMessages.VIDEO_OPENED.format(self._video_path))

    def _init_writer(self) -> None:
        video_writer_pipeline = self._construct_video_writer_pipeline()

        # Log pipeline for debugging
        self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                         f"GStreamer pipeline: {video_writer_pipeline}")

        # We write frames resized to (self._frame_width, self._frame_height)
        frame_size = (self._frame_width, self._frame_height)

        self._writer = cv2.VideoWriter(
            video_writer_pipeline,
            cv2.CAP_GSTREAMER,
            self._frame_rate,
            frame_size,
            True  # isColor
        )
        
        if not self._writer.isOpened():
            # Try simpler approach - write to raw file
            self._logger.log(ConstStrings.LOG_NAME_ERROR,
                             "GStreamer pipeline failed, using raw file writer", level=logging.ERROR)
            shm_path = f"/dev/shm/cam{self._video_id}.avi"
            self._writer = cv2.VideoWriter(
                shm_path,
                cv2.VideoWriter_fourcc(*'MJPG'),
                self._frame_rate,
                (self._frame_width, self._frame_height)
            )
            
        if not self._writer.isOpened():
            self._logger.log(ConstStrings.LOG_NAME_ERROR,
                             f"Cannot open shared memory writer for video {self._video_id}", level=logging.ERROR)
            raise ValueError(f"Cannot open shared memory writer for video {self._video_id}")
            
        self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                         LoggerMessages.SHM_WRITER_READY.format(self._video_id))

    def _construct_video_writer_pipeline(self) -> str:
        shared_memory_path = ConstStrings.SHARED_MEMORY_CAM_PATH.format(camera_id=self._video_id)

        return ConstStrings.SHARED_MEMORY_PIPELINE.format(
            frame_height=Consts.ALGO_FRAME_HEIGHT,
            frame_width=Consts.ALGO_FRAME_WIDTH,
            frame_rate=self._frame_rate,
            scaled_width=self._frame_width,
            scaled_height=self._frame_height,
            shared_memory_path=shared_memory_path,
        )