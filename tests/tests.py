from collections import defaultdict, OrderedDict
from copy import deepcopy
from .fixtures import (
    BULBASAUR,
    CHARMANDER,
    SQUIRTLE,
    ASH,
    FIRST_SET,
    SECOND_SET,
    BASE,
    proxy,
    scalpl_class,
    underlying_dict_class,
)
import pytest
from types import GeneratorType


class TestCutTraverse:
    def test_traverse_single_key(self, proxy):
        parent, last_key = proxy._traverse(ASH, "name")
        assert parent == ASH
        assert last_key == "name"

    def test_traverse_single_undefined_key(self, proxy):
        parent, last_key = proxy._traverse(ASH, "undefined_key")
        assert parent == ASH
        assert last_key == "undefined_key"

    def test_traverse_nested_keys(self, proxy):
        parent, last_key = proxy._traverse(ASH, "badges.Boulder")
        assert parent == ASH["badges"]
        assert last_key == "Boulder"

    def test_traverse_undefined_nested_keys(self, proxy):
        with pytest.raises(KeyError) as error:
            parent, last_key = proxy._traverse(ASH, "undefined_key.name")

        expected_error = KeyError(
            "Cannot access key 'undefined_key' in path 'undefined_key.name', "
            "because of error: KeyError('undefined_key',)."
        )
        assert str(error.value) == str(expected_error)

    def test_traverse_single_list_item(self, proxy):
        data = {"types": ["Fire"]}
        parent, last_key = proxy._traverse(data, "types[0]")
        assert parent == data["types"]
        assert last_key == 0

    def test_traverse_undefined_list_item_do_not_throw_error(self, proxy):
        data = {"types": ["Fire"]}
        parent, last_key = proxy._traverse(data, "types[1]")
        assert parent == data["types"]
        assert last_key == 1

    def test_traverse_undefined_list_raises_exception(self, proxy):
        data = {"types": ["Fire"]}

        with pytest.raises(KeyError) as error:
            proxy._traverse(data, "colors[0]")

        expected_error = KeyError(
            "Cannot access key 'colors' in path 'colors[0]', "
            "because of error: KeyError('colors',)."
        )
        assert str(error.value) == str(expected_error)

    def test_traverse_nested_list_item(self, proxy):
        data = {"types": [["Fire", "Water"]]}
        parent, last_key = proxy._traverse(BULBASAUR, "types[0][1]")
        assert parent == BULBASAUR["types"][0]
        assert last_key == 1

    def test_traverse_undefined_nested_list_item_raises_exception(self, proxy):
        data = {"types": [["Fire", "Water"]]}

        with pytest.raises(IndexError) as error:
            proxy._traverse(BULBASAUR, "types[42][0]")

        expected_error = IndexError(
            "Cannot access index '42' in path 'types[42][0]', "
            "because of error: IndexError('list index out of range',)."
        )
        assert str(error.value) == str(expected_error)

    def test_traverse_with_non_integer_index_raises_exception(self, proxy):
        data = {"types": [["Fire", "Water"]]}

        with pytest.raises(IndexError) as error:
            proxy._traverse(BULBASAUR, "types[toto]")

        expected_error = IndexError(
            "Cannot access index 'toto' in path 'types[toto]', "
            "because of error: ValueError(\"invalid literal for int() with base 10: 'toto'\",)."
        )

        assert str(error.value) == str(expected_error)


class TestBool:
    def test_evaluate_to_true_for_existing_data(self, proxy):
        assert bool(proxy) is True

    def test_evaluate_to_false_for_empty_data(self, proxy):
        proxy.clear()
        assert bool(proxy) is False


class TestClear:
    def test_clear(self, proxy):
        proxy.clear()
        assert len(proxy) == 0


class TestCopy:
    def test_copy(self, proxy):
        assert proxy.copy() == BASE


class TestEquals:
    def test_against_another_scalpl_class(self, proxy):
        assert proxy == deepcopy(proxy)

    def test_against_another_dict(self, proxy):
        other = dict(proxy.data)
        assert proxy == other

    def test_against_another_ordered_dict(self, proxy):
        other = OrderedDict(proxy.data)
        assert proxy == other

    def test_against_another_default_dict(self, proxy):
        other = defaultdict(None, proxy.data)
        assert proxy == other


