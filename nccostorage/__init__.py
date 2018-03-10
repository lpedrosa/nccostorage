import json

from aiohttp import web

from nccostorage import api
from nccostorage.bucket import BucketOperations, DictionaryBucketStorage


def create_app(config):
    loop = config.get('loop', None)

    app = web.Application(loop=loop)

    storage = DictionaryBucketStorage(loop=loop)
    app['buckets'] = BucketOperations(storage)

    # bucket operations
    api.setup_bucket_api(app)
    # ncco operations
    api.setup_ncco_api(app)

    return app
