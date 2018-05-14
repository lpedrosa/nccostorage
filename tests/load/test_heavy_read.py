import asyncio
import argparse
import collections
import os
import uuid

import aiohttp

Config = collections.namedtuple('Config', ['url', 'read_concurrency', 'runs', 'load_rate'])


def read_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', help='target url of the load test', default='http://localhost:8080')
    parser.add_argument('--read_concurrency', type=int, help='number of concurrent reader', default=10)
    parser.add_argument('--runs', type=int, help='number of times single test is run', default=100)
    parser.add_argument('--rate', type=float, help='time in seconds to wait before firing the next test', default=2.0)

    args = parser.parse_args()

    return Config(url=args.target, read_concurrency=args.read_concurrency, runs=args.runs, load_rate=args.rate)


async def read_ncco(session, url, bucket_id, ncco_id):
    render_url = f'{url}/bucket/{bucket_id}/ncco/{ncco_id}/render'
    await session.get(render_url)


async def load_job(session, url, read_concurrency):
    # Create bucket
    create_bucket_url = f'{url}/bucket'
    bucket_id = str(uuid.uuid4())
    await session.post(create_bucket_url, json={'id': bucket_id})

    # Create NCCO
    ncco_body = {'ncco': '[{"action": "talk", "text": "Hello World!"}]'}
    create_ncco_url = f'{url}/bucket/{bucket_id}/ncco'

    res = await session.post(create_ncco_url, json=ncco_body)

    res_json = await res.json()
    ncco_id = res_json['ncco_id']

    # spin read_concurrency readers
    outstanding = []
    for _ in range(read_concurrency):
        task = asyncio.ensure_future(read_ncco(session, url, bucket_id, ncco_id))
        outstanding.append(task)

    # wait for readers
    await asyncio.gather(*outstanding)

    # delete bucket
    await session.delete(f'{url}/bucket/{bucket_id}')


async def run_test(config):
    # spin a load job every load_rate seconds
    outstanding = []

    async with aiohttp.ClientSession(raise_for_status=True) as session:
        for _ in range(config.runs):
            task = asyncio.ensure_future(load_job(session, config.url, config.read_concurrency))
            outstanding.append(task)
            asyncio.sleep(config.load_rate)

        await asyncio.gather(*outstanding)


def main():
    config = read_config()

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run_test(config))
    loop.run_until_complete(future)


if __name__ == '__main__':
    main()
