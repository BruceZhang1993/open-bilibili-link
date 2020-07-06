import asyncio
from pprint import pprint

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QShowEvent, QPixmap, QPalette, QBrush
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QSizePolicy, QVBoxLayout, QGridLayout, QLabel, QPushButton, \
    QPlainTextEdit, QLineEdit
from asyncqt import asyncSlot

from open_bilibili_link.services import BilibiliLiveService


class UserCardMain(QFrame):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def setup_ui(self):
        self.glayout = QGridLayout()
        self.glayout.setAlignment(Qt.AlignTop)
        self.avatar = QLabel()
        self.avatar.setMaximumSize(70, 70)
        self.glayout.addWidget(self.avatar, 0, 0)
        rlayout = QVBoxLayout()
        self.label_username = QLabel('Login')
        self.label_username.setObjectName('label-username')
        self.label_bio = QLabel('')
        self.label_bio.setObjectName('label-bio')
        self.label_stat = QLabel('')
        self.label_stat.setObjectName('label-stat')
        rlayout.addWidget(self.label_username)
        rlayout.addWidget(self.label_stat)
        rlayout.addWidget(self.label_bio)
        self.glayout.addLayout(rlayout, 0, 1)
        self.setLayout(self.glayout)

    def set_user_info(self, userinfo):
        print(userinfo)
        if userinfo.sex == '男':
            sex_icon = '♂️'
        elif userinfo.sex == '女':
            sex_icon = '♀️'
        else:
            sex_icon = '❓️'
        self.label_username.setText(f'{sex_icon}{userinfo.name}  (UID#{userinfo.mid}) Lv{userinfo.level}')
        self.label_bio.setText(userinfo.sign)
        self.label_stat.setText(f'Follow: {userinfo.following} Fans: {userinfo.follower} Coins: {userinfo.coins}')

    def set_avatar(self, avatar):
        pixmap = QPixmap()
        pixmap.loadFromData(avatar)
        self.avatar.setPixmap(pixmap.scaledToWidth(self.avatar.width(), Qt.SmoothTransformation))


class UserCardLive(QFrame):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def setup_ui(self):
        self.setStyleSheet('QLabel { color: #ccc; }')
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        self.top_label = QLabel('')
        self.top_label.setObjectName('room-info-title')
        self.label_roomid = QLabel('')
        title_row = QHBoxLayout()
        self.label_title = QLabel('房间标题:')
        self.label_title_content = QLineEdit()
        self.label_title_content.setReadOnly(True)
        self.label_title_edit = QPushButton('修改')
        self.label_title_edit.setObjectName('label-title-edit')
        self.label_title_edit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        title_row.addWidget(self.label_title)
        title_row.addWidget(self.label_title_content)
        title_row.addWidget(self.label_title_edit)
        self.label_area = QLabel('')
        self.label_desc = QLabel('')
        self.label_roomid.setTextFormat(Qt.RichText)
        self.label_roomid.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.label_roomid.setOpenExternalLinks(True)
        layout.addWidget(self.top_label)
        layout.addWidget(self.label_roomid)
        # layout.addWidget(self.label_title)
        layout.addLayout(title_row)
        layout.addWidget(self.label_area)
        layout.addWidget(self.label_desc)
        self.setLayout(layout)
        self.label_title_edit.clicked.connect(self.label_title_edit_clicked)

    @asyncSlot()
    async def label_title_edit_clicked(self):
        if self.label_title_content.isReadOnly():
            self.label_title_edit.setText('保存')
            self.label_title_content.setReadOnly(False)
        else:
            self.label_title_edit.setText('...')
            self.label_title_edit.setEnabled(False)
            print(await BilibiliLiveService().update_live_heading(title=self.label_title_content.text()))
            self.label_title_edit.setText('修改')
            self.label_title_content.setReadOnly(True)
            self.label_title_edit.setEnabled(True)

    def set_room_info(self, room_info):
        pprint(room_info)
        self.top_label.setText('直播中' if room_info.live_status else '未开播')
        self.label_roomid.setText(f'房间号: {room_info.room_id} <a href="https://live.bilibili.com/{room_info.room_id}">Go</a>')
        self.label_title_content.setText(f'{room_info.title}')
        self.label_desc.setText(f'个人简介: {room_info.description}')
        self.label_area.setText(f'直播分区: {room_info.parent_area_name}/{room_info.area_name}')


class UserCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setFixedHeight(400)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.main_card = UserCardMain()
        self.right_card = UserCardLive()
        layout.addWidget(self.main_card, stretch=3)
        layout.addWidget(self.right_card, stretch=2)
        self.setLayout(layout)

    def show_data(self):
        asyncio.gather(self.load_info())

    def set_background(self, path):
        self.setStyleSheet(f'UserCard {{ border-image: url({path}) 0 0 0 0 stretch stretch; }}')

    async def load_info(self):
        if BilibiliLiveService().logged_in:
            user_info = await BilibiliLiveService().get_user_info()
            room = await BilibiliLiveService().get_room_info()
            self.main_card.set_user_info(user_info)
            # self.right_card.set_live_info(await BilibiliLiveService().live_info())
            self.right_card.set_room_info(room)
            self.main_card.set_avatar(await BilibiliLiveService().get_cached_face(user_info))
            self.set_background(await BilibiliLiveService().get_cached_background(room))
