import asyncio.locks as locks
from uuid import uuid4 as uuid

DEFAULT_TTL = 86400


def _bucket_key_for(name):
    return f'bucket_{name}'


class BucketStorageError(Exception):
    pass

class DictionaryBucketStorage(object):

    def __init__(self, loop=None):
        self._store = {}
        self._lock = locks.Lock(loop=loop)

    async def create(self, name, ttl=DEFAULT_TTL):
        bucket_data = dict()
        key = _bucket_key_for(name)

        async with self._lock:
            if key in self._store:
                raise BucketStorageError(f'duplicate bucket {name}')
            self._store[key] = bucket_data

        return name

    async def exists(self, name):
        key = _bucket_key_for(name)
        async with self._lock:
            return key in self._store

    async def remove(self, name):
        bucket_key = _bucket_key_for(name)
        async with self._lock:
            if bucket_key not in self._store:
                return None
            del self._store[bucket_key]

        return name

    async def add_ncco(self, name, ncco):
        async with self._lock:
            bucket_data = self._store.get(_bucket_key_for(name))

            if bucket_data is None:
                raise BucketStorageError(f'non-existing bucket {name}')

            ncco_id = str(uuid())
            bucket_data[ncco_id] = ncco

            return ncco_id

    async def get_ncco(self, name, ncco_id):
        async with self._lock:
            bucket_data = self._store.get(_bucket_key_for(name))
            if bucket_data is None:
                raise BucketStorageError(f'non-existing bucket {name}')

            return bucket_data.get(ncco_id)

    async def remove_ncco(self, name, ncco_id):
        async with self._lock:
            bucket_data = self._store.get(_bucket_key_for(name))
            if bucket_data is None:
                raise BucketStorageError(f'non-existing bucket {name}')

            return bucket_data.pop(ncco_id, None)

class BucketOperations(object):

    def __init__(self, storage):
        self.storage = storage

    async def create(self, name, ttl=DEFAULT_TTL):
        try:
            await self.storage.create(name, ttl=ttl)
        except BucketStorageError:
            return None

        return Bucket(name, self.storage)

    async def lookup(self, name):
        if await self.storage.exists(name):
            return Bucket(name, self.storage)

        return None

class Bucket(object):

    def __init__(self, name, storage):
        self.name = name
        self.storage = storage

    async def add(self, ncco):
        return await self.storage.add_ncco(self.name, ncco)

    async def remove(self, ncco_id):
        return await self.storage.remove_ncco(self.name, ncco_id)

    async def lookup(self, ncco_id):
        return await self.storage.get_ncco(self.name, ncco_id)
