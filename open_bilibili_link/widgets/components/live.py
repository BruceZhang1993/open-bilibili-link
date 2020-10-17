import asyncio

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QGridLayout, QLabel, QLineEdit, QPushButton, QApplication
from asyncqt import asyncSlot

from open_bilibili_link.config import ConfigManager
from open_bilibili_link.logger import LogManager
from open_bilibili_link.services import BilibiliLiveService, BilibiliServiceException, BilibiliLiveDanmuService
from open_bilibili_link.utils import create_obs_configuration, check_exists, run_command
from open_bilibili_link.widgets.components.button import CopyButton
from open_bilibili_link.widgets.components.danmu import DanmuWidget, DanmuPusher
from open_bilibili_link.widgets.components.toast import Toast


class LiveControlCenter(QFrame):
    def __init__(self, *args, **kwargs):
        self.homepage = None
        self.roomid = 0
        if 'homepage' in kwargs.keys():
            self.homepage = kwargs.pop('homepage')
        super().__init__(*args, **kwargs)
        self.setup_ui()
        self.danmu_pusher = None

    def setup_ui(self):
        layout = QGridLayout()
        label_live_rtmp = QLabel('RTMP地址')
        label_live_code = QLabel('直播码')
        self.live_rtmp = QLineEdit()
        self.live_rtmp.setReadOnly(True)
        self.live_code = QLineEdit()
        self.live_code.setReadOnly(True)
        self.live_code.setEchoMode(QLineEdit.Password)
        self.live_rtmp_copy = CopyButton('复制', target=self.live_rtmp)
        self.live_code_copy = CopyButton('复制', target=self.live_code)
        self.live_code_show = QPushButton('展示')
        layout.addWidget(label_live_rtmp, 0, 0)
        layout.addWidget(self.live_rtmp, 0, 1)
        layout.addWidget(self.live_rtmp_copy, 0, 2, 1, 2)
        layout.addWidget(label_live_code, 1, 0)
        layout.addWidget(self.live_code, 1, 1)
        layout.addWidget(self.live_code_copy, 1, 2)
        layout.addWidget(self.live_code_show, 1, 3)
        button_layout = QGridLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        self.refresh_live_code = QPushButton('刷新直播码')
        self.toggle_live_button = QPushButton('开启直播')
        self.update_obs_config = QPushButton('更新 OBS 配置')
        self.start_obs_studio = QPushButton('启动 OBS')
        self.sign_in_btn = QPushButton('签到')
        self.sign_in_btn.setCheckable(True)
        test_danmu = QPushButton('弹幕视图')
        test_danmu_txt = QPushButton('开启弹幕输出')
        plugin_page_btn = QPushButton('我的插件')
        self.toggle_live_button.setCheckable(True)
        test_danmu_txt.setCheckable(True)
        button_layout.addWidget(self.refresh_live_code, 0, 0)
        button_layout.addWidget(self.toggle_live_button, 0, 1)
        button_layout.addWidget(self.update_obs_config, 0, 2)
        button_layout.addWidget(self.start_obs_studio, 0, 3)
        button_layout.addWidget(self.sign_in_btn, 0, 4)
        button_layout.addWidget(test_danmu, 1, 0)
        button_layout.addWidget(test_danmu_txt, 1, 1)
        button_layout.addWidget(plugin_page_btn, 1, 2)
        button_frame = QFrame()
        button_frame.setLayout(button_layout)
        layout.addWidget(button_frame, 2, 0, 3, 0)
        self.setLayout(layout)
        self.refresh_live_code.clicked.connect(self.refresh_code)
        self.toggle_live_button.clicked.connect(self.toggle_live)
        self.update_obs_config.clicked.connect(self.update_obs)
        self.start_obs_studio.clicked.connect(self.start_obs_profile)
        self.live_code_show.clicked.connect(self.toggle_code_show)
        self.sign_in_btn.clicked.connect(self.sign_in)
        test_danmu.clicked.connect(self.launch_danmu)
        test_danmu_txt.clicked.connect(self.launch_danmu_txt)
        plugin_page_btn.clicked.connect(self.go_plugin_page)

    def go_plugin_page(self, _):
        self.homepage.context.goto('obl://plugin')

    def launch_danmu_txt(self):
        if self.danmu_pusher is None:
            self.danmu_pusher = DanmuPusher(self.roomid)
            clipboard = QApplication.clipboard()
            clipboard.setText(self.danmu_pusher.target.as_posix())
            Toast.toast(self, '已复制文件路径，可作为 OBS 文本源')
            BilibiliLiveDanmuService().register_callback(self.danmu_pusher.append_danmu, external=False)
            asyncio.gather(BilibiliLiveDanmuService().ws_connect(self.roomid))
        else:
            BilibiliLiveDanmuService().unregister_callback(self.danmu_pusher.append_danmu)
            self.danmu_pusher.close()
            self.danmu_pusher = None

    def launch_danmu(self):
        danmu_w = DanmuWidget(roomid=self.roomid)
        danmu_w.show_data()
        danmu_w.show()

    def toggle_code_show(self, _):
        if self.live_code.echoMode() == QLineEdit.Password:
            self.live_code_show.setText('隐藏')
            self.live_code.setEchoMode(QLineEdit.Normal)
        else:
            self.live_code_show.setText('展示')
            self.live_code.setEchoMode(QLineEdit.Password)

    @asyncSlot()
    async def sign_in(self):
        if not self.sign_in_btn.isChecked():
            self.sign_in_btn.setChecked(True)
            Toast.toast(self, '今日已签到')
            return
        try:
            data = await BilibiliLiveService().checkin()
            Toast.toast(self, data.text)
            await self.load_info()
        except BilibiliServiceException as err:
            Toast.toast(self, f'[{err.args[1]}] {err.args[0]}')

    @asyncSlot()
    async def start_obs_profile(self):
        _, exists = await check_exists('obs')
        if not exists:
            Toast.toast(self, '未安装 OBS Studio')
        _, __, code = await run_command('obs', '--profile', 'BilibiliLive')
        LogManager.instance().debug(f'[Shell] OBS 命令执行完成（进程结束 exitcode: {code}）')

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
            self.roomid = await BilibiliLiveService().roomid
            self.set_live_code(await BilibiliLiveService().get_live_code())
            self.toggle_live_button.setText('关闭直播' if live_status else '开启直播')
            self.toggle_live_button.setChecked(live_status)
            check_info = await BilibiliLiveService().check_info()
            self.sign_in_btn.setText('已签到' if check_info.status else '签到')
            self.sign_in_btn.setChecked(check_info.status)
            auto_sign = ConfigManager().get('live', 'autosign')
            if auto_sign and not check_info.status:
                self.sign_in_btn.click()
