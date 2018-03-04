import asyncio.locks as locks
from uuid import uuid4 as uuid

DEFAULT_TTL = 86400


def _bucket_key_for(name):
    return f'bucket_{name}'


class BucketOperations(object):

    def __init__(self, storage):
        self.storage = storage

    async def create(self, name, ttl=DEFAULT_TTL):
        bucket_data = dict()
        await self.storage.write_if_absent(_bucket_key_for(name), bucket_data)
        return Bucket(name, self)

    async def lookup(self, name):
        bucket = await self.storage.lookup(_bucket_key_for(name))
        if bucket is None:
            return None

        return Bucket(name, self)

    async def add_ncco(self, bucket_name, ncco, ttl=DEFAULT_TTL):
        ncco_id = str(uuid())

        def update_func(bucket_data, ncco):
            bucket_data[ncco_id] = ncco
            return bucket_data

        key_name = _bucket_key_for(bucket_name)
        await self.storage.update(key_name, ncco, update_func)
        return ncco_id

    async def remove_ncco(self, bucket_name, ncco_id):
        def update_func(bucket_data, _):
            bucket_data.pop(ncco_id, None)
            return bucket_data

        key_name = _bucket_key_for(bucket_name)
        await self.storage.update(key_name, None, update_func)

    async def lookup_ncco(self, bucket_name, ncco_id):
        key_name = _bucket_key_for(bucket_name)
        bucket_data = await self.storage.read(key_name)
        ncco = bucket_data.get(ncco_id)
        return ncco

class Bucket(object):

    def __init__(self, name, bucket_operations: BucketOperations):
        self.name = name
        self.buckets = bucket_operations

    async def add(self, ncco, **kwargs):
        return await self.buckets.add_ncco(self.name, ncco, kwargs)

    async def remove(self, ncco_id):
        await self.buckets.remove_ncco(self.name, ncco_id)

    async def lookup(self, ncco_id):
        return await self.buckets.lookup_ncco(self.name, ncco_id)
