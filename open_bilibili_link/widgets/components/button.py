import asyncio
from typing import Optional

from PyQt5.QtWidgets import QPushButton, QLineEdit, QApplication
from asyncqt import asyncSlot

from open_bilibili_link.widgets.components.toast import Toast


class CopyButton(QPushButton):
    target: Optional[QLineEdit]

    def __init__(self, *args, **kwargs):
        self.target = None
        if 'target' in kwargs:
            self.target = kwargs.pop('target')
        super().__init__(*args, **kwargs)
        self.clicked.connect(self.btn_clicked)

    @asyncSlot()
    async def btn_clicked(self):
        if self.target is not None and self.target.text().strip() != '':
            clipboard = QApplication.clipboard()
            clipboard.setText(self.target.text().strip())
            # self.setText('已复制')
            Toast.toast(self.parent(), '已复制')
