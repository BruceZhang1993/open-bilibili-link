import datetime
from pathlib import Path
from typing import Any, List, Union, Optional

import rsa
from pydantic import BaseModel, validator, Field


class OBSServiceData(BaseModel):
    class Settings(BaseModel):
        bwtest: bool
        use_auth: bool
        server: str
        key: str

    type: str
    settings: Settings


class BaseResponse(BaseModel):
    ts: int
    code: int
    data: Any


class BaseResponseV2(BaseModel):
    code: int
    message: str
    data: Any


class HashKey(BaseModel):
    hash: str
    key: str

    @property
    def pubkey(self):
        return rsa.PublicKey.load_pkcs1_openssl_pem(self.key.encode())


class TokenData(BaseModel):
    mid: int
    access_token: str
    refresh_token: str
    expires_in: int

    @property
    def expire_date(self):
        now = datetime.datetime.now()
        now += datetime.timedelta(seconds=self.expires_in)
        return now


class CookieItem(BaseModel):
    name: str
    value: str
    http_only: bool
    expires: datetime.datetime


class CookieData(BaseModel):
    cookies: List[CookieItem]
    domains: List[str]


class LoginData(BaseModel):
    status: int
    token_info: TokenData
    cookie_info: CookieData
    sso: List[str]

    def save_to_file(self, path: Path):
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        with open(path.as_posix(), 'w') as f:
            f.write(self.json())
            f.flush()


class UserInfoData(BaseModel):
    mid: int
    name: str
    sex: str
    face: str
    sign: str
    rank: int
    level: int
    moral: int
    email_status: bool
    tel_status: bool
    identification: int
    vip: dict
    pendant: dict
    nameplate: dict
    official: dict
    birthday: datetime.datetime
    is_tourist: bool
    is_fake_account: bool
    level_exp: dict
    coins: float
    following: int
    follower: int


class LiveInfoData(BaseModel):
    class LiveMaster(BaseModel):
        level: int
        current: int
        next: int
        medalInfo: Any

    achieves: int
    count: dict
    liveTime: int
    master: LiveMaster
    san: int
    userInfo: dict
    roomid: str
    userCoinIfo: dict
    discount: bool
    is_guild_master: bool


class LiveCodeData(BaseModel):
    class RtmpData(BaseModel):
        addr: str
        code: str

    rtmp: RtmpData
    stream_line: List[dict]


class StartLiveData(BaseModel):
    class RtmpInfo(BaseModel):
        addr: str
        code: str
        new_link: str
        provider: str

    change: bool
    notice: dict
    protocols: List[dict]
    room_type: int
    rtmp: RtmpInfo
    status: str


class LiveArea(BaseModel):
    id: int
    act_id: int
    area_type: int
    hot_status: bool
    lock_status: bool
    name: str
    old_area_id: int
    parent_id: int
    parent_name: str
    pic: str
    pinyin: str
    pk_status: bool


class LiveCheckinData(BaseModel):
    all_days: int = Field(alias='allDays')
    had_sign_days: int = Field(alias='hadSignDays')
    is_bonus_day: bool = Field(alias='isBonusDay')
    special_text: str = Field(alias='specialText')
    text: str


class LiveCheckInfoData(BaseModel):
    text: str
    special_text: str = Field(alias='specialText')
    status: bool
    all_days: int = Field(alias='allDays')
    current_month: int = Field(alias='curMonth')
    current_year: int = Field(alias='curYear')
    current_day: int = Field(alias='curDay')
    current_date: str = Field(alias='curDate')
    had_sign_days: int = Field(alias='hadSignDays')
    new_task: int = Field(alias='newTask')
    sign_days_list: List[int] = Field(alias='signDaysList')
    sign_bonus_days_list: List[int] = Field(alias='signBonusDaysList')


class RoomInfoData(BaseModel):
    uid: int
    room_id: int
    short_id: int
    attention: int
    online: int
    is_portrait: bool
    description: str
    live_status: bool
    area_id: int
    parent_area_id: int
    parent_area_name: str
    old_area_id: int
    background: str
    title: str
    user_cover: str
    keyframe: str
    is_strict_room: bool
    live_time: str
    tags: str
    room_silent_type: str
    room_silent_level: int
    room_silent_second: int
    area_name: str
    hot_words: List[str]
    hot_words_status: bool
    pk_status: bool
    pk_id: int
    battle_id: int
    allow_change_area_time: int
    allow_upload_cover_time: int


