import cv2
import os
from numpy import ndarray

class VideoStreamHandler:
    def __init__(self, video_id: int, video_path: str):
        self.video_id = video_id
        self.video_path = video_path
        self.cap = None
        self._writer = None

    def start(self) -> None:
        self._init_capture()
        self._init_writer()

    def _init_capture(self) -> None:
        self._cap = cv2.VideoCapture(self.video_path)

        if not self._cap.isOpened():
            raise ValueError(f"Cannot open video file: {self.video_path}")
        
        self._total_frames = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._current_frame = 0

    def _init_writer(self) -> None:
        width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self._cap.get(cv2.CAP_PROP_FPS)

        shm_path = f"/dev/shm/video_{self.video_id}"

        pipeline = (
            f"appsrc is-live=true do-timestamp=true ! "
            f"video/x-raw,format=BGR,width={width},height={height},framerate={fps}/1 ! "
            f"videoconvert ! "
            f"shmsink socket-path={shm_path} sync=false wait-for-connection=false shm-size=200000000"
        )
        
        self.writer = cv2.VideoWriter(
            pipeline,
            cv2.CAP_GSTREAMER,
            0,
            fps,
            (width, height)
        )

    def read_frame(self) -> ndarray:
        ret, frame = self._cap.read()
        if not ret:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self._cap.read()
        
        return frame if ret else None
    
    def write_frame(self, frame: ndarray) -> None:
        if self.writer is not None and self.writer.isOpened():
            self.writer.write(frame)

    def release(self) -> None:
        if self._cap and self._cap.isOpened():
            self._cap.release()
        if self.writer and self.writer.isOpened():
            self.writer.release()