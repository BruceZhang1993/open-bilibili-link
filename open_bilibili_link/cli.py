import asyncio

from open_bilibili_link.models import DanmuData
from open_bilibili_link.services import BilibiliLiveService, BilibiliServiceException, BilibiliLiveDanmuService
from open_bilibili_link.widgets.components.danmu import DanmuPusher


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
        print('Gently shutting down...')
        BilibiliLiveDanmuService().unregister_callback(self._danmu)

    async def danmu(self, roomid: int = 0, *, output: str = 'stdout'):
        if output not in ['stdout', 'file']:
            print('output must be stdout or file')
            return
        if roomid == 0:
            roomid = await BilibiliLiveService().roomid
        import signal
        signal.signal(signal.SIGINT, self._danmu_off)
        if output == 'stdout':
            BilibiliLiveDanmuService().register_callback(self._danmu, external=False)
        elif output == 'file':
            danmu_pusher = DanmuPusher(roomid)
            self._danmu = danmu_pusher.append_danmu
            BilibiliLiveDanmuService().register_callback(self._danmu, external=False)
        danmus = await BilibiliLiveService().get_danmu_history(roomid)
        for danmu in danmus:
            if output == 'stdout':
                print(danmu)
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
