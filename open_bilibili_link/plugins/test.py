from open_bilibili_link.services import BilibiliLiveDanmuService


def test_danmu_plugin(danmu):
    print('test plugin', danmu)


def register():
    BilibiliLiveDanmuService().register_callback(test_danmu_plugin)


def unregister():
    BilibiliLiveDanmuService().unregister_callback(test_danmu_plugin)
