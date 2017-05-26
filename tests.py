from collections import defaultdict, OrderedDict
from copy import deepcopy
from timeit import timeit
from types import GeneratorType
import unittest

from scalpl import Cut, LightCut

from addict import Dict
from box import Box
import requests


ASH = {
    'name': 'Ash',
    'age': 666,
    'sex': None,
    'badges': {
        'Boulder': True,
        'Cascade': False,
    }
}

BULBASAUR = {
    'name': 'Bulbasaur',
    'type': ['Grass', 'Poison'],
    'category': 'Seed',
    'ability': 'Overgrow'
}

CHARMANDER = {
    'name': 'Charmander',
    'type': 'Fire',
    'category': 'Lizard',
    'ability': 'Blaze',
}

SQUIRTLE = {
    'name': 'Squirtle',
    'type': 'Water',
    'category': 'Tiny Turtle',
    'ability': 'Torrent',
}

BASE = {
    'trainer': ASH,
    'pokemons': [
            BULBASAUR,
            CHARMANDER,
            SQUIRTLE
    ],
}


class TestLightCutProxiedMethods(unittest.TestCase):
    """
        Here lives tests of dict methods that are simply proxied by scalpl.
    """
    Dict = dict
    Wrapper = LightCut

    def setUp(self):
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
        expected = self.Wrapper({
            'Catz': 'Lulz',
            'Dogz': 'Lulz',
            'Fishz': 'Lulz',
        })

        seq = ['Catz', 'Dogz', 'Fishz']
        value = 'Lulz'
        assert self.Wrapper.fromkeys(seq, value) == expected

    def test_fromkeys_default(self):
        expected = self.Wrapper({
            'Catz': None,
            'Dogz': None,
            'Fishz': None,
        })

        seq = ['Catz', 'Dogz', 'Fishz']
        assert self.Wrapper.fromkeys(seq) == expected

    def test_inequalty_with_Cut(self):
        other = self.Wrapper(deepcopy(BASE))
        other['trainer.name'] = 'Giovanni'
        assert self.data != other

    def test_inequalty_with_dict(self):
        other = self.Wrapper(deepcopy(BASE))
        other['trainer.name'] = 'Giovanni'
        assert self.data != other.data

    def test_items(self):
        result = sorted(self.data.items())
        expected = [
            ('pokemons', [BULBASAUR, CHARMANDER, SQUIRTLE]),
            ('trainer', ASH)
        ]
        self.assertListEqual(result, expected)

    def test_iter(self):
        keys = sorted([key for key in self.data])
        assert keys[0] == 'pokemons'
        assert keys[1] == 'trainer'

    def test_keys(self):
        result = sorted(self.data.keys())
        expected = ['pokemons', 'trainer']
        self.assertListEqual(result, expected)

    def test_len(self):
        assert len(self.data) == 2

    def test_popitem(self):
        self.data.popitem()
        assert len(self.data) == 1

    def test_str(self):
        result = str(self.Wrapper(OrderedDict(deepcopy(BASE))))
        expected = str(OrderedDict(deepcopy(BASE)))
        assert result == expected

    def test_values(self):
        result = list(self.Wrapper(OrderedDict(deepcopy(BASE))).values())
        expected = list(OrderedDict(deepcopy(BASE)).values())
        assert result == expected


