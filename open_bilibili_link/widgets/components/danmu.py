import asyncio
from pathlib import Path

from PyQt5.QtCore import Qt, QSize, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFontMetrics
from PyQt5.QtWidgets import QDockWidget, QVBoxLayout, QListView, QScrollArea, QStyledItemDelegate, QStyleOptionViewItem
from asyncqt import asyncClose

from open_bilibili_link.models import DanmuData
from open_bilibili_link.services import BilibiliLiveDanmuService


class DanmuItemDelegate(QStyledItemDelegate):
    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        fm = QFontMetrics(option.font)
        model = index.model()
        text = str(model.data(index, Qt.DisplayRole))
        rect = fm.boundingRect(option.rect, Qt.TextWordWrap, text)
        return QSize(option.rect.width(), rect.height())


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
        self.danmu_list_view.setWordWrap(True)
        self.danmu_list_view.setItemDelegate(DanmuItemDelegate(self))
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
        elif danmu.msg_type == BilibiliLiveDanmuService.TYPE_GIFT:
            self.danmu_list_model.appendRow([QStandardItem(
                f'{danmu.content.data.uname} {danmu.content.data.action} '
                f'{danmu.content.data.gift_name} x{danmu.content.data.num}'
            )])
        elif danmu.msg_type == BilibiliLiveDanmuService.TYPE_ENTER:
            vip_text = ''
            if danmu.content.data.vip:
                vip_text += '[VIP] '
            if danmu.content.data.svip:
                vip_text += '[SVIP] '
            self.danmu_list_model.appendRow([QStandardItem(
                f'{vip_text}{danmu.content.data.uname} 进入房间'
            )])
        elif danmu.msg_type == BilibiliLiveDanmuService.TYPE_BROADCAST:
            print(danmu.content)
        elif danmu.msg_type == BilibiliLiveDanmuService.TYPE_OTHER:
            if isinstance(danmu.content, str) or isinstance(danmu.content, bytes):
                print(danmu.content)
            else:
                print(danmu.content.cmd)
        self.danmu_list_view.scrollToBottom()

    @asyncClose
    async def closeEvent(self, _):
        await BilibiliLiveDanmuService(self.append_danmu).session.close()

    async def load_danmu(self):
        await BilibiliLiveDanmuService(self.append_danmu).ws_connect(self.roomid)
