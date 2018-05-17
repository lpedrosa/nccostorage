import logging
import sys

from aiohttp import web
from prometheus_async import aio

from nccostorage import api, middleware
from nccostorage.bucket import BucketOperations, DictionaryBucketStorage
from nccostorage.bucket.instrumentation import InstrumentedBucketStorage
from nccostorage.renderer import Jinja2NccoRenderer
from nccostorage.renderer.instrumentation import InstrumentedRenderer


def configure_logging():
    logger = logging.getLogger(__name__)

    # setup stdout handler
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(logging.INFO)

    # setup formatter
    formatter = logging.Formatter(
        fmt='ts=%(asctime)s,%(msecs)d lvl=%(levelname)s caller=%(filename)s:%(lineno)d %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S')
    handler.setFormatter(formatter)

    logger.addHandler(handler)


def setup_middlewares(app):
    import json

    error_middleware = middleware.create_error_handler({
        json.decoder.JSONDecodeError: {'code': 400, 'json': {'status': 'error', 'text': 'request body must be json'}}
    })

    app.middlewares.append(error_middleware)


def create_app(config):
    loop = config.get('loop', None)

    configure_logging()

    app = web.Application(loop=loop)

    storage = InstrumentedBucketStorage(DictionaryBucketStorage(loop=loop))
    buckets = BucketOperations(storage)
    ncco_renderer = InstrumentedRenderer(Jinja2NccoRenderer())

    # bucket operations
    api.bucket.setup_routes(app, buckets)
    # ncco operations
    api.ncco.setup_routes(app, buckets, ncco_renderer)

    app.router.add_get('/metrics', aio.web.server_stats)

    setup_middlewares(app)

    return app
