.. image:: https://github.com/ducdetronquito/scalpl/blob/master/scalpl.png
    :target: https://github.com/ducdetronquito/scalpl

Scalpl
======

.. image:: https://img.shields.io/badge/license-public%20domain-ff69b4.svg
    :target: #

.. image:: https://img.shields.io/badge/coverage-100%25-green.svg
    :target: #

.. image:: https://img.shields.io/badge/pypi-v0.1-blue.svg
    :target: https://pypi.python.org/pypi/scalpl/



**Scalpl** provides a **lightweight wrapper** that helps you to operate
on **nested dictionaries** seamlessly **through the built-in** ``dict``
**API**, by using dot-separated string keys.

It's not a drop-in replacement for your dictionnaries, just syntactic
sugar to avoid ``this['annoying']['kind']['of']['things']`` and
``prefer['a.different.approach']``.

No conversion cost, a thin computation overhead: that's **Scalpl** in a
nutshell.

Benefits
~~~~~~~~
There are a lot of good libraries to operate on nested dictionaries,
such as `Addict <https://github.com/mewwts/addict>`_ or 
`Box <https://github.com/cdgriffith/Box>`_ , but if you give **Scalpl**
a try, you will find it:

* Fast ⚡
* Powerful as the standard dict API 🚀
* Well tested 👌

Installation
~~~~~~~~~~~~

**Scalpl** is a Python3-only module that you can install via ``pip``

.. code:: sh

    pip3 install scalpl

Usage
~~~~~

**Scalpl** provides two classes that can wrap around your dictionaries:

-  **LightCut**: a wrapper that handles operations on nested ``dict``.
-  **Cut**: a wrapper that handles operations on nested ``dict`` and
   that can cut accross ``list`` item.

Usually, you will only need to use the ``Cut`` wrapper, but if you do
not need to operate through lists, you should work with the ``LightCut``
wrapper as its computation overhead is a bit smaller.

These two wrappers strictly follow the standard ``dict``
`API <https://docs.python.org/3/library/stdtypes.html#dict>`__, that
means you can operate seamlessly on ``dict``,
``collections.defaultdict`` or ``collections.OrderedDict``.

Let's see what it looks like with a toy dictionary ! 👇

.. code:: python

    from scalpl import Cut

    data = {
        'pokemons': [
            {
                'name': 'Bulbasaur',
                'type': ['Grass', 'Poison'],
                'category': 'Seed',
                'ability': 'Overgrow'
            },
            {   
                'name': 'Charmander',
                'type': 'Fire',
                'category': 'Lizard',
                'ability': 'Blaze',
            },
            {
                'name': 'Squirtle',
                'type': 'Water',
                'category': 'Tiny Turtle',
                'ability': 'Torrent',
            }
        ],
        'trainers': [
            {
                'name': 'Ash',
                'hometown': 'Pallet Town'
            }
        ]
    }
    # Just wrap your data, and you're ready to go deeper !
    proxy = Cut(data)

You can use the built-in ``dict`` API to access its values.

.. code:: python

    proxy['pokemons[0].name']
    # 'Bulbasaur'
    proxy.get('pokemons[1].sex', 'Unknown')
    # 'Unknown'
    'trainers[0].hometown' in proxy
    # True

By default, **Scalpl** uses dot as a key separator, but you are free to
use a different character that better suits your needs.

.. code:: python

    # You just have to provide one when you wrap your data.
    proxy = Cut(data, sep='->')
    # Yarrr!
    proxy['pokemons[0]->name']

You can also easily create or update any key/value pair.

.. code:: python

    proxy['pokemons[1].weaknesses'] = ['Ground', 'Rock', 'Water']
    proxy['pokemons[1].weaknesses']
    # ['Ground', 'Rock', 'Water']
    proxy.setdefault('pokemons[2].ability', 'Torrent')
    # 'Torrent'
    proxy.update({
        'trainers[0].region': 'Kanto',
    })

And it is still possible to iterate over your data.

.. code:: python

    proxy.items()
    # [('pokemons', [...]), ('trainers', [...])]
    proxy.keys()
    # ['pokemons', 'trainers']
    proxy.values()
    # [[...], [...]]

By the way, if you have to operate on a list of dictionaries, the
``Cut.all`` method is what you are looking for.

.. code:: python

    pokemons = proxy['pokemons']
    # Let's teach these pokemons some sick moves !
    for pokemon in Cut.all(pokemons):
        pokemon['moves.Scratch.power'] = 40

Also, you can remove a specific or an arbitrary key/value pair.

.. code:: python

    proxy.pop('pokemons[0].category')
    # 'Seed'
    proxy.popitem()
    # ('trainers', [...])
    del proxy['pokemons[1].type']

Because **Scalpl** is only a wrapper around your data, it means you can
get it back at will without any conversion cost. If you use an external
API that operates on dictionary, it will just work.

.. code:: python

    import json
    json.dumps(proxy.data)
    # "{'pokemons': [...]}"

Finally, you can retrieve a shallow copy of the inner dictionary or
remove all keys.

.. code:: python

    shallow_copy = proxy.copy()

    proxy.clear()

License
~~~~~~~

**Scalpl** is released into the **Public Domain**. 🎉

Ps: If we meet some day, and you think this small stuff worths it, you
can give me a beer, a coffee or a high-five in return: I would be really
happy to share a moment with you ! 🍻
