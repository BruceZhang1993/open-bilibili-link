import asyncio
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QDialog, QSizePolicy, QTextEdit
from qasync import asyncSlot, asyncClose

from open_bilibili_link.services import BilibiliLiveService, BilibiliServiceException
from open_bilibili_link.utils import save_cookie
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
        # Login switcher
        self.login_switcher = QClickableLabel('切换 Cookie 登录 >>')
        # Login icon
        header = QSvgWidget((Path(__file__).parent.parent / 'images'/ 'bilibili.svg').as_posix())
        header.renderer().setAspectRatioMode(Qt.KeepAspectRatio)
        header.setFixedHeight(80)
        header.setObjectName('login-header')
        self.username = QLineEdit()
        self.username.setPlaceholderText('Mobile/Email')
        self.password = QLineEdit()
        self.password.setPlaceholderText('Password')
        self.password.setEchoMode(QLineEdit.Password)
        self.cookie_box = QTextEdit()
        self.cookie_box.setPlaceholderText('Cookie')
        self.commit = QClickableLabel('LOGIN')
        self.commit.setObjectName('login-commit')
        header.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.username.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.password.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.commit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.cookie_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        header.setFixedWidth(180)
        self.username.setFixedWidth(180)
        self.password.setFixedWidth(180)
        self.commit.setFixedWidth(180)
        self.cookie_box.setFixedWidth(180)
        self.cookie_box.setFixedHeight(120)
        # header.setAlignment(Qt.AlignCenter)
        self.username.setAlignment(Qt.AlignCenter)
        self.password.setAlignment(Qt.AlignCenter)
        self.commit.setAlignment(Qt.AlignCenter)
        self.cookie_box.setAlignment(Qt.AlignLeft)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.login_switcher, Qt.AlignLeft)
        main_layout.addStretch(1)
        main_layout.addWidget(header, Qt.AlignCenter)
        main_layout.addWidget(self.username, Qt.AlignCenter)
        main_layout.addWidget(self.password, Qt.AlignCenter)
        main_layout.addWidget(self.cookie_box, Qt.AlignCenter)
        main_layout.addWidget(self.commit, Qt.AlignCenter)
        main_layout.addStretch(2)
        self.setLayout(main_layout)
        self.cookie_box.hide()
        self.username.textChanged.connect(self.text_changed)
        self.password.textChanged.connect(self.text_changed)
        self.commit.clicked.connect(self.proceed_login)
        self.login_switcher.clicked.connect(self.switch_login_type)

    def switch_login_type(self):
        if self.username.isVisible():
            self.username.hide()
            self.password.hide()
            self.cookie_box.show()
            self.login_switcher.setText('切换用户名密码登录 >>')
        else:
            self.username.show()
            self.password.show()
            self.cookie_box.hide()
            self.login_switcher.setText('切换 Cookie 登录 >>')

    @asyncSlot()
    async def proceed_login(self):
        if not BilibiliLiveService().logged_in:
            username = self.username.text().strip()
            password = self.password.text().strip()
            cookie = self.cookie_box.toPlainText().strip()
            if cookie == '' and (username == '' or password == ''):
                Toast.toast(self, '请输入帐号信息')
                return
            try:
                if cookie != '':
                    save_cookie(cookie, BilibiliLiveService.COOKIE_FILE, '.live.bilibili.com')
                else:
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
