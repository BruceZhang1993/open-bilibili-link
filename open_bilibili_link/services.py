import asyncio
from base64 import b64encode
from hashlib import md5
from pathlib import Path
from pprint import pprint
from typing import List
from urllib.parse import quote_plus

import rsa
from aiohttp import ClientSession, CookieJar, TraceConfig, TraceRequestStartParams
from pydantic import ValidationError

from open_bilibili_link import models
from open_bilibili_link.models import UserInfoData, RoomInfoData
from open_bilibili_link.utils import ping


def login_required(func):
    """
    验证登录状态装饰器
    :param func:
    :return:
    """

    def wrapper(*args, **kwargs):
        if not args[0].token_data:
            raise BilibiliServiceException('Login required', -90001)
        return func(*args, **kwargs)

    return wrapper


class Singleton(type):
    """
    单例类
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


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
                                    params={'access_key': self.token_data.token_info.access_token}) as r:
            res = models.UserInfoResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    @classmethod
    async def get_cached_face(cls, userinfo: UserInfoData):
        target = cls.FACE_CACHE_DIR / f'{userinfo.mid}.png'
        if target.exists():
            with open(target.as_posix(), 'rb') as f:
                return f.read()
        target.parent.mkdir(parents=True)
        async with cls().session.get(userinfo.face) as r:
            with open(target.as_posix(), 'wb') as f:
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

    async def ping(self) -> float:
        """
        测试直播接口延迟
        :return: 延迟毫秒数
        :rtype: float
        """
        return await ping(self.host)

    @classmethod
    async def get_cached_background(cls, roominfo: RoomInfoData):
        target = cls.IMAGE_CACHE_DIR / f'{roominfo.room_id}.jpg'
        if target.exists():
            with open(target.as_posix(), 'rb') as f:
                return f.read()
        target.parent.mkdir(parents=True)
        async with cls().session.get(roominfo.background) as r:
            with open(target.as_posix(), 'wb') as f:
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

    @login_required
    async def live_info(self) -> models.LiveInfoData:
        """
        获取我的直播信息 并缓存 room_id
        :raises BilibiliServiceException
        :return: 直播信息数据
        :rtype: models.LiveInfoData
        """
        uri = f'https://{self.host}/live_user/v1/UserInfo/live_info'
        async with self.session.get(uri, params={'access_key': self.token_data.token_info.access_token}) as r:
            res = models.LiveInfoResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            self._roomid = int(res.data.roomid)
            return res.data

    @login_required
    async def get_room_info(self):
        uri = f'https://{self.host}/room/v1/Room/get_info'
        async with self.session.get(uri, params={'access_key': self.token_data.token_info.access_token,
                                                 'room_id': await self.roomid}) as r:
            res = models.RoomInfoResponse(**(await r.json()))
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
        async with self.session.get(uri, params={'access_key': self.token_data.token_info.access_token}) as r:
            res = models.LiveCheckinResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    async def get_live_areas(self) -> List[models.LiveArea]:
        """
        获取直播分区信息
        :raises: BilibiliServiceException
        :return: 直播分区列表
        :rtype: List[models.LiveArea]
        """
        uri = f'https://{self.host}/room/v1/Area/getList'
        async with self.session.get(uri, params={'show_pinyin': 1}) as r:
            res = models.LiveAreaResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    @login_required
    async def start_live(self, areaid) -> models.StartLiveData:
        """
        开始直播
        :raises: BilibiliServiceException
        :param areaid: 分区 ID
        :type areaid: int
        :return: 开播数据
        :rtype: models.StartLiveData
        """
        uri = f'https://{self.LIVE_API_HOST}/room/v1/Room/startLive'
        csrf = self.get_csrf()
        data = {
            'room_id': await self.roomid,
            'platform': 'pc',
            'area_v2': areaid,
            'csrf_token': csrf,
            'csrf': csrf,
        }
        async with self.session.post(uri,
                                     params={'access_key': self.token_data.token_info.access_token},
                                     data=data) as r:
            res = models.StartLiveResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    @login_required
    async def stop_live(self):
        uri = f'https://{self.LIVE_API_HOST}/room/v1/Room/stopLive'
        csrf = self.get_csrf()
        data = {
            'room_id': await self.roomid,
            'platform': 'pc',
            'csrf_token': csrf,
            'csrf': csrf,
        }
        async with self.session.post(uri,
                                     params={'access_key': self.token_data.token_info.access_token},
                                     data=data) as r:
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
        csrf = self.get_csrf()
        uid = self.get_user_id()
        data = {
            'room_id': await self.roomid,
            'uid': uid,
            'csrf_token': csrf,
            'csrf': csrf,
        }
        for key, value in kwargs.items():
            if value is not None:
                data[key] = value
        async with self.session.post(uri,
                                     params={'access_key': self.token_data.token_info.access_token},
                                     data=data) as r:
            res = models.BaseResponseV2(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)

    @login_required
    async def get_live_code(self):
        uri = f'https://{self.LIVE_API_HOST}/live_stream/v1/StreamList/get_stream_by_roomId'
        params = {'room_id': await self.roomid, 'access_key': self.token_data.token_info.access_token}
        async with self.session.get(uri, params=params) as r:
            res = models.LiveCodeResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    @login_required
    async def get_loop_status(self):
        uri = f'https://{self.host}/i/api/round'
        async with self.session.get(uri, params={'access_key': self.token_data.token_info.access_token}) as r:
            res = models.LiveLoopStatusResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    @login_required
    async def set_loop_status(self, status: bool):
        uri = f'https://{self.host}/i/ajaxRoundOn'
        csrf = self.get_csrf()
        data = {
            'on': int(status),
            'csrf': csrf,
            'csrf_token': csrf,
        }
        async with self.session.post(uri, data=data,
                                     params={'access_key': self.token_data.token_info.access_token}) as r:
            res = models.BaseResponseV2(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
