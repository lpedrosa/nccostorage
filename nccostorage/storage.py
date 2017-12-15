class DictionaryStorage(object):

    def __init__(self):
        self._store = {}

    async def lookup(self, key):
        return key in self._store

    async def write(self, key, value):
        self._store[key] = value

    async def read(self, key):
        return self._store.get(key)
