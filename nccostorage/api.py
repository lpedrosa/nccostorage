import json

from aiohttp import web

from nccostorage.bucket import BucketOperations, DuplicateBucketError
from nccostorage.renderer import RenderError
from nccostorage.util import error_response


def validate_ttl(ttl):
    if ttl is None or ttl < 60:
        return 60
    elif ttl > 86400:
        return 86400
    else:
        return ttl


async def create_bucket(request):
    body = await request.json()
    bucket_name = body.get('id')
    ttl = validate_ttl(body.get('ttl'))

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


async def add_ncco_to_bucket(request):
    bucket_id = request.match_info['bucket_id']

    buckets: BucketOperations = request.app['buckets']
    bucket = await buckets.lookup(bucket_id)
    if bucket is None:
        return error_response(status=404, text=f'bucket with id {bucket_id} not found')

    body = await request.json()

    ncco = body.get('ncco')
    if ncco is None:
        return error_response(status=400, text="missing 'ncco' in request body")

    ncco_str = str(ncco)
    ncco_id = await bucket.add(ncco_str)

    res_body = {
        'ncco_id': ncco_id,
        'ncco': ncco_str
    }

    return web.Response(status=201, text=json.dumps(res_body), content_type='application/json')


async def lookup_ncco(request):
    bucket_id = request.match_info['bucket_id']

    buckets: BucketOperations = request.app['buckets']
    bucket = await buckets.lookup(bucket_id)
    if bucket is None:
        return error_response(status=404, text=f'bucket with id {bucket_id} not found')

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

    buckets: BucketOperations = request.app['buckets']
    bucket = await buckets.lookup(bucket_id)
    if bucket is None:
        return error_response(status=404, text=f'bucket with id {bucket_id} not found')

    ncco_id = request.match_info['ncco_id']
    if await bucket.remove(ncco_id) is None:
        return error_response(status=404, text=f'ncco with id {ncco_id} not found')

    return web.Response(status=204)


async def render_ncco(request):
    bucket_id = request.match_info['bucket_id']

    buckets: BucketOperations = request.app['buckets']
    bucket = await buckets.lookup(bucket_id)
    if bucket is None:
        return error_response(status=404, text=f'bucket with id {bucket_id} not found')

    ncco_id = request.match_info['ncco_id']
    ncco = await bucket.lookup(ncco_id)

    if ncco is None:
        return error_response(status=404, text=f'ncco with id {ncco_id} not found')

    ncco_renderer = request.app['ncco_renderer']
    query_params = request.query

    try:
        result = ncco_renderer.render(ncco, query_params)
    except RenderError:
        return error_response(status=400, text=f'missing params while rendering ncco with id {ncco_id}')

    try:
        resp = json.loads(result)
    except json.decoder.JSONDecodeError:
        return error_response(status=400, text=f'rendered ncco is not valid json')

    return web.Response(status=200, text=json.dumps(resp), content_type='application/json')


def requires_json(handler):
    async def middleware(request):
        if request.content_type != 'application/json':
            return error_response(status=400, text='request body must be json')

        return await handler(request)

    return middleware


def setup_bucket_api(app, buckets):
    _wire_bucket_operations(app, buckets)

    app.router.add_post('/bucket', requires_json(create_bucket))
    app.router.add_delete('/bucket/{bucket_id}', remove_bucket)

    return app


def setup_ncco_api(app, buckets, ncco_renderer):
    _wire_bucket_operations(app, buckets)
    app['ncco_renderer'] = ncco_renderer

    app.router.add_post('/bucket/{bucket_id}/ncco', add_ncco_to_bucket)
    app.router.add_get('/bucket/{bucket_id}/ncco/{ncco_id}', lookup_ncco)
    app.router.add_delete('/bucket/{bucket_id}/ncco/{ncco_id}', remove_ncco)
    app.router.add_get('/bucket/{bucket_id}/ncco/{ncco_id}/render', render_ncco)

    return app


def _wire_bucket_operations(app, buckets):
    if app.get('buckets') is None:
        app['buckets'] = buckets
