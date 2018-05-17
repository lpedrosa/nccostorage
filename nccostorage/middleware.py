import logging

from aiohttp import web


def create_error_handler(mappings):
    default_error_response = {'status': 'error', 'text': 'failed to process request'}

    @web.middleware
    async def error_handler(request, handler):
        try:
            return await handler(request)
        except Exception as ex:
            logger = logging.getLogger(__name__)
            response = mappings.get(type(ex), None)
            if response is None:
                # this will generate a 500 so log it as well
                logger.error(f'msg="failed to process request error={type(ex)}"', exc_info=True)
                response = web.json_response(default_error_response, status=500)
            else:
                logger.warn(f'msg="{ex}"')
                response = web.json_response(response['json'], status=response['code'])
            return response

    return error_handler
