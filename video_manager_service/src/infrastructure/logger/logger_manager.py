import datetime
import logging
import os
from typing import Dict
from globals.consts.const_strings import ConstStrings
from infrastructure.interfaces.ilogger_manager import ILoggerManager
from globals.consts.const_collections import ConstCollections


class LoggerManager(ILoggerManager):
    def __init__(self):
        self._loggers: Dict[str, logging.Logger] = {}

    def log(self, log_name: str, msg: str, level=logging.DEBUG):
        logger = self._get_or_create_logger(log_name, level)
        logger.log(level, msg)

    def _get_or_create_logger(self, log_name: str, level) -> logging.Logger:
        if log_name in self._loggers:
            return self._loggers[log_name]

        log_file_path = os.getenv(
            ConstStrings.LOG_ENV, ConstStrings.LOG_FILEPATH.format(log_name, datetime.datetime.now().strftime(ConstStrings.DATE_TIME_FORMAT)))
        log_directory = os.path.dirname(log_file_path)
        os.makedirs(log_directory, exist_ok=True)

        logger = logging.getLogger(log_name)
        logger.setLevel(level)

        if not logger.handlers:
            if (log_name in ConstCollections.LOG_NAMES_WITH_FILE):
                self._add_file_handler(level, log_file_path, logger)
            if (log_name in ConstCollections.LOG_NAMES_WITH_CONSOLE):
                self._add_console_handler(level, logger)
        self._loggers[log_name] = logger
        return logger

    def _add_file_handler(self, level, log_file_path, logger):
        file_handler = logging.FileHandler(
            log_file_path, mode=ConstStrings.LOG_MODE)
        file_handler.setLevel(level)
        formatter = logging.Formatter(ConstStrings.LOG_FORMATTER)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    def _add_console_handler(self, level, logger):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        formatter = logging.Formatter(ConstStrings.LOG_FORMATTER)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
