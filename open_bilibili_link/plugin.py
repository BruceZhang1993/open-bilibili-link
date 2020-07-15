import importlib
import sys
from pathlib import Path
from typing import Optional

from open_bilibili_link.utils import Singleton


class PluginManager(object, metaclass=Singleton):
    PLUGIN_DIRS = [Path(__file__).parent / 'plugins', Path.home() / '.local' / 'share' / 'OBL' / 'plugins']

    _plugin_list: Optional[list] = None

    @property
    def plugin_list(self):
        if self._plugin_list is not None:
            return self._plugin_list
        self.search_plugins()
        return self._plugin_list

    def register_plugins(self):
        for plugin in self.plugin_list:
            try:
                plugin.register()
            except Exception as e:
                print(f'[Plugin] {e}')

    def search_plugins(self):
        self._plugin_list = []
        for plugin_dir in self.PLUGIN_DIRS:
            if not plugin_dir.exists():
                continue
            sys.path.append(plugin_dir.as_posix())
            for file in plugin_dir.iterdir():
                if file.is_file() and file.name.startswith('obl_'):
                    self._plugin_list.append(importlib.import_module(file.stem))
            sys.path.remove(plugin_dir.as_posix())
