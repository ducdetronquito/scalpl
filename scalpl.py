from itertools import chain

# TODO:
#  1. Test Cut.all
#  2. Add proper description
#  3. Publish on Pypi
#  4. Is it possible to handle non-string key seamlessly ?
#  5. Is it interesting use Cut inside a context manager ?

class Cut:
    """
        Cut is a simple proxy over the built-in dict class that
        provides read and write operations on nested dictionnaries
        by using semilicon composite key.

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

    def clear(self):
        return self.data.clear()

    def copy(self):
        return self.data.copy()

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
    def all(dicts):
        return (Cut(_dict) for _dict in dicts)

