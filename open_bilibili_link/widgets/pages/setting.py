from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QPushButton

from open_bilibili_link.config import ConfigManager
from open_bilibili_link.models import LiveConfiguration
from open_bilibili_link.widgets.components.setting import SettingGroup


class SettingPage(QFrame):
    btn1: QPushButton

    def __init__(self, context=None):
        super().__init__()
        self.context = context
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setting1 = SettingGroup(title='General')
        live = ConfigManager().get('live')
        self.setting1.set_items(LiveConfiguration(**live))
        self.btn1 = QPushButton('Home')
        self.btn1.clicked.connect(lambda: self.context.goto('obl://home'))
        layout.addWidget(self.setting1, alignment=Qt.AlignTop)
        layout.addWidget(self.btn1, alignment=Qt.AlignBottom)
        self.setLayout(layout)
