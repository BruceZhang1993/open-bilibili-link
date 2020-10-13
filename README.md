### Open Bilibili Link
Working in progress

#### Development
```shell script
pipenv install
# Print help
python3 -m open_bilibili_link --help
# Run GUI to default page
python3 -m open_bilibili_link gui
# Login from Cli
python3 -m open_bilibili_link login [Username] [Password]
# Checkin for current account
python3 -m open_bilibili_link checkin
```

#### Commands

```
gui ([OBL链接])  启动图形界面
login ([用户名] [密码]) (--login_type=cookie)  登录
checkin  直播中心签到
danmu [直播间ID] ([--output=stdout|file]) 直播弹幕鸡 -- 支持输出到文件 文件可在 OBS 中加载为聊天模式文本源
logout 退出登录
```

#### Cookie 登录流程

_如帐号密码登录异常请使用 Cookie 登录方式_

- F12 打开浏览器调试工具
- 进入 [直播个人中心](https://link.bilibili.com/p/center/index) 并登录
- 点击任意 XHR 类型请求，右侧 Request Header 请求头完整复制 Cookie
- 执行 `python3 -m open_bilibili_link login --login_type=cookie`
- 粘贴完整 Cookie 并回车
- 可执行 `python3 -m open_bilibili_link checkin` 测试签到接口是否正常
- 执行 `python3 -m open_bilibili_link gui` 打开图形界面

#### Features
- [x] 帐号密码登录
- [x] Cookie 登录
- [x] 直播签到
- [x] 用户基础信息
- [x] 直播间信息
- [x] 获取直播码
- [x] 开始和关闭直播
- [x] 生成 OBS 配置
- [x] 启动 OBS
- [x] 简单弹幕视图
- [x] 简单弹幕视图支持发送普通弹幕
- [ ] 弹幕颜色 字体大小 样式等等
- [x] 同步弹幕到文件 (OBS 可加载为弹幕视图)

More...

#### Structure
```text
├── LICENSE # LGPL3
├── open_bilibili_link # Package root
│   ├── __init__.py
│   ├── __main__.py # Starter file
│   ├── __meta__.py # Project meta constant
│   ├── models.py # Models from JSON string
│   ├── plugins # Plugin root
│   │   ├── __init__.py
│   │   └── test.py
│   ├── services.py # Bilibili API services
│   ├── utils.py # Some helper functions and classes
│   └── widgets # GUI root
│       ├── components # Components root 
│       │   ├── areas.py # Live area components
│       │   ├── button.py # Custom button components
│       │   ├── danmu.py # Danmu components
│       │   ├── dialog.py # Custom dialog
│       │   ├── __init__.py
│       │   ├── label.py # Custom label component
│       │   ├── live.py # Live control panel
│       │   ├── toast.py # Toast component support auto dismiss
│       │   └── usercard.py # Usercard components shows user infomations
│       ├── images # Image resources
│       │   └── bilibili.svg
│       ├── __init__.py
│       ├── main.py # Main window here
│       ├── menu.py # Left menu
│       ├── pages # Pages root
│       │   ├── home.py # Home page
│       │   ├── __init__.py
│       │   └── test.py # Test page
│       ├── routes.py # Router helper to load pages
│       └── styles # Qss files root
│           └── material.qss # Custom default dark theme
├── open-bilibili-link.iml # Project configuration for JetBrains IDE
├── Pipfile # pipenv configuration
└── README.md # Readme file
```

#### Powered by
- Qt5 & PyQt5 & asyncqt: _GUI & GUI asynchronous event loop_
- asyncio & aiohttp: _Asynchronous IO & network_
- rsa: _RSA encryption_
- pydantic: _JSON model & validation_
- pipenv(dev): _Virtualenv manager_

#### License
This project is licensed under [LGPL3](https://github.com/BruceZhang1993/open-bilibili-link/blob/master/LICENSE).
