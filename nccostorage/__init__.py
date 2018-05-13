import json

from aiohttp import web
from prometheus_async import aio

from nccostorage import api
from nccostorage.bucket import BucketOperations, DictionaryBucketStorage
from nccostorage.bucket.instrumentation import InstrumentedBucketStorage
from nccostorage.renderer import Jinja2NccoRenderer
from nccostorage.renderer.instrumentation import InstrumentedRenderer


def create_app(config):
    loop = config.get('loop', None)

    app = web.Application(loop=loop)

    storage = InstrumentedBucketStorage(DictionaryBucketStorage(loop=loop))
    buckets = BucketOperations(storage)
    ncco_renderer = InstrumentedRenderer(Jinja2NccoRenderer())

    # bucket operations
    api.setup_bucket_api(app, buckets)
    # ncco operations
    api.setup_ncco_api(app, buckets, ncco_renderer)

    app.router.add_get('/metrics', aio.web.server_stats)

    return app
