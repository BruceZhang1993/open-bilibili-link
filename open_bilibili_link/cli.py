import asyncio

from open_bilibili_link.services import BilibiliLiveService, BilibiliServiceException


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

    def __del__(self):
        if BilibiliLiveService().session and not BilibiliLiveService().session.closed:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(BilibiliLiveService().session.close())
