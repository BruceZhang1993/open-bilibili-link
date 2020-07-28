import asyncio
import json
import zlib
from base64 import b64encode
from hashlib import md5
from pathlib import Path
from pprint import pprint
from random import random
from struct import unpack
from time import time
from typing import List, Callable, Optional
from urllib.parse import quote_plus

import rsa
from aiohttp import ClientSession, CookieJar, TraceConfig, TraceRequestStartParams, WSMsgType, WSMessage

from open_bilibili_link import models
from open_bilibili_link.models import UserInfoData, RoomInfoData, DanmuKeyResponse, DanmuKeyData, RoomInitResponse, \
    DanmuData, RoomInitData, DanmuHistoryResponse
from open_bilibili_link.utils import ping, Timer, color_hex_to_int, Singleton


def login_required(func):
    """
    验证登录状态装饰器
    :param func: 方法
    :type func: Callable
    :return:
    """

    def wrapper(*args, **kwargs):
        if not args[0].token_data:
            raise BilibiliServiceException('Login required', -90001)
        return func(*args, **kwargs)

    return wrapper


class BilibiliServiceException(Exception):
    """
    Bilibili 服务异常类
    """
    pass


class BilibiliBaseService:
    """
    Bilibili 服务基础类
    """
    # 服务配置
    APPKEY = '1d8b6e7d45233436'
    SALT = '560c52ccd288fed045859ed18bffd973'

    # 默认请求信息
    DEFAULT_HEADERS = {'User-Agent': 'Mozilla/5.0 BilibiliLive/1.0'}

    # 接口请求域名
    PASSPORT_API_HOST = 'passport.bilibili.com'
    ACCOUNT_API_HOST = 'account.bilibili.com'
    LIVE_API_HOST = 'api.live.bilibili.com'
    MAIN_API_HOST = 'api.bilibili.com'
    ACTIVITY_API_HOST = 'bilibili.hdslb.net'
    DANMU_API_HOST = 'livecmt-2.bilibili.com'

    # 项目默认配置
    CACHE_DIR = Path.home() / '.cache' / 'OBL'
    TOKEN_FILE = CACHE_DIR / 'token.json'
    FACE_CACHE_DIR = CACHE_DIR / 'faces'
    IMAGE_CACHE_DIR = CACHE_DIR / 'images'

    def __init__(self):
        self.cookie_jar = CookieJar()
        self.token_data = None
        if self.TOKEN_FILE.exists():
            self.token_data = models.LoginData.parse_file(self.TOKEN_FILE)
        self.trace = TraceConfig()
        self.trace.on_connection_create_end.append(self.on_connected)
        self.trace.on_request_start.append(self.on_request_start)
        self.trace.on_request_end.append(self.on_request_end)
        self.session = ClientSession(cookie_jar=self.cookie_jar, headers=self.DEFAULT_HEADERS,
                                     trace_configs=[self.trace])

    @staticmethod
    async def on_connected(_, __, ___):
        print(f'Connection established.')

    @staticmethod
    async def on_request_start(_, __, params: TraceRequestStartParams):
        print(f'Requesting: [{params.method}] {params.url}')

    @staticmethod
    async def on_request_end(_, __, ___):
        print('Request ok.')

    @property
    def logged_in(self):
        return self.token_data is not None

    @login_required
    def with_token(self, data=None):
        if data is None:
            data = {}
        return dict(data, access_key=self.token_data.token_info.access_token)

    @login_required
    def with_csrf(self, data=None):
        if data is None:
            data = {}
        csrf = self.get_csrf()
        return dict(data, csrf=csrf, csrf_token=csrf)

    def calc_sign(self, param: str) -> str:
        """
        计算签名
        :param param: 请求字符串
        :type param: str
        :return: 签名字符串
        :rtype: str
        """
        sign_hash = md5()
        sign_hash.update(f'{param}{self.SALT}'.encode())
        return sign_hash.hexdigest()

    async def get_hash(self) -> models.HashKey:
        """
        获取认证 Hash 和公钥
        :raises: BilibiliServiceException
        :return: HashKey model, 包含 hash 和导入的 pubkey
        :rtype: models.HashKey
        """
        uri = f'https://{self.PASSPORT_API_HOST}/api/oauth2/getKey'
        data = {'appkey': self.APPKEY, 'sign': self.calc_sign(f'appkey={self.APPKEY}')}
        async with self.session.post(uri, data=data) as r:
            res = models.HashKeyResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException('', res.code)
            return res.data

    async def login(self, username: str, password: str) -> models.LoginData:
        """
        帐号密码登录
        :param username: 用户名
        :type username: str
        :param password: 密码
        :type password: str
        :raises BilibiliServiceException
        :return: 返回登录数据，包含 cookie & token 可保存到文件
        :rtype: models.LoginData
        """
        hash_data = await self.get_hash()
        if not hash_data:
            raise BilibiliServiceException('get hash failed', -90000)
        uri = f'https://{self.PASSPORT_API_HOST}/api/v3/oauth2/login'
        param = f"appkey={self.APPKEY}&password=" \
                f"{quote_plus(b64encode(rsa.encrypt(f'{hash_data.hash}{password}'.encode(), hash_data.pubkey)))}" \
                f"&username={quote_plus(username)}"
        data = f'{param}&sign={self.calc_sign(param)}'
        headers = self.DEFAULT_HEADERS
        headers['Content-type'] = 'application/x-www-form-urlencoded'
        async with self.session.post(uri, data=data, headers=headers) as r:
            res = models.LoginResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message or '', res.code)
            res.data.save_to_file(self.TOKEN_FILE)
            self.token_data = res.data
            return res.data

    @login_required
    async def stat(self):
        uri = f'https://{self.MAIN_API_HOST}/x/web-interface/nav/stat'
        async with self.session.get(uri, headers=self.DEFAULT_HEADERS,
                                    params=self.with_token()) as r:
            return await r.json()

    @login_required
    def get_user_id(self) -> int:
        """
        从缓存 cookie 获取用户 ID
        :return: 用户 ID
        :rtype: int
        :raises: BilibiliServiceException
        """
        for cookie in self.token_data.cookie_info.cookies:
            if cookie.name == 'DedeUserID':
                return int(cookie.value)
        raise BilibiliServiceException('user id not found in cookie', -90002)

    @login_required
    def get_csrf(self) -> str:
        """
        从缓存 cookie 获取 csrf 凭证
        :raises BilibiliServiceException
        :return: csrf 字符串
        :rtype: str
        """
        for cookie in self.token_data.cookie_info.cookies:
            if cookie.name == 'bili_jct':
                return cookie.value
        raise BilibiliServiceException('csrf not found in cookie', -90003)

    @login_required
    async def get_user_info(self) -> models.UserInfoData:
        """
        获取用户信息
        :raises BilibiliServiceException
        :return: 用户信息数据
        :rtype: models.UserInfoData
        """
        uri = f'https://{self.MAIN_API_HOST}/x/space/myinfo?jsonp='
        headers = self.DEFAULT_HEADERS
        headers['Host'] = self.MAIN_API_HOST
        headers['Referer'] = f'https://space.bilibili.com/{self.get_user_id()}/'
        async with self.session.get(uri, headers=headers,
                                    params=self.with_token()) as r:
            res = models.UserInfoResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    @classmethod
    async def get_cached_face(cls, userinfo: UserInfoData):
        target = cls.FACE_CACHE_DIR / f'{userinfo.mid}.png'
        if target.exists():
            with target.open('rb') as f:
                return f.read()
        target.parent.mkdir(parents=True)
        async with cls().session.get(userinfo.face) as r:
            with target.open('wb') as f:
                data = await r.content.read()
                f.write(data)
                f.flush()
            return data


