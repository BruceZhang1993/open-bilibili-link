from types import ModuleType

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QSizePolicy


class PluginTile(QFrame):
    def __init__(self, plugin: ModuleType, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin = plugin
        try:
            self.plugin_info = {
                'id': plugin.__plugin_id__,
                'name': plugin.__plugin_name__,
                'description': plugin.__plugin_desc__,
                'register': plugin.register,
                'unregister': plugin.unregister,
            }
        except AttributeError:
            print(f'[Plugin] Unrecognized plugin {plugin}')
            self.plugin_info = None
        self.setup_ui()

    def setup_ui(self):
        self.setFixedHeight(150)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout = QVBoxLayout()
        if self.plugin_info:
            plugin_name = QLabel(self.plugin_info['name'])
            plugin_id = QLabel(self.plugin_info['id'])
            plugin_desc = QLabel(self.plugin_info['description'])
            layout.addWidget(plugin_name)
            layout.addWidget(plugin_id)
            layout.addWidget(plugin_desc)
        self.setLayout(layout)
