import atexit
import shutil

import yaml
from pathlib import Path
from typing import Optional

from open_bilibili_link.logger import LogManager
from open_bilibili_link.utils import Singleton


class ConfigManager(object, metaclass=Singleton):
    CONFIG_FILE = Path.home() / '.config' / 'OBL' / 'settings.yaml'
    DEFAULT_CONFIG_FILE = Path(__file__).parent / 'configs' / 'settings.default.yaml'

    def __init__(self, fpath: Path = None):
        self.fpath = fpath if fpath is not None else self.CONFIG_FILE
        if not self.fpath.exists():
            self.fpath.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(self.DEFAULT_CONFIG_FILE, self.fpath)
        self._config: Optional[dict] = None

    def load(self):
        with self.fpath.open('r') as f:
            self._config = yaml.safe_load(f)
        atexit.register(self.save)
        LogManager.instance().debug('[Config] 已加载配置文件')

    @property
    def config(self):
        if self._config is None:
            self.load()
        return self._config

    def get(self, *args, default=None):
        conf = self.config
        for key in args:
            conf = conf.get(key, {})
        return conf if conf else default

    def remove(self, *args):
        conf = self.config
        for key in args[0:-1]:
            conf = conf.get(key)
            if conf is None:
                return False
        if args[-1] in conf.keys():
            conf.pop(args[1])
            return True
        return False

    def save(self):
        with self.fpath.open('w') as f:
            yaml.dump(self.config, f)
            f.flush()
            f.close()
        LogManager.instance().debug('[Config] 已保存配置文件')
