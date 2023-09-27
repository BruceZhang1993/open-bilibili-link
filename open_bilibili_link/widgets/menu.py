from PySide6.QtCore import Qt, QSize, QAbstractItemModel, QItemSelection
from PySide6.QtWidgets import QListView, QWidget, QVBoxLayout, QFrame, QSizePolicy
from qasync import QtGui


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
    def __init__(self, *args, **kwargs):
        self.role = None
        self.target = None
        if 'role' in kwargs.keys():
            self.role = kwargs.pop('role')
        if 'target' in kwargs.keys():
            self.target = kwargs.pop('target')
        super().__init__(*args, **kwargs)
        self._about_to_close = False
        self.setFixedWidth(60)
        # self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def selection_change(self, current: QItemSelection, previous: QItemSelection):
        if self.role == 'down' and current.first().indexes()[0].row() == 0:
            self._about_to_close = True

    def mouseReleaseEvent(self, _):
        if self.target and self._about_to_close:
            self.target.close()

    def setModel(self, model: QAbstractItemModel):
        super().setModel(model)
        self.selectionModel().selectionChanged.connect(self.selection_change)
        self.setFixedHeight(50 * self.model().rowCount())
