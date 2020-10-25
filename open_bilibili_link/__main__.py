import argparse
import asyncio
import inspect
import os
import sys
from asyncio import iscoroutinefunction
from pathlib import Path

import yaml
from aiocache import caches

from open_bilibili_link.cli import CliApp
from open_bilibili_link.logger import LogManager

PID_FILE = Path('/') / 'tmp' / 'obl.pid'
CACHE_CONFIG = Path(__file__).parent / 'configs' / 'cache.default.yaml'


def init():
    with CACHE_CONFIG.open('r') as f:
        caches.set_config(yaml.safe_load(f))
    parser = argparse.ArgumentParser(description='Open bilibili link')
    subparsers = parser.add_subparsers(help='Subcommands')
    gui_parser = subparsers.add_parser('gui', help='Gui mode')
    gui_parser.set_defaults(command='gui')
    gui_parser.add_argument('uri', nargs='?', help='uri')
    for i in filter(lambda property_: not property_.startswith('_'), dir(CliApp)):
        subp = subparsers.add_parser(i, help=f'Subcommand {i}')
        for param in inspect.signature(getattr(CliApp, i)).parameters.values():
            if param.name == 'self':
                continue
            if param.kind == param.KEYWORD_ONLY:
                subp.add_argument(f'--{param.name}', type=None if param.annotation == inspect.Parameter.empty else param.annotation,
                                  help=param.name, default=None if param.default == inspect.Parameter.empty else param.default)
            else:
                arg_ = {}
                if param.default is not None:
                    arg_['nargs'] = '?'
                subp.add_argument(param.name, **arg_, type=None if param.annotation == inspect.Parameter.empty else param.annotation,
                                  help=param.name, default=None if param.default == inspect.Parameter.empty else param.default)
        subp.set_defaults(command=i)
    return parser, parser.parse_args()


def main():
    parser, args = init()
    if not hasattr(args, 'command'):
        parser.print_help()
        sys.exit(0)
    if args.command != 'gui':
        try:
            fun = getattr(CliApp(args), args.command)
            params = vars(args)
            params.pop('command')
            if iscoroutinefunction(fun):
                loop = asyncio.get_event_loop()
                loop.run_until_complete(fun(**params))
            else:
                fun(**params)
            sys.exit(0)
        except AttributeError:
            LogManager.instance().error(f'未知命令: {args.uri}')
            sys.exit(1)
    if PID_FILE.exists():
        pid = PID_FILE.read_text()
        LogManager.instance().error(f'应用正在运行 {pid}')
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
        LogManager.instance().error(f'未知错误，请上报开发者 {str(err)}')
        PID_FILE.unlink(missing_ok=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
