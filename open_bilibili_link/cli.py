from open_bilibili_link.services import BilibiliLiveService, BilibiliServiceException


class CliApp(object):
    def __init__(self, args):
        self.args = args

    async def checkin(self):
        if not BilibiliLiveService().logged_in:
            print('Need login')
            return
        try:
            await BilibiliLiveService().checkin()
        except BilibiliServiceException as e:
            print(e.args)
        finally:
            await BilibiliLiveService().session.close()
