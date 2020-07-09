from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QPushButton, QScrollArea, QSizePolicy, QGridLayout
from asyncqt import asyncSlot

from open_bilibili_link.services import BilibiliLiveService
from open_bilibili_link.widgets.components.live import LiveControlCenter
from open_bilibili_link.widgets.components.usercard import UserCard


class HomePage(QFrame):
    btn1: QPushButton

    def __init__(self, context=None):
        super().__init__()
        self.context = context
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        area = QScrollArea()
        area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        inner_layout = QVBoxLayout()
        inner_layout.setAlignment(Qt.AlignTop)
        # area.setStyleSheet('QScrollArea {background: gray;}')
        self.usercard = UserCard()
        self.usercard.show_data()
        live_control = LiveControlCenter(homepage=self)
        live_control.show_data()
        inner_layout.addWidget(self.usercard)
        inner_layout.addWidget(live_control)
        area.setLayout(inner_layout)
        layout.addWidget(area)
        area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.setContentsMargins(0, 5, 5, 5)
        self.setLayout(layout)

    @asyncSlot()
    async def ping_host(self):
        self.btn1.setText('Wait...')
        self.btn1.setText(f'{await BilibiliLiveService().ping()} ms')
