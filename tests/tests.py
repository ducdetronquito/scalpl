from collections import defaultdict, OrderedDict
from copy import deepcopy
from types import GeneratorType

from scalpl import Cut, LightCut


ASH = {
    "name": "Ash",
    "age": 666,
    "sex": None,
    "badges": {"Boulder": True, "Cascade": False},
}

BULBASAUR = {
    "name": "Bulbasaur",
    "type": ["Grass", "Poison"],
    "category": "Seed",
    "ability": "Overgrow",
}

CHARMANDER = {
    "name": "Charmander",
    "type": "Fire",
    "category": "Lizard",
    "ability": "Blaze",
}

SQUIRTLE = {
    "name": "Squirtle",
    "type": "Water",
    "category": "Tiny Turtle",
    "ability": "Torrent",
}

FIRST_SET = [CHARMANDER, SQUIRTLE, BULBASAUR]
SECOND_SET = [CHARMANDER, BULBASAUR, SQUIRTLE]

BASE = {
    "trainer": ASH,
    "pokemons": [BULBASAUR, CHARMANDER, SQUIRTLE],
    "team_sets": [FIRST_SET, SECOND_SET],
}


class TestLightCutProxiedMethods:
    """
        Here lives tests of dict methods that are simply proxied by scalpl.
    """

    Dict = dict
    Wrapper = LightCut

    def setup(self):
        self.data = self.Wrapper(deepcopy(self.Dict(BASE)))

    def test_bool(self):
        assert bool(self.data) is True

    def test_clear(self):
        self.data.clear()
        assert len(self.data) == 0

    def test_copy(self):
        assert self.data.copy() == BASE

    def test_equalty_with_Cut(self):
        other = self.Wrapper(self.data.data)
        assert self.data == other

    def test_equalty_with_dict(self):
        other = self.data.data
        assert self.data == other

    def test_fromkeys(self):
        expected = self.Wrapper({"Catz": "Lulz", "Dogz": "Lulz", "Fishz": "Lulz"})

        seq = ["Catz", "Dogz", "Fishz"]
        value = "Lulz"
        assert self.Wrapper.fromkeys(seq, value) == expected

    def test_fromkeys_default(self):
        expected = self.Wrapper({"Catz": None, "Dogz": None, "Fishz": None})

        seq = ["Catz", "Dogz", "Fishz"]
        assert self.Wrapper.fromkeys(seq) == expected

    def test_inequalty_with_Cut(self):
        other = self.Wrapper(deepcopy(BASE))
        other["trainer.name"] = "Giovanni"
        assert self.data != other

    def test_inequalty_with_dict(self):
        other = self.Wrapper(deepcopy(BASE))
        other["trainer.name"] = "Giovanni"
        assert self.data != other.data

    def test_items(self):
        result = sorted(self.data.items())
        expected = [
            ("pokemons", [BULBASAUR, CHARMANDER, SQUIRTLE]),
            ("team_sets", [FIRST_SET, SECOND_SET]),
            ("trainer", ASH),
        ]
        assert result == expected

    def test_iter(self):
        keys = sorted([key for key in self.data])
        assert keys[0] == "pokemons"
        assert keys[1] == "team_sets"
        assert keys[2] == "trainer"

    def test_keys(self):
        result = sorted(self.data.keys())
        expected = ["pokemons", "team_sets", "trainer"]
        assert result == expected

    def test_len(self):
        assert len(self.data) == 3

    def test_popitem(self):
        self.data.popitem()
        assert len(self.data) == 2

    def test_str(self):
        result = str(self.Wrapper(OrderedDict(deepcopy(BASE))))
        expected = str(OrderedDict(deepcopy(BASE)))
        assert result == expected

    def test_values(self):
        result = list(self.Wrapper(OrderedDict(deepcopy(BASE))).values())
        expected = list(OrderedDict(deepcopy(BASE)).values())
        assert result == expected


