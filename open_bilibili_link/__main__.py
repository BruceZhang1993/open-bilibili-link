import argparse
import asyncio
import sys

import asyncqt
from PyQt5.QtWidgets import QWidget, QMainWindow

from open_bilibili_link.widgets.main import AppMainWindow


def init():
    parser = argparse.ArgumentParser(description='Open bilibili link')
    parser.add_argument('--version', '-V', action='store_true', default=False, help='show version')
    parser.add_argument('--verbose', '-v', action='store_true', default=False, help='verbose mode')
    parser.add_argument('uri', nargs='?', help='uri')
    return parser.parse_args()


def main(args):
    app = asyncqt.QApplication(sys.argv)
    loop = asyncqt.QEventLoop(app)
    asyncio.set_event_loop(loop)
    win = AppMainWindow(app, args)
    win.show()
    with loop:
        sys.exit(loop.run_forever())


if __name__ == '__main__':
    main(init())
