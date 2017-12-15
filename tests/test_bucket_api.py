import pytest

from nccostorage import create_app


@pytest.fixture
def app_client(loop, test_client):
    return loop.run_until_complete(test_client(create_app))


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

