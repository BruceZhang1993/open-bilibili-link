import asyncio
from pathlib import Path

from open_bilibili_link.models import OBSServiceData


async def check_exists(command):
    process = await asyncio.create_subprocess_exec(
        'which', command,
        stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
    await process.communicate()
    return command, process.returncode == 0


async def run_command(*args, allow_fail=False):
    process = await asyncio.create_subprocess_exec(
        *args,
        stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    if not allow_fail and process.returncode != 0:
        raise Exception(stderr.decode().strip())
    return stdout.decode().strip(), stderr.decode().strip(), process.returncode


async def ping(host: str) -> float:
    """
    执行 ping 命令测试延迟
    :param host: str
    :return: 延迟毫秒数 ms
    :rtype: float
    """
    out, _, __ = await run_command('ping', '-q', '-c', '5', host)
    for line in out.splitlines():
        if 'avg' in line:
            numbers = line.split('=')[1].strip().split('/')
            return float(numbers[1])
    return 0


def create_obs_configuration(rtmp, key, profile='BilibiliLive'):
    target = Path.home() / '.config/obs-studio/basic/profiles' / profile
    if not target.exists():
        target.mkdir(parents=True)
    basic = f'[General]\nName={profile}\n'
    if not (target / 'basic.ini').exists():
        with open((target / 'basic.ini').as_posix(), 'w') as f:
            f.write(basic)
            f.flush()
    service = OBSServiceData(type='rtmp_custom', settings={
        'bwtest': False,
        'use_auth': False,
        'server': rtmp,
        'key': key,
    })
    with open((target / 'service.json').as_posix(), 'w') as f:
        f.write(service.json(indent=4))
        f.flush()
