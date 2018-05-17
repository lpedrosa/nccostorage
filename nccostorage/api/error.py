from aiohttp import web


class ApiError(Exception):

    def __init__(self, text, status=400):
        self.text = text
        self.status = status


def to_response(api_error):
    api_response = {'status': 'error', 'text': api_error.text}
    return web.json_response(api_response, status=api_error.status)
