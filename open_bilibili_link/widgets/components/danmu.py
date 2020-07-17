import asyncio
from pathlib import Path
from typing import Optional

from PyQt5.QtCore import Qt, QSize, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFontMetrics
from PyQt5.QtWidgets import QDockWidget, QVBoxLayout, QListView, QScrollArea, QStyledItemDelegate, QStyleOptionViewItem, \
    QFrame, QLineEdit
from asyncqt import asyncClose, asyncSlot

from open_bilibili_link.models import DanmuData
from open_bilibili_link.services import BilibiliLiveDanmuService, BilibiliLiveService
from open_bilibili_link.widgets.components.toast import Toast


class DanmuParser:
    @staticmethod
    def parse(danmu: DanmuData) -> Optional[str]:
        print('[WS] Received', danmu.msg_type)
        if danmu.msg_type == BilibiliLiveDanmuService.TYPE_DANMUKU:
            return f'{danmu.name}: {danmu.content}'
        elif danmu.msg_type == BilibiliLiveDanmuService.TYPE_GIFT:
            return f'{danmu.content.data.uname} {danmu.content.data.action} {danmu.content.data.gift_name} ' \
                   f'x{danmu.content.data.num}'
        elif danmu.msg_type == BilibiliLiveDanmuService.TYPE_ENTER:
            vip_text = ''
            if danmu.content.data.vip:
                vip_text += '[VIP] '
            if danmu.content.data.svip:
                vip_text += '[SVIP] '
            return f'{vip_text}{danmu.content.data.uname} 进入房间'
        elif danmu.msg_type == BilibiliLiveDanmuService.TYPE_BROADCAST:
            print('[WS] Received broadcast', danmu.content)
        elif danmu.msg_type == BilibiliLiveDanmuService.TYPE_OTHER:
            if isinstance(danmu.content, str) or isinstance(danmu.content, bytes):
                print('[WS] Received data', danmu.content)
            else:
                print('[WS] Received cmd', danmu.content.cmd)
        return None


class DanmuPusher:
    CACHE_DIR = Path.home() / '.cache/OBL'

    def __init__(self, roomid):
        self.roomid = roomid
        if not self.CACHE_DIR.exists():
            self.CACHE_DIR.mkdir(parents=True)
        self.target = self.CACHE_DIR / f'{roomid}.txt'
        self.target.unlink(missing_ok=True)
        self.file = self.target.open('a')

    def append_danmu(self, danmu: DanmuData):
        text = DanmuParser.parse(danmu)
        if text is not None:
            self.file.write(text + '\n')
            self.file.flush()

    def close(self):
        self.file.flush()
        self.file.close()


class DanmuItemDelegate(QStyledItemDelegate):
    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        fm = QFontMetrics(option.font)
        model = index.model()
        text = str(model.data(index, Qt.DisplayRole))
        rect = fm.boundingRect(option.rect, Qt.TextWordWrap, text)
        return QSize(option.rect.width(), rect.height() + 6)


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
        main = QFrame()
        main.setContentsMargins(0, 0, 0, 0)
        self.danmu_send = QLineEdit()
        self.danmu_send.setPlaceholderText('发送弹幕')
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main.setLayout(main_layout)
        area = QScrollArea()
        area.setContentsMargins(0, 0, 0, 0)
        area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.danmu_list_view = QListView()
        self.danmu_list_view.setContentsMargins(0, 0, 0, 0)
        self.danmu_list_view.setWordWrap(True)
        self.danmu_list_view.setItemDelegate(DanmuItemDelegate(self))
        self.danmu_list_view.setStyleSheet('QListView { background: skyblue; font-size: 13px; }')
        self.danmu_list_model = QStandardItemModel()
        self.danmu_list_view.setModel(self.danmu_list_model)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.danmu_list_view)
        area.setLayout(layout)
        self.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(area)
        main_layout.addWidget(self.danmu_send)
        self.setWidget(main)
        self.danmu_send.returnPressed.connect(self.send_danmu_text)

    @asyncSlot()
    async def send_danmu_text(self):
        if self.danmu_send.text().strip() == '':
            return
        if not BilibiliLiveService().logged_in:
            Toast.toast(self, '用户未登录')
            return
        await BilibiliLiveService().send_danmu(self.roomid, self.danmu_send.text().strip())
        self.danmu_send.setText('')

    def show_data(self):
        if self.roomid is not None:
            asyncio.gather(self.load_history())
            self.load_danmu()

    def append_danmu(self, danmu: DanmuData):
        text = DanmuParser.parse(danmu)
        if text is not None:
            self.danmu_list_model.appendRow([QStandardItem(text)])
            self.danmu_list_view.scrollToBottom()

    def closeEvent(self, _):
        BilibiliLiveDanmuService().unregister_callback(self.append_danmu)

    async def load_history(self):
        danmus = await BilibiliLiveService().get_danmu_history(self.roomid)
        for danmu in danmus:
            self.danmu_list_model.appendRow([QStandardItem(f'{danmu.nickname}: {danmu.text}')])
            self.danmu_list_view.scrollToBottom()

    def load_danmu(self):
        BilibiliLiveDanmuService().register_callback(self.append_danmu, external=False)
        asyncio.gather(BilibiliLiveDanmuService().ws_connect(self.roomid))
