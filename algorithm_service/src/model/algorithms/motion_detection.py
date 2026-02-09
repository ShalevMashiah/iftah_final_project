from typing import Any, Dict, Optional, Tuple

import cv2
import numpy as np

from globals.consts.consts import Consts
from infrastructure.factories.logger_factory import LoggerFactory
from globals.consts.const_strings import ConstStrings
from globals.consts.logger_messages import LoggerMessages


class MotionDetectionAlgorithm:
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger_manager()
        self._bg_subtractor: Optional[cv2.BackgroundSubtractor] = None
        self._kernel: Optional[np.ndarray] = None
        self._min_contour_area: int = Consts.MOTION_MIN_AREA
        self._threshold: int = Consts.MOTION_BG_VAR_THRESHOLD
        self._dilate_iterations: int = Consts.MOTION_DILATE_ITER
        self._erode_iterations: int = 0
        self._history: int = Consts.MOTION_BG_HISTORY
        self._detect_shadows: bool = Consts.MOTION_DETECT_SHADOWS
        self._draw_bbox: bool = True
        self._draw_mask: bool = False
        self._mask_rect: Optional[Tuple[int, int, int, int]] = None  # x, y, w, h
        self._frame_idx: int = 0

    def setup(self, config: Dict[str, Any]) -> None:
        self._min_contour_area = int(config.get("min_contour_area", self._min_contour_area))
        self._threshold = int(config.get("threshold", self._threshold))
        self._dilate_iterations = int(config.get("dilate_iterations", self._dilate_iterations))
        self._erode_iterations = int(config.get("erode_iterations", self._erode_iterations))
        self._history = int(config.get("history", self._history))
        self._detect_shadows = bool(config.get("detect_shadows", self._detect_shadows))
        self._draw_bbox = bool(config.get("draw_bbox", self._draw_bbox))
        self._draw_mask = bool(config.get("draw_mask", self._draw_mask))
        mask_rect = config.get("mask_rect")
        if isinstance(mask_rect, (list, tuple)) and len(mask_rect) == 4:
            self._mask_rect = (int(mask_rect[0]), int(mask_rect[1]), int(mask_rect[2]), int(mask_rect[3]))

        self._bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=self._history, varThreshold=self._threshold, detectShadows=self._detect_shadows)
        self._kernel = np.ones((3, 3), np.uint8)
        try:
            self._logger.log(ConstStrings.LOG_NAME_DEBUG, f"MotionDetectionAlgorithm initialized: min_area={self._min_contour_area} threshold={self._threshold} history={self._history} shadows={self._detect_shadows}")
        except Exception:
            pass

    def process(self, frame: Any) -> Any:
        if self._bg_subtractor is None:
            return frame

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self._mask_rect is not None:
            x, y, w, h = self._mask_rect
            mask = np.zeros_like(gray)
            cv2.rectangle(mask, (x, y), (x + w, y + h), 255, thickness=-1)
            gray = cv2.bitwise_and(gray, mask)
            if self._draw_mask:
                overlay = frame.copy()
                cv2.rectangle(overlay, (x, y), (x + w, y + h), (255, 0, 0), 2)
                frame = overlay

        fgmask = self._bg_subtractor.apply(frame)
        _, fgmask = cv2.threshold(fgmask, 244, 255, cv2.THRESH_BINARY)
        if self._erode_iterations > 0:
            fgmask = cv2.erode(fgmask, self._kernel, iterations=self._erode_iterations)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (Consts.MOTION_KERNEL_SIZE, Consts.MOTION_KERNEL_SIZE))
        fgmask = cv2.dilate(fgmask, kernel, iterations=self._dilate_iterations)

        contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        regions = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self._min_contour_area:
                continue
            x, y, w, h = cv2.boundingRect(cnt)
            if self._draw_bbox:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            regions += 1

        self._frame_idx += 1
        if regions > 0 and (self._frame_idx % max(1, Consts.ALGO_FRAME_RATE) == 0):
            try:
                self._logger.log(ConstStrings.LOG_NAME_DEBUG, LoggerMessages.MOTION_REGION_COUNT.format("motion", regions))
            except Exception:
                pass

        return frame

    def release(self) -> None:
        self._bg_subtractor = None
        self._kernel = None