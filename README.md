#### Open Bilibili Link
Working in progress

##### Development
```shell script
pipenv install
python3 -m open_bilibili_link
```

##### Structure
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

##### Powered by
- Qt5 & PyQt5 & asyncqt: _GUI & GUI asynchronous event loop_
- asyncio & aiohttp: _Asynchronous IO & network_
- rsa: _RSA encryption_
- pydantic: _JSON model & validation_
- pipenv(dev): _Virtualenv manager_

##### License
This project is licensed under [LGPL3](https://github.com/BruceZhang1993/open-bilibili-link/blob/master/LICENSE).