class BilibiliLiveService(BilibiliBaseService, metaclass=Singleton):
    """
    Bilibili 直播服务类
    """
    DEFAULT_PROFILE = 'Bilibili'

    def __init__(self):
        super().__init__()
        self.host = self.LIVE_API_HOST
        self._roomid = 0
        self._live_status = None
        self._areaid = 0

    @property
    async def areaid(self):
        if self._areaid:
            return self._areaid
        await self.live_info()
        return self._areaid

    @areaid.setter
    def areaid(self, v):
        self._areaid = v

    async def ping(self) -> float:
        """
        测试直播接口延迟
        :return: 延迟毫秒数
        :rtype: float
        """
        return await ping(self.host)

    @classmethod
    async def get_image(cls, url):
        async with cls().session.get(url) as r:
            return await r.content.read()

    @classmethod
    async def get_cached_background(cls, roominfo: RoomInfoData):
        target = cls.IMAGE_CACHE_DIR / f'{roominfo.room_id}.jpg'
        if target.exists():
            with target.open('rb') as f:
                return f.read()
        target.parent.mkdir(parents=True)
        async with cls().session.get(roominfo.background) as r:
            with target.open('wb') as f:
                data = await r.content.read()
                f.write(data)
                f.flush()
            return data

    @property
    async def roomid(self):
        """
        获取直播间号缓存
        :return: 直播间房间号
        :rtype: int
        """
        if self._roomid > 0:
            return self._roomid
        await self.live_info()
        return self._roomid

    @property
    async def live_status(self):
        if self._live_status is not None:
            return self._live_status
        await self.get_room_info()
        return self._live_status

    @live_status.setter
    def live_status(self, v):
        self._live_status = v

    @login_required
    async def live_info(self) -> models.LiveInfoData:
        """
        获取我的直播信息 并缓存 room_id
        :raises BilibiliServiceException
        :return: 直播信息数据
        :rtype: models.LiveInfoData
        """
        uri = f'https://{self.host}/live_user/v1/UserInfo/live_info'
        async with self.session.get(uri, params=self.with_token()) as r:
            res = models.LiveInfoResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            self._roomid = int(res.data.roomid)
            return res.data

    @login_required
    async def get_room_info(self):
        uri = f'https://{self.host}/room/v1/Room/get_info'
        async with self.session.get(uri, params=self.with_token({'room_id': await self.roomid})) as r:
            res = models.RoomInfoResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            self._live_status = res.data.live_status
            self._areaid = res.data.area_id
            return res.data

    @login_required
    async def check_info(self):
        uri = f'https://{self.host}/xlive/web-ucenter/v1/sign/WebGetSignInfo'
        async with self.session.get(uri, params=self.with_token()) as r:
            res = models.LiveCheckInfoResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    @login_required
    async def checkin(self) -> models.LiveCheckinData:
        """
        签到
        :raises: BilibiliServiceException
        :return: 直播签到
        :rtype: models.LiveCheckinData
        """
        uri = f'https://{self.host}/xlive/web-ucenter/v1/sign/DoSign'
        async with self.session.get(uri, params=self.with_token()) as r:
            res = models.LiveCheckinResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    async def get_live_areas(self) -> List[models.LiveAreaResponse.LiveAreaCategory]:
        """
        获取直播分区信息
        :raises: BilibiliServiceException
        :return: 直播分区列表
        :rtype: List[models.LiveAreaResponse.LiveAreaCategory]
        """
        uri = f'https://{self.host}/room/v1/Area/getList'
        async with self.session.get(uri, params={'show_pinyin': 1}) as r:
            res = models.LiveAreaResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    async def get_history_areas(self, roomid=None) -> List[models.LiveAreaHistoryResponse.HistoryLiveArea]:
        """
        获取历史直播分区信息
        :raises: BilibiliServiceException
        :return: 直播分区列表
        :rtype: List[models.LiveAreaHistoryResponse.HistoryLiveArea]
        """
        uri = f'https://{self.host}/room/v1/Area/getMyChooseArea?roomid=496150'
        async with self.session.get(uri, params={'roomid': roomid or (await self.roomid)}) as r:
            res = models.LiveAreaHistoryResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    @login_required
    async def start_live(self, areaid: int = None) -> models.StartLiveData:
        """
        开始直播
        :raises: BilibiliServiceException
        :param areaid: 分区 id
        :type areaid: Optional[int]
        :return: 开播数据
        :rtype: models.StartLiveData
        """
        uri = f'https://{self.LIVE_API_HOST}/room/v1/Room/startLive'
        data = self.with_csrf({'room_id': await self.roomid, 'platform': 'pc',
                               'area_v2': areaid or (await self.areaid)})
        async with self.session.post(uri, params=self.with_token(), data=data) as r:
            res = models.StartLiveResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    @login_required
    async def stop_live(self):
        uri = f'https://{self.LIVE_API_HOST}/room/v1/Room/stopLive'
        data = self.with_csrf({'room_id': await self.roomid, 'platform': 'pc'})
        async with self.session.post(uri, params=self.with_token(), data=data) as r:
            res = models.StopLiveResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    @login_required
    async def update_live_heading(self, **kwargs):
        """
        :param kwargs: See kwargs
        Kwargs:
            title str: 直播标题
            description str: 个人简介
        """
        uri = f'https://{self.LIVE_API_HOST}/room/v1/Room/update'
        uid = self.get_user_id()
        data = self.with_csrf({'room_id': await self.roomid, 'uid': uid})
        for key, value in kwargs.items():
            if value is not None:
                data[key] = value
        async with self.session.post(uri, params=self.with_token(), data=data) as r:
            res = models.BaseResponseV2(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)

    @login_required
    async def get_live_code(self):
        uri = f'https://{self.LIVE_API_HOST}/live_stream/v1/StreamList/get_stream_by_roomId'
        params = self.with_token({'room_id': await self.roomid})
        async with self.session.get(uri, params=params) as r:
            res = models.LiveCodeResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    @login_required
    async def get_loop_status(self):
        uri = f'https://{self.host}/i/api/round'
        async with self.session.get(uri, params=self.with_token()) as r:
            res = models.LiveLoopStatusResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    @login_required
    async def set_loop_status(self, status: bool):
        uri = f'https://{self.host}/i/ajaxRoundOn'
        data = self.with_csrf({'on': int(status)})
        async with self.session.post(uri, data=data, params=self.with_token()) as r:
            res = models.BaseResponseV2(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)

    @login_required
    async def send_danmu(self, roomid, content, color='#ffffff', fontsize=25, mode=1, bubble=0):
        uri = f'https://{self.host}/msg/send'
        data = self.with_csrf({
            'color': color_hex_to_int(color),
            'fontsize': fontsize,
            'mode': mode,
            'msg': content,
            'rnd': int(time()),
            'roomid': roomid,
            'bubble': bubble,
        })
        async with self.session.post(uri, data=data, params=self.with_token()) as r:
            res = models.BaseResponseV2(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    async def get_live_news(self, roomid=None):
        uri = f'https://{self.host}/room_ex/v1/RoomNews/get'
        async with self.session.get(uri, params={'roomid': roomid or (await self.roomid)}) as r:
            res = models.LiveNewsResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    @login_required
    async def update_live_news(self, content):
        uri = f'https://{self.host}/room_ex/v1/RoomNews/update'
        data = self.with_csrf({'roomid': await self.roomid, 'content': content})
        async with self.session.post(uri, data=data,
                                     params=self.with_token()) as r:
            res = models.BaseResponseV2(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    @login_required
    async def get_danmu_history(self, roomid=None) -> List[DanmuHistoryResponse.DanmuHistoryData.DanmuHistory]:
        uri = f'https://{self.host}/xlive/web-room/v1/dM/gethistory'
        data = self.with_csrf({'roomid': roomid or (await self.roomid), 'visit_id': ''})
        async with self.session.post(uri, data=data, params=self.with_token()) as r:
            res = models.DanmuHistoryResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data.room


class BilibiliLiveDanmuService(metaclass=Singleton):
    # API 域名
    LIVE_API_HOST = 'api.live.bilibili.com'

    # 弹幕地址
    DANMU_WS = 'wss://broadcastlv.chat.bilibili.com/sub'

    # 操作类型
    TYPE_JOIN_ROOM = 7
    TYPE_HEARTBEAT = 2

    # 消息类型
    TYPE_DANMUKU = 'danmaku'
    TYPE_ENTER = 'enter'
    TYPE_BROADCAST = 'broadcast'
    TYPE_GIFT = 'gift'
    TYPE_OTHER = 'other'

    def __init__(self):
        super().__init__()
        self.ws = None
        self.timer: Optional[Timer] = None
        self.callbacks = set()
        self.external_callbacks = set()
        self.session = ClientSession()

    def register_callback(self, callback, external=True):
        if external:
            self.external_callbacks.add(callback)
        else:
            self.callbacks.add(callback)

    def unregister_callback(self, callback):
        try:
            self.callbacks.remove(callback)
            self.external_callbacks.remove(callback)
        except KeyError:
            pass
        if len(self.callbacks) == 0:
            if self.timer is not None:
                self.timer.cancel()
            asyncio.gather(self.ws.close())

    async def get_danmu_key(self, roomid) -> DanmuKeyData:
        params = {'id': roomid, 'type': 0}
        async with self.session.get(f'https://{self.LIVE_API_HOST}/xlive/web-room/v1/index/getDanmuInfo',
                                    params=params) as r:
            res = DanmuKeyResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    @staticmethod
    def decode_msg(data):
        dm_list_compressed = []
        dm_list = []
        ops = []
        msgs = []
        while True:
            try:
                packet_len, header_len, ver, op, seq = unpack('!IHHII', data[0:16])
            except:
                break
            if len(data) < packet_len:
                break
            if ver == 1 or ver == 0:
                ops.append(op)
                dm_list.append(data[16:packet_len])
            elif ver == 2:
                dm_list_compressed.append(data[16:packet_len])
            if len(data) == packet_len:
                data = b''
                break
            else:
                data = data[packet_len:]
        for dm in dm_list_compressed:
            d = zlib.decompress(dm)
            while True:
                try:
                    packet_len, header_len, ver, op, seq = unpack('!IHHII', d[0:16])
                except:
                    break
                if len(d) < packet_len:
                    break
                ops.append(op)
                dm_list.append(d[16:packet_len])
                if len(d) == packet_len:
                    d = b''
                    break
                else:
                    d = d[packet_len:]
        for i, d in enumerate(dm_list):
            try:
                msg = {}
                if ops[i] == 5:
                    j = json.loads(d)
                    msg['msg_type'] = {'SEND_GIFT': 'gift', 'DANMU_MSG': 'danmaku',
                                       'WELCOME': 'enter', 'NOTICE_MSG': 'broadcast'}.get(j.get('cmd'), 'other')
                    if msg['msg_type'] == 'danmaku':
                        msg['name'] = (j.get('info', ['', '', ['', '']])[2][1]
                                       or j.get('data', {}).get('uname', ''))
                        msg['content'] = j.get('info', ['', ''])[1]
                    elif msg['msg_type'] == 'broadcast':
                        msg['type'] = j.get('msg_type', 0)
                        msg['roomid'] = j.get('real_roomid', 0)
                        msg['content'] = j.get('msg_common', 'none')
                        msg['raw'] = j
                    else:
                        msg['content'] = j
                else:
                    msg = {'name': '', 'content': d, 'msg_type': 'other'}
                msgs.append(msg)
            except:
                pass
        return msgs

    @staticmethod
    def encode_payload(data, type_=TYPE_HEARTBEAT):
        payload = json.dumps(data, separators=(',', ':')).encode('ascii')
        payload_length = len(payload) + 16
        data = payload_length.to_bytes(4, byteorder='big')
        data += (16).to_bytes(2, byteorder='big')
        data += (1).to_bytes(2, byteorder='big')
        data += type_.to_bytes(4, byteorder='big')
        data += (1).to_bytes(4, byteorder='big')
        data += payload
        return data

    async def send_heatbeat(self):
        print('[WS] Sending heartbeat package')
        await self.ws.send_bytes(self.encode_payload('[object Object]'))

    async def room_init(self, roomid) -> RoomInitData:
        room_init_uri = f'https://{self.LIVE_API_HOST}/room/v1/Room/room_init'
        room_init_params = {'id': roomid}
        async with self.session.get(room_init_uri, params=room_init_params) as r:
            res = RoomInitResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
        return res.data

    async def ws_connect(self, roomid):
        loop = asyncio.get_event_loop()
        if self.ws and not self.ws.closed:
            return
        room_init_data = await self.room_init(roomid)
        token_data = await self.get_danmu_key(room_init_data.room_id)
        async with self.session.ws_connect(self.DANMU_WS) as ws:
            self.ws = ws
            payload = {'uid': int(1e14 + 2e14 * random()), 'roomid': room_init_data.room_id, 'protover': 1,
                       'platform': 'web', 'clientver': '1.14.1', 'type': 2, 'key': token_data.token}
            await ws.send_bytes(self.encode_payload(payload, type_=self.TYPE_JOIN_ROOM))
            self.timer = Timer(30, self.send_heatbeat)
            async for msg in ws:
                msg: WSMessage
                if msg.type == WSMsgType.BINARY:
                    for data in self.decode_msg(msg.data):
                        danmu = DanmuData(**data)
                        for cb in self.callbacks.union(self.external_callbacks):
                            try:
                                if asyncio.iscoroutinefunction(cb):
                                    await cb(danmu)
                                else:
                                    loop.run_in_executor(None, cb, danmu)
                            except Exception as err:
                                print('DanmuPushError: ' + str(err))
                else:
                    print(msg)


async def main():
    print(await BilibiliLiveService().update_live_news('11'))
    await BilibiliLiveService().session.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
