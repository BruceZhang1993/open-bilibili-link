from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QGridLayout
from pydantic import BaseModel


class SettingGroup(QFrame):
    def __init__(self, *, title):
        super(SettingGroup, self).__init__()
        self.title = title
        self.items = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.titleWidget = QLabel(self.title)
        self.settingLayout = QGridLayout()
        layout.addWidget(self.titleWidget, alignment=Qt.AlignTop)
        layout.addLayout(self.settingLayout)
        self.setLayout(layout)

    def set_items(self, setting: BaseModel):
        self.items.clear()
        i = 0
        for k, v in setting.__fields__.items():
            self.items.append(QLabel(v.field_info.title))
            self.settingLayout.addWidget(self.items[i], i, 0, alignment=Qt.AlignTop)
            i += 1
        self.show()
