import importlib
import sys
from pathlib import Path
from typing import Optional

from open_bilibili_link.config import ConfigManager
from open_bilibili_link.logger import LogManager
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
        LogManager.instance().warning(f'[Plugin] 未找到插件 {pid}')

    def unregister_by_id(self, pid):
        for plugin in self.plugin_list:
            if plugin.__plugin_id__ == pid:
                self.unregister_plugin(plugin)
        LogManager.instance().warning(f'[Plugin] 未找到插件 {pid}')

    @staticmethod
    def register_plugin(plugin):
        try:
            plugin.register()
            plugin.__loaded__ = True
            LogManager.instance().debug(f'[Plugin] {plugin.__plugin_id__} 已加载')
        except Exception as e:
            LogManager.instance().warning(f'[Plugin] 插件加载异常 {str(e)}')

    @staticmethod
    def unregister_plugin(plugin):
        try:
            plugin.unregister()
            plugin.__loaded__ = False
        except Exception as e:
            LogManager.instance().warning(f'[Plugin] 插件加载异常 {str(e)}')

    def register_plugins(self):
        for plugin in self.plugin_list:
            is_auto = ConfigManager().get(*(plugin.__plugin_id__.split('.')), 'autostart')
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
                    user_config = ConfigManager().get(*(p.__plugin_id__.split('.'))) # noqa
                    p.__config__ = {}
                    for k, v in p.__plugin_settings__.items():
                        type_, title, subtitle, default = v
                        user_v = user_config.get(k)
                        try:
                            if user_v is not None:
                                try:
                                    p.__config__[k] = type_(user_v)
                                except ValueError as e:
                                    LogManager.instance().warning(f'[Plugin] 加载用户插件设置项类型异常 '
                                                                  f'需要类型 {str(type_)} '
                                                                  f'当前 {type(user_v)} 将使用默认值 {str(e)}')
                                    p.__config__[k] = type_(default)
                            else:
                                p.__config__[k] = type_(default)
                        except ValueError as e:
                            p.__config__[k] = None
                            LogManager.instance().warning(f'[Plugin] 加载插件默认设置项类型异常 '
                                                          f'需要类型 {str(type_)} '
                                                          f'当前 {type(default)} 将使用 None {str(e)}')
                    self._plugin_list.append(p)
            sys.path.remove(plugin_dir.as_posix())
