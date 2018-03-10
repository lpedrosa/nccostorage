"""
Application end to end scenarios
"""
from nccostorage import create_app


async def test_simple_storage_and_retrieval(test_client):
    config = {}
    client = await test_client(create_app(config))

    bucket_name = 'test_bucket'

    await create_bucket(client, bucket_name)

    test_ncco = [{
        "action": "connect",
        "eventUrl": ["https://example.com/events"],
        "from":"447700900000",
        "endpoint": [{
            "type": "phone",
            "number": "447700900001"
        }]
    }]

    ncco_id = await store_ncco(client, bucket_name, test_ncco)

    ncco = await lookup_ncco(client, bucket_name, ncco_id)

    assert ncco == test_ncco

    await remove_ncco(client, bucket_name, ncco_id)

    resp = await client.get(f'/bucket/{bucket_name}/ncco/{ncco_id}')

    assert resp.status == 404


#
# Helpers
#

async def create_bucket(app_client, bucket_name):
    resp = await app_client.post('/bucket', json={'id': bucket_name})

    assert resp.status == 204

async def store_ncco(app_client, bucket_name, ncco):
    resp = await app_client.post(f'/bucket/{bucket_name}/ncco', json=ncco)

    assert resp.status == 201

    resp_body = await resp.json()
    ncco_id = resp_body.get('ncco_id')

    assert ncco_id is not None

    return ncco_id

async def lookup_ncco(app_client, bucket_name, ncco_id):
    resp = await app_client.get(f'/bucket/{bucket_name}/ncco/{ncco_id}')

    assert resp.status == 200

    resp_body = await resp.json()

    return resp_body.get('ncco')

async def remove_ncco(app_client, bucket_name, ncco_id):
    resp = await app_client.delete(f'/bucket/{bucket_name}/ncco/{ncco_id}')

    assert resp.status == 204
