import importlib

from open_bilibili_link.logger import LogManager

SCHEMA = 'obl://'
DEFAULT = 'home'


class RouteException(Exception):
    pass


class RouteManager:
    @staticmethod
    def parse_uri(uri: str):
        try:
            if not uri.startswith(SCHEMA):
                raise RouteException('Not a valid uri')
            segments = uri.replace(SCHEMA, '').split('/')
            module = importlib.import_module(f'{__package__}.pages.' + '.'.join(segments))
            return getattr(module, f'{segments[-1].capitalize()}Page')
        except ImportError as e:
            LogManager.instance().warning(f'Unknown uri: {uri}: {str(e)}')
            LogManager.instance().warning(f'trying default: {SCHEMA + DEFAULT}')
            return RouteManager.parse_uri(SCHEMA + DEFAULT)

    @staticmethod
    def get_uri_menu(uri: str):
        if not uri.startswith(SCHEMA):
            raise RouteException('Not a valid uri')
        segments = uri.replace(SCHEMA, '').split('/')
        if len(segments) < 1:
            return None
        return segments[0].lower()
