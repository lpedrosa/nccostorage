import json

from aiohttp import web

from nccostorage.bucket import BucketOperations, DictionaryBucketStorage
from nccostorage.ncco import validate


async def index(request):
    return web.Response(text='Hello Aiohttp!')


async def create_bucket(request):
    body = await request.json()
    bucket_name = body.get('id')

    if bucket_name is None:
        return error_response(status=400, text="missing 'id' in request body")

    bucket_ops: BucketOperations = request.app['bucket_ops']
    await bucket_ops.create(bucket_name)

    return web.Response(status=204)


async def add_ncco_to_bucket(request):
    bucket_id = request.match_info['bucket_id']

    bucket_ops: BucketOperations = request.app['bucket_ops']
    bucket = await bucket_ops.lookup(bucket_id)

    ncco = await request.json()
    try:
        ncco = validate(ncco)
    except Exception:
        return web.Response(status=400, text='Failed to validate NCCO')

    ncco_id = await bucket.add(ncco)

    res_body = {
        'ncco_id': ncco_id,
        'ncco': ncco
    }

    return web.Response(status=201, text=json.dumps(res_body), content_type='application/json')


async def lookup_ncco(request):
    bucket_id = request.match_info['bucket_id']

    bucket_ops: BucketOperations = request.app['bucket_ops']
    bucket = await bucket_ops.lookup(bucket_id)

    ncco_id = request.match_info['ncco_id']
    ncco = await bucket.lookup(ncco_id)

    if ncco is None:
        return error_response(status=404, text=f'ncco with id {ncco_id} not found')

    res_body = {
        'ncco_id': ncco_id,
        'ncco': ncco,
    }

    return web.Response(text=json.dumps(res_body), content_type='application/json')


async def remove_ncco(request):
    bucket_id = request.match_info['bucket_id']

    bucket_ops: BucketOperations = request.app['bucket_ops']
    bucket = await bucket_ops.lookup(bucket_id)

    ncco_id = request.match_info['ncco_id']
    await bucket.remove(ncco_id)

    return web.Response(status=204)


#
# web helpers
#
def error_response(status=None, text=None):
    if not 399 < status < 600:
        raise ValueError('status must be a valid HTTP error code')

    body = json.dumps({'status': 'error', 'text': text})
    content_type = 'application/json'
    return web.Response(status=status, text=body, content_type=content_type)


def requires_json(handler):
    async def middleware(request):
        if request.content_type != 'application/json':
            return error_response(status=400, text='request body must be json')
        try:
            return await handler(request)
        except json.decoder.JSONDecodeError:
            return error_response(status=400, text='request body must be json')
    return middleware


def create_app(args, loop=None):
    app = web.Application(loop=loop)

    storage = DictionaryBucketStorage(loop=loop)
    app['bucket_ops'] = BucketOperations(storage)

    app.router.add_get('/', index)

    # bucket operations
    app.router.add_post('/bucket', requires_json(create_bucket))

    # ncco operations
    app.router.add_post('/bucket/{bucket_id}/ncco', add_ncco_to_bucket)
    app.router.add_get('/bucket/{bucket_id}/ncco/{ncco_id}', lookup_ncco)
    app.router.add_delete('/bucket/{bucket_id}/ncco/{ncco_id}', remove_ncco)

    return app
