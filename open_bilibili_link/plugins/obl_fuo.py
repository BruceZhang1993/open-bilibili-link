from open_bilibili_link.models import DanmuData
from open_bilibili_link.services import BilibiliLiveDanmuService
from open_bilibili_link.utils import run_command

# Plugin metadata
__plugin_id__ = 'io.github.brucezhang1993.danmu_fuo'
__plugin_name__ = 'FeelUOwn Danmu'
__plugin_desc__ = 'FeelUOwn plugin for Bilibili danmu aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
__plugin_settings__ = {
    'prefix': (str, '触发关键词', '-', '/FUO'),
}

# Loaded when plugin found
__config__: dict = {}
__loaded__ = False


async def test_danmu_plugin(danmu: DanmuData):
    if danmu.msg_type == BilibiliLiveDanmuService.TYPE_DANMUKU and danmu.content. \
            startswith(__config__.get('prefix', '/FUO')):
        arguments = danmu.content[4:].strip().split()
        if len(arguments) > 0:
            print(f'弹幕点歌：{arguments}')
            await run_command('fuo', 'play', f'{arguments[0]}'
                                             f'{("-" + arguments[1]) if len(arguments) > 2 else ""}', allow_fail=True)


def register():
    BilibiliLiveDanmuService().register_callback(test_danmu_plugin)


def unregister():
    BilibiliLiveDanmuService().unregister_callback(test_danmu_plugin)
