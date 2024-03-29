from pathlib import Path

from PySide6.QtCore import QItemSelection, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QFrame, QHBoxLayout, QListView, QSizePolicy, QApplication
from qasync import asyncClose

from open_bilibili_link.services import BilibiliLiveService, BilibiliLiveDanmuService
from open_bilibili_link.widgets.menu import MenuView, MenuFrame
from open_bilibili_link.widgets.routes import RouteManager
from open_bilibili_link.plugin import PluginManager


class AppMainWindow(QMainWindow):
    DEFAULT_HOME = 'obl://home'

    def __init__(self, app: QApplication, args):
        super().__init__()
        self.app = app
        self.args = args
        self.content_area = None
        self.h_layout = None
        self.menu_area: QListView
        self.menu_model: QStandardItemModel
        self.pages = {}
        self.setup_ui()
        PluginManager().register_plugins()

    @asyncClose
    async def closeEvent(self, event):
        if BilibiliLiveDanmuService().session and not BilibiliLiveDanmuService().session.closed:
            await BilibiliLiveDanmuService().session.close()
        if BilibiliLiveService().session and not BilibiliLiveService().session.closed:
            await BilibiliLiveService().session.close()

    def setup_ui(self):
        # load qss
        with open(Path(__file__).parent / 'styles' / 'material.qss', 'r') as f:
            self.setStyleSheet(f.read())
        self.app.setApplicationName('Open Bilibili Link')
        self.app.setApplicationDisplayName('Open Bilibili Link')
        self.setWindowTitle('Open Bilibili Link')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(900, 600)

        central = QFrame()
        self.h_layout = QHBoxLayout()
        menu_layout = QVBoxLayout()
        menu_frame = MenuFrame(window=self)
        menu_frame.setLayout(menu_layout)
        self.menu_area = MenuView(self)
        # self.menu_model = QStringListModel()
        self.down_menu = MenuView(self, role='down', target=self)
        self.menu_model = QStandardItemModel()
        self.menu_strings = ['home', 'plugin', 'setting']
        icon_base = Path(__file__).parent / 'images'
        self.menu_icons = list(map(lambda s: QIcon((icon_base / f'{s}.svg').as_posix()), self.menu_strings))
        self.menu_model.appendColumn(list(map(lambda s: QStandardItem(s, ''), self.menu_icons)))
        self.down_menu_strings = ['exit']
        self.down_menu_icons = [QIcon((icon_base / 'exit.svg').as_posix())]
        self.down_menu_model = QStandardItemModel()
        self.down_menu_model.appendColumn(list(map(lambda s: QStandardItem(s, ''), self.down_menu_icons)))
        self.down_menu.setModel(self.down_menu_model)
        self.menu_area.setModel(self.menu_model)
        self.menu_area.selectionModel().selectionChanged.connect(self.switch_page) # noqa
        self.down_menu.selectionModel().selectionChanged.connect(self.action_trigger) # noqa
        self.menu_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.menu_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.down_menu.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.down_menu.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        menu_layout.addWidget(self.menu_area)
        spacer = MenuFrame(window=self)
        spacer.setFixedWidth(60)
        spacer.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        menu_layout.addWidget(spacer)
        menu_layout.addWidget(self.down_menu)
        menu_frame.setFixedWidth(60)
        self.h_layout.addWidget(menu_frame)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setContentsMargins(0, 0, 0, 0)

        if self.args.uri:
            self.goto(self.args.uri)
        else:
            self.goto('obl://home')
        central.setLayout(self.h_layout)
        self.setCentralWidget(central)

    def action_trigger(self, current: QItemSelection, previous: QItemSelection):
        pass

    def switch_page(self, current: QItemSelection, previous: QItemSelection):
        try:
            self.goto(f'obl://{self.menu_strings[current.first().indexes()[0].row()]}')
        except IndexError:
            print('index error')

    def goto(self, uri):
        cls = RouteManager.parse_uri(uri)
        if not isinstance(self.content_area, cls):
            if self.content_area:
                self.content_area.setParent(None)
            if uri not in self.pages.keys():
                self.pages[uri] = cls(context=self)
            self.content_area = self.pages[uri]
            self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.h_layout.addWidget(self.content_area)
            menu = RouteManager.get_uri_menu(uri)
            if menu and menu in self.menu_strings:
                index = self.menu_strings.index(menu)
                self.menu_area.setCurrentIndex(self.menu_model.index(index, 0))