class DanmuKeyData(BaseModel):
    class DanmuHost(BaseModel):
        host: str
        port: int
        wss_port: int
        ws_port: int

    group: str
    business_id: int
    refresh_row_factor: float
    refresh_rate: int
    max_delay: int
    token: str
    host_list: List[DanmuHost]


class RoomInitData(BaseModel):
    room_id: int
    short_id: int
    uid: int
    need_p2p: bool
    is_hidden: bool
    is_locked: bool
    is_portrait: bool
    live_status: bool
    hidden_till: int
    lock_till: int
    encrypted: bool
    pwd_verified: bool
    live_time: int
    room_shield: int
    is_sp: bool
    special_type: int


class HashKeyResponse(BaseResponse):
    data: HashKey


class LoginResponse(BaseResponse):
    class VerifyUrlData(BaseModel):
        url: str
    message: Optional[str]
    data: Union[LoginData, VerifyUrlData]


class UserInfoResponse(BaseResponseV2):
    ttl: int
    data: UserInfoData


class LiveInfoResponse(BaseResponseV2):
    msg: str
    data: LiveInfoData


class LiveCodeResponse(BaseResponseV2):
    data: LiveCodeData


class StartLiveResponse(BaseResponseV2):
    msg: str
    data: Union[StartLiveData, list]


class StopLiveResponse(BaseResponseV2):
    class StopLiveData(BaseModel):
        change: bool
        status: str

    msg: str
    data: Union[StopLiveData, list]


class LiveAreaResponse(BaseResponseV2):
    class LiveAreaCategory(BaseModel):
        id: int
        name: str
        list: List[LiveArea]

    msg: str
    data: List[LiveAreaCategory]


class LiveCheckInfoResponse(BaseResponseV2):
    ttl: int
    data: Optional[LiveCheckInfoData]


class LiveCheckinResponse(BaseResponseV2):
    ttl: int
    data: Optional[LiveCheckinData]


class LiveLoopStatusResponse(BaseResponseV2):
    class LiveLoopStatusData(BaseModel):
        auto_update: bool = Field(alias='autoUpdate')
        has_round_room: bool = Field(alias='hasRoundRoom')
        is_round: bool = Field(alias='isRound')
        updating: bool
        verify_round_status: bool = Field(alias='verifyRoundStatus')

    data: LiveLoopStatusData


class RoomInfoResponse(BaseResponseV2):
    data: RoomInfoData


class DanmuKeyResponse(BaseResponseV2):
    ttl: int
    data: DanmuKeyData


class RoomInitResponse(BaseResponseV2):
    data: RoomInitData


class DanmuHistoryResponse(BaseResponseV2):
    class DanmuHistoryData(BaseModel):
        class DanmuHistory(BaseModel):
            uid: int
            nickname: str
            vip: bool
            svip: bool
            timeline: datetime.datetime
            text: str
        admin: list
        room: List[DanmuHistory]
    data: DanmuHistoryData


class LiveAreaHistoryResponse(BaseResponseV2):
    class HistoryLiveArea(BaseModel):
        id: int
        name: str
        parent_id: int
        parent_name: str
        act_flag: int
    data: List[HistoryLiveArea]


class LiveNews(BaseModel):
    roomid: int
    uid: int
    content: str
    ctime: datetime.datetime
    status: int
    uname: str


class LiveNewsResponse(BaseResponseV2):
    data: LiveNews


class SendGiftData(BaseModel):
    draw: int
    gold: int
    silver: int
    num: int
    total_coin: int
    effect: int
    broadcast_id: int
    crit_prob: int
    guard_level: int
    rcost: int
    uid: int
    timestamp: datetime.datetime
    gift_type: int = Field(alias='giftType')
    price: int
    action: str
    coin_type: str
    uname: str
    face: str
    gift_name: str = Field(alias='giftName')


class WelcomeData(BaseModel):
    uid: int
    uname: str
    is_admin: bool
    svip: bool
    vip: bool
    mock_effect: int


class RoomBannerData(BaseModel):
    rank_status: bool
    task_status: bool
    rank_default: int
    rank_info: dict
    task_info: dict


class RoomRealTimeMessageUpdateData(BaseModel):
    roomid: int
    fans: int
    red_notice: int
    fans_club: int


class DanmuContent(BaseModel):
    cmd: str
    type: Optional[int]
    id: Optional[int]
    data: Union[RoomRealTimeMessageUpdateData, WelcomeData, SendGiftData, Any, None]


class DanmuData(BaseModel):
    msg_type: str
    name: Optional[str]
    type: Optional[int]
    roomid: Optional[int]
    raw: Optional[dict]
    content: Union[DanmuContent, str, bytes]
