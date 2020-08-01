import asyncio

from open_bilibili_link.models import DanmuData
from open_bilibili_link.services import BilibiliLiveService, BilibiliServiceException, BilibiliLiveDanmuService


class CliApp(object):
    def __init__(self, args):
        self.args = args

    async def login(self, username: str, password: str):
        if BilibiliLiveService().logged_in:
            print('Already logged in')
            await BilibiliLiveService().session.close()
            return
        try:
            print(await BilibiliLiveService().login(username, password))
        except BilibiliServiceException as e:
            print(e.args)

    async def checkin(self):
        if not BilibiliLiveService().logged_in:
            print('Need login')
            await BilibiliLiveService().session.close()
            return
        try:
            print(await BilibiliLiveService().checkin())
        except BilibiliServiceException as e:
            print(e.args)

    def _danmu(self, danmu: DanmuData):
        print(danmu)

    def _danmu_off(self, _, __):
        BilibiliLiveDanmuService().unregister_callback(self._danmu)

    def danmu(self, roomid):
        import signal
        signal.signal(signal.SIGINT, self._danmu_off)
        BilibiliLiveDanmuService().register_callback(self._danmu, external=False)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(BilibiliLiveDanmuService().ws_connect(roomid))

    def __del__(self):
        loop = asyncio.get_event_loop()
        if BilibiliLiveService().session and not BilibiliLiveService().session.closed:
            loop.run_until_complete(BilibiliLiveService().session.close())
        if BilibiliLiveDanmuService().session and not BilibiliLiveDanmuService().session.closed:
            loop.run_until_complete(BilibiliLiveDanmuService().session.close())