class TestFromKeys:
    def test_scalpl_class_from_keys(self, scalpl_class, underlying_dict_class):
        expected = scalpl_class(
            {"Bulbasaur": "captured", "Charmander": "captured", "Squirtle": "captured"}
        )
        seq = ["Bulbasaur", "Charmander", "Squirtle"]
        value = "captured"

        assert scalpl_class.fromkeys(seq, value) == expected

    def test_with_default_values(self, scalpl_class, underlying_dict_class):
        expected = scalpl_class(
            {"Bulbasaur": None, "Charmander": None, "Squirtle": None}
        )
        seq = ["Bulbasaur", "Charmander", "Squirtle"]

        assert scalpl_class.fromkeys(seq) == expected


class TestItems:
    def test_items(self, proxy):
        result = sorted(proxy.items())
        expected = [
            ("pokemon", [BULBASAUR, CHARMANDER, SQUIRTLE]),
            ("team_sets", [FIRST_SET, SECOND_SET]),
            ("trainer", ASH),
        ]
        assert result == expected


class TestIter:
    def test_iter(self, proxy):
        keys = sorted([key for key in proxy])
        assert keys == ["pokemon", "team_sets", "trainer"]


class TestKeys:
    def test_keys(self, proxy):
        result = sorted(proxy.keys())
        assert result == ["pokemon", "team_sets", "trainer"]


class TestLen:
    def test_len(self, proxy):
        assert len(proxy) == 3


class TestPopitem:
    def test_popitem(self, proxy):
        proxy.popitem()
        assert len(proxy) == 2


class TestDelitem:
    def test_delitem(self, proxy):
        del proxy["trainer"]
        assert "trainer" not in proxy

    def test_on_nested_key(self, proxy):
        del proxy["trainer.name"]
        assert "name" not in proxy["trainer"]
        assert "trainer" in proxy

    def test_on_undefined_key(self, proxy):
        with pytest.raises(KeyError) as error:
            del proxy["trainer.bicycle"]

        expected_error = KeyError(
            "Cannot access key 'bicycle' in path 'trainer.bicycle', "
            "because of error: KeyError('bicycle',)."
        )
        assert str(error.value) == str(expected_error)

    def test_through_list(self, proxy):
        del proxy["pokemon[1].category"]
        assert "category" not in proxy.data["pokemon"][1]

    def test_undefined_key_through_list_(self, proxy):
        with pytest.raises(KeyError) as error:
            del proxy["pokemon[1].has_been_seen"]

        expected_error = KeyError(
            "Cannot access key 'has_been_seen' in path 'pokemon[1].has_been_seen', "
            "because of error: KeyError('has_been_seen',)."
        )
        assert str(error.value) == str(expected_error)

    def test_through_nested_list(self, proxy):
        del proxy["team_sets[0][0].name"]
        assert "name" not in proxy.data["team_sets"][0][0]

    def test_undefined_key_through_nested_list(self, proxy):
        with pytest.raises(KeyError) as error:
            del proxy["team_sets[0][0].can_fly"]

        expected_error = KeyError(
            "Cannot access key 'can_fly' in path 'team_sets[0][0].can_fly', "
            "because of error: KeyError('can_fly',)."
        )
        assert str(error.value) == str(expected_error)

    def test_list_item(self, proxy):
        del proxy["pokemon[0].types[1]"]
        assert len(proxy.data["pokemon"][0]["types"]) == 1

    def test_undefined_list_item(self, proxy):
        with pytest.raises(IndexError) as error:
            del proxy["pokemon[0].types[42]"]

        expected_error = IndexError(
            "Cannot access index '42' in path 'pokemon[0].types[42]', "
            "because of error: IndexError('list assignment index out of range',)."
        )
        assert str(error.value) == str(expected_error)

    def test_undefined_list_index(self, proxy):
        with pytest.raises(IndexError) as error:
            del proxy["pokemon[42].types[1]"]

        expected = IndexError(
            "Cannot access index '42' in path 'pokemon[42].types[1]', "
            "because of error: IndexError('list index out of range',)."
        )
        assert str(error.value) == str(expected)

    def test_list_item_through_nested_list(self, proxy):
        del proxy["team_sets[0][0]"]
        assert len(proxy.data["team_sets"][0]) == 2


class TestGet:
    def test_get(self, proxy):
        assert proxy.get("trainer") == ASH
        assert proxy.get("trainer.badges") == {"Boulder": True, "Cascade": False}
        assert proxy.get("trainer.badges.Boulder") is True

    def test_get_undefined_key_raises_exception(self, proxy):
        with pytest.raises(KeyError) as error:
            proxy.get("trainer.hometown")

        expected = KeyError(
            "Cannot access key 'hometown' in path 'trainer.hometown', "
            "because of error: KeyError('hometown',)."
        )
        assert str(error.value) == str(expected)

    def test_get_undefined_key_when_default_is_provided(self, proxy):
        assert proxy.get("game", "Pokemon Blue") == "Pokemon Blue"
        assert proxy.get("trainer.hometown", "Pallet Town") == "Pallet Town"
        assert proxy.get("trainer.badges.Thunder", False) is False

    def test_get_through_list(self, proxy):
        assert proxy.get("pokemon[0].types[1]") == "Poison"

    def test_get_through_nested_list(self, proxy):
        result = proxy.get("team_sets[0][0].name", "Unknwown")
        assert result == "Charmander"

    def test_get_undefined_key_through_list(self, proxy):
        assert proxy.get("pokemon[0].sex", "Unknown") == "Unknown"

    def test_get_undefined_list_item(self, proxy):
        assert proxy.get("pokemon[0].types[42]", "Unknown") == "Unknown"


class TestGetitem:
    def test_getitem(self, proxy):
        assert proxy["trainer"] == ASH
        assert proxy["trainer.badges"] == {"Boulder": True, "Cascade": False}
        assert proxy["trainer.badges.Cascade"] is False

    def test_getitem_undefined_key(self, proxy):
        with pytest.raises(KeyError) as error:
            proxy["trainer.badges.Thunder"]

        expected_error = KeyError(
            "Cannot access key 'Thunder' in path 'trainer.badges.Thunder', "
            "because of error: KeyError('Thunder',)."
        )
        assert str(error.value) == str(expected_error)

    def test_getitem_with_custom_separator(self, proxy):
        proxy.sep = "+"
        assert proxy["trainer"] == ASH
        assert proxy["trainer+badges"] == {"Boulder": True, "Cascade": False}
        assert proxy["trainer+badges+Boulder"] is True

    def test_getitem_through_list(self, proxy):
        assert proxy["pokemon[0].types[1]"] == "Poison"

    def test_getitem_through_nested_list(self, proxy):
        assert proxy["team_sets[0][0].name"] == "Charmander"

    def test_getitem_through_undefined_list_item_raises_exception(self, proxy):
        with pytest.raises(IndexError) as error:
            proxy["pokemon[42].types[1]"]

        expected = IndexError(
            "Cannot access index '42' in path 'pokemon[42].types[1]', "
            "because of error: IndexError('list index out of range',)."
        )
        assert str(error.value) == str(expected)

    def test_getitem_through_undefined_list_item_raises_exception(self, proxy):
        with pytest.raises(IndexError) as error:
            proxy["pokemon[0].types[42]"]

        expected = IndexError(
            "Cannot access index '42' in path 'pokemon[0].types[42]', "
            "because of error: IndexError('list index out of range',)."
        )
        assert str(error.value) == str(expected)


class TestIn:
    def test_in(self, proxy):
        assert "trainer" in proxy
        assert "trainer.badges" in proxy
        assert "trainer.badges.Boulder" in proxy

    def test_on_undefined_nested_key_raises_exception(self, proxy):
        with pytest.raises(KeyError) as error:
            "trainer.hometown.size" not in proxy

        expected = KeyError(
            "Cannot access key 'hometown' in path 'trainer.hometown.size', "
            "because of error: KeyError('hometown',)."
        )
        assert str(error.value) == str(expected)

    def test_through_list(self, proxy):
        assert "pokemon[0].types[1]" in proxy

    def test_through_nested_list(self, proxy):
        assert "team_sets[0][0].name" in proxy

    def test_through_undefined_list_item(self, proxy):
        with pytest.raises(IndexError) as error:
            "pokemon[42].favorite_meal" in proxy

        expected = IndexError(
            "Cannot access index '42' in path 'pokemon[42].favorite_meal', "
            "because of error: IndexError('list index out of range',)."
        )
        assert str(error.value) == str(expected)


class TestPop:
    def test_pop(self, proxy):
        assert proxy.pop("trainer") == ASH
        assert "trainer" not in proxy

    def test_with_nested_key(self, proxy):
        assert proxy.pop("trainer.badges.Cascade") is False
        assert "trainer.badges.Cascade" not in proxy

    def test_when_key_is_undefined_and_default_value_is_provided(self, proxy):
        assert proxy.pop("trainer.bicycle", "Not Found") == "Not Found"

    def test_when_key_is_undefined(self, proxy):
        with pytest.raises(KeyError) as error:
            proxy.pop("trainer.bicycle")

        expected_error = KeyError(
            "Cannot access key 'bicycle' in path 'trainer.bicycle', "
            "because of error: KeyError('bicycle',)."
        )

        assert str(error.value) == str(expected_error)

    def test_returns_default_when_key_is_undefined(self, proxy):
        result = proxy.pop("trainer.bicycle", False)
        assert result is False

    def test_when_index_is_undefined(self, proxy):
        with pytest.raises(IndexError) as error:
            proxy.pop("pokemon[42]")

        expected_error = IndexError(
            "Cannot access index '42' in path 'pokemon[42]', "
            "because of error: IndexError('pop index out of range',)."
        )
        assert str(error.value) == str(expected_error)

    def test_pop_list_item(self, proxy):
        assert proxy.pop("pokemon[0].types[1]") == "Poison"
        assert len(proxy.data["pokemon"][0]["types"]) == 1

    def test_pop_list_item_through_nested_list(self, proxy):
        assert proxy.pop("team_sets[0][0]") == CHARMANDER
        assert len(proxy.data["team_sets"][0]) == 2

    def test_pop_through_list(self, proxy):
        assert proxy.pop("pokemon[0].types") == ["Grass", "Poison"]
        assert "types" not in proxy.data["pokemon"][0]

    def test_pop_through_nested_list(self, proxy):
        assert proxy.pop("team_sets[0][0].types") == ["Fire"]
        assert "types" not in proxy.data["team_sets"][0][0]


class TestSetitem:
    def test_setitem(self, proxy):
        proxy["trainer.badges.Boulder"] = False
        assert proxy["trainer"]["badges"]["Boulder"] is False

    def test_set_a_value_through_list(self, proxy):
        proxy["pokemon[0].category"] = "Onion"
        assert proxy.data["pokemon"][0]["category"] == "Onion"

    def test_set_a_value_through_nested_list(self, proxy):
        proxy["team_sets[0][0].category"] = "Lighter"
        assert proxy.data["team_sets"][0][0]["category"] == "Lighter"

    def test_set_a_value_through_a_nested_item(self, proxy):
        proxy["pokemon[0].types[1]"] = "Fire"
        assert proxy["pokemon"][0]["types"][1] == "Fire"

    def test_set_value_on_an_undefined_list_item(self, proxy):
        with pytest.raises(IndexError) as error:
            proxy["pokemon[42].types[1]"] = "Fire"

            expected = 'Index out of range in key "pokemon[42].types[1]".'
            assert str(error) == expected

    def test_set_a_value_in_nested_list_item(self, proxy):
        proxy["team_sets[0][2]"] = CHARMANDER
        assert proxy.data["team_sets"][0][2] == CHARMANDER

    def test_settitem_nested_undefined_list_item_raises_exception(self, proxy):
        with pytest.raises(IndexError) as error:
            proxy["team_sets[0][42]"] = CHARMANDER

        expected_error = IndexError(
            "Cannot access index '42' in path 'team_sets[0][42]', "
            "because of error: IndexError('list assignment index out of range',)."
        )
        assert str(error.value) == str(expected_error)


class TestSetdefault:
    def test_setdefault(self, proxy):
        assert proxy.setdefault("trainer", "Not Found") == ASH

    def test_with_nested_key(self, proxy):
        result = proxy.setdefault("trainer.badges.Boulder", "Undefined")
        assert result is True

    def test_when_key_is_undefined(self, proxy):
        result = proxy.setdefault("trainer.bicycle.size", 180)
        assert result == 180
        assert proxy.data["trainer"]["bicycle"]["size"] == 180

    def test_on_list_item(self, proxy):
        assert proxy.setdefault("pokemon[0].types[1]", "Funny") == "Poison"

    def test_on_list_item_through_nested_list(self, proxy):
        result = proxy.setdefault("team_sets[0][0]", "MissingNo")
        assert result == CHARMANDER

    def test_on_undefined_first_item(self, proxy):
        with pytest.raises(IndexError) as error:
            proxy.setdefault("pokemon[666]", BULBASAUR)

            assert str(error) == 'Index out of range in key "pokemon[666]".'

    def test_on_undefined_list_item(self, proxy):
        with pytest.raises(IndexError) as error:
            proxy.setdefault("pokemon[0].types[2]", "Funny")

            expected = 'Index out of range in key "pokemon[0].types[2]".'
            assert str(error) == expected

    def test_through_list(self, proxy):
        assert proxy.setdefault("pokemon[0].sex", "Unknown") == "Unknown"
        assert proxy.data["pokemon"][0]["sex"] == "Unknown"

    def test_undefined_key_through_list(self, proxy):
        with pytest.raises(IndexError) as error:
            proxy.setdefault("pokemon[42].sex", "Unknown")

            expected = 'Index out of range in key "pokemon[42].sex".'
            assert str(error) == expected

    def test_through_nested_list(self, proxy):
        result = proxy.setdefault("team_sets[0][0].sex", "Unknown")
        assert result == "Unknown"
        assert proxy.data["team_sets"][0][0]["sex"] == "Unknown"

    def test_undefined_list_item(self, proxy):
        with pytest.raises(IndexError) as error:
            proxy.setdefault("pokemon[42]", BULBASAUR)

            expected_error = IndexError(
                "Cannot access index '42' in path 'pokemon[42]', "
                "because of error: IndexError('list index out of range',)."
            )
            assert str(error) == expected

    def test_undefined_nested_list_item(self, proxy):
        with pytest.raises(IndexError) as error:
            proxy.setdefault("team_sets[0][42]", BULBASAUR)

            expected_error = IndexError(
                "Cannot access index '42' in path 'team_sets[0][42]', "
                "because of error: IndexError('list index out of range',)."
            )
            assert str(error) == expected


class TestUpdate:
    def test_from_dict(self, proxy):
        from_other = {"trainer.friend": "Brock"}
        proxy.update(from_other)
        assert proxy["trainer"]["friend"] == "Brock"

    def test_from_dict_and_keyword_args(self, proxy):
        from_other = {"trainer.friend": "Brock"}
        proxy.update(from_other, game="Pokemon Blue")
        assert proxy["trainer"]["friend"] == "Brock"
        assert proxy["game"] == "Pokemon Blue"

    def test_from_list(self, proxy):
        from_other = [("trainer.friend", "Brock")]
        proxy.update(from_other)
        assert proxy["trainer"]["friend"] == "Brock"

    def test_from_list_and_keyword_args(self, proxy):
        from_other = [("trainer.friend", "Brock")]
        proxy.update(from_other, game="Pokemon Blue")
        assert proxy["trainer"]["friend"] == "Brock"
        assert proxy["game"] == "Pokemon Blue"

    def test_update_from_dict_through_list(self, proxy):
        from_other = {"pokemon[1].category": "Lighter"}
        proxy.update(from_other)
        assert proxy.data["pokemon"][1]["category"] == "Lighter"

    def test_update_from_dict_through_nested_list(self, proxy):
        from_other = {"team_sets[0][0].category": "Lighter"}
        proxy.update(from_other)
        assert proxy.data["team_sets"][0][0]["category"] == "Lighter"

    def test_update_list_item_from_dict(self, proxy):
        from_other = {"pokemon[0].types[1]": "Onion"}
        proxy.update(from_other)
        assert proxy["pokemon"][0]["types"][1] == "Onion"

    def test_update_nested_list_item_from_dict(self, proxy):
        from_other = {"team_sets[0][0]": SQUIRTLE}
        proxy.update(from_other)
        assert proxy.data["team_sets"][0][0] == SQUIRTLE

    def test_update_from_dict_and_keyword_args_through_list(self, proxy):
        from_other = {"pokemon[1].category": "Lighter"}
        proxy.update(from_other, game="Pokemon Blue")
        assert proxy["pokemon"][1]["category"] == "Lighter"
        assert proxy["game"] == "Pokemon Blue"

    def test_update_from_list_through_list(self, proxy):
        from_other = [("pokemon[1].category", "Lighter")]
        proxy.update(from_other)
        assert proxy["pokemon"][1]["category"] == "Lighter"

    def test_update_from_list_and_keyword_args_through_list(self, proxy):
        from_other = [("pokemon[1].category", "Lighter")]
        proxy.update(from_other, game="Pokemon Blue")
        assert proxy["pokemon"][1]["category"] == "Lighter"
        assert proxy["game"] == "Pokemon Blue"


class TestAll:
    def test_all_returns_generator(self, proxy):
        result = proxy.all("pokemon")
        assert isinstance(result, GeneratorType) is True

    def test_generated_values(self, proxy):
        values = [item.data for item in proxy.all("pokemon")]
        assert values == [BULBASAUR, CHARMANDER, SQUIRTLE]

    def test_all_with_custom_separator(self, proxy):
        proxy.sep = "/"
        separators = [item.sep for item in proxy.all("pokemon")]

        assert all(sep == "/" for sep in separators)
