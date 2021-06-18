from collections import defaultdict, OrderedDict
from copy import deepcopy
from functools import partial
from scalpl.scalpl import Cut, is_index, split_path, traverse
import pytest
from types import GeneratorType


@pytest.fixture(params=[dict, OrderedDict, partial(defaultdict, None)])
def dict_type(request):
    return request.param


class TestIsIndex:
    @pytest.mark.parametrize(
        "key,result",
        [("0", True), ("-1", True), ("1e1", False), ("-1e1", False), ("00", False), ("-0", False)],
    )
    def test_is_index(self, key, result):
        assert is_index(key) == result


class TestSplitPath:
    def setup(self):
        self.key_separator = "."

    @pytest.mark.parametrize(
        "path,result",
        [
            ("", [""]),
            ("users", ["users"]),
            ("users.names.first-name", ["users", "names", "first-name"]),
            ("users[0][1]", ["users", 0, 1]),
            ("users[0][1].name", ["users", 0, 1, "name"]),
            ("users.names[0][1]", ["users", "names", 0, 1]),
            ("users0][1][2][3]", ["users0]", 1, 2, 3]),
            (0, [0]),
            ("0.a", [0, "a"]),
        ],
    )
    def test_split_path(self, path, result):
        assert split_path(path, self.key_separator) == result

    @pytest.mark.parametrize(
        "path,failing_index",
        [
            ("users[name][1][2][3]", "name"),
            ("users[0][name][2][3]", "name"),
            ("users[0][1][2][name]", "name"),
        ],
    )
    def test_error_when_index_is_not_an_integer(self, path, failing_index):
        with pytest.raises(ValueError) as error:
            split_path(path, self.key_separator)

        expected_error = ValueError(
            f"Unable to access item '{failing_index}' in key '{path}': "
            "you can only provide integers to access list items."
        )
        assert str(error.value) == str(expected_error)

    @pytest.mark.parametrize(
        "path",
        [
            "users[0[1][2][3]",
            "users[0]1][2][3]",
            "users[0][1[2][3]",
            "users[0][1[2]3]",
            "users[0][1][2][3",
            "users[",
            "users[]",
            "users[0][][2][3]",
            "users[0][1][2][]",
        ],
    )
    def test_error_when_missing_brackets(self, path):
        with pytest.raises(ValueError) as error:
            split_path(path, self.key_separator)

        expected_error = ValueError(f"Key '{path}' is badly formated.")
        assert str(error.value) == str(expected_error)


class TestTraverse:
    @pytest.mark.parametrize(
        "data,keys,original_path,result",
        [
            ({"a": 42}, [], "", {"a": 42}),
            ({"a": 42}, ["a"], "a", 42),
            ({"a": {"b": {"c": 42}}}, ["a", "b", "c"], "a.b.c", 42),
            ({"a": [42]}, ["a", 0], "a[0]", 42),
            ({"a": [[21], [42]]}, ["a", 1, 0], "a[1][0]", 42),
            ([{"a": 42}], [0], 0, {"a": 42}),
            ([{"a": 42}], [0, "a"], "0.a", 42),
        ],
    )
    def test_traverse(self, data, keys, original_path, result):
        assert traverse(data=data, keys=keys, original_path=original_path) == result

    @pytest.mark.parametrize(
        "data,keys,original_path,failing_key,failing_item_type",
        [
            (42, ["users"], "users", "users", int),
            ({"users": 42}, ["users", 0], "users[0]", "0", int),
        ],
    )
    def test_type_error(self, data, keys, original_path, failing_key, failing_item_type):
        with pytest.raises(TypeError) as error:
            traverse(data=data, keys=keys, original_path=original_path)

        expected_error = TypeError(
            f"Cannot access key '{failing_key}' in path '{original_path}': "
            f"the element must be a dictionary or a list but is of type '{failing_item_type}'."
        )
        assert str(error.value) == str(expected_error)

    def test_key_error(self):
        with pytest.raises(KeyError) as error:
            traverse(data={"a": 42}, keys=["b"], original_path="...")

        expected_error = KeyError(
            f"Cannot access key 'b' in path '...', because of error: {repr(KeyError('b'))}."
        )
        assert str(error.value) == str(expected_error)

    def test_index_error(self):
        with pytest.raises(IndexError) as error:
            traverse(data={"a": [42]}, keys=["a", 1], original_path="...")

        expected_error = IndexError(
            "Cannot access index '1' in path '...', "
            f"because of error: {repr(IndexError('list index out of range'))}."
        )
        assert str(error.value) == str(expected_error)


