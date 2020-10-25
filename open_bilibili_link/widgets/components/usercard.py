import asyncio
from datetime import timezone
from pprint import pprint
from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QSizePolicy, QVBoxLayout, QGridLayout, QLabel, QPushButton, \
    QLineEdit
from asyncqt import asyncSlot

from open_bilibili_link.services import BilibiliLiveService
from open_bilibili_link.widgets.components.areas import AreaSelector
from open_bilibili_link.widgets.components.dialog import LoginPanel
from open_bilibili_link.widgets.components.label import QClickableLabel, KeyframeLabel


class UserCardMain(QFrame):
    login_complete = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_ui()
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def setup_ui(self):
        self.glayout = QGridLayout()
        self.glayout.setHorizontalSpacing(15)
        self.glayout.setVerticalSpacing(20)
        self.glayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.avatar = QLabel()
        self.avatar.setObjectName('label-avatar')
        self.avatar.setFixedSize(70, 70)
        self.glayout.addWidget(self.avatar, 0, 0, Qt.AlignTop)
        rlayout = QVBoxLayout()
        self.label_username = QClickableLabel('LOGIN')
        self.label_username.setObjectName('label-username')
        self.label_bio = QLabel('')
        self.label_bio.setObjectName('label-bio')
        self.label_stat = QLabel('')
        self.label_stat.setObjectName('label-stat')
        self.label_birth = QLabel('')
        self.label_birth.setObjectName('label-birth')
        rlayout.addWidget(self.label_username)
        rlayout.addWidget(self.label_stat)
        rlayout.addWidget(self.label_bio)
        rlayout.addWidget(self.label_birth)
        rlayout.setAlignment(Qt.AlignTop)
        self.glayout.addLayout(rlayout, 0, 1, Qt.AlignTop)
        self.setLayout(self.glayout)
        self.label_username.clicked.connect(self.show_login)
        self.login_complete.connect(self.after_login)

    @asyncSlot()
    async def after_login(self):
        self.parent().show_data()

    def set_user_info(self, userinfo):
        if userinfo.sex == '男':
            sex_icon = '♂️'
        elif userinfo.sex == '女':
            sex_icon = '♀️'
        else:
            sex_icon = '❓️'
        self.label_username.setText(f'{sex_icon}{userinfo.name}  (UID#{userinfo.mid}) Lv{userinfo.level}')
        self.label_bio.setText(userinfo.sign)
        self.label_stat.setText(f'Follow: {userinfo.following} Fans: {userinfo.follower} Coins: {userinfo.coins}')
        self.label_birth.setText(
            f'Birth: {userinfo.birthday.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%Y-%m-%d")}')

    def set_avatar(self, avatar):
        pixmap = QPixmap()
        pixmap.loadFromData(avatar)
        self.avatar.setPixmap(pixmap.scaledToWidth(self.avatar.width(), Qt.SmoothTransformation))

    @asyncSlot()
    async def show_login(self):
        if not BilibiliLiveService().logged_in:
            panel = LoginPanel(self)
            panel.show()


