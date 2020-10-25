from typing import get_type_hints

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QGridLayout

from open_bilibili_link.plugin import PluginManager
from open_bilibili_link.utils import reset_style
from open_bilibili_link.widgets.components.plugin import PluginTile


class PluginPage(QFrame):
    def __init__(self, context=None):
        super().__init__()
        self.context = context
        self.manager = PluginManager()
        self.setup_ui()

    def setup_ui(self):
        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.show_plugins()
        self.setLayout(self.layout)
        reset_style(self, self.layout)

    def show_plugins(self):
        for i, plugin in enumerate(self.manager.plugin_list):
            tile = PluginTile(plugin)
            self.layout.addWidget(tile, i // 3, i % 3, Qt.AlignTop)