class TestLightCutCustomLogicMethods(unittest.TestCase):
    """
        Here lives tests of dict methods where scalpl adds its custom logic
        to handle operate on nested dictionnaries.
    """
    Dict = dict
    Wrapper = LightCut

    def setUp(self):
        self.data = self.Wrapper(deepcopy(self.Dict(BASE)))

    def test_delitem(self):
        del self.data['trainer']
        assert 'trainer' not in self.data

    def test_delitem_nested_key(self):
        del self.data['trainer.name']
        assert 'name' not in self.data['trainer']
        assert 'trainer' in self.data

    def test_delitem_undefined_key(self):
        with self.assertRaises(KeyError):
            del self.data['trainer.bicycle']

    def test_get(self):
        assert self.data.get('trainer') == ASH
        assert self.data.get('trainer.badges') == {
            'Boulder': True,
            'Cascade': False,
        }
        assert self.data.get('trainer.badges.Boulder') is True

    def test_get_undefined_key(self):
        assert self.data.get('game', 'Pokemon Blue') == 'Pokemon Blue'
        assert (
            self.data.get('trainer.hometown', 'Pallet Town') == 'Pallet Town'
        )
        assert self.data.get('trainer.badges.Thunder', False) is False

    def test_getitem(self):
        assert self.data['trainer'] == ASH
        assert self.data['trainer.badges'] == {
            'Boulder': True,
            'Cascade': False,
        }
        assert self.data['trainer.badges.Cascade'] is False

    def test_getitem_undefined_key(self):
        with self.assertRaises(KeyError):
            self.data['game']

        with self.assertRaises(KeyError):
            self.data['trainer.hometown']

        with self.assertRaises(KeyError):
            self.data['trainer.badges.Thunder']

    def test_getitem_with_custom_separator(self):
        self.data = self.Wrapper(deepcopy(BASE), sep='+')
        assert self.data['trainer'] == ASH
        assert self.data['trainer+badges'] == {
            'Boulder': True,
            'Cascade': False,
        }
        assert self.data['trainer+badges+Boulder'] is True

    def test_in(self):
        assert 'trainer' in self.data
        assert 'trainer.badges' in self.data
        assert 'trainer.badges.Boulder' in self.data

    def test_not_in(self):
        assert 'game' not in self.data
        assert 'trainer.hometown' not in self.data
        assert 'trainer.badges.Thunder' not in self.data

    def test_pop(self):
        assert self.data.pop('trainer') == ASH
        assert 'trainer' not in self.data

    def test_pop_nested_key(self):
        assert self.data.pop('trainer.badges.Cascade') is False
        assert 'trainer.badges.Cascade' not in self.data

    def test_pop_undefined_key(self):
        assert self.data.pop('trainer.bicycle', 'Not Found') == 'Not Found'

    def test_set(self):
        self.data['trainer.badges.Boulder'] = False
        assert self.data['trainer']['badges']['Boulder'] is False

    def test_setdefault(self):
        assert self.data.setdefault('trainer', 'Not Found') == ASH

    def test_setdefault_nested_key(self):
        result = self.data.setdefault('trainer.badges.Boulder', 'Undefined')
        assert result is True

    def test_setdefault_on_undefined_key(self):
        assert self.data.setdefault('trainer.badges.Thunder', True) is True
        assert self.data['trainer']['badges']['Thunder'] is True

    def test_update_from_dict(self):
        from_other = {'trainer.friend': 'Brock'}
        self.data.update(from_other)
        assert self.data['trainer']['friend'] == 'Brock'

    def test_update_from_dict_and_keyword_args(self):
        from_other = {'trainer.friend': 'Brock'}
        self.data.update(from_other, game='Pokemon Blue')
        assert self.data['trainer']['friend'] == 'Brock'
        assert self.data['game'] == 'Pokemon Blue'

    def test_update_from_list(self):
        from_other = [('trainer.friend', 'Brock')]
        self.data.update(from_other)
        assert self.data['trainer']['friend'] == 'Brock'

    def test_update_from_list_and_keyword_args(self):
        from_other = [('trainer.friend', 'Brock')]
        self.data.update(from_other, game='Pokemon Blue')
        assert self.data['trainer']['friend'] == 'Brock'
        assert self.data['game'] == 'Pokemon Blue'

    def test_all_returns_generator(self):
        pokemons = self.data['pokemons']
        result = self.Wrapper.all(pokemons)
        assert isinstance(result, GeneratorType) is True
        result = list(result)
        assert result[0].data == BULBASAUR
        assert result[1].data == CHARMANDER
        assert result[2].data == SQUIRTLE

    def test_all_with_custom_separator(self):
        pokemons = self.data['pokemons']
        result = self.Wrapper.all(pokemons, sep='/')
        result = list(result)
        assert result[0].sep == '/'
        assert result[1].sep == '/'
        assert result[2].sep == '/'


class TestLightCutWithOrderedDictPM(TestLightCutProxiedMethods):
    Dict = OrderedDict
    Wrapper = LightCut


class TestLightCutWithOrderedDictCLM(TestLightCutCustomLogicMethods):
    Dict = OrderedDict
    Wrapper = LightCut


class TestLightCutWithDefaultDictPM(TestLightCutProxiedMethods):
    Dict = defaultdict
    Wrapper = LightCut

    def setUp(self):
        self.data = self.Wrapper(deepcopy(self.Dict(None, BASE)))


