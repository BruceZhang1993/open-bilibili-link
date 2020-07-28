import atexit
import toml
from pathlib import Path
from typing import Optional

from open_bilibili_link.utils import Singleton


class ConfigManager(object, metaclass=Singleton):
    CONFIG_FILE = Path.home() / '.config' / 'OBL' / 'default.toml'

    def __init__(self):
        if not self.CONFIG_FILE.exists():
            self.CONFIG_FILE.parent.mkdir(parents=True)
            self.CONFIG_FILE.touch()
        self._config: Optional[dict] = None

    def load(self):
        with self.CONFIG_FILE.open('r') as f:
            self._config = toml.load(f)
        atexit.register(self.save)
        print('[Config] Configuration loaded')

    @property
    def config(self):
        if self._config is None:
            self.load()
        return self._config

    def get(self, *args):
        conf = self.config
        for key in args:
            conf = conf.get(key, {})
        return conf if conf is not None else None

    def save(self):
        with self.CONFIG_FILE.open('w') as f:
            toml.dump(self.config, f)
            f.flush()
            f.close()
        print('[Config] Configuration saved')
