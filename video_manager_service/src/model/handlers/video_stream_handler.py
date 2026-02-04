import cv2
import os
import logging
from numpy import ndarray
from infrastructure.interfaces.handlers.ivideo_stream_handler import IVideoStreamHandler
from infrastructure.factories.logger_factory import LoggerFactory
from globals.consts.const_strings import ConstStrings
from globals.consts.logger_messages import LoggerMessages


class VideoStreamHandler(IVideoStreamHandler):
    def __init__(self, video_id: int, video_path: str):
        self._video_id = video_id
        self._video_path = video_path
        self._frame_width = 1280  # Output size for shared memory
        self._frame_height = 720
        self._frame_rate = 30
        self._cap = None
        self._writer = None
        self._logger = LoggerFactory.get_logger_manager()

    def read_frame(self) -> ndarray:
        ret, frame = self._cap.read()
        if not ret:
            # Loop video when it ends
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self._cap.read()
        return frame if ret else None

    def write_frame(self, frame: ndarray) -> None:
        if frame is None:
            return
        
        # Resize to target dimensions
        resized = cv2.resize(frame, (self._frame_width, self._frame_height))

        if self._writer and self._writer.isOpened():
            self._writer.write(resized)
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
            raise ValueError(f"Cannot open video file: {self._video_path}")
        
        self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                         LoggerMessages.VIDEO_OPENED.format(self._video_path))

    def _init_writer(self) -> None:
        video_writer_pipeline = self._construct_video_writer_pipeline()
        
        source_width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        source_height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Log pipeline for debugging
        self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                         f"GStreamer pipeline: {video_writer_pipeline}")
        
        self._writer = cv2.VideoWriter(
            video_writer_pipeline,
            cv2.CAP_GSTREAMER,
            30,  # VIDEO_FPS = 30 (from Consts)
            (source_width, source_height),
            True  # isColor
        )
        
        if not self._writer.isOpened():
            # Try simpler approach - write to raw file
            self._logger.log(ConstStrings.LOG_NAME_ERROR,
                             "GStreamer pipeline failed, using raw file writer", level=logging.ERROR)
            shm_path = f"/dev/shm/video{self._video_id}.avi"
            self._writer = cv2.VideoWriter(
                shm_path,
                cv2.VideoWriter_fourcc(*'MJPG'),
                30,
                (self._frame_width, self._frame_height)
            )
            
        if not self._writer.isOpened():
            raise ValueError(f"Cannot open shared memory writer for video {self._video_id}")
            
        self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                         LoggerMessages.SHM_WRITER_READY.format(self._video_id))

    def _construct_video_writer_pipeline(self) -> str:
        source_width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        source_height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        shared_memory_path = f"/dev/shm/video{self._video_id}"
        
        pipeline = (
            "appsrc is-live=true do-timestamp=true ! "
            f"video/x-raw,format=BGR,width={source_width},height={source_height},framerate={self._frame_rate}/1 ! "
            "videoconvert ! videoscale ! "
            f"video/x-raw,format=I420,width={self._frame_width},height={self._frame_height} ! "
            f"shmsink socket-path={shared_memory_path} sync=false wait-for-connection=false shm-size=200000000"
        )
        
        return pipeline