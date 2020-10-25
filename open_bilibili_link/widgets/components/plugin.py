from types import ModuleType

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QSizePolicy

from open_bilibili_link.logger import LogManager


class PluginTile(QFrame):
    def __init__(self, plugin: ModuleType, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin = plugin
        self.loaded = False
        try:
            self.plugin_info = {
                'id': plugin.__plugin_id__,
                'name': plugin.__plugin_name__,
                'description': plugin.__plugin_desc__,
                'register': plugin.register,
                'unregister': plugin.unregister,
                'loaded': plugin.__loaded__,
            }
            self.loaded = plugin.__loaded__ is True
        except AttributeError:
            LogManager.instance().warning(f'[Plugin] 未识别的插件 {plugin}，请检查插件代码')
            self.plugin_info = None
        self.setProperty('pluginloaded', self.loaded)
        self.setup_ui()

    def setup_ui(self):
        self.setFixedHeight(150)
        self.setFixedWidth(300)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        if self.plugin_info:
            plugin_name = QLabel(self.plugin_info['name'])
            plugin_name.setObjectName('plugin-name')
            plugin_name.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            plugin_id = QLabel(f'{self.plugin_info["id"]} []')
            plugin_id.setObjectName('plugin-id')
            plugin_id.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            plugin_desc = QLabel(self.plugin_info['description'])
            plugin_desc.setObjectName('plugin-desc')
            plugin_desc.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            plugin_desc.setWordWrap(True)
            layout.addWidget(plugin_name, Qt.AlignTop)
            layout.addWidget(plugin_id, Qt.AlignTop)
            layout.addWidget(plugin_desc, Qt.AlignTop)
            layout.addStretch()
        self.setLayout(layout)
