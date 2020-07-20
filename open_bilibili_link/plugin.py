import importlib
import sys
from pathlib import Path
from typing import Optional

from open_bilibili_link.config import ConfigManager
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

    def register_by_id(self, pid):
        for plugin in self.plugin_list:
            if plugin.__plugin_id__ == pid:
                self.register_plugin(plugin)
        print(f'[Plugin] Plugin {pid} not found')

    def unregister_by_id(self, pid):
        for plugin in self.plugin_list:
            if plugin.__plugin_id__ == pid:
                self.unregister_plugin(plugin)
        print(f'[Plugin] Plugin {pid} not found')

    @staticmethod
    def register_plugin(plugin):
        try:
            plugin.register()
            plugin.__loaded__ = True
            print(f'[Plugin] {plugin.__plugin_id__} loaded')
        except Exception as e:
            print(f'[Plugin] {e}')

    @staticmethod
    def unregister_plugin(plugin):
        try:
            plugin.unregister()
            plugin.__loaded__ = False
        except Exception as e:
            print(f'[Plugin] {e}')

    def register_plugins(self):
        for plugin in self.plugin_list:
            is_auto = ConfigManager().get(plugin.__plugin_id__, 'autostart')
            if not is_auto:
                continue
            self.register_plugin(plugin)

    def search_plugins(self):
        self._plugin_list = []
        for plugin_dir in self.PLUGIN_DIRS:
            if not plugin_dir.exists():
                continue
            sys.path.append(plugin_dir.as_posix())
            for file in plugin_dir.iterdir():
                if file.is_file() and file.name.startswith('obl_'):
                    p = importlib.import_module(file.stem)
                    p.__loaded__ = False
                    p.__config__ = ConfigManager().section(p.__plugin_id__)
                    self._plugin_list.append(p)
            sys.path.remove(plugin_dir.as_posix())
