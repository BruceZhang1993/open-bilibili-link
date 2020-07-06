import importlib

SCHEMA = 'obl://'


class RouteException(Exception):
    pass


class RouteManager:
    @staticmethod
    def parse_uri(uri: str):
        if not uri.startswith(SCHEMA):
            raise RouteException('Not a valid uri')
        segments = uri.replace(SCHEMA, '').split('/')
        module = importlib.import_module(f'{__package__}.pages.' + '.'.join(segments))
        return getattr(module, f'{segments[-1].capitalize()}Page')

    @staticmethod
    def get_uri_menu(uri: str):
        if not uri.startswith(SCHEMA):
            raise RouteException('Not a valid uri')
        segments = uri.replace(SCHEMA, '').split('/')
        if len(segments) < 1:
            return None
        return segments[0].lower()