class TestLightCutWithDefaultDictCLM(TestLightCutCustomLogicMethods):
    Dict = defaultdict
    Wrapper = LightCut

    def setUp(self):
        self.data = self.Wrapper(deepcopy(self.Dict(None, BASE)))


class TestCutWithDictPM(TestLightCutProxiedMethods):
    Dict = dict
    Wrapper = Cut


class TestCutWithDictCLM(TestLightCutCustomLogicMethods):
    Dict = dict
    Wrapper = Cut

    def test_delitem_through_list(self):
        del self.data['pokemons[1].category']
        assert 'category' not in self.data['pokemons'][1]

    def test_delitem_list_item(self):
        assert len(self.data['pokemons'][0]['type']) == 2
        del self.data['pokemons[0].type[1]']
        assert len(self.data['pokemons'][0]['type']) == 1

    def test_get_through_list(self):
        assert self.data.get('pokemons[0].type[1]') == 'Poison'

    def test_get_undefined_key_through_list(self):
        assert self.data.get('pokemons[0].sex', 'Unknown') == 'Unknown'

    def test_get_undefined_list_item(self):
        assert self.data.get('pokemons[0].type[42]', 'Unknown') == 'Unknown'

    def test_getitem_through_list(self):
        assert self.data['pokemons[0].type[1]'] == 'Poison'

    def test_in_through_list(self):
        assert 'pokemons[0].type[1]' in self.data

    def test_not_in_through_list(self):
        assert 'pokemons[1].category' in self.data

    def test_pop_list_item(self):
        assert len(self.data['pokemons'][0]['type']) == 2
        result = self.data.pop('pokemons[0].type[1]')
        assert result == 'Poison'
        assert len(self.data['pokemons'][0]['type']) == 1

    def test_pop_through_list(self):
        result = self.data.pop('pokemons[0].type')
        assert result == ['Grass', 'Poison']
        assert 'type' not in self.data['pokemons'][0]

    def test_setdefault_on_list_item(self):
        assert self.data.setdefault('pokemons[0].type[1]', 'Funny') == 'Poison'

    def test_setdefault_on_undefined_list_item(self):
        with self.assertRaises(IndexError):
            self.data.setdefault('pokemons[0].type[2]', 'Funny') == 'Funny'

    def test_setdefault_through_list(self):
        assert 'sex' not in self.data['pokemons'][0]
        assert self.data.setdefault('pokemons[0].sex', 'Unknown') == 'Unknown'
        assert self.data['pokemons'][0]['sex'] == 'Unknown'

    def test_set_through_list(self):
        self.data['pokemons[0].category'] = 'Onion'
        assert self.data.data['pokemons'][0]['category'] == 'Onion'

    def test_setitem_list_item(self):
        assert self.data['pokemons'][0]['type'][1] == 'Poison'
        self.data['pokemons[0].type[1]'] = 'Fire'
        assert self.data['pokemons'][0]['type'][1] == 'Fire'

    def test_update_from_dict_through_list(self):
        assert self.data['pokemons'][1]['category'] == 'Lizard'
        from_other = {'pokemons[1].category': 'Lighter'}
        self.data.update(from_other)
        assert self.data['pokemons'][1]['category'] == 'Lighter'

    def test_update_list_item_from_dict(self):
        assert self.data['pokemons'][0]['type'][1] == 'Poison'
        from_other = {'pokemons[0].type[1]': 'Onion'}
        self.data.update(from_other)
        assert self.data['pokemons'][0]['type'][1] == 'Onion'

    def test_update_from_dict_and_keyword_args_through_list(self):
        assert 'game' not in self.data
        assert self.data['pokemons'][1]['category'] == 'Lizard'
        from_other = {'pokemons[1].category': 'Lighter'}
        self.data.update(from_other, game='Pokemon Blue')
        assert self.data['pokemons'][1]['category'] == 'Lighter'
        assert self.data['game'] == 'Pokemon Blue'

    def test_update_from_list_through_list(self):
        assert self.data['pokemons'][1]['category'] == 'Lizard'
        from_other = [('pokemons[1].category', 'Lighter')]
        self.data.update(from_other)
        assert self.data['pokemons'][1]['category'] == 'Lighter'

    def test_update_from_list_and_keyword_args_through_list(self):
        assert 'game' not in self.data
        assert self.data['pokemons'][1]['category'] == 'Lizard'
        from_other = [('pokemons[1].category', 'Lighter')]
        self.data.update(from_other, game='Pokemon Blue')
        assert self.data['pokemons'][1]['category'] == 'Lighter'
        assert self.data['game'] == 'Pokemon Blue'


