from open_bilibili_link.services import BilibiliLiveService, BilibiliServiceException


class CliApp(object):
    def __init__(self, args):
        self.args = args

    async def login(self):
        if BilibiliLiveService().logged_in:
            print('Already logged in')
            await BilibiliLiveService().session.close()
            return
        try:
            print(await BilibiliLiveService().login())
        except BilibiliServiceException as e:
            print(e.args)
        finally:
            await BilibiliLiveService().session.close()

    async def checkin(self):
        if not BilibiliLiveService().logged_in:
            print('Need login')
            await BilibiliLiveService().session.close()
            return
        try:
            print(await BilibiliLiveService().checkin())
        except BilibiliServiceException as e:
            print(e.args)
        finally:
            await BilibiliLiveService().session.close()
