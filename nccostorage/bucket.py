import asyncio.locks as locks
from uuid import uuid4 as uuid

from prometheus_client import Gauge

from nccostorage.util import Observable


DEFAULT_TTL = 86400


def _bucket_key_for(name):
    return f'bucket_{name}'


class BucketStorageError(Exception):
    pass


class DuplicateBucketError(BucketStorageError):
    pass


class BucketStorageEventManager(object):

    def __init__(self):
        self.on_bucket_created = Observable()
        self.on_bucket_deleted = Observable()
        self.on_ncco_created = Observable()
        self.on_ncco_deleted = Observable()


class DictionaryBucketStorage(object):

    def __init__(self, loop=None):
        self._store = {}
        self._lock = locks.Lock(loop=loop)
        self.event_manager = BucketStorageEventManager()

    async def create(self, name, ttl=DEFAULT_TTL):
        bucket_data = dict()
        key = _bucket_key_for(name)

        async with self._lock:
            if key in self._store:
                raise DuplicateBucketError(f'duplicate bucket {name}')
            self._store[key] = bucket_data
            self.event_manager.on_bucket_created()

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
            self.event_manager.on_bucket_deleted()

        return name

    async def add_ncco(self, name, ncco):
        async with self._lock:
            bucket_data = self._store.get(_bucket_key_for(name))

            if bucket_data is None:
                raise BucketStorageError(f'non-existing bucket {name}')

            ncco_id = str(uuid())
            bucket_data[ncco_id] = ncco
            self.event_manager.on_ncco_created()

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

            self.event_manager.on_ncco_deleted()
            return bucket_data.pop(ncco_id, None)


class BucketOperations(object):

    def __init__(self, storage):
        self.storage = storage

    async def create(self, name, ttl=None):
        ttl = ttl or DEFAULT_TTL
        await self.storage.create(name, ttl=ttl)

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
