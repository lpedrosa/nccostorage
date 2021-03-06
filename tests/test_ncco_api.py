import pytest
from aiohttp import web

from nccostorage import api, setup_middlewares
from nccostorage.bucket import BucketOperations, DictionaryBucketStorage
from nccostorage.renderer import Jinja2NccoRenderer


def setup_dummy_app():
    app = web.Application()
    storage = DictionaryBucketStorage()
    buckets = BucketOperations(storage)
    ncco_renderer = Jinja2NccoRenderer()

    api.bucket.setup_routes(app, buckets)
    api.ncco.setup_routes(app, buckets, ncco_renderer)
    setup_middlewares(app)
    return app


@pytest.fixture
def app_client(loop, aiohttp_client):
    app = setup_dummy_app()
    return loop.run_until_complete(aiohttp_client(app))


################
# Render Tests #
################
async def test_render_template_correctly(app_client):
    bucket_id = 'test_bucket'
    await app_client.post('/bucket', json={'id': bucket_id})

    ncco = '[{"action": "{{action_name}}"}]'
    req_body = {'ncco': ncco}

    resp = await app_client.post(f'/bucket/{bucket_id}/ncco', json=req_body)
    assert resp.status == 201

    body = await resp.json()
    ncco_id = body['ncco_id']

    params = {'action_name': 'connect'}
    resp = await app_client.get(f'/bucket/{bucket_id}/ncco/{ncco_id}/render', params=params)
    assert resp.status == 200

    body = await resp.json()
    expected_render = [{"action": "connect"}]
    assert body == expected_render


async def test_render_template_missing_attribute(app_client):
    bucket_id = 'test_bucket'
    await app_client.post('/bucket', json={'id': bucket_id})

    ncco = '[{"action": "{{action_name}}"}]'
    req_body = {'ncco': ncco}

    resp = await app_client.post(f'/bucket/{bucket_id}/ncco', json=req_body)
    assert resp.status == 201

    body = await resp.json()
    ncco_id = body['ncco_id']

    params = {'does_not_exist': 'foo'}
    resp = await app_client.get(f'/bucket/{bucket_id}/ncco/{ncco_id}/render', params=params)
    assert resp.status == 400


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


async def test_lookup_existing_ncco(app_client):
    bucket_id = 'test_bucket'
    await app_client.post('/bucket', json={'id': bucket_id})

    ncco = '[{"action": "{{action_name}}"}]'
    req_body = {'ncco': ncco}

    resp = await app_client.post(f'/bucket/{bucket_id}/ncco', json=req_body)
    assert resp.status == 201

    body = await resp.json()
    ncco_id = body['ncco_id']

    resp = await app_client.get(f'/bucket/{bucket_id}/ncco/{ncco_id}')
    assert resp.status == 200

    body = await resp.json()
    assert body.get('ncco_id') == ncco_id
    assert body.get('ncco') == ncco


#############
# Add Tests #
#############
async def test_add_ncco_response(app_client):
    bucket_id = 'test_bucket'
    await app_client.post('/bucket', json={'id': bucket_id})

    ncco = '[{"action": "record"}]'
    req_body = {'ncco': ncco}

    resp = await app_client.post(f'/bucket/{bucket_id}/ncco', json=req_body)

    assert resp.status == 201

    body = await resp.json()

    assert body.get('ncco_id') is not None
    assert body.get('ncco') == ncco


async def test_add_ncco_non_existing_bucket(app_client):
    bucket_id = 'test_bucket'
    ncco = '[{"action": "record"}]'
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
async def test_remove_non_existing_ncco(app_client):
    bucket_id = 'test_bucket'
    await app_client.post('/bucket', json={'id': bucket_id})

    ncco_id = 'some_id'

    resp = await app_client.delete(f'/bucket/{bucket_id}/ncco/{ncco_id}')

    assert resp.status == 404


async def test_remove_ncco_non_existing_bucket(app_client):
    bucket_id = 'test_bucket'
    ncco_id = 'some_id'

    resp = await app_client.delete(f'/bucket/{bucket_id}/ncco/{ncco_id}')

    assert resp.status == 404


async def test_remove_ncco_response(app_client):
    bucket_id = 'test_bucket'
    await app_client.post('/bucket', json={'id': bucket_id})

    ncco = '[{"action": "record"}]'
    req_body = {'ncco': ncco}

    resp = await app_client.post(f'/bucket/{bucket_id}/ncco', json=req_body)
    assert resp.status == 201

    body = await resp.json()
    ncco_id = body['ncco_id']

    resp = await app_client.delete(f'/bucket/{bucket_id}/ncco/{ncco_id}')

    assert resp.status == 204
