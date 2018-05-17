import json

from aiohttp import web

from nccostorage.bucket import BucketOperations, DuplicateBucketError
from nccostorage.middleware import requires_json
from nccostorage.util import error_response


def _validate_ttl(ttl):
    if ttl is None or ttl < 60:
        return 60
    elif ttl > 86400:
        return 86400
    else:
        return ttl


async def create_bucket(request):
    body = await request.json()
    bucket_name = body.get('id')
    ttl = _validate_ttl(body.get('ttl'))

    if bucket_name is None:
        return error_response(status=400, text="missing 'id' in request body")

    buckets: BucketOperations = request.app['buckets']
    try:
        await buckets.create(bucket_name, ttl=ttl)
    except DuplicateBucketError:
        return error_response(status=409, text=f'bucket with id {bucket_name} already exists')

    res_body = {
        'id': bucket_name,
        'ttl': ttl
    }
    return web.Response(status=201, text=json.dumps(res_body), content_type='application/json')


async def remove_bucket(request):
    bucket_id = request.match_info['bucket_id']

    buckets: BucketOperations = request.app['buckets']
    bucket_name = await buckets.remove(bucket_id)
    if bucket_name is None:
        return error_response(status=404, text=f'bucket with id {bucket_id} not found')

    return web.Response(status=204)


def setup_routes(app, buckets):
    _wire_bucket_operations(app, buckets)

    app.router.add_post('/bucket', requires_json(create_bucket))
    app.router.add_delete('/bucket/{bucket_id}', remove_bucket)

    return app


def _wire_bucket_operations(app, buckets):
    if app.get('buckets') is None:
        app['buckets'] = buckets
