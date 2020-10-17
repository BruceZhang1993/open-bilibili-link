import logging
import logging.config
from enum import Enum
from pathlib import Path
from typing import Dict

import yaml


class LoggerName(Enum):
    default = 'default'


class LogManager(object):
    LOGGER_FILE = Path(__file__).parent / 'configs' / 'logger.default.yaml'
    LOG_DIRECTORY = Path.home() / '.cache' / 'OBL' / 'logs'

    instances: Dict[str, 'LogManager'] = {}

    def __init__(self, name: LoggerName = None):
        self._name = name
        self._logger = logging.getLogger(name.value if name is not None else None)
        with self.LOGGER_FILE.open('r') as f:
            log_config = yaml.safe_load(f)
            if isinstance(log_config, dict):
                base_fname = log_config.get('handlers', {}).get('file', {}).get('filename', None)
                if base_fname:
                    self.LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)
                    log_config['handlers']['file']['filename'] = (self.LOG_DIRECTORY / base_fname).as_posix()
                logging.config.dictConfig(log_config)

    @classmethod
    def instance(cls, name: LoggerName = LoggerName.default) -> 'LogManager':
        if name.value not in cls.instances.keys():
            cls.instances[name.value] = cls(name)
        return cls.instances[name.value]

    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)

    warn = warning

    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        self._logger.exception(msg, *args, exc_info=exc_info, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)

    fatal = critical

    def log(self, level, msg, *args, **kwargs):
        self._logger.log(level, msg, *args, **kwargs)
