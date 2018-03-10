import pytest

from aiohttp import web
from nccostorage.api import setup_bucket_api
from nccostorage.bucket import BucketOperations, DictionaryBucketStorage


def setup_dummy_app(loop):
    app = web.Application(loop=loop)
    storage = DictionaryBucketStorage(loop=loop)
    buckets = BucketOperations(storage)
    return setup_bucket_api(app, buckets)


@pytest.fixture
def app_client(loop, test_client):
    app = setup_dummy_app(loop)
    return loop.run_until_complete(test_client(app))


async def test_create_bucket_bad_json_request(app_client):
    # missing important keys
    resp = await app_client.post('/bucket', json={'some_crap': 23})
    assert resp.status == 400

    # crap json
    headers = {'Content-Type': 'application/json'}
    resp = await app_client.post('/bucket', data='{some_crap', headers=headers)
    assert resp.status == 400


async def test_create_bucket_invalid_request(app_client):
    resp = await app_client.post('/bucket', data={})
    assert resp.status == 400


async def test_create_bucket_success(app_client):
    resp = await app_client.post('/bucket', json={'id': 'my_bucket'})
    assert resp.status == 204

