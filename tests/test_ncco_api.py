import pytest

from aiohttp import web
from nccostorage.api import setup_bucket_api, setup_ncco_api
from nccostorage.bucket import BucketOperations, DictionaryBucketStorage


def setup_dummy_app(loop):
    app = web.Application(loop=loop)
    storage = DictionaryBucketStorage(loop=loop)
    buckets = BucketOperations(storage)

    setup_bucket_api(app, buckets)
    setup_ncco_api(app, buckets)
    return app


@pytest.fixture
def app_client(loop, test_client):
    app = setup_dummy_app(loop)
    return loop.run_until_complete(test_client(app))

################
# Lookup Tests #
################
async def test_lookup_unknown_ncco(app_client):
    bucket_id = 'test_bucket'
    await app_client.post('/bucket', json={'id': bucket_id})

    ncco_id = 'some_id'
    resp = await app_client.get(f'/bucket/{bucket_id}/ncco/{ncco_id}')

    assert resp.status == 404

async def test_lookup_ncco_non_existing_bucket(app_client):
    bucket_id = 'test_bucket'
    ncco_id = 'some_id'
    resp = await app_client.get(f'/bucket/{bucket_id}/ncco/{ncco_id}')

    assert resp.status == 404

#############
# Add Tests #
#############
async def test_add_ncco_response(app_client):
    bucket_id = 'test_bucket'
    await app_client.post('/bucket', json={'id': bucket_id})

    ncco = [{"action": "record"}]
    req_body = {'ncco': ncco}

    resp = await app_client.post(f'/bucket/{bucket_id}/ncco', json=req_body)

    assert resp.status == 201

    body = await resp.json()

    assert body.get('ncco_id') is not None
    assert body.get('ncco') == ncco


async def test_add_ncco_non_existing_bucket(app_client):
    bucket_id = 'test_bucket'
    ncco = [{"action": "record"}]
    req_body = {'ncco': ncco}

    resp = await app_client.post(f'/bucket/{bucket_id}/ncco', json=req_body)

    assert resp.status == 404


async def test_add_ncco_invalid_body(app_client):
    bucket_id = 'test_bucket'
    await app_client.post('/bucket', json={'id': bucket_id})

    resp = await app_client.post(f'/bucket/{bucket_id}/ncco', json={'invalid': 'stuff'})
    assert resp.status == 400


################
# Remove Tests #
################
async def test_remove_ncco_response(app_client):
    bucket_id = 'test_bucket'
    await app_client.post('/bucket', json={'id': bucket_id})

    ncco_id = 'some_id'

    resp = await app_client.delete(f'/bucket/{bucket_id}/ncco/{ncco_id}')

    assert resp.status == 204

async def test_remove_ncco_non_existing_bucket(app_client):
    bucket_id = 'test_bucket'
    ncco_id = 'some_id'

    resp = await app_client.delete(f'/bucket/{bucket_id}/ncco/{ncco_id}')

    assert resp.status == 404