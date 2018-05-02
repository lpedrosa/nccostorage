import json

from aiohttp import web
from prometheus_async import aio
from prometheus_client import Gauge

from nccostorage import api
from nccostorage.bucket import BucketOperations, DictionaryBucketStorage
from nccostorage.renderer import Jinja2NccoRenderer


def instrument_storage(storage):

    # pylint: disable-msg=no-value-for-parameter
    LIVE_BUCKETS = Gauge('bucket_count', 'number of live buckets in storage')
    # pylint: disable-msg=no-value-for-parameter
    LIVE_NCCOS = Gauge('ncco_count', 'number of live nccos in storage')

    storage.event_manager.on_bucket_created += lambda: LIVE_BUCKETS.inc()
    storage.event_manager.on_bucket_deleted += lambda: LIVE_BUCKETS.dec()
    storage.event_manager.on_ncco_created += lambda: LIVE_NCCOS.inc()
    storage.event_manager.on_ncco_deleted += lambda: LIVE_NCCOS.dec()

    return storage


def create_app(config):
    loop = config.get('loop', None)

    app = web.Application(loop=loop)

    storage = instrument_storage(DictionaryBucketStorage(loop=loop))
    buckets = BucketOperations(storage)
    ncco_renderer = Jinja2NccoRenderer()

    # bucket operations
    api.setup_bucket_api(app, buckets)
    # ncco operations
    api.setup_ncco_api(app, buckets, ncco_renderer)

    app.router.add_get('/metrics', aio.web.server_stats)

    return app
