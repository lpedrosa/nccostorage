from uuid import uuid4 as uuid

DEFAULT_TTL = 86400
BUCKET_KEY_FORMAT = 'bucket_{name}'


def _bucket_key_for(name):
    return BUCKET_KEY_FORMAT.format(name=name)


class BucketOperations(object):

    def __init__(self, storage):
        self.storage = storage

    async def create(self, name, ttl=DEFAULT_TTL):
        bucket_data = dict()
        await self.storage.write(_bucket_key_for(name), bucket_data)
        return Bucket(name, self.storage)

    async def lookup(self, name):
        bucket = await self.storage.lookup(_bucket_key_for(name))
        if bucket is None:
            return None

        return Bucket(name, self.storage)


class Bucket(object):

    def __init__(self, name, storage):
        self.name = name
        self.storage = storage
        self._key_name = _bucket_key_for(self.name)

    async def add(self, ncco, ttl=DEFAULT_TTL):
        # TODO add proper storage lock access
        bucket_data = await self.storage.read(self._key_name)
        ncco_id = str(uuid())
        bucket_data[ncco_id] = ncco

        await self.storage.write(self._key_name, bucket_data)

        return ncco_id

    async def remove(self, ncco_id):
        bucket_data = await self.storage.read(self._key_name)

        bucket_data.pop(ncco_id, None)

    async def lookup(self, ncco_id):
        bucket_data = await self.storage.read(self._key_name)
        ncco = bucket_data.get(ncco_id)
        return ncco
