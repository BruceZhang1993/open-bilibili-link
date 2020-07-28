import argparse
import asyncio
import os
import sys
from asyncio import iscoroutinefunction
from pathlib import Path

PID_FILE = Path('/') / 'tmp' / 'obl.pid'


def init():
    parser = argparse.ArgumentParser(description='Open bilibili link')
    parser.add_argument('--version', '-V', action='store_true', default=False, help='show version')
    parser.add_argument('--verbose', '-v', action='store_true', default=False, help='verbose mode')
    parser.add_argument('uri', nargs='?', help='uri')
    return parser.parse_args()


def main(args):
    if args.uri and not args.uri.startswith('obl://'):
        from open_bilibili_link.cli import CliApp
        try:
            fun = getattr(CliApp(args), args.uri)
            if iscoroutinefunction(fun):
                loop = asyncio.get_event_loop()
                loop.run_until_complete(fun())
            else:
                fun()
            sys.exit(0)
        except AttributeError:
            print(f'Unknown command: {args.uri}')
            sys.exit(1)
    if PID_FILE.exists():
        pid = PID_FILE.read_text()
        print(f'Already running on PID {pid}')
        sys.exit(0)
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()))
    try:
        import asyncqt
        from PyQt5.QtWidgets import QWidget, QMainWindow
        from open_bilibili_link.widgets.main import AppMainWindow
        app = asyncqt.QApplication(sys.argv)
        loop = asyncqt.QEventLoop(app)
        asyncio.set_event_loop(loop)
        win = AppMainWindow(app, args)
        win.show()
        with loop:
            r = loop.run_forever()
            PID_FILE.unlink(missing_ok=True)
            sys.exit(r)
    except Exception as err:
        print('Fatal error: ' + str(err))
        PID_FILE.unlink(missing_ok=True)
        sys.exit(1)


if __name__ == '__main__':
    main(init())