class TestCutWithOrderedDictPM(TestCutWithDictPM):
    Dict = OrderedDict
    Wrapper = Cut


class TestCutWithOrderedDictCLM(TestCutWithDictCLM):
    Dict = OrderedDict
    Wrapper = Cut


class TestCutWithDefaultDictPM(TestCutWithDictPM):
    Dict = defaultdict
    Wrapper = Cut

    def setUp(self):
        self.data = self.Wrapper(deepcopy(self.Dict(None, BASE)))


class TestCutWithDefaultDictCLM(TestCutWithDictCLM):
    Dict = defaultdict
    Wrapper = Cut

    def setUp(self):
        self.data = self.Wrapper(deepcopy(self.Dict(None, BASE)))


class TestDictPerformance(unittest.TestCase):
    """
        Base class to test performance of different
        dict wrapper regarding insertion and lookup.
    """

    PYTHON_REDDIT = requests.get(
        'https://reddit.com/r/Python/.json'
    ).json()

    namespace = {
        'Wrapper': dict
    }

    def setUp(self):
        self.data = deepcopy(self.PYTHON_REDDIT)
        self.namespace.update(self=self)

    def execute(self, statement, method):
        n = 1000
        time = timeit(statement, globals=self.namespace, number=n)
        print('# ', self.namespace['Wrapper'], ' - ', method, ': ', time/n)

    def test_init(self):
        self.execute('Wrapper(self.data)', 'instanciate')

    def test_getitem(self):
        self.execute("Wrapper(self.data)['data']['modhash']", 'get')

    def test_getitem_through_list(self):
        statement = (
            "Wrapper(self.data)['data']['children'][0]['data']['author']"
        )
        self.execute(statement, 'get through list')

    def test_setitem(self):
        statement = "Wrapper(self.data)['data']['modhash'] = 'dunno'"
        self.execute(statement, 'set')

    def test_setitem_through_list(self):
        statement = (
            "Wrapper(self.data)['data']['children'][0]"
            "['data']['author'] = 'Captain Obvious'"
        )
        self.execute(statement, 'set through list')


class TestCutPerformance(TestDictPerformance):

    namespace = {
        'Wrapper': Cut
    }

    def test_getitem(self):
        self.execute("Wrapper(self.data)['data.modhash']", 'get')

    def test_getitem_through_list(self):
        statement = (
            "Wrapper(self.data)['data.children[0].data.author']"
        )
        self.execute(statement, 'get through list')

    def test_setitem(self):
        statement = "Wrapper(self.data)['data.modhash'] = 'dunno'"
        self.execute(statement, 'set')

    def test_setitem_through_list(self):
        statement = (
            "Wrapper(self.data)['data.children[0]"
            ".data.author'] = 'Captain Obvious'"
        )
        self.execute(statement, 'set through list')


class TestBoxPerformance(TestDictPerformance):

    namespace = {
        'Wrapper': Box
    }

    def test_getitem(self):
        self.execute("Wrapper(self.data).data.modhash", 'get')
        self.execute("Wrapper(self.data).data.modhash", 'get - REAL')

    def test_getitem_through_list(self):
        statement = (
            "Wrapper(self.data).data.children[0].data.author"
        )
        self.execute(statement, 'get through list')
        self.execute(statement, 'get through list - REAL')

    def test_setitem(self):
        statement = "Wrapper(self.data).data.modhash = 'dunno'"
        self.execute(statement, 'set')
        self.execute(statement, 'set - REAL')

    def test_setitem_through_list(self):
        statement = (
            "Wrapper(self.data).data.children[0]"
            ".data.author = 'Captain Obvious'"
        )
        self.execute(statement, 'set through list')
        self.execute(statement, 'set through list - REAL')


class TestAddictPerformance(TestDictPerformance):

    namespace = {
        'Wrapper': Dict
    }


if __name__ == '__main__':
    unittest.main()
