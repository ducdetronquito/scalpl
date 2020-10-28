"""
    A lightweight wrapper to operate on nested dictionaries seamlessly.
"""
from itertools import chain
from typing import (
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    ValuesView,
)

TCut = TypeVar("TCut", bound="Cut")
TKeyList = List[Union[str, int]]


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


def type_error(failing_key, original_path, item):
    raise TypeError(
        f"Cannot access key '{failing_key}' in path '{original_path}': "
        f"the element must be a dictionary or a list but is of type '{type(item)}'."
    )


def split_path(path: str, key_separator: str) -> TKeyList:
    sections = path.split(key_separator)
    result = []  # type: TKeyList

    for section in sections:
        key, *indexes = section.split("[")
        result.append(key)
        if not indexes:
            continue

        try:
            for index in indexes:
                index = index[:-1]
                result.append(int(index))
        except ValueError:
            if index != "" and "]" not in index:
                raise ValueError(
                    f"Unable to access item '{index}' in key '{section}': "
                    "you can only provide integers to access list items."
                )
            else:
                raise ValueError(f"Key '{section}' is badly formated.")

    return result


def traverse(data: dict, keys: List[Union[str, int]], original_path: str):
    value = data
    try:
        for key in keys:
            value = value[key]
    except KeyError as error:
        raise key_error(key, original_path, error)
    except IndexError as error:
        raise index_error(key, original_path, error)
    except TypeError:
        raise type_error(key, original_path, value)

    return value


class Cut:
    """
    Cut is a simple wrapper over the built-in dict class.

    It enables the standard dict API to operate on nested dictionnaries
    and cut accross list item by using dot-separated string keys.

    ex:
        query = {...} # Any dict structure
        proxy = Cut(query)
        proxy['pokemon[0].level']
        proxy['pokemon[0].level'] = 666
    """

    __slots__ = ("data", "sep")

    def __init__(self, data: Optional[dict] = None, sep: str = ".") -> None:
        self.data = data or {}
        self.sep = sep

    def __bool__(self) -> bool:
        return bool(self.data)

    def __contains__(self, path: str) -> bool:
        *keys, last_key = split_path(path, self.sep)

        try:
            item = traverse(data=self.data, keys=keys, original_path=path)
        except (KeyError, IndexError):
            return False

        try:
            item[last_key]
            return True
        except (KeyError, IndexError):
            return False

    def __delitem__(self, path: str) -> None:
        *keys, last_key = split_path(path, self.sep)
        item = traverse(data=self.data, keys=keys, original_path=path)

        try:
            del item[last_key]
        except KeyError as error:
            raise key_error(last_key, path, error)
        except IndexError as error:
            raise index_error(last_key, path, error)
        except TypeError:
            raise type_error(last_key, path, item)

    def __eq__(self, other) -> bool:
        return self.data == other

    def __getitem__(self, path: str):
        *keys, last_key = split_path(path, self.sep)
        item = traverse(data=self.data, keys=keys, original_path=path)

        try:
            return item[last_key]
        except KeyError as error:
            raise key_error(last_key, path, error)
        except IndexError as error:
            raise index_error(last_key, path, error)
        except TypeError:
            raise type_error(last_key, path, item)

    def __iter__(self) -> Iterator:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __ne__(self, other) -> bool:
        return not self.data == other

    def __setitem__(self, path: str, value) -> None:
        *keys, last_key = split_path(path, self.sep)
        item = traverse(data=self.data, keys=keys, original_path=path)

        try:
            item[last_key] = value
        except IndexError as error:
            raise index_error(last_key, path, error)
        except TypeError:
            raise type_error(last_key, path, item)

    def __str__(self) -> str:
        return str(self.data)

    def __repr__(self) -> str:
        return f"Cut: {self.data}"

    def all(self: TCut, path: str) -> Iterator[TCut]:
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
        cls: Type[TCut], seq: Iterable, value: Optional[Iterable] = None
    ) -> TCut:
        return cls(dict.fromkeys(seq, value))

    def get(self, path: str, default=None):
        try:
            return self[path]
        except (KeyError, IndexError) as error:
            return default

    def keys(self) -> KeysView:
        return self.data.keys()

    def items(self) -> ItemsView:
        return self.data.items()

    def pop(self, path: str, *args):
        *keys, last_key = split_path(path, self.sep)

        try:
            item = traverse(data=self.data, keys=keys, original_path=path)
        except (KeyError, IndexError) as error:
            if args:
                return args[0]
            raise error

        try:
            return item.pop(last_key)
        except KeyError as error:
            if args:
                return args[0]
            raise key_error(last_key, path, error)
        except IndexError as error:
            if args:
                return args[0]
            raise index_error(last_key, path, error)
        except AttributeError as error:
            raise AttributeError(
                f"Unable to pop item '{last_key}' in key '{path}': "
                f"the element must be a dictionary or a list but is of type '{type(item)}'."
            )

    def popitem(self):
        return self.data.popitem()

    def setdefault(self, path: str, default=None):
        *keys, last_key = split_path(path, self.sep)

        item = self.data
        for key in keys:
            try:
                item = item[key]
            except KeyError:
                item[key] = {}
                item = item[key]
            except IndexError as error:
                raise index_error(key, path, error)

        try:
            return item[last_key]
        except KeyError:
            item[last_key] = default
            return default
        except IndexError as error:
            raise index_error(last_key, path, error)
        except TypeError:
            raise type_error(last_key, path, item)

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
