from scalpl import Cut

from copy import deepcopy
from types import GeneratorType
import unittest

from collections import defaultdict, OrderedDict


class TestProxiedMethods(unittest.TestCase):
    """
        Here lives tests of dict methods that are simply proxied by scalpl.
    """
    BASE = {
        'Catz': 'Meoww',
        'Dogz': 'Waff',
        'Fishz': 'Blubz'
    }
    Dict = dict

    def setUp(self):
        self.data = Cut(deepcopy(self.Dict(self.BASE)))

    def test_bool(self):
        assert bool(self.data) is True

    def test_clear(self):
        self.data.clear()
        assert len(self.data) == 0

    def test_copy(self):
        assert self.data.copy() == {
            'Catz': 'Meoww',
            'Dogz': 'Waff',
            'Fishz': 'Blubz'
        }

    def test_delete_key(self):
        l = self.data.copy()
        del l['Catz']
        assert 'Catz' not in l

    def test_equalty_with_Cut(self):
        other = Cut(self.data.copy())
        assert self.data == other

    def test_equalty_with_dict(self):
        other = self.data.copy()
        assert self.data == other

    def test_fromkeys(self):
        expected = Cut({
            'Catz': 'Lulz',
            'Dogz': 'Lulz',
            'Fishz': 'Lulz',
        })

        seq = ['Catz', 'Dogz', 'Fishz']
        value = 'Lulz'
        assert Cut.fromkeys(seq, value) == expected

    def test_fromkeys_default(self):
        expected = Cut({
            'Catz': None,
            'Dogz': None,
            'Fishz': None,
        })

        seq = ['Catz', 'Dogz', 'Fishz']
        assert Cut.fromkeys(seq) == expected

    def test_inequalty_with_Cut(self):
        other = Cut({
            'Catz': 'Meoww',
            'Dogz': 'Waff',
            'Snakz': 'Kzzz'
        })
        assert self.data != other

    def test_inequalty_with_dict(self):
        other = {
            'Catz': 'Meoww',
            'Dogz': 'Waff',
            'Snakz': 'Kzzz'
        }
        assert self.data != other

    def test_items(self):
        result = sorted(self.data.items())
        expected = [('Catz', 'Meoww'), ('Dogz', 'Waff'), ('Fishz', 'Blubz')]
        self.assertListEqual(result, expected)

    def test_keys(self):
        result = sorted(self.data.keys())
        expected = ['Catz', 'Dogz', 'Fishz']
        self.assertListEqual(result, expected)

    def test_len(self):
        assert len(self.data) == 3

    def test_popitem(self):
        self.data.popitem()
        assert len(self.data) == 2

    def test_values(self):
        result = sorted(self.data.values())
        expected = ['Blubz', 'Meoww', 'Waff']
        self.assertListEqual(result, expected)


class TestCustomLogicMethods(unittest.TestCase):
    """
        Here lives tests of dict methods where scalpl adds its custom logic
        to handle operate on nested dictionnaries.
    """
    BASE = {
        'users': {
            'john': {
                'age': 666,
                'sex': None,
            }
        }
    }
    Dict = dict

    def setUp(self):
        self.data = Cut(deepcopy(self.Dict(self.BASE)))

    def test_get(self):
        assert self.data.get('users') == {'john': {'age': 666, 'sex': None}}
        assert self.data.get('users:john') == {'age': 666, 'sex': None}
        assert self.data.get('users:john:age') == 666

    def test_get_undefined_key(self):
        assert self.data.get('admins', 'default') == 'default'
        assert self.data.get('users:jack', 'default') == 'default'
        assert self.data.get('users:john:email', 'default') == 'default'

    def test_getitem(self):
        assert self.data['users'] == {'john': {'age': 666, 'sex': None}}
        assert self.data['users:john'] == {'age': 666, 'sex': None}
        assert self.data['users:john:age'] == 666

    def test_getitem_undefined_key(self):
        with self.assertRaises(KeyError):
            self.data['admins']

        with self.assertRaises(KeyError):
            self.data['users:jack']

        with self.assertRaises(KeyError):
            self.data['users:john:email']

    def test_getitem_with_custom_separator(self):
        self.data = Cut(deepcopy(self.BASE), sep='+')
        assert self.data['users'] == {'john': {'age': 666, 'sex': None}}
        assert self.data['users+john'] == {'age': 666, 'sex': None}
        assert self.data['users+john+age'] == 666

    def test_in(self):
        assert 'users' in self.data
        assert 'users:john' in self.data
        assert 'users:john:age' in self.data
        assert 'users:john:sex' in self.data

    def test_not_in(self):
        assert 'admins' not in self.data
        assert 'users:jack' not in self.data
        assert 'users:john:email' not in self.data

    def test_pop(self):
        data = Cut({
            'users': {
                'john': {
                    'age': 666,
                }
            }
        })
        assert data.pop('users:john:age') == 666
        assert 'users:john:age' not in data

    def test_set(self):
        data = Cut()
        data['users:john:age'] = 666
        assert data['users']['john']['age'] == 666

    def test_setdefault_on_undefined_key(self):
        data = Cut()
        assert data.setdefault('users:john:age', 666) == 666
        assert data['users']['john']['age'] == 666

    def test_update_from_dict(self):
        data = Cut()
        from_other = {'user:john:age': 666}
        data.update(from_other)
        assert data['user:john:age'] == 666

    def test_update_from_dict_and_keyword_args(self):
        data = Cut()
        from_other = {'user:john:age': 666}
        data.update(from_other, admin='jack')
        assert data['user:john:age'] == 666
        assert data['admin'] == 'jack'

    def test_update_from_list(self):
        data = Cut()
        from_other = [('user:john:age', 666)]
        data.update(from_other)
        assert data['user:john:age'] == 666

    def test_update_from_list_and_keyword_args(self):
        data = Cut()
        data = Cut()
        from_other = [('user:john:age', 666)]
        data.update(from_other, admin='jack')
        assert data['user:john:age'] == 666
        assert data['admin'] == 'jack'


class TestCutOwnAPI(unittest.TestCase):

    def setUp(self):
        self.john = {'name': 'John'}
        self.joe = {'name': 'Joe'}
        self.users = [self.joe, self.john]

    def test_all_returns_generator(self):
        result = Cut.all(self.users)
        assert isinstance(result, GeneratorType) is True
        result = list(result)
        assert result[0].data == self.joe
        assert result[1].data == self.john

    def test_all_with_custom_separator(self):
        result = Cut.all(self.users, sep='/')
        result = list(result)
        assert result[0].sep == '/'
        assert result[1].sep == '/'


class TestOrderedDictPM(TestProxiedMethods):
    Dict = OrderedDict


class TestOrderedDictCLM(TestCustomLogicMethods):
    Dict = OrderedDict


class TestDefaultDictPM(TestProxiedMethods):
    Dict = defaultdict

    def setUp(self):
        self.data = Cut(deepcopy(self.Dict(None, self.BASE)))


class TestDefaultDictCLM(TestCustomLogicMethods):
    Dict = defaultdict

    def setUp(self):
        self.data = Cut(deepcopy(self.Dict(None, self.BASE)))


if __name__ == '__main__':
    unittest.main()