class TestLightCutCustomLogicMethods:
    """
        Here lives tests of dict methods where scalpl adds its custom logic
        to handle operate on nested dictionnaries.
    """

    Dict = dict
    Wrapper = LightCut

    def setup(self):
        self.data = self.Wrapper(deepcopy(self.Dict(BASE)))

    def test_delitem(self):
        del self.data["trainer"]
        assert "trainer" not in self.data

    def test_delitem_nested_key(self):
        del self.data["trainer.name"]
        assert "name" not in self.data["trainer"]
        assert "trainer" in self.data

    def test_delitem_undefined_key(self):
        try:
            del self.data["trainer.bicycle"]
            self.fail()
        except KeyError as error:
            expected = "'Key \"trainer.bicycle\" not found.'"
            assert str(error) == expected

    def test_get(self):
        assert self.data.get("trainer") == ASH
        assert self.data.get("trainer.badges") == {"Boulder": True, "Cascade": False}
        assert self.data.get("trainer.badges.Boulder") is True

    def test_get_undefined_key(self):
        assert self.data.get("game", "Pokemon Blue") == "Pokemon Blue"
        assert self.data.get("trainer.hometown", "Pallet Town") == "Pallet Town"
        assert self.data.get("trainer.badges.Thunder", False) is False

    def test_getitem(self):
        assert self.data["trainer"] == ASH
        assert self.data["trainer.badges"] == {"Boulder": True, "Cascade": False}
        assert self.data["trainer.badges.Cascade"] is False

    def test_getitem_undefined_key(self):
        try:
            self.data["trainer.badges.Thunder"]
            self.fail()
        except KeyError as error:
            assert str(error) == "'Key \"trainer.badges.Thunder\" not found.'"

    def test_getitem_with_custom_separator(self):
        self.data = self.Wrapper(deepcopy(BASE), sep="+")
        assert self.data["trainer"] == ASH
        assert self.data["trainer+badges"] == {"Boulder": True, "Cascade": False}
        assert self.data["trainer+badges+Boulder"] is True

    def test_in(self):
        assert "trainer" in self.data
        assert "trainer.badges" in self.data
        assert "trainer.badges.Boulder" in self.data

    def test_not_in(self):
        assert "game" not in self.data
        assert "trainer.hometown" not in self.data
        assert "trainer.badges.Thunder" not in self.data

    def test_pop(self):
        assert self.data.pop("trainer") == ASH
        assert "trainer" not in self.data

    def test_pop_nested_key(self):
        assert self.data.pop("trainer.badges.Cascade") is False
        assert "trainer.badges.Cascade" not in self.data

    def test_pop_undefined_key(self):
        assert self.data.pop("trainer.bicycle", "Not Found") == "Not Found"

    def test_setitem(self):
        self.data["trainer.badges.Boulder"] = False
        assert self.data["trainer"]["badges"]["Boulder"] is False

    def test_settitem_on_undefined_key(self):
        try:
            self.data["trainer.bicycle.size"] = 180
            self.fail()
        except KeyError as error:
            assert str(error) == "'Key \"trainer.bicycle.size\" not found.'"

    def test_setdefault(self):
        assert self.data.setdefault("trainer", "Not Found") == ASH

    def test_setdefault_nested_key(self):
        result = self.data.setdefault("trainer.badges.Boulder", "Undefined")
        assert result is True

    def test_setdefault_on_undefined_key(self):
        result = self.data.setdefault("trainer.bicycle.size", 180)
        assert result == 180
        assert self.data.data["trainer"]["bicycle"]["size"] == 180

    def test_update_from_dict(self):
        from_other = {"trainer.friend": "Brock"}
        self.data.update(from_other)
        assert self.data["trainer"]["friend"] == "Brock"

    def test_update_from_dict_and_keyword_args(self):
        from_other = {"trainer.friend": "Brock"}
        self.data.update(from_other, game="Pokemon Blue")
        assert self.data["trainer"]["friend"] == "Brock"
        assert self.data["game"] == "Pokemon Blue"

    def test_update_from_list(self):
        from_other = [("trainer.friend", "Brock")]
        self.data.update(from_other)
        assert self.data["trainer"]["friend"] == "Brock"

    def test_update_from_list_and_keyword_args(self):
        from_other = [("trainer.friend", "Brock")]
        self.data.update(from_other, game="Pokemon Blue")
        assert self.data["trainer"]["friend"] == "Brock"
        assert self.data["game"] == "Pokemon Blue"

    def test_all_returns_generator(self):
        result = self.data.all("pokemons")
        assert isinstance(result, GeneratorType) is True
        result = list(result)
        assert result[0].data == BULBASAUR
        assert result[1].data == CHARMANDER
        assert result[2].data == SQUIRTLE

    def test_all_with_custom_separator(self):
        self.data.sep = "/"
        result = self.data.all("pokemons")
        result = list(result)
        assert result[0].sep == "/"
        assert result[1].sep == "/"
        assert result[2].sep == "/"


class TestLightCutWithOrderedDictPM(TestLightCutProxiedMethods):
    Dict = OrderedDict
    Wrapper = LightCut


class TestLightCutWithOrderedDictCLM(TestLightCutCustomLogicMethods):
    Dict = OrderedDict
    Wrapper = LightCut


class TestLightCutWithDefaultDictPM(TestLightCutProxiedMethods):
    Dict = defaultdict
    Wrapper = LightCut

    def setup(self):
        self.data = self.Wrapper(deepcopy(self.Dict(None, BASE)))


class TestLightCutWithDefaultDictCLM(TestLightCutCustomLogicMethods):
    Dict = defaultdict
    Wrapper = LightCut

    def setup(self):
        self.data = self.Wrapper(deepcopy(self.Dict(None, BASE)))


class TestCutWithDictPM(TestLightCutProxiedMethods):
    Dict = dict
    Wrapper = Cut


class TestCutWithDictCLM(TestLightCutCustomLogicMethods):
    Dict = dict
    Wrapper = Cut

    def test_delitem_through_list(self):
        del self.data["pokemons[1].category"]
        assert "category" not in self.data.data["pokemons"][1]

    def test_delitem_through_nested_list(self):
        del self.data["team_sets[0][0].name"]
        assert "name" not in self.data.data["team_sets"][0][0]

    def test_delitem_list_item(self):
        assert len(self.data.data["pokemons"][0]["type"]) == 2
        del self.data["pokemons[0].type[1]"]
        assert len(self.data.data["pokemons"][0]["type"]) == 1

    def test_delitem_undefined_list_item(self):
        try:
            del self.data["pokemons[42].type[1]"]
            self.fail()
        except IndexError as error:
            expected = 'Index out of range in key "pokemons[42].type[1]".'
            assert str(error) == expected

    def test_delitem_list_item_through_nested_list(self):
        assert len(self.data.data["team_sets"][0]) == 3
        del self.data["team_sets[0][0]"]
        assert len(self.data.data["team_sets"][0]) == 2

    def test_delitem_list_item_through_undefined_nested_list(self):
        try:
            del self.data["team_sets[42][0]"]
            self.fail()
        except IndexError as error:
            expected = 'Index out of range in key "team_sets[42][0]".'
            assert str(error) == expected

    def test_get_through_list(self):
        assert self.data.get("pokemons[0].type[1]") == "Poison"

    def test_get_through_nested_list(self):
        result = self.data.get("team_sets[0][0].name", "Unknwown")
        assert result == "Charmander"

    def test_get_undefined_key_through_list(self):
        assert self.data.get("pokemons[0].sex", "Unknown") == "Unknown"

    def test_get_undefined_list_item(self):
        assert self.data.get("pokemons[0].type[42]", "Unknown") == "Unknown"

    def test_getitem_through_list(self):
        assert self.data["pokemons[0].type[1]"] == "Poison"

    def test_getitem_through_nested_list(self):
        result = self.data["team_sets[0][0].name"]
        assert result == "Charmander"

    def test_getitem_through_undefined_list_item(self):
        try:
            self.data["pokemons[42].type[1]"]
            self.fail()
        except IndexError as error:
            expected = 'Index out of range in key "pokemons[42].type[1]".'
            assert str(error) == expected

    def test_in_through_list(self):
        assert "pokemons[0].type[1]" in self.data

    def test_in_through_nested_list(self):
        assert "team_sets[0][0].name" in self.data

    def test_not_in_through_list(self):
        assert "pokemons[1].favorite_meal" not in self.data

    def test_not_in_through_nested_list(self):
        assert "team_sets[0][0].favorite_meal" not in self.data

    def test_not_in_through_undefined_list_item(self):
        assert "pokemons[42].favorite_meal" not in self.data

    def test_pop_list_item(self):
        assert len(self.data.data["pokemons"][0]["type"]) == 2
        result = self.data.pop("pokemons[0].type[1]")
        assert result == "Poison"
        assert len(self.data.data["pokemons"][0]["type"]) == 1

    def test_pop_list_item_through_nested_list(self):
        assert len(self.data.data["team_sets"][0]) == 3
        result = self.data.pop("team_sets[0][0]")
        assert result == CHARMANDER
        assert len(self.data.data["team_sets"][0]) == 2

    def test_pop_through_list(self):
        result = self.data.pop("pokemons[0].type")
        assert result == ["Grass", "Poison"]
        assert "type" not in self.data.data["pokemons"][0]

    def test_pop_through_nested_list(self):
        result = self.data.pop("team_sets[0][0].type")
        assert result == "Fire"
        assert "type" not in self.data.data["team_sets"][0][0]

    def test_setdefault_on_list_item(self):
        assert self.data.setdefault("pokemons[0].type[1]", "Funny") == "Poison"

    def test_setdefault_on_list_item_through_nested_list(self):
        result = self.data.setdefault("team_sets[0][0]", "MissingNo")
        assert result == CHARMANDER

    def test_setdefault_on_undefined_first_item(self):
        try:
            self.data.setdefault("pokemons[666]", BULBASAUR)
            self.fail()
        except IndexError as error:
            assert str(error) == 'Index out of range in key "pokemons[666]".'

    def test_setdefault_on_undefined_list_item(self):
        try:
            self.data.setdefault("pokemons[0].type[2]", "Funny")
            self.fail()
        except IndexError as error:
            expected = 'Index out of range in key "pokemons[0].type[2]".'
            assert str(error) == expected

    def test_setdefault_through_list(self):
        assert "sex" not in self.data["pokemons"][0]
        assert self.data.setdefault("pokemons[0].sex", "Unknown") == "Unknown"
        assert self.data.data["pokemons"][0]["sex"] == "Unknown"

    def test_setdefault_undefined_key_through_list(self):
        try:
            self.data.setdefault("pokemons[42].sex", "Unknown")
            self.fail()
        except IndexError as error:
            expected = 'Index out of range in key "pokemons[42].sex".'
            assert str(error) == expected

    def test_setdefault_through_nested_list(self):
        assert "sex" not in self.data["team_sets"][0][0]
        result = self.data.setdefault("team_sets[0][0].sex", "Unknown")
        assert result == "Unknown"
        assert self.data.data["team_sets"][0][0]["sex"] == "Unknown"

    def test_setdefault_undefined_first_item_in_nested_list_item(self):
        try:
            self.data.setdefault("team_sets[42][0]", BULBASAUR)
            self.fail()
        except IndexError as error:
            expected = 'Index out of range in key "team_sets[42][0]".'
            assert str(error) == expected

    def test_setdefault_undefined_nested_list_item(self):
        try:
            self.data.setdefault("team_sets[0][42]", BULBASAUR)
            self.failt()
        except IndexError as error:
            expected = 'Index out of range in key "team_sets[0][42]".'
            assert str(error) == expected

    def test_setitem_through_list(self):
        self.data["pokemons[0].category"] = "Onion"
        assert self.data.data["pokemons"][0]["category"] == "Onion"

    def test_setitem_through_nested_list(self):
        self.data["team_sets[0][0].category"] = "Lighter"
        assert self.data.data["team_sets"][0][0]["category"] == "Lighter"

    def test_setitem_list_item(self):
        assert self.data.data["pokemons"][0]["type"][1] == "Poison"
        self.data["pokemons[0].type[1]"] = "Fire"
        assert self.data["pokemons"][0]["type"][1] == "Fire"

    def test_setitem_undefined_list_item(self):
        try:
            self.data["pokemons[42].type[1]"] = "Fire"
            self.fail()
        except IndexError as error:
            expected = 'Index out of range in key "pokemons[42].type[1]".'
            assert str(error) == expected

    def test_settitem_nested_list_item(self):
        assert self.data.data["team_sets"][0][2] == BULBASAUR
        self.data["team_sets[0][2]"] = CHARMANDER
        assert self.data.data["team_sets"][0][2] == CHARMANDER

    def test_settitem_nested_undefined_list_item(self):
        try:
            self.data["team_sets[42][0]"] = CHARMANDER
            self.fail()
        except IndexError as error:
            expected = 'Index out of range in key "team_sets[42][0]".'
            assert str(error) == expected

    def test_update_from_dict_through_list(self):
        assert self.data.data["pokemons"][1]["category"] == "Lizard"
        from_other = {"pokemons[1].category": "Lighter"}
        self.data.update(from_other)
        assert self.data.data["pokemons"][1]["category"] == "Lighter"

    def test_update_from_dict_through_nested_list(self):
        assert self.data.data["team_sets"][0][0]["category"] == "Lizard"
        from_other = {"team_sets[0][0].category": "Lighter"}
        self.data.update(from_other)
        assert self.data.data["team_sets"][0][0]["category"] == "Lighter"

    def test_update_list_item_from_dict(self):
        assert self.data["pokemons"][0]["type"][1] == "Poison"
        from_other = {"pokemons[0].type[1]": "Onion"}
        self.data.update(from_other)
        assert self.data["pokemons"][0]["type"][1] == "Onion"

    def test_update_nested_list_item_from_dict(self):
        assert self.data.data["team_sets"][0][0] == CHARMANDER
        from_other = {"team_sets[0][0]": SQUIRTLE}
        self.data.update(from_other)
        assert self.data.data["team_sets"][0][0] == SQUIRTLE

    def test_update_from_dict_and_keyword_args_through_list(self):
        assert "game" not in self.data
        assert self.data["pokemons"][1]["category"] == "Lizard"
        from_other = {"pokemons[1].category": "Lighter"}
        self.data.update(from_other, game="Pokemon Blue")
        assert self.data["pokemons"][1]["category"] == "Lighter"
        assert self.data["game"] == "Pokemon Blue"

    def test_update_from_list_through_list(self):
        assert self.data["pokemons"][1]["category"] == "Lizard"
        from_other = [("pokemons[1].category", "Lighter")]
        self.data.update(from_other)
        assert self.data["pokemons"][1]["category"] == "Lighter"

    def test_update_from_list_and_keyword_args_through_list(self):
        assert "game" not in self.data
        assert self.data["pokemons"][1]["category"] == "Lizard"
        from_other = [("pokemons[1].category", "Lighter")]
        self.data.update(from_other, game="Pokemon Blue")
        assert self.data["pokemons"][1]["category"] == "Lighter"
        assert self.data["game"] == "Pokemon Blue"


class TestCutWithOrderedDictPM(TestCutWithDictPM):
    Dict = OrderedDict
    Wrapper = Cut


class TestCutWithOrderedDictCLM(TestCutWithDictCLM):
    Dict = OrderedDict
    Wrapper = Cut


class TestCutWithDefaultDictPM(TestCutWithDictPM):
    Dict = defaultdict
    Wrapper = Cut

    def setup(self):
        self.data = self.Wrapper(deepcopy(self.Dict(None, BASE)))


class TestCutWithDefaultDictCLM(TestCutWithDictCLM):
    Dict = defaultdict
    Wrapper = Cut

    def setup(self):
        self.data = self.Wrapper(deepcopy(self.Dict(None, BASE)))
