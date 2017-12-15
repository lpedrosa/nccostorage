import pytest

from nccostorage import create_app


@pytest.fixture
def app_client(loop, test_client):
    return loop.run_until_complete(test_client(create_app))


async def test_lookup_unknown_ncco(app_client):
    bucket_id = 'test_bucket'
    await app_client.post('/bucket', json={'id': bucket_id})

    ncco_id = 'some_id'
    resp = await app_client.get(f'/bucket/{bucket_id}/ncco/{ncco_id}')

    assert resp.status == 404


async def test_add_ncco_response(app_client):
    bucket_id = 'test_bucket'
    await app_client.post('/bucket', json={'id': bucket_id})

    ncco = [{"action": "record"}]

    resp = await app_client.post(f'/bucket/{bucket_id}/ncco', json=ncco)

    assert resp.status == 201

    body = await resp.json()

    assert body.get('ncco_id') is not None
    assert body.get('ncco') == ncco


async def test_remove_ncco_response(app_client):
    bucket_id = 'test_bucket'
    await app_client.post('/bucket', json={'id': bucket_id})

    ncco_id = 'some_id'

    resp = await app_client.delete(f'/bucket/{bucket_id}/ncco/{ncco_id}')

    assert resp.status == 204
