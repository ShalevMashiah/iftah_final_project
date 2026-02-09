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
        self._is_rtsp = video_path.startswith("rtsp://")

    def read_frame(self) -> ndarray:
        if not self._cap or not self._cap.isOpened():
            # Try to reconnect for RTSP streams
            if self._is_rtsp:
                self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                                f"RTSP stream disconnected, attempting reconnect: {self._video_path}")
                try:
                    self._init_capture()
                except Exception as e:
                    self._logger.log(ConstStrings.LOG_NAME_ERROR,
                                   f"Failed to reconnect RTSP: {e}", level=logging.ERROR)
                    return None
            else:
                return None
        
        # For RTSP, flush buffer to get latest frame
        if self._is_rtsp:
            # Grab and discard 1 old frame from buffer
            self._cap.grab()
            ret, frame = self._cap.retrieve()
        else:
            ret, frame = self._cap.read()
            
        if not ret and self._is_rtsp:
            # RTSP connection lost, will retry on next call
            self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                           f"Lost RTSP connection for video {self._video_id}")
            if self._cap:
                self._cap.release()
            return None
        return frame if ret else None

    def write_frame(self, frame: ndarray) -> None:
        if frame is None:
            return
        
        # Resize to target dimensions
        resized = cv2.resize(frame, (self._frame_width, self._frame_height))

        if self._writer and self._writer.isOpened():
            self._writer.write(resized)
            # Don't sleep for RTSP to minimize latency
            if not self._is_rtsp:
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
        # Release existing capture if any
        if self._cap:
            self._cap.release()
            
        self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                        f"Opening video source: {self._video_path}")
        
        # For RTSP streams, retry with timeout
        if self._is_rtsp:
            max_retries = 60  # 60 attempts
            retry_delay = 5   # 5 seconds between attempts
            
            for attempt in range(1, max_retries + 1):
                self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                               f"Attempt {attempt}/{max_retries} to connect to RTSP camera: {self._video_path}")
                
                # Set low-latency FFMPEG options BEFORE creating VideoCapture
                os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = (
                    'rtsp_transport;tcp|'
                    'fflags;nobuffer|'
                    'flags;low_delay'
                )
                
                self._cap = cv2.VideoCapture(self._video_path, cv2.CAP_FFMPEG)
                
                # Minimize buffer to 2 frames for balance between latency and quality
                self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
                
                if self._cap.isOpened():
                    self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                                   f"Successfully connected to RTSP camera on attempt {attempt}")
                    break
                    
                self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                               f"Failed to connect. Waiting {retry_delay} seconds before retry...")
                #time.sleep(retry_delay)
                
            if not self._cap.isOpened():
                error_msg = f"Cannot open RTSP camera after {max_retries} attempts: {self._video_path}"
                self._logger.log(ConstStrings.LOG_NAME_ERROR, error_msg, level=logging.ERROR)
                raise ValueError(error_msg)
        else:
            self._cap = cv2.VideoCapture(self._video_path)
            if not self._cap.isOpened():
                error_msg = f"Cannot open video file: {self._video_path}"
                self._logger.log(ConstStrings.LOG_NAME_ERROR, error_msg, level=logging.ERROR)
                raise ValueError(error_msg)
        
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

        if self._is_rtsp:
            return ConstStrings.SHARED_MEMORY_PIPELINE_RTSP.format(
                frame_width=self._frame_width,
                frame_height=self._frame_height,
                frame_rate=self._frame_rate,
                queue_max_buffers=Consts.GSTREAMER_QUEUE_MAX_BUFFERS,
                shared_memory_path=shared_memory_path,
                shm_size=Consts.GSTREAMER_SHM_SIZE,
            )
        else:
            return ConstStrings.SHARED_MEMORY_PIPELINE.format(
                frame_height=Consts.ALGO_FRAME_HEIGHT,
                frame_width=Consts.ALGO_FRAME_WIDTH,
                frame_rate=self._frame_rate,
                scaled_width=self._frame_width,
                scaled_height=self._frame_height,
                shared_memory_path=shared_memory_path,
            )