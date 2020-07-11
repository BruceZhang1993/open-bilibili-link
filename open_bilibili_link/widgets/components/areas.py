import asyncio
from pathlib import Path
from typing import List

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QFrame, QGridLayout, QSizePolicy

from open_bilibili_link.services import BilibiliLiveService
from open_bilibili_link.widgets.components.label import QClickableLabel


class AreaSelector(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_ui()

    def setup_ui(self):
        # load qss
        with open(Path(__file__).parent.parent / 'styles' / 'material.qss', 'r') as f:
            self.setStyleSheet(f.read())
        self.setFixedWidth(600)
        self.setFixedHeight(360)
        main_layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        self.cate_tabs: List[QFrame] = []
        self.areas_list: List[dict] = []
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

    def show_data(self):
        asyncio.gather(self.load_info())

    async def load_info(self):
        if BilibiliLiveService().logged_in:
            area_data = await BilibiliLiveService().get_live_areas()
            for category in area_data:
                self.cate_tabs.append(QFrame())
                self.tab_widget.addTab(self.cate_tabs[-1], category.name)
                self.init_tab(self.cate_tabs[-1], category.list)

    def init_tab(self, tab, areas):
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        for i, area in enumerate(areas):
            area_label = QClickableLabel(area.name)
            area_label.setMinimumWidth(100)
            area_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            layout.addWidget(area_label, i // 6, i % 6)
        tab.setLayout(layout)
