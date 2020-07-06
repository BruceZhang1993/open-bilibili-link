from PyQt5.QtCore import Qt, QSize, QAbstractItemModel
from PyQt5.QtWidgets import QListView, QWidget, QVBoxLayout, QFrame, QSizePolicy
from asyncqt import QtGui


class MenuFrame(QFrame):
    moving = False
    mouse_position = None

    def __init__(self, window: QWidget = None):
        super().__init__()
        self._window = window

    @property
    def parent_window(self):
        return self._window

    def mousePressEvent(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.moving = True
            self.mouse_position = e.pos()

    def mouseMoveEvent(self, e: QtGui.QMouseEvent):
        if e.buttons() == Qt.LeftButton and self.moving:
            self.parent_window.move(self.parent_window.pos() + (e.pos() - self.mouse_position))

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.moving = False
            self.mouse_position = None


class MenuView(QListView):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(60)
        # self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def setModel(self, model: QAbstractItemModel):
        super().setModel(model)
        self.setFixedHeight(50 * self.model().rowCount())
