import asyncio

from open_bilibili_link.models import DanmuData
from open_bilibili_link.services import BilibiliLiveService, BilibiliServiceException, BilibiliLiveDanmuService
from open_bilibili_link.utils import run_command, timed_input, save_cookie
from open_bilibili_link.widgets.components.danmu import DanmuPusher, DanmuParser


class CliApp(object):
    def __init__(self, args):
        self.args = args

    async def login(self, *, login_type: str = 'account'):
        f = getattr(self, login_type + '_login')
        if f is None:
            self.error(f'未定义的登录方式 {login_type} 可选值 [account,cookie]')
            return
        await f()

    async def cookie_login(self):
        if BilibiliLiveService().logged_in:
            self.error('当前已登录')
            await BilibiliLiveService().session.close()
            return
        cookie = await timed_input('Cookie:\n')
        save_cookie(cookie, BilibiliLiveService.COOKIE_FILE, '.live.bilibili.com')
        self.success('Cookie 登录成功')

    async def account_login(self):
        if BilibiliLiveService().logged_in:
            self.error('当前已登录')
            await BilibiliLiveService().session.close()
            return
        try:
            username = await timed_input('用户名: ')
            password = await timed_input('  密码: ')
            self.info(await BilibiliLiveService().login(username, password))
        except BilibiliServiceException as e:
            self.error(f'[{e.args[0]}] 登录失败，请尝试使用 Cookie 登录 [--login_type=cookie]')

    def logout(self):
        if BilibiliLiveService().logged_in:
            BilibiliLiveService().TOKEN_FILE.unlink(missing_ok=True)
            BilibiliLiveService().COOKIE_FILE.unlink(missing_ok=True)
            self.success('已退出登录')

    async def checkin(self):
        if not BilibiliLiveService().logged_in:
            self.error('当前未登录')
            await BilibiliLiveService().session.close()
            return
        try:
            data = await BilibiliLiveService().checkin()
            self.success(f'{data.text} {data.special_text}')
        except BilibiliServiceException as e:
            self.error(f'[{e.args[1]}] {e.args[0]}')

    def _danmu(self, danmu: DanmuData):
        text = DanmuParser.parse(danmu)
        if text is not None:
            self.info(text)

    def _danmu_off(self, _, __):
        self.info('正在关闭弹幕连接请耐心等待...')
        BilibiliLiveDanmuService().unregister_callback(self._danmu)

    async def danmu(self, roomid: int = 0, *, output: str = 'stdout'):
        if output not in ['stdout', 'file']:
            self.error('未知输出目标 output 取值必须为 stdout,file')
            return
        if roomid == 0:
            roomid = await BilibiliLiveService().roomid
        room_data = await BilibiliLiveDanmuService().room_init(roomid)
        roomid = room_data.room_id
        import signal
        signal.signal(signal.SIGINT, self._danmu_off)
        if output == 'stdout':
            BilibiliLiveDanmuService().register_callback(self._danmu, external=False)
        elif output == 'file':
            danmu_pusher = DanmuPusher(roomid)
            self._danmu = danmu_pusher.append_danmu # noqa
            BilibiliLiveDanmuService().register_callback(self._danmu, external=False)
        danmus = await BilibiliLiveService().get_danmu_history(roomid)
        for danmu in danmus:
            if output == 'stdout':
                self.write_line(f'{danmu.nickname}: {danmu.text}')
            elif output == 'file':
                danmu_pusher.file.write(f'{danmu.nickname}: {danmu.text}\n')
                danmu_pusher.file.flush()
        await BilibiliLiveDanmuService().ws_connect(roomid)

    def __del__(self):
        loop = asyncio.get_event_loop()
        if BilibiliLiveService().session and not BilibiliLiveService().session.closed:
            loop.run_until_complete(BilibiliLiveService().session.close())
        if BilibiliLiveDanmuService().session and not BilibiliLiveDanmuService().session.closed:
            loop.run_until_complete(BilibiliLiveDanmuService().session.close())

    @classmethod
    def info(cls, message):
        cls.write_line(message, prefix='[!]')

    @classmethod
    def success(cls, message):
        cls.write_line(message, prefix='[✔️️]')

    @classmethod
    def error(cls, message):
        cls.write_line(message, prefix='[X]')

    @staticmethod
    def write_line(message, prefix=''):
        print(f'{prefix} {message}')
