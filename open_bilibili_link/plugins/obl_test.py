from open_bilibili_link.services import BilibiliLiveDanmuService


__plugin_id__ = 'io.github.brucezhang1993.danmu_demo'
__plugin_name__ = 'Danmu Logger'
__plugin_desc__ = 'This is a demo plugin to print danmu to console'


def test_danmu_plugin(danmu):
    print('test plugin', danmu)


def register():
    BilibiliLiveDanmuService().register_callback(test_danmu_plugin)


def unregister():
    BilibiliLiveDanmuService().unregister_callback(test_danmu_plugin)
