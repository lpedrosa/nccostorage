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
    bucket_id = 'my_bucket'
    bucket_ttl = 360
    resp = await app_client.post('/bucket', json={'id': bucket_id, 'ttl': bucket_ttl})
    assert resp.status == 201
    body = await resp.json()
    assert body['id'] == bucket_id
    assert body['ttl'] == bucket_ttl


async def test_create_bucket_ttl_range(app_client):
    ttl_test_ranges = [
        ('min_ttl', 10, 60),
        ('max_ttl', 99999, 86400),
        ('no_ttl', None, 60),
    ]

    for bucket_id, ttl, expected_ttl in ttl_test_ranges:
        req_body = dict()
        req_body['id'] = bucket_id
        if ttl is not None:
            req_body['ttl'] = ttl

        resp = await app_client.post('/bucket', json=req_body)
        assert resp.status == 201

        body = await resp.json()
        assert body['id'] == bucket_id
        assert body['ttl'] == expected_ttl, f'unexpected ttl for {bucket_id}'


async def test_create_bucket_already_exists(app_client):
    resp = await app_client.post('/bucket', json={'id': 'my_bucket'})
    assert resp.status == 201
    resp = await app_client.post('/bucket', json={'id': 'my_bucket'})
    assert resp.status == 409


async def test_delete_bucket_not_existing(app_client):
    non_existing_bucket_id = 'idontexist'
    resp = await app_client.delete(f'/bucket/{non_existing_bucket_id}')
    assert resp.status == 404


async def test_delete_bucket_success(app_client):
    bucket_id = 'my_bucket'
    bucket_ttl = 360
    resp = await app_client.post('/bucket', json={'id': bucket_id, 'ttl': bucket_ttl})
    assert resp.status == 201

    resp = await app_client.delete(f'/bucket/{bucket_id}')
    assert resp.status == 204
