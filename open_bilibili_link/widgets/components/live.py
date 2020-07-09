import asyncio

from PyQt5.QtWidgets import QFrame, QGridLayout, QLabel, QLineEdit, QPushButton
from asyncqt import asyncSlot

from open_bilibili_link.services import BilibiliLiveService
from open_bilibili_link.utils import create_obs_configuration, check_exists, run_command
from open_bilibili_link.widgets.components.button import CopyButton
from open_bilibili_link.widgets.components.toast import Toast


class LiveControlCenter(QFrame):
    def __init__(self, *args, **kwargs):
        self.homepage = None
        if 'homepage' in kwargs.keys():
            self.homepage = kwargs.pop('homepage')
        super().__init__(*args, **kwargs)
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout()
        label_live_rtmp = QLabel('RTMP地址')
        label_live_code = QLabel('直播码')
        self.live_rtmp = QLineEdit()
        self.live_rtmp.setReadOnly(True)
        self.live_code = QLineEdit()
        self.live_code.setReadOnly(True)
        self.live_rtmp_copy = CopyButton('复制', target=self.live_rtmp)
        self.live_code_copy = CopyButton('复制', target=self.live_code)
        layout.addWidget(label_live_rtmp, 0, 0)
        layout.addWidget(self.live_rtmp, 0, 1)
        layout.addWidget(self.live_rtmp_copy, 0, 2)
        layout.addWidget(label_live_code, 1, 0)
        layout.addWidget(self.live_code, 1, 1)
        layout.addWidget(self.live_code_copy, 1, 2)
        button_layout = QGridLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        self.refresh_live_code = QPushButton('刷新直播码')
        self.toggle_live_button = QPushButton('开启直播')
        self.update_obs_config = QPushButton('更新 OBS 配置')
        self.start_obs_studio = QPushButton('启动 OBS 配置')
        self.toggle_live_button.setCheckable(True)
        button_layout.addWidget(self.refresh_live_code, 0, 0)
        button_layout.addWidget(self.toggle_live_button, 0, 1)
        button_layout.addWidget(self.update_obs_config, 0, 2)
        button_layout.addWidget(self.start_obs_studio, 0, 3)
        button_frame = QFrame()
        button_frame.setLayout(button_layout)
        layout.addWidget(button_frame, 2, 0, 3, 0)
        self.setLayout(layout)
        self.refresh_live_code.clicked.connect(self.refresh_code)
        self.toggle_live_button.clicked.connect(self.toggle_live)
        self.update_obs_config.clicked.connect(self.update_obs)
        self.start_obs_studio.clicked.connect(self.start_obs_profile)

    @asyncSlot()
    async def start_obs_profile(self):
        _, exists = await check_exists('obs')
        if not exists:
            Toast.toast(self, '未安装 OBS Studio')
        await run_command('obs', '--profile', 'BilibiliLive')
        print('obs end')

    def update_obs(self):
        create_obs_configuration(self.live_rtmp.text().strip(), self.live_code.text().strip())
        Toast.toast(self, '配置已更新')

    @asyncSlot()
    async def toggle_live(self):
        status = await BilibiliLiveService().live_status
        if status:
            await BilibiliLiveService().stop_live()
        else:
            await BilibiliLiveService().start_live()
        BilibiliLiveService().live_status = None
        await self.homepage.usercard.load_info()
        await self.load_info()

    @asyncSlot()
    async def refresh_code(self):
        if BilibiliLiveService().logged_in:
            self.set_live_code(await BilibiliLiveService().get_live_code())

    def set_live_code(self, live_code):
        if live_code.rtmp:
            self.live_rtmp.setText(live_code.rtmp.addr)
            self.live_code.setText(live_code.rtmp.code)

    def show_data(self):
        asyncio.gather(self.load_info())

    async def load_info(self):
        if BilibiliLiveService().logged_in:
            live_status = await BilibiliLiveService().live_status
            self.set_live_code(await BilibiliLiveService().get_live_code())
            self.toggle_live_button.setText('关闭直播' if live_status else '开启直播')
            self.toggle_live_button.setChecked(live_status)
