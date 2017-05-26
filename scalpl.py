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
        keys = key.split(self.sep)
        try:
            self._traverse(keys, LightCut._get_next)
            return True
        except KeyError:
            return False

    def __delitem__(self, key: str) -> None:
        *parent_keys, last_key = key.split(self.sep)
        try:
            if parent_keys:
                parent = self._traverse(parent_keys, LightCut._get_next)
            else:
                parent = self.data
            del parent[last_key]
        except KeyError as err:
            raise KeyError('Key ' + key + ' not found.') from err

    def __eq__(self, other: Any) -> bool:
        return self.data == other

    def __getitem__(self, key: str) -> Any:
        keys = key.split(self.sep)
        try:
            return self._traverse(keys, LightCut._get_next)
        except KeyError as err:
            raise KeyError('Key ' + key + ' not found.') from err

    def __iter__(self):
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __ne__(self, other: Any) -> bool:
        return self.data != other

    def __setitem__(self, key: str, value: Any) -> None:
        *parent_keys, last_key = key.split(self.sep)
        if parent_keys:
            parent = self._traverse(parent_keys, LightCut._get_or_create_next)
        else:
            parent = self.data
        parent[last_key] = value

    def __str__(self) -> str:
        return str(self.data)

    def _get_next(self, _dict, key):
        return _dict[key]

    def _get_or_create_next(self, _dict, key):
        return _dict.setdefault(key, {})

    def _traverse(self, keys, getter):
        current_dict = self.data
        for k in keys:
            current_dict = getter(self, current_dict, k)
        return current_dict

    @classmethod
    def all(cls, dicts, sep='.'):
        """Wrap each dictionary from an Iterable."""
        return (cls(_dict, sep) for _dict in dicts)

    def clear(self) -> None:
        return self.data.clear()

    def copy(self) -> dict:
        return self.data.copy()

    @classmethod
    def fromkeys(cls, seq, value=None):
        return cls(dict.fromkeys(seq, value))

    def get(self, key: str, default: Any=None) -> Any:
        keys = key.split(self.sep)
        try:
            return self._traverse(keys, LightCut._get_next)
        except KeyError:
            return default

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def pop(self, key: str, default: Any=None) -> Any:
        *parent_keys, last_key = key.split(self.sep)
        try:
            if parent_keys:
                parent = self._traverse(parent_keys, LightCut._get_next)
            else:
                parent = self.data
            return parent.pop(last_key)
        except KeyError:
            return default

    def popitem(self) -> Any:
        return self.data.popitem()

    def setdefault(self, key: str, default: Any=None) -> Any:
        *parent_keys, last_key = key.split(self.sep)
        try:
            if parent_keys:
                parent = self._traverse(parent_keys, LightCut._get_next)
            else:
                parent = self.data
            return parent[last_key]
        except KeyError:
            parent[last_key] = default
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

    def __delitem__(self, key: str) -> None:
        *parent_keys, last_key = key.split(self.sep)
        try:
            if parent_keys:
                parent = self._traverse(parent_keys, Cut._get_next)
            else:
                parent = self.data

            last_key, *str_index = last_key.split('[')
            if str_index:
                index = int(str_index[0][:-1])
                del parent[last_key][index]
            else:
                del parent[last_key]

        except KeyError as err:
            raise KeyError('Key ' + key + ' not found.') from err

    def __setitem__(self, key: str, value: Any) -> None:
        *parent_keys, last_key = key.split(self.sep)
        if parent_keys:
            parent = self._traverse(parent_keys, Cut._get_or_create_next)
        else:
            parent = self.data

        last_key, *str_index = last_key.split('[')
        if str_index:
            index = int(str_index[0][:-1])
            parent[last_key][index] = value
        else:
            parent[last_key] = value

    def _traverse(self, keys, getter):
        step = self.data
        for _key in keys:
            _key, *str_index = _key.split('[')
            step = getter(self, step, _key)
            if str_index:
                index = int(str_index[0][:-1])
                step = step[index]
        return step

    def get(self, key: str, default: Any=None) -> Any:
        try:
            return super().get(key, default)
        except IndexError:
            return default

    def pop(self, key: str, default: Any=None) -> Any:
        *parent_keys, last_key = key.split(self.sep)
        try:
            if parent_keys:
                parent = self._traverse(parent_keys, Cut._get_next)
            else:
                parent = self.data
            last_key, *str_index = last_key.split('[')
            if str_index:
                index = int(str_index[0][:-1])
                return parent[last_key].pop(index)
            return parent.pop(last_key)
        except KeyError:
            return default

    def setdefault(self, key: str, default: Any=None) -> Any:
        *parent_keys, last_key = key.split(self.sep)
        try:
            if parent_keys:
                parent = self._traverse(parent_keys, Cut._get_next)
            else:
                parent = self.data

            last_key, *str_index = last_key.split('[')
            if str_index:
                index = int(str_index[0][:-1])
                return parent[last_key][index]
            else:
                return parent[last_key]
        except KeyError:
            parent[last_key] = default
            return default
