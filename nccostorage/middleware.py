import logging

from aiohttp import web

from nccostorage.api.error import ApiError, to_response


def _lookup_handler(mappings, cls):
    for m_cls, handler in mappings.items():
        if isinstance(cls, m_cls):
            return handler
    return None


def create_error_handler(mappings):
    default_api_error = ApiError('failed to process request', status=500)

    @web.middleware
    async def error_handler(request, handler):
        try:
            return await handler(request)
        except Exception as ex:
            logger = logging.getLogger(__name__)
            error_handler = _lookup_handler(mappings, ex)

            if error_handler is None:
                # this will generate a 500 so log it as well
                logger.error(f'msg="internal error while handling request" error="{type(ex)}"', exc_info=True)
                response = to_response(default_api_error)
            else:
                response = error_handler(ex)
                logger.warn(f'msg="failed to process request" error="{response.text}"')
            return response

    return error_handler


def requires_json(handler):
    async def middleware(request):
        if request.content_type != 'application/json':
            return web.json_response({'status': 'error', 'text': 'request body must be json'}, status=400)

        return await handler(request)

    return middleware
