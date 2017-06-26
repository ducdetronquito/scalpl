"""
    A lightweight wrapper to operate on nested dictionaries seamlessly.
"""
from typing import Any, Optional
from itertools import chain


class LightCut:
    """
        LightCut is a simple wrapper over the built-in dict class.

        It enables the standard dict API to operate on nested dictionnaries
        by using dot-separated string keys.

        ex:
            query = {...} # Any dict structure
            proxy = Cut(query)
            proxy['pokemons.charmander.level']
            proxy['pokemons.charmander.level'] = 666
    """
    __slots__ = ('data', 'sep')

    def __init__(self, data: Optional[dict]=None, sep: str='.') -> None:
        self.data = data or {}
        self.sep = sep

    def __bool__(self) -> bool:
        return bool(self.data)

    def __contains__(self, key: str) -> bool:
        try:
            parent, last_key = self._traverse(self.data, key)
            parent[last_key]
            return True
        except (IndexError, KeyError):
            return False

    def __delitem__(self, key: str) -> None:
        try:
            parent, last_key = self._traverse(self.data, key)
            del parent[last_key]
        except KeyError:
            raise KeyError('key "' + key + '" not found.')
        except IndexError:
            raise IndexError('index out of range in key "' + key + '".')

    def __eq__(self, other: Any) -> bool:
        return self.data == other

    def __getitem__(self, key: str) -> Any:
        try:
            parent, last_key = self._traverse(self.data, key)
            return parent[last_key]
        except KeyError:
            raise KeyError('key "' + key + '" not found.')
        except IndexError:
            raise IndexError('index out of range in key "' + key + '".')

    def __iter__(self):
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __ne__(self, other: Any) -> bool:
        return self.data != other

    def __setitem__(self, key: str, value: Any) -> None:
        try:
            parent, last_key = self._traverse(self.data, key)
            parent[last_key] = value
        except KeyError:
            raise KeyError('key "' + key + '" not found.')
        except IndexError:
            raise IndexError('index out of range in key "' + key + '".')

    def __str__(self) -> str:
        return str(self.data)

    def _traverse(self, parent, key: str):
        *parent_keys, last_key = key.split(self.sep)
        if parent_keys:
            for key in parent_keys:
                parent = parent[key]
        return parent, last_key

    def all(self, key: str):
        """Wrap each item of an Iterable."""
        items = self[key]
        cls = self.__class__
        return (cls(_dict, self.sep) for _dict in items)

    def clear(self) -> None:
        return self.data.clear()

    def copy(self) -> dict:
        return self.data.copy()

    @classmethod
    def fromkeys(cls, seq, value=None):
        return cls(dict.fromkeys(seq, value))

    def get(self, key: str, default: Any=None) -> Any:
        try:
            return self[key]
        except (KeyError, IndexError):
            return default

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def pop(self, key: str, default: Any=None) -> Any:
        try:
            parent, last_key = self._traverse(self.data, key)
            return parent.pop(last_key)
        except (KeyError, IndexError):
            return default

    def popitem(self) -> Any:
        return self.data.popitem()

    def setdefault(self, key: str, default: Any=None) -> Any:
        parent = self.data
        *parent_keys, last_key = key.split(self.sep)
        if parent_keys:
            for key in parent_keys:
                parent = parent.setdefault(key, {})
        return parent.setdefault(last_key, default)

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


class Cut(LightCut):
    """
        Cut is a simple wrapper over the built-in dict class.

        It enables the standard dict API to operate on nested dictionnaries
        and cut accross list item by using dot-separated string keys.

        ex:
            query = {...} # Any dict structure
            proxy = Cut(query)
            proxy['pokemons[0].level']
            proxy['pokemons[0].level'] = 666
    """
    __slots__ = ()

    def setdefault(self, key: str, default: Any=None) -> Any:
        try:
            parent = self.data
            *parent_keys, last_key = key.split(self.sep)
            if parent_keys:
                for _key in parent_keys:
                    parent, _key = self._traverse_list(parent, _key)
                    try:
                        parent = parent[_key]
                    except KeyError:
                        child = {}
                        parent[_key] = child
                        parent = child
            parent, last_key = self._traverse_list(parent, last_key)
            return parent[last_key]
        except KeyError:
            parent[last_key] = default
            return default
        except IndexError:
            raise IndexError('index out of range in key "' + key + '".')

    def _traverse_list(self, parent, key):
        key, *str_indexes = key.split('[')
        if str_indexes:
            parent = parent[key]
            for str_index in str_indexes[:-1]:
                index = int(str_index[:-1])
                parent = parent[index]
            return parent, int(str_indexes[-1][:-1])
        else:
            return parent, key

    def _traverse(self, parent, key):
        *parent_keys, last_key = key.split(self.sep)
        if parent_keys:
            for _key in parent_keys:
                parent, _key = self._traverse_list(parent, _key)
                parent = parent[_key]
        parent, last_key = self._traverse_list(parent, last_key)
        return parent, last_key