class UserCardLive(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_ui()
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def setup_ui(self):
        self.setStyleSheet('QLabel { color: #ccc; }')
        hlayout = QGridLayout()
        hlayout.setHorizontalSpacing(10)
        hlayout.setAlignment(Qt.AlignTop)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        self.label_keyframe = KeyframeLabel()
        self.label_keyframe.setFixedSize(180, 100)
        self.label_keyframe.hide()
        self.top_label = QLabel('')
        self.top_label.setObjectName('room-info-title')
        self.label_roomid = QLabel('')

        # 直播标题行
        title_row = QHBoxLayout()
        self.label_title = QLabel('')
        self.label_title_content = QLineEdit()
        self.label_title_content.setReadOnly(True)
        self.label_title_edit = QPushButton('修改')
        self.label_title_edit.hide()
        self.label_title_edit.setObjectName('label-title-edit')
        self.label_title_edit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        title_row.addWidget(self.label_title)
        title_row.addWidget(self.label_title_content)
        title_row.addWidget(self.label_title_edit)

        # 直播分区行
        area_row = QHBoxLayout()
        self.label_area = QLabel('')
        self.label_area_content = QLabel('')
        self.label_area_edit = QPushButton('修改')
        self.label_area_edit.setObjectName('label-label-edit')
        self.label_area_edit.hide()
        self.label_area_edit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        area_row.addWidget(self.label_area)
        area_row.addWidget(self.label_area_content)
        area_row.addStretch(1)
        area_row.addWidget(self.label_area_edit)

        self.label_tags = QLabel('')
        self.label_news = QLabel('')
        self.label_desc = QLabel('')
        self.label_roomid.setTextFormat(Qt.RichText)
        self.label_roomid.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.label_roomid.setOpenExternalLinks(True)
        # layout.addWidget(self.label_keyframe)
        # layout.addWidget(self.top_label)
        layout.addWidget(self.label_roomid)
        # layout.addWidget(self.label_title)
        layout.addLayout(title_row)
        layout.addLayout(area_row)
        layout.addWidget(self.label_tags)
        layout.addWidget(self.label_news)
        layout.addWidget(self.label_desc)
        hlayout.addWidget(self.label_keyframe, 0, 0, Qt.AlignTop)
        hlayout.addLayout(layout, 0, 1, Qt.AlignTop)
        self.setLayout(hlayout)
        self.label_title_edit.clicked.connect(self.label_title_edit_clicked)
        self.label_area_edit.clicked.connect(self.label_area_edit_clicked)

    def label_area_edit_clicked(self):
        selector = AreaSelector(self)
        selector.show_data()
        selector.exec()

    @asyncSlot()
    async def label_title_edit_clicked(self):
        if self.label_title_content.isReadOnly():
            self.label_title_edit.setText('保存')
            self.label_title_content.setReadOnly(False)
        else:
            self.label_title_edit.setText('...')
            self.label_title_edit.setEnabled(False)
            await BilibiliLiveService().update_room(title=self.label_title_content.text())
            self.label_title_edit.setText('修改')
            self.label_title_content.setReadOnly(True)
            self.label_title_edit.setEnabled(True)

    async def set_room_info(self, room_info, news):
        self.label_roomid.setText(
            f'房间号: {room_info.room_id} <a href="https://live.bilibili.com/{room_info.room_id}">Go</a>')
        self.label_title_content.setText(f'{room_info.title}')
        self.label_tags.setText(f'个人标签：{room_info.tags}')
        self.label_news.setText(f'直播公告：{news.content}')
        self.label_desc.setText(f'个人简介: {room_info.description}')
        self.label_area_content.setText(f'{room_info.parent_area_name}/{room_info.area_name}')
        pixmap = QPixmap()
        pixmap.loadFromData(await BilibiliLiveService.get_image(room_info.keyframe))
        self.label_keyframe.setPixmap(pixmap.scaled(self.label_keyframe.width(), self.label_keyframe.height(),
                                                    Qt.KeepAspectRatioByExpanding))
        self.label_keyframe.show()
        self.label_keyframe.live_status_text = '直播中' if room_info.live_status else '未开播'
        self.label_keyframe.live_online = room_info.online
        self.label_keyframe.repaint()


class UserCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.background_image: Optional[QPixmap] = None

    def setup_ui(self):
        self.setFixedHeight(280)
        hlayout = QVBoxLayout()
        hlayout.setAlignment(Qt.AlignTop)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.main_card = UserCardMain(self)
        self.right_card = UserCardLive(self)
        layout.addWidget(self.right_card, stretch=3)
        layout.addWidget(self.main_card, stretch=2)
        hlayout.addLayout(layout)
        self.setLayout(hlayout)

    def show_data(self):
        asyncio.gather(self.load_info())

    def paintEvent(self, _):
        if self.background_image:
            painter = QPainter(self)
            self.background_image.scaled(self.width(), self.height(), Qt.KeepAspectRatioByExpanding)
            self.background_image.rect().moveCenter(self.rect().center())
            painter.drawPixmap(self.background_image.rect().topLeft(), self.background_image)

    def set_background(self, data):
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        pixmap = pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatioByExpanding)
        self.background_image = pixmap
        self.repaint()

    async def load_info(self):
        if BilibiliLiveService().logged_in:
            self.main_card.label_username.setText('Loading...')
            self.right_card.label_title.setText('房间标题:')
            self.right_card.label_area.setText('分区信息:   ')
            self.right_card.label_title_edit.show()
            self.right_card.label_area_edit.show()
            user_info = await BilibiliLiveService().get_user_info()
            room = await BilibiliLiveService().get_room_info()
            news = await BilibiliLiveService().get_live_news()
            self.main_card.set_user_info(user_info)
            # self.right_card.set_live_info(await BilibiliLiveService().live_info())
            await self.right_card.set_room_info(room, news)
            self.main_card.set_avatar(await BilibiliLiveService().get_cached_face(user_info))
            self.set_background(await BilibiliLiveService().get_cached_background(room))
