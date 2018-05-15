import logging

from aiohttp import web

from nccostorage.util import error_response


def create_error_handler(mappings):
    default_error_response = error_response(status=500, text='failed to process request')

    @web.middleware
    async def error_handler(request, handler):
        try:
            return await handler(request)
        except Exception as ex:
            response = mappings.get(type(ex), None)
            logger = logging.getLogger(__name__)
            if response is None:
                # this will generate a 500 so log it as well
                logger.error('msg="failed to process request"', exc_info=True)
                response = default_error_response
            else:
                logger.warn(f'msg="{ex}"')

            return response

    return error_handler
