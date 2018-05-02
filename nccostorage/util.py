class Observable(object):
    def __init__(self):
        self._susbcribers = []

    def __call__(self, *args, **kwargs):
        for sub in self._susbcribers:
            sub(*args, **kwargs)

    def __iadd__(self, other):
        self._susbcribers.append(other)
        return self

    def __isub__(self, other):
        self._susbcribers.remove(other)
        return self