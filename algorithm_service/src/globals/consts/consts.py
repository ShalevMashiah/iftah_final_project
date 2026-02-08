class Consts:
    SEND_MESSAGE_DURATION = 1
    ZMQ_SERVER_LOOP_DURATION = 0.01
    # Algorithm expected frame size from shared memory
    ALGO_FRAME_WIDTH = 1280
    ALGO_FRAME_HEIGHT = 720
    # Algorithm expected frame rate
    ALGO_FRAME_RATE = 30
    # SHM reader open wait times (seconds)
    SHM_OPEN_GST_WAIT_SECONDS = 5
    SHM_OPEN_AVI_WAIT_SECONDS = 10
    
    # Motion detection
    MOTION_BG_HISTORY = 300
    MOTION_BG_VAR_THRESHOLD = 32
    MOTION_DETECT_SHADOWS = True
    MOTION_MIN_AREA = 800
    MOTION_DILATE_ITER = 2
    MOTION_KERNEL_SIZE = 3