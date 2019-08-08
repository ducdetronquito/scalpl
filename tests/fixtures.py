from collections import defaultdict, OrderedDict
from copy import deepcopy
from functools import partial
import pytest
from scalpl import Cut


ASH = {
    "name": "Ash",
    "age": 666,
    "sex": None,
    "badges": {"Boulder": True, "Cascade": False},
}

BULBASAUR = {
    "name": "Bulbasaur",
    "types": ["Grass", "Poison"],
    "category": "Seed",
    "ability": "Overgrow",
}

CHARMANDER = {
    "name": "Charmander",
    "types": ["Fire"],
    "category": "Lizard",
    "ability": "Blaze",
}

SQUIRTLE = {
    "name": "Squirtle",
    "types": ["Water"],
    "category": "Tiny Turtle",
    "ability": "Torrent",
}

FIRST_SET = [CHARMANDER, SQUIRTLE, BULBASAUR]
SECOND_SET = [CHARMANDER, BULBASAUR, SQUIRTLE]
TEAM_SETS = [FIRST_SET, SECOND_SET]
POKEMON = [BULBASAUR, CHARMANDER, SQUIRTLE]


BASE = {"trainer": ASH, "pokemon": POKEMON, "team_sets": TEAM_SETS}


@pytest.fixture(
    params=[(Cut, dict), (Cut, OrderedDict), (Cut, partial(defaultdict, None))]
)
def proxy(request):
    scalpl_class = request.param[0]
    underlying_dict_class = request.param[1]
    return scalpl_class(underlying_dict_class(deepcopy(BASE)))


@pytest.fixture()
def scalpl_class(request):
    return Cut


@pytest.fixture(params=[dict, OrderedDict, partial(defaultdict, None)])
def underlying_dict_class(request):
    return request.param
