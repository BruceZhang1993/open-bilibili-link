import atexit
from configparser import ConfigParser
from pathlib import Path
from typing import Optional

from open_bilibili_link.utils import Singleton


class ConfigManager(object, metaclass=Singleton):
    CONFIG_FILE = Path.home() / '.config' / 'OBL' / 'default.ini'

    def __init__(self):
        if not self.CONFIG_FILE.exists():
            self.CONFIG_FILE.parent.mkdir(parents=True)
            self.CONFIG_FILE.touch()
        self._parser: Optional[ConfigParser] = None

    def load(self):
        self._parser = ConfigParser()
        with self.CONFIG_FILE.open('r') as f:
            self._parser.read_file(f)
        atexit.register(self.save)
        print('[Config] Configuration loaded')

    @property
    def config(self):
        if self._parser is not None:
            return self._parser
        self.load()
        return self._parser

    def get(self, section: str, key: str):
        return self.config.get(section, key, fallback=None)

    def section(self, section: str):
        return dict(self.config.items(section=section))

    def save(self):
        with self.CONFIG_FILE.open('w') as f:
            self._parser.write(f)
            f.flush()
            f.close()
        print('[Config] Configuration saved')