class TestInit:
    def test_without_data(self):
        proxy = Cut()
        assert proxy.data == {}

    def test_with_an_empty_dict(self, dict_type):
        data = dict_type()
        proxy = Cut(data)
        assert proxy.data is data


@pytest.mark.parametrize("data,result", [({"a": 42}, True), ({}, False)])
def test_bool(dict_type, data, result):
    proxy = Cut(dict_type(data))
    assert bool(proxy) is result


def test_clear(dict_type):
    proxy = Cut(dict_type({"a": 42}))
    proxy.clear()
    assert len(proxy) == 0


def test_copy(dict_type):
    data = {"a": 42}
    proxy = Cut(dict_type(data))
    assert proxy.copy() == data


class TestEquals:
    def test_against_another_scalpl_class(self, dict_type):
        data = {"a": 42}
        proxy = Cut(dict_type(data))
        assert proxy == Cut(dict_type(data))

    def test_against_another_dict(self, dict_type):
        data = {"a": 42}
        proxy = Cut(dict_type(data))
        assert proxy == dict(data)

    def test_against_another_ordered_dict(self, dict_type):
        data = {"a": 42}
        proxy = Cut(dict_type(data))
        assert proxy == OrderedDict(data)

    def test_against_another_default_dict(self, dict_type):
        data = {"a": 42}
        proxy = Cut(dict_type(data))
        assert proxy == defaultdict(None, data)


class TestFromkeys:
    def test_fromkeys(self):
        assert Cut.fromkeys(["Bulbasaur", "Charmander", "Squirtle"]) == Cut(
            {"Bulbasaur": None, "Charmander": None, "Squirtle": None}
        )

    def test_fromkeys_with_default_value(self):
        assert Cut.fromkeys(["Bulbasaur", "Charmander", "Squirtle"], "captured") == Cut(
            {"Bulbasaur": "captured", "Charmander": "captured", "Squirtle": "captured"}
        )


def test_items(dict_type):
    proxy = Cut(dict_type({"a": 1, "b": 2, "c": 3}))
    assert sorted(proxy.items()) == [("a", 1), ("b", 2), ("c", 3)]


def test_iter(dict_type):
    proxy = Cut(dict_type({"a": 1, "b": 2, "c": 3}))
    assert sorted([key for key in proxy]) == ["a", "b", "c"]


def test_keys(dict_type):
    proxy = Cut(dict_type({"a": 1, "b": 2, "c": 3}))
    assert sorted(proxy.keys()) == ["a", "b", "c"]


def test_len(dict_type):
    proxy = Cut(dict_type({"a": 1, "b": 2, "c": 3}))
    assert len(proxy) == 3


def test_popitem(dict_type):
    proxy = Cut(dict_type({"a": 1, "b": 2, "c": 3}))
    proxy.popitem()
    assert len(proxy) == 2


class TestAll:
    def test_return_generator(self, dict_type):
        proxy = Cut(dict_type({"users": [{"name": "a"}, {"name": "b"}]}))
        result = proxy.all("users")
        assert isinstance(result, GeneratorType) is True

    def test_all(self, dict_type):
        proxy = Cut(dict_type({"users": [{"name": "a"}, {"name": "b"}]}))
        values = [item for item in proxy.all("users")]
        assert values == [Cut({"name": "a"}), Cut({"name": "b"})]

    def test_keep_the_same_operator(self, dict_type):
        proxy = Cut(dict_type({"users": [{"name": "a"}, {"name": "b"}]}), sep="/")
        separators = []

        assert all(item.sep == "/" for item in proxy.all("users"))


class TestGetitem:
    @pytest.mark.parametrize(
        "data,key,result",
        [
            ({"a": 42}, "a", 42),
            ({"a": {"b": 42}}, "a.b", 42),
            ({"a": {"b": {"c": 42}}}, "a.b.c", 42),
            ({"a": [42]}, "a[0]", 42),
            ({"a": [{"b": 42}]}, "a[0].b", 42),
        ],
    )
    def test_getitem(self, dict_type, data, key, result):
        proxy = Cut(dict_type(data))
        assert proxy[key] == result

    def test_key_error(self, dict_type):
        proxy = Cut(dict_type({"a": {"b": 42}}))
        with pytest.raises(KeyError) as error:
            proxy["a.c"]

        expected_error = KeyError(
            f"Cannot access key 'c' in path 'a.c', because of error: {repr(KeyError('c'))}."
        )
        assert str(error.value) == str(expected_error)

    def test_index_error(self, dict_type):
        proxy = Cut(dict_type({"a": [42]}))
        with pytest.raises(IndexError) as error:
            proxy["a[1]"]

        expected_error = IndexError(
            "Cannot access index '1' in path 'a[1]', "
            f"because of error: {repr(IndexError('list index out of range'))}."
        )
        assert str(error.value) == str(expected_error)

    def test_type_error(self, dict_type):
        proxy = Cut(dict_type({"a": 42}))
        with pytest.raises(TypeError) as error:
            proxy["a[1]"]

        expected_error = TypeError(
            f"Cannot access key '1' in path 'a[1]': "
            f"the element must be a dictionary or a list but is of type '<class 'int'>'."
        )
        assert str(error.value) == str(expected_error)


class TestSetitem:
    @pytest.mark.parametrize(
        "data,key,result",
        [
            ({"a": 1}, "a", 42),
            ({"a": 1}, "b", 42),
            ({"a": {"b": 1}}, "a.b", 42),
            ({"a": {"b": {"c": 1}}}, "a.b.c", 42),
            ({"a": [1]}, "a[0]", 42),
            ({"a": [{"b": 1}]}, "a[0].b", 42),
        ],
    )
    def test_setitem(self, dict_type, data, key, result):
        proxy = Cut(dict_type(data))
        proxy[key] = result
        assert proxy[key] == result

    def test_index_error(self, dict_type):
        proxy = Cut(dict_type({"a": [1]}))
        with pytest.raises(IndexError) as error:
            proxy["a[1]"] = 42

        expected_error = IndexError(
            "Cannot access index '1' in path 'a[1]', "
            f"because of error: {repr(IndexError('list assignment index out of range'))}."
        )
        assert str(error.value) == str(expected_error)

    def test_type_error(self, dict_type):
        proxy = Cut(dict_type({"a": 1}))
        with pytest.raises(TypeError) as error:
            proxy["a[1]"] = 42

        expected_error = TypeError(
            f"Cannot access key '1' in path 'a[1]': "
            f"the element must be a dictionary or a list but is of type '<class 'int'>'."
        )
        assert str(error.value) == str(expected_error)


class TestGet:
    @pytest.mark.parametrize(
        "data,key,result",
        [
            ({"a": 42}, "a", 42),
            ({"a": {"b": 42}}, "a.b", 42),
            ({"a": {"b": {"c": 42}}}, "a.b.c", 42),
            ({"a": [42]}, "a[0]", 42),
            ({"a": [{"b": 42}]}, "a[0].b", 42),
            ({"a": 42}, "b", None),
            ({"a": {"b": 42}}, "a.c", None),
            ({"a": {"b": {"c": 42}}}, "a.b.d", None),
            ({"a": [42]}, "a[1]", None),
            ({"a": [{"b": 42}]}, "a[1].b", None),
        ],
    )
    def test_get(self, dict_type, data, key, result):
        proxy = Cut(dict_type(data))
        assert proxy.get(key) == result

    @pytest.mark.parametrize(
        "data,key,default",
        [
            ({}, "b", None),
            ({"a": 42}, "b", "default"),
            ({"a": {"b": 42}}, "a.c", "default"),
            ({"a": {"b": {"c": 42}}}, "a.b.d", "default"),
            ({"a": [42]}, "a[1]", "default"),
            ({"a": [{"b": 42}]}, "a[1].b", "default"),
        ],
    )
    def test_with_default(self, dict_type, data, key, default):
        proxy = Cut(dict_type(data))
        assert proxy.get(key, default) == default


class TestDelitem:
    @pytest.mark.parametrize(
        "data,key",
        [
            ({"a": 42}, "a"),
            ({"a": {"b": 42}}, "a.b"),
            ({"a": {"b": {"c": 42}}}, "a.b.c"),
            ({"a": [42]}, "a[0]"),
            ({"a": [{"b": 42}]}, "a[0].b"),
        ],
    )
    def test_delitem(self, dict_type, data, key):
        proxy = Cut(dict_type(deepcopy(data)))
        del proxy[key]
        assert key not in proxy

    def test_key_error(self, dict_type):
        proxy = Cut(dict_type({"a": {"b": 42}}))
        with pytest.raises(KeyError) as error:
            del proxy["a.c"]

        expected_error = KeyError(
            f"Cannot access key 'c' in path 'a.c', because of error: {repr(KeyError('c'))}."
        )
        assert str(error.value) == str(expected_error)

    def test_index_error(self, dict_type):
        proxy = Cut(dict_type({"a": [42]}))
        with pytest.raises(IndexError) as error:
            del proxy["a[1]"]

        expected_error = IndexError(
            "Cannot access index '1' in path 'a[1]', "
            f"because of error: {repr(IndexError('list assignment index out of range'))}."
        )
        assert str(error.value) == str(expected_error)

    def test_type_error(self, dict_type):
        proxy = Cut(dict_type({"a": 42}))
        with pytest.raises(TypeError) as error:
            del proxy["a[1]"]

        expected_error = TypeError(
            f"Cannot access key '1' in path 'a[1]': "
            f"the element must be a dictionary or a list but is of type '<class 'int'>'."
        )
        assert str(error.value) == str(expected_error)


class TestContains:
    @pytest.mark.parametrize(
        "data,key,result",
        [
            ({"a": 42}, "a", True),
            ({"a": {"b": 42}}, "a.b", True),
            ({"a": {"b": 42}}, "c.b", False),
            ({"a": {"b": {"c": 42}}}, "a.b.c", True),
            ({"a": [42]}, "a[0]", True),
            ({"a": [{"b": 42}]}, "a[0].b", True),
            ({"a": 42}, "b", False),
            ({"a": {"b": 42}}, "a.c", False),
            ({"a": {"b": {"c": 42}}}, "a.b.d", False),
            ({"a": [42]}, "a[1]", False),
            ({"a": [{"b": 42}]}, "a[0].c", False),
            ({"a": [{"b": 42}]}, "a[1].b", False),
        ],
    )
    def test_contains(self, dict_type, data, key, result):
        proxy = Cut(dict_type(data))
        assert (key in proxy) is result


class TestPop:
    @pytest.mark.parametrize(
        "data,key,result",
        [
            ({"a": 42}, "a", 42),
            ({"a": {"b": 42}}, "a.b", 42),
            ({"a": {"b": {"c": 42}}}, "a.b.c", 42),
            ({"a": [42]}, "a[0]", 42),
            ({"a": [{"b": 42}]}, "a[0].b", 42),
        ],
    )
    def test_pop(self, dict_type, data, key, result):
        proxy = Cut(dict_type(deepcopy(data)))
        assert proxy.pop(key) == result
        assert key not in proxy

    @pytest.mark.parametrize(
        "data,key,default",
        [
            ({}, "b", None),
            ({"a": 1}, "b", 42),
            ({"a": {"b": 1}}, "c.b", 42),
            ({"a": {"b": 1}}, "a.c", 42),
            ({"a": {"b": {"c": 1}}}, "a.d.c", 42),
            ({"a": {"b": {"c": 1}}}, "a.b.d", 42),
            ({"a": [[1]]}, "a[1][0]", 42),
            ({"a": [[1]]}, "a[0][1]", 42),
            ({"a": [{"b": 1}]}, "a[1].b", 42),
            ({"a": [{"b": 1}]}, "a[0].c", 42),
        ],
    )
    def test_with_default(self, dict_type, data, key, default):
        proxy = Cut(dict_type(deepcopy(data)))
        assert proxy.pop(key, default) == default

    @pytest.mark.parametrize(
        "data,path,failing_key",
        [
            ({"a": 1}, "b", "b"),
            ({"a": {"b": 1}}, "c.b", "c"),
            ({"a": {"b": 1}}, "a.c", "c"),
            ({"a": {"b": {"c": 1}}}, "a.d.c", "d"),
            ({"a": {"b": {"c": 1}}}, "a.b.d", "d"),
        ],
    )
    def test_key_error_when_no_default_provided(self, dict_type, data, path, failing_key):
        proxy = Cut(dict_type(deepcopy(data)))
        with pytest.raises(KeyError) as error:
            proxy.pop(path)

        expected_error = KeyError(
            f"Cannot access key '{failing_key}' in path '{path}', "
            f"because of error: {repr(KeyError(failing_key))}."
        )
        assert str(error.value) == str(expected_error)

    @pytest.mark.parametrize(
        "data,path,failing_index",
        [
            ({"a": [[1]]}, "a[1][0]", 1),
            ({"a": [{"b": 1}]}, "a[1].b", 1),
        ],
    )
    def test_list_index_error_when_no_default_provided(self, dict_type, data, path, failing_index):
        proxy = Cut(dict_type(deepcopy(data)))
        with pytest.raises(IndexError) as error:
            proxy.pop(path)

        expected_error = IndexError(
            f"Cannot access index '{failing_index}' in path '{path}', "
            f"because of error: {repr(IndexError('list index out of range'))}."
        )
        assert str(error.value) == str(expected_error)

    def test_pop_index_error_when_no_default_provided(self, dict_type):
        proxy = Cut(dict_type({"a": [[1]]}))
        with pytest.raises(IndexError) as error:
            proxy.pop("a[0][1]")

        expected_error = IndexError(
            f"Cannot access index '1' in path 'a[0][1]', "
            f"because of error: {repr(IndexError('pop index out of range'))}."
        )
        assert str(error.value) == str(expected_error)

    def test_attribute_error(self, dict_type):
        proxy = Cut(dict_type({"a": 42}))
        with pytest.raises(AttributeError) as error:
            proxy.pop("a.b")

        expected_error = AttributeError(
            "Unable to pop item 'b' in key 'a.b': "
            "the element must be a dictionary or a list but is of type '<class 'int'>'."
        )
        assert str(error.value) == str(expected_error)


class TestUpdate:
    def test_from_dict(self, dict_type):
        proxy = Cut(dict_type({"a": {"b": 1}}))
        proxy.update({"a.b": 42})
        assert proxy["a"]["b"] == 42

    def test_from_dict_and_keyword_args(self, dict_type):
        proxy = Cut(dict_type({"a": {"b": 1}}))
        from_other = {"a.b": 42}
        proxy.update(from_other, c=666)
        assert proxy["a"]["b"] == 42
        assert proxy["c"] == 666

    def test_from_list(self, dict_type):
        proxy = Cut(dict_type({"a": {"b": 1}}))
        from_other = [("a.b", 42)]
        proxy.update(from_other)
        assert proxy["a"]["b"] == 42

    def test_from_list_and_keyword_args(self, dict_type):
        proxy = Cut(dict_type({"a": {"b": 1}}))
        from_other = [("a.b", 42)]
        proxy.update(from_other, c=666)
        assert proxy["a"]["b"] == 42
        assert proxy["c"] == 666


class TestSetdefault:
    @pytest.mark.parametrize(
        "data,key,result",
        [
            ({"a": 42}, "a", 42),
            ({"a": {"b": 42}}, "a.b", 42),
            ({"a": {"b": {"c": 42}}}, "a.b.c", 42),
            ({"a": [42]}, "a[0]", 42),
            ({"a": [{"b": 42}]}, "a[0].b", 42),
            ({"a": 1}, "b", None),
            ({"a": {"b": 1}}, "a.c", None),
            ({"a": {"b": {"c": 1}}}, "a.b.d", None),
            ({"a": [{"b": 1}]}, "a[0].c", None),
            ({"a": {"b": {"c": 42}}}, "a.d.e.f", None),
        ],
    )
    def test_setdefault(self, dict_type, data, key, result):
        proxy = Cut(dict_type(deepcopy(data)))
        assert proxy.setdefault(key) == result
        assert proxy[key] == result

    @pytest.mark.parametrize(
        "data,key,default",
        [
            ({}, "b", None),
            ({"a": 1}, "b", "default"),
            ({"a": {"b": 1}}, "a.c", "default"),
            ({"a": {"b": {"c": 1}}}, "a.b.d", "default"),
            ({"a": [{"b": 1}]}, "a[0].c", "default"),
            ({"a": {"b": {"c": 42}}}, "a.d.e.f", "default"),
        ],
    )
    def test_with_default(self, dict_type, data, key, default):
        proxy = Cut(dict_type(deepcopy(data)))
        assert proxy.setdefault(key, default) == default
        assert proxy[key] == default

    def test_type_error(self, dict_type):
        proxy = Cut(dict_type({"a": 1}))
        with pytest.raises(TypeError) as error:
            proxy.setdefault("a[1]")

        expected_error = TypeError(
            f"Cannot access key '1' in path 'a[1]': "
            f"the element must be a dictionary or a list but is of type '<class 'int'>'."
        )
        assert str(error.value) == str(expected_error)

    @pytest.mark.parametrize(
        "data,key,error_message",
        [
            (
                {"a": [42]},
                "a[1]",
                f"Cannot access index '1' in path 'a[1]', because of error:",
            ),
            (
                {"a": [{"b": 1}]},
                "a[1].c",
                f"Cannot access index '1' in path 'a[1].c', because of error:",
            ),
        ],
    )
    def test_nested_index_error(self, dict_type, data, key, error_message):
        proxy = Cut(dict_type(data))
        with pytest.raises(IndexError) as error:
            proxy.setdefault(key, 42)

        expected_error_message = f"{error_message} {repr(IndexError('list index out of range'))}."

        assert str(error.value) == expected_error_message
