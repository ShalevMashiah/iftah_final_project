class ConstStrings:
    VERSION = "version 1.3"

    # ? Server's address environment variables
    ZMQ_SERVER_HOST = 'ZMQ_SERVER_HOST'
    ZMQ_SERVER_PORT = 'ZMQ_SERVER_PORT'

    # ? Error messages
    ERROR_MESSAGE = "error"
    UNKNOWN_OPERATION_ERROR_MESSAGE = "unknown operation"
    UNKNOWN_RESOURCE_ERROR_MESSAGE = "unknown resource"
    ERROR_EXAMPLE_FUNCTION = "error_in_example_function"

    # ? ZMQ server connection
    BASE_TCP_CONNECTION_STRINGS = "tcp://"

    # ? ZMQ request format identifiers
    RESOURCE_IDENTIFIER = "resource"
    OPERATION_IDENTIFIER = "operation"
    DATA_IDENTIFIER = "data"

    # ? ZMQ response format indentifiers
    STATUS_IDENTIFIER = "status"

    # ? ZMQ Resources
    EXAMPLE_RESOURCE = "example_resource"

    # ? ZMQ Operations
    EXAMPLE_OPERATION = "example_operation"

    # ? Kafka Configuration
    GLOBAL_CONFIG_PATH = "/app/config/configuration.xml"
    BOOTSTRAP_SERVERS_ROOT = 'bootstrap_servers'
    KAFKA_ROOT_CONFIGURATION_NAME = "kafka_configuration"

    EXAMPLE_TOPIC = "example_topic"
    EXAMPLE_MESSAGE = "example_message"

    DECODE_FORMAT = 'utf-8'
    ENCODE_FORMAT = 'utf-8'

    # ? Kafka settings
    AUTO_OFFSET_RESET = 'earliest'
    GROUP_ID = 'my-group'

    # ? Log
    LOG_NAME_DEBUG = "debug"
    LOG_ENV = "LOG_FILE_PATH"
    LOG_FILEPATH = "./logs/{}_{}.log"
    LOG_MODE = "a"
    LOG_FORMATTER = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_TIME_FORMAT = '%Y_%m_%d-%H_%M_%S'

    # Shared memory paths and pipeline templates (aligned with video manager)
    SHARED_MEMORY_CAM_PATH = "/dev/shm/cam{camera_id}"
    SHARED_MEMORY_PATH = "/dev/shm/"
    SHARED_MEMORY_PIPELINE = (
        "appsrc is-live=true do-timestamp=true ! "
        "video/x-raw,format=BGR,width={frame_width},height={frame_height},framerate={frame_rate}/1 ! "
        "videoconvert ! videoscale ! "
        "video/x-raw,format=I420,width={scaled_width},height={scaled_height} ! "
        "shmsink socket-path={shared_memory_path} sync=false wait-for-connection=false shm-size=200000000"
    )
