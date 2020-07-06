import asyncio
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtSvg import QSvgRenderer, QSvgWidget
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QDialog, QSizePolicy
from asyncqt import asyncSlot, asyncClose

from open_bilibili_link.services import BilibiliLiveService, BilibiliServiceException
from open_bilibili_link.widgets.components.label import QClickableLabel
from open_bilibili_link.widgets.components.toast import Toast


class LoginPanel(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(280, 400)
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        # Login icon
        header = QSvgWidget((Path(__file__).parent.parent / 'images'/ 'bilibili.svg').as_posix())
        header.renderer().setAspectRatioMode(Qt.KeepAspectRatio)
        header.setFixedHeight(90)
        header.setObjectName('login-header')
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.commit = QClickableLabel('LOGIN')
        self.commit.setObjectName('login-commit')
        header.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.username.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.password.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.commit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        header.setFixedWidth(180)
        self.username.setFixedWidth(180)
        self.password.setFixedWidth(180)
        self.commit.setFixedWidth(180)
        # header.setAlignment(Qt.AlignCenter)
        self.username.setAlignment(Qt.AlignCenter)
        self.password.setAlignment(Qt.AlignCenter)
        self.commit.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addStretch(1)
        main_layout.addWidget(header, Qt.AlignCenter)
        main_layout.addWidget(self.username, Qt.AlignCenter)
        main_layout.addWidget(self.password, Qt.AlignCenter)
        main_layout.addWidget(self.commit, Qt.AlignCenter)
        main_layout.addStretch(2)
        self.setLayout(main_layout)
        self.username.textChanged.connect(self.text_changed)
        self.password.textChanged.connect(self.text_changed)
        self.commit.clicked.connect(self.proceed_login)

    @asyncSlot()
    async def proceed_login(self):
        if not BilibiliLiveService().logged_in:
            username = self.username.text().strip()
            password = self.password.text().strip()
            try:
                await BilibiliLiveService().login(username, password)
                self.parent().login_complete.emit()
                self.close()
            except BilibiliServiceException as err:
                msg, code = err.args
                Toast.toast(self, f'[{code}] {msg}')

    def text_changed(self):
        if self.username.text() != '' and self.password.text() != '':
            self.commit.setStyleSheet('#login-commit { color: rgba(120, 209, 205, 1); }')
        else:
            self.commit.setStyleSheet('#login-commit { color: rgba(120, 209, 205, .5); }')
