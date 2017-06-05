from copy import deepcopy
import json
from timeit import timeit
import unittest

from scalpl import Cut

from addict import Dict
from box import Box
import requests


class TestDictPerformance(unittest.TestCase):
    """
        Base class to test performance of different
        dict wrapper regarding insertion and lookup.
    """

    # We use the JSON dump of the Python Reddit page.
    # We only collect it once.
    try:
        with open('reddit.json', 'r') as f:
            PYTHON_REDDIT = json.loads(f.read())
    except:
        PYTHON_REDDIT = requests.get(
            'https://reddit.com/r/Python/.json'
        ).json()

        with open('reddit.json', 'w') as f:
            f.write(json.dumps(PYTHON_REDDIT))

    namespace = {
        'Wrapper': dict
    }

    def setUp(self):
        self.data = deepcopy(self.PYTHON_REDDIT)
        self.namespace.update(self=self)

    def execute(self, statement, method):
        n = 1000
        time = timeit(statement, globals=self.namespace, number=n)
        print(
            '# ',
            self.namespace['Wrapper'],
            ' - ',
            method,
            ': ',
            int(60 / (time/n)),
            ' ops per second.'
        )

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
        self.execute("Wrapper(self.data).data.modhash", 'get - 1st lookup')
        self.execute("Wrapper(self.data).data.modhash", 'get - 2nd lookup')

    def test_getitem_through_list(self):
        statement = (
            "Wrapper(self.data).data.children[0].data.author"
        )
        self.execute(statement, 'get through list - 1st lookup')
        self.execute(statement, 'get through list - 2nd lookup')

    def test_setitem(self):
        statement = "Wrapper(self.data).data.modhash = 'dunno'"
        self.execute(statement, 'set - 1st lookup')
        self.execute(statement, 'set - 2nd lookup')

    def test_setitem_through_list(self):
        statement = (
            "Wrapper(self.data).data.children[0]"
            ".data.author = 'Captain Obvious'"
        )
        self.execute(statement, 'set through list - 1st lookup')
        self.execute(statement, 'set through list - 2nd lookup')


class TestAddictPerformance(TestDictPerformance):

    namespace = {
        'Wrapper': Dict
    }


if __name__ == '__main__':
    unittest.main()
