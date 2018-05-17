import json

from aiohttp import web

from nccostorage.api import error
from nccostorage.bucket import BucketOperations
from nccostorage.renderer import RenderError


async def add_ncco_to_bucket(request):
    bucket_id = request.match_info['bucket_id']

    buckets: BucketOperations = request.app['buckets']
    bucket = await buckets.lookup(bucket_id)
    if bucket is None:
        raise error.ApiError(status=404, text=f'bucket with id {bucket_id} not found')

    body = await request.json()

    ncco = body.get('ncco')
    if ncco is None:
        raise error.ApiError(status=400, text="missing 'ncco' in request body")

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
        raise error.ApiError(status=404, text=f'bucket with id {bucket_id} not found')

    ncco_id = request.match_info['ncco_id']
    ncco = await bucket.lookup(ncco_id)

    if ncco is None:
        raise error.ApiError(status=404, text=f'ncco with id {ncco_id} not found')

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
        raise error.ApiError(status=404, text=f'bucket with id {bucket_id} not found')

    ncco_id = request.match_info['ncco_id']
    if await bucket.remove(ncco_id) is None:
        raise error.ApiError(status=404, text=f'ncco with id {ncco_id} not found')

    return web.Response(status=204)


async def render_ncco(request):
    bucket_id = request.match_info['bucket_id']

    buckets: BucketOperations = request.app['buckets']
    bucket = await buckets.lookup(bucket_id)
    if bucket is None:
        raise error.ApiError(status=404, text=f'bucket with id {bucket_id} not found')

    ncco_id = request.match_info['ncco_id']
    ncco = await bucket.lookup(ncco_id)

    if ncco is None:
        raise error.ApiError(status=404, text=f'ncco with id {ncco_id} not found')

    ncco_renderer = request.app['ncco_renderer']
    query_params = request.query

    try:
        result = ncco_renderer.render(ncco, query_params)
    except RenderError:
        raise error.ApiError(status=400, text=f'missing params while rendering ncco with id {ncco_id}')

    try:
        resp = json.loads(result)
    except json.decoder.JSONDecodeError:
        raise error.ApiError(status=400, text=f'rendered ncco is not valid json')

    return web.Response(status=200, text=json.dumps(resp), content_type='application/json')


def setup_routes(app, buckets, ncco_renderer):
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
