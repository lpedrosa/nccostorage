import json

from aiohttp import web


class Observable(object):
    def __init__(self):
        self._susbcribers = []

    def __call__(self, *args, **kwargs):
        for sub in self._susbcribers:
            sub(*args, **kwargs)

    def __iadd__(self, other):
        self._susbcribers.append(other)
        return self

    def __isub__(self, other):
        self._susbcribers.remove(other)
        return self


def error_response(status=None, text=None):
    if not 399 < status < 600:
        raise ValueError('status must be a valid HTTP error code')

    body = json.dumps({'status': 'error', 'text': text})
    content_type = 'application/json'
    return web.Response(status=status, text=body, content_type=content_type)
