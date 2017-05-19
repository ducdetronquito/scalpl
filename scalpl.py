"""
    A minimalist tool to operate on nested dictionaries.
"""
from typing import Any, Iterator, List, Optional
from itertools import chain

# TODO:
#  - Test scalpl with dict subclasses ?
#  - Is it worth it to add a way to handle Lists ?
#  - Is it interesting use Cut inside a context manager ?


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

    def __init__(self, data: Optional[dict]=None, sep: str=':') -> None:
        self.data = data or {}
        self.sep = sep

    def __bool__(self) -> bool:
        return bool(self.data)

    def __contains__(self, key: str) -> bool:
        keys = key.split(self.sep)
        try:
            self.__traverse(keys)
            return True
        except KeyError:
            return False

    def __delitem__(self, key: str) -> None:
        keys = key.split(self.sep)
        last_key = keys[-1]
        parent_keys = keys[:-1]
        try:
            value = self.__traverse(parent_keys)
            del value[last_key]
        except KeyError as err:
            raise KeyError('Key ' + key + ' not found.') from err

    def __eq__(self, other: Any) -> bool:
        return self.data == other

    def __getitem__(self, key: str) -> Any:
        keys = key.split(self.sep)
        try:
            return self.__traverse(keys)
        except KeyError as err:
            raise KeyError('Key ' + key + ' not found.') from err

    def __iter__(self):
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __ne__(self, other: Any) -> bool:
        return self.data != other

    def __setitem__(self, key: str, value: Any) -> None:
        keys = key.split(self.sep)
        last_key = keys[-1]
        parent_keys = keys[:-1]
        current_dict = self.data
        for k in parent_keys:
            current_dict = current_dict.setdefault(k, {})

        current_dict[last_key] = value

    def __str__(self) -> str:
        return str(self.data)

    def __traverse(self, keys: List[str]) -> Any:
        current_dict = self.data
        for k in keys:
            current_dict = current_dict[k]
        return current_dict

    @staticmethod
    def all(dicts: Iterator[dict], sep: str=':') -> Iterator['Cut']:
        """Proxy each dictionary from an Iterable."""
        return (Cut(_dict, sep) for _dict in dicts)

    def clear(self) -> None:
        return self.data.clear()

    def copy(self) -> dict:
        return self.data.copy()

    @staticmethod
    def fromkeys(seq: List[str], value: Any=None) -> 'Cut':
        return Cut(dict.fromkeys(seq, value))

    def get(self, key: str, default: Any=None) -> Any:
        keys = key.split(self.sep)
        try:
            return self.__traverse(keys)
        except KeyError:
            return default

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def pop(self, key: str, default: Any=None) -> Any:
        keys = key.split(self.sep)
        last_key = keys[-1]
        parent_keys = keys[:-1]
        try:
            value = self.__traverse(parent_keys)
            return value.pop(last_key)
        except KeyError:
            return default

    def popitem(self) -> Any:
        return self.data.popitem()

    def setdefault(self, key: str, default: Any=None) -> Any:
        keys = key.split(self.sep)
        try:
            return self.__traverse(keys)
        except KeyError:
            self.__setitem__(key, default)
            return default

    def update(self, data=None, **kwargs) -> None:
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
