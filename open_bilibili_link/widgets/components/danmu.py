import asyncio
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDockWidget, QVBoxLayout, QListView, QScrollArea
from asyncqt import asyncClose

from open_bilibili_link.models import DanmuData
from open_bilibili_link.services import BilibiliLiveDanmuService


class DanmuWidget(QDockWidget):
    def __init__(self, *args, **kwargs):
        self.roomid = None
        if 'roomid' in kwargs.keys():
            self.roomid = kwargs.pop('roomid')
        super().__init__(*args, **kwargs)
        self.setup_ui()

    def setup_ui(self):
        # load qss
        with open(Path(__file__).parent.parent / 'styles' / 'material.qss', 'r') as f:
            self.setStyleSheet(f.read())
        self.setFixedSize(400, 700)
        area = QScrollArea()
        area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.danmu_list_view = QListView()
        self.danmu_list_view.setStyleSheet('QListView { background: skyblue; font-size: 13px; }')
        self.danmu_list_model = QStandardItemModel()
        self.danmu_list_view.setModel(self.danmu_list_model)
        layout = QVBoxLayout()
        layout.addWidget(self.danmu_list_view)
        area.setLayout(layout)
        self.setWidget(area)

    def show_data(self):
        if self.roomid is not None:
            asyncio.gather(self.load_danmu())

    def append_danmu(self, danmu: DanmuData):
        print('danmu received', danmu.msg_type)
        if danmu.msg_type == BilibiliLiveDanmuService.TYPE_DANMUKU:
            self.danmu_list_model.appendRow([QStandardItem(f'{danmu.name}: {danmu.content}')])
            self.danmu_list_view.scrollToBottom()

    @asyncClose
    async def closeEvent(self, _):
        await BilibiliLiveDanmuService(self.append_danmu).session.close()

    async def load_danmu(self):
        await BilibiliLiveDanmuService(self.append_danmu).ws_connect(self.roomid)
