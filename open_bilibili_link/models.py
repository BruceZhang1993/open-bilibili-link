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


class HashKeyResponse(BaseResponse):
    data: HashKey


class LoginResponse(BaseResponse):
    message: Optional[str]
    data: Optional[LoginData]


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
