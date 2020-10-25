import asyncio
import re
import sys
from http.cookies import BaseCookie
from pathlib import Path
from typing import Tuple
from urllib.parse import urlparse

from aiohttp import CookieJar
from yarl import URL

from open_bilibili_link.logger import LogManager
from open_bilibili_link.models import OBSServiceData


def color_hex_to_int(hexs: str) -> int:
    return int(hexs.lstrip('#'), 16)


async def check_exists(command):
    _, __, returncode = await run_command('which', command, allow_fail=True)
    return command, returncode == 0


async def run_command(*args, allow_fail=False):
    LogManager.instance().debug(f'[Shell] 正在执行命令 {" ".join(args)}')
    process = await asyncio.create_subprocess_exec(
        *args,
        stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    LogManager.instance().debug(f'[Shell] 命令执行完成 exitcode: {process.returncode}')
    if not allow_fail and process.returncode != 0:
        raise Exception(stderr.decode().strip())
    return stdout.decode().strip(), stderr.decode().strip(), process.returncode


async def ping(host: str) -> Tuple[str, float]:
    """
    执行 ping 命令测试延迟
    :param host: str 域名/IP/HTTP(S)/RTMP地址
    :return: 延迟毫秒数 ms
    :rtype: Tuple[str, float]
    """
    host = host.strip()
    if re.match(r'^(https?|rtmp)://', host):
        host = urlparse(host).hostname
    out, _, __ = await run_command('ping', '-q', '-c', '5', host)
    for line in out.splitlines():
        if 'avg' in line:
            numbers = line.split('=')[1].strip().split('/')
            return host, float(numbers[1])
    return host, 0


def create_obs_configuration(rtmp, key, profile='BilibiliLive'):
    target = Path.home() / '.config/obs-studio/basic/profiles' / profile
    if not target.exists():
        target.mkdir(parents=True)
    basic = f'[General]\nName={profile}\n'
    if not (target / 'basic.ini').exists():
        with (target / 'basic.ini').open('w') as f:
            f.write(basic)
            f.flush()
    service = OBSServiceData(type='rtmp_custom', settings={
        'bwtest': False,
        'use_auth': False,
        'server': rtmp,
        'key': key,
    })
    with (target / 'service.json').open('w') as f:
        f.write(service.json(indent=4))
        f.flush()


class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()
        await self._job()

    def cancel(self):
        self._task.cancel()


class Singleton(type):
    """
    单例类
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def reset_style(*args):
    for o in args:
        o.setContentsMargins(0, 0, 0, 0)


async def timed_input(prompt, timeout=None):
    """Wait for input from the user
    Note that user input is not available until the user pressed the enter or
    return key.
    Arguments:
        prompt  - text that is used to prompt the users response
        timeout - the number of seconds to wait for input
    Raises:
        An asyncio.exceptions.TimeoutError is raised if the user does not provide
        input within the specified timeout period.
    Returns:
        A string containing the users response
    """
    # Write the prompt to stdout
    sys.stdout.write(prompt)
    sys.stdout.flush()

    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()

    # The response callback will receive the users input and put it onto the
    # queue in an independent task.
    def response():
        loop.create_task(queue.put(sys.stdin.readline()))

    # Create a reader so that the response callback is invoked if the user
    # provides input on stdin.
    loop.add_reader(sys.stdin.fileno(), response)

    try:
        # Wait for an item to be placed on the queue. The only way this can
        # happen is if the reader callback is invoked.
        return (await asyncio.wait_for(queue.get(), timeout=timeout)).strip()
    except asyncio.exceptions.TimeoutError:
        # Make sure that any output to stdout or stderr that happens following
        # this coroutine, happens on a new line.
        sys.stdout.write('\n')
        sys.stdout.flush()
        raise
    finally:
        # Whatever happens, we should remove the reader so that the callback
        # never gets called.
        loop.remove_reader(sys.stdin.fileno())


def save_cookie(cookie_data: str, save_path: Path, uri: str):
    cookie_jar = CookieJar()
    cookie_dict = {}
    for c in cookie_data.split(';'):
        s = c.strip().split('=')
        if len(s) < 2:
            continue
        cookie_dict[s[0]] = s[1]
    base_cookie = BaseCookie(cookie_dict)
    clist = []
    for k in cookie_dict.keys():
        clist.append((k, base_cookie.get(k)))
    cookie_jar.update_cookies(clist, URL(uri))
    cookie_jar.save(save_path)
