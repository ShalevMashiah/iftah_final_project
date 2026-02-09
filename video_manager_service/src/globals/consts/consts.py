class Consts:
    SEND_MESSAGE_DURATION = 1
    ZMQ_SERVER_LOOP_DURATION = 0.01
    # Algorithm output frame size used for shared memory caps
    ALGO_FRAME_WIDTH = 1280
    ALGO_FRAME_HEIGHT = 720
    # Target frame rate for SHM writer
    ALGO_FRAME_RATE = 30
    
    # GStreamer pipeline configuration for RTSP
    GSTREAMER_QUEUE_MAX_BUFFERS = 2
    GSTREAMER_SHM_SIZE = 50000000  # 50MB
