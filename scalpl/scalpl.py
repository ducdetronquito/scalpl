"""
    A lightweight wrapper to operate on nested dictionaries seamlessly.
"""
from itertools import chain
from typing import (
    Any,
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    Optional,
    Type,
    TypeVar,
    ValuesView,
)


TLightCut = TypeVar("TLightCut", bound="LightCut")


def key_error(failing_key, original_path, raised_error):
    return KeyError(
        f"Cannot access key '{failing_key}' in path '{original_path}',"
        f" because of error: {repr(raised_error)}."
    )


def index_error(failing_key, original_path, raised_error):
    return IndexError(
        f"Cannot access index '{failing_key}' in path '{original_path}',"
        f" because of error: {repr(raised_error)}."
    )


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

    __slots__ = ("data", "sep")

    def __init__(self, data: Optional[dict] = None, sep: str = ".") -> None:
        self.data = data or {}
        self.sep = sep

    def __bool__(self) -> bool:
        return bool(self.data)

    def __contains__(self, path: str) -> bool:
        parent, last_key = self._traverse(self.data, path)
        try:
            parent[last_key]
            return True
        except (IndexError, KeyError):
            return False

    def __delitem__(self, path: str) -> None:
        parent, last_key = self._traverse(self.data, path)

        try:
            del parent[last_key]
        except KeyError as error:
            raise key_error(last_key, path, error)
        except IndexError as error:
            raise index_error(last_key, path, error)

    def __eq__(self, other: Any) -> bool:
        return self.data == other

    def __getitem__(self, path: str) -> Any:
        parent, last_key = self._traverse(self.data, path)

        try:
            return parent[last_key]
        except KeyError as error:
            raise key_error(last_key, path, error)
        except IndexError as error:
            raise index_error(last_key, path, error)

    def __iter__(self) -> Iterator:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __ne__(self, other: Any) -> bool:
        return self.data != other

    def __setitem__(self, path: str, value: Any) -> None:
        parent, last_key = self._traverse(self.data, path)

        try:
            parent[last_key] = value
        except IndexError as error:
            raise index_error(last_key, path, error)

    def __str__(self) -> str:
        return str(self.data)

    def _traverse(self, parent, path: str):
        *parent_keys, last_key = path.split(self.sep)
        if len(parent_keys) == 0:
            return parent, last_key

        try:
            for sub_key in parent_keys:
                parent = parent[sub_key]
        except KeyError as error:
            raise key_error(sub_key, path, error)

        return parent, last_key

    def all(self: TLightCut, path: str) -> Iterator[TLightCut]:
        """Wrap each item of an Iterable."""
        items = self[path]
        cls = self.__class__
        return (cls(_dict, self.sep) for _dict in items)

    def clear(self) -> None:
        return self.data.clear()

    def copy(self) -> dict:
        return self.data.copy()

    @classmethod
    def fromkeys(
        cls: Type[TLightCut], seq: Iterable, value: Optional[Iterable] = None
    ) -> TLightCut:
        return cls(dict.fromkeys(seq, value))

    def get(self, path: str, default: Optional[Any] = None) -> Any:
        try:
            return self[path]
        except (KeyError, IndexError) as error:
            if default is not None:
                return default
            raise error

    def keys(self) -> KeysView:
        return self.data.keys()

    def items(self) -> ItemsView:
        return self.data.items()

    def pop(self, path: str, default: Any = None) -> Any:
        parent, last_key = self._traverse(self.data, path)
        try:
            return parent.pop(last_key)
        except IndexError as error:
            if default is not None:
                return default
            raise index_error(last_key, path, error)
        except KeyError as error:
            if default is not None:
                return default
            raise key_error(last_key, path, error)

    def popitem(self) -> Any:
        return self.data.popitem()

    def setdefault(self, path: str, default: Any = None) -> Any:
        parent = self.data
        *parent_keys, last_key = path.split(self.sep)
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

    def values(self) -> ValuesView:
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

    def setdefault(self, path: str, default: Optional[Any] = None) -> Any:
        parent = self.data
        *parent_keys, last_key = path.split(self.sep)

        if parent_keys:
            for _key in parent_keys:
                parent, _key = self._traverse_list(parent, _key, path)
                try:
                    parent = parent[_key]
                except KeyError:
                    child: dict = {}
                    parent[_key] = child
                    parent = child
                except IndexError as error:
                    raise index_error(_key, path, error)

        parent, last_key = self._traverse_list(parent, last_key, path)

        try:
            return parent[last_key]
        except KeyError:
            parent[last_key] = default
            return default
        except IndexError as error:
            raise index_error(last_key, path, error)

    def _traverse_list(self, parent, key, original_path: str):
        key, *str_indexes = key.split("[")
        if not str_indexes:
            return parent, key

        try:
            parent = parent[key]
        except KeyError as error:
            raise key_error(key, original_path, error)

        try:
            for str_index in str_indexes[:-1]:
                index = int(str_index[:-1])
                parent = parent[index]
        except IndexError as error:
            raise index_error(index, original_path, error)

        try:
            last_index = int(str_indexes[-1][:-1])
        except ValueError as error:
            raise index_error(str_indexes[-1][:-1], original_path, error)

        return parent, last_index

    def _traverse(self, parent, path: str):
        *parent_keys, last_key = path.split(self.sep)
        if len(parent_keys) > 0:
            try:
                for sub_key in parent_keys:
                    parent, sub_key = self._traverse_list(parent, sub_key, path)
                    parent = parent[sub_key]
            except KeyError as error:
                raise key_error(sub_key, path, error)
            except IndexError as error:
                raise index_error(sub_key, path, error)

        parent, last_key = self._traverse_list(parent, last_key, path)
        return parent, last_key
