import asyncio.locks as locks
from uuid import uuid4 as uuid

from prometheus_client import Gauge


DEFAULT_TTL = 86400


def _bucket_key_for(name):
    return f'bucket_{name}'


class BucketStorageError(Exception):
    pass


class DuplicateBucketError(BucketStorageError):
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
                raise DuplicateBucketError(f'duplicate bucket {name}')
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


class InstrumentedBucketStorage(object):

    # pylint: disable-msg=no-value-for-parameter
    LIVE_BUCKETS = Gauge('bucket_count', 'number of live buckets in storage')
    # pylint: disable-msg=no-value-for-parameter
    LIVE_NCCOS = Gauge('ncco_count', 'number of live nccos in storage')

    def __init__(self, storage):
        self.storage = storage

    async def create(self, name, ttl=DEFAULT_TTL):
        result = await self.storage.create(name, ttl)
        InstrumentedBucketStorage.LIVE_BUCKETS.inc()
        return result

    async def exists(self, name):
        return await self.storage.exists(name)

    async def remove(self, name):
        result = await self.storage.remove(name)
        InstrumentedBucketStorage.LIVE_BUCKETS.dec()
        return result

    async def add_ncco(self, name, ncco):
        result = await self.storage.add_ncco(name, ncco)
        InstrumentedBucketStorage.LIVE_NCCOS.inc()
        return result

    async def get_ncco(self, name, ncco_id):
        return await self.storage.get_ncco(name, ncco_id)

    async def remove_ncco(self, name, ncco_id):
        result = await self.storage.remove_ncco(name, ncco_id)
        InstrumentedBucketStorage.LIVE_NCCOS.dec()
        return result


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
