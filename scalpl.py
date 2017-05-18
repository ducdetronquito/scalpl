"""
    A minimalist tool to operate on nested dictionaries.
"""

from itertools import chain

# TODO:
#  - Add proper description
#  - Add proper README/DOC
#  - Add type annotation
#  - Publish on Pypi
#  - Is it interesting use Cut inside a context manager ?
#  - Is it possible to use scalpl with dict subclasses ?
#  - Is it worth it to add a way yo handle Lists ?


class Cut:
    """
        Cut is a simple proxy over the built-in dict class.

        It enables the standard dict API to operate on nested dictionnaries
        by using colon-separated string keys.

        ex:
            query = {...} # Any dict structure
            proxy = Cut(query)
            proxy['users:john:age']
            proxy['users:john:age'] = 42
    """
    __slots__ = ('data', 'sep')

    def __init__(self, data=None, sep: str=':'):
        self.data = data or {}
        self.sep = sep

    def __bool__(self):
        return bool(self.data)

    def __contains__(self, key: str):
        keys = key.split(self.sep)
        try:
            self.__traverse(keys)
            return True
        except KeyError:
            return False

    def __delitem__(self, key: str):
        keys = key.split(self.sep)
        last_key = keys[-1]
        parent_keys = keys[:-1]
        try:
            value = self.__traverse(parent_keys)
            del value[last_key]
        except KeyError as err:
            raise KeyError('Key ' + key + ' not found.') from err

    def __eq__(self, other):
        return self.data == other

    def __getitem__(self, key: str):
        keys = key.split(self.sep)
        try:
            return self.__traverse(keys)
        except KeyError as err:
            raise KeyError('Key ' + key + ' not found.') from err

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __ne__(self, other):
        return self.data != other

    def __setitem__(self, key: str, value):
        keys = key.split(self.sep)
        last_key = keys[-1]
        parent_keys = keys[:-1]
        current_dict = self.data
        for k in parent_keys:
            current_dict = current_dict.setdefault(k, {})

        current_dict[last_key] = value

    def __str__(self):
        return str(self.data)

    def __traverse(self, keys):
        current_dict = self.data
        for k in keys:
            current_dict = current_dict[k]
        return current_dict

    @staticmethod
    def all(dicts, sep: str=':'):
        """Proxy each dictionary from an Iterable."""
        return (Cut(_dict, sep) for _dict in dicts)

    def clear(self):
        return self.data.clear()

    def copy(self):
        return self.data.copy()

    @staticmethod
    def fromkeys(seq, value=None):
        return dict.fromkeys(seq, value)

    def get(self, key: str, default=None):
        keys = key.split(self.sep)
        try:
            return self.__traverse(keys)
        except KeyError:
            return default

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def pop(self, key: str, default=None):
        keys = key.split(self.sep)
        last_key = keys[-1]
        parent_keys = keys[:-1]
        try:
            value = self.__traverse(parent_keys)
            return value.pop(last_key)
        except KeyError:
            return default

    def popitem(self):
        return self.data.popitem()

    def setdefault(self, key: str, default=None):
        keys = key.split(self.sep)
        try:
            return self.__traverse(keys)
        except KeyError:
            self.__setitem__(key, default)
            return default

    def update(self, data=None, **kwargs):
        data = data or {}
        try:
            data.update(kwargs)
            pairs = data.items()
        except AttributeError:
            pairs = chain(data, kwargs.items())

        for key, value in pairs:
            self.__setitem__(key, value)

    def values(self):
        return self.data.values()
