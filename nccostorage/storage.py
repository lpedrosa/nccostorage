import asyncio.locks as locks

class DictionaryStorage(object):

    def __init__(self, loop=None):
        self._store = {}
        self._lock = locks.Lock(loop=loop)

    async def lookup(self, key):
        async with self._lock:
            return key in self._store

    async def write_if_absent(self, key, value):
        async with self._lock:
            if key not in self._store:
                self._store[key] = value

    async def read(self, key):
        async with self._lock:
            return self._store.get(key)

    async def update(self, key, value, update_func):
        async with self._lock:
            old_value = self._store.get(key)
            new_value = update_func(old_value, value)
            self._store[key] = new_value

        return new_value
