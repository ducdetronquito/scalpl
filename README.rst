.. image:: https://raw.githubusercontent.com/ducdetronquito/scalpl/master/scalpl.png
    :target: https://github.com/ducdetronquito/scalpl

Scalpl
======

.. image:: https://img.shields.io/badge/license-public%20domain-ff69b4.svg
    :target: https://github.com/ducdetronquito/scalpl#license

.. image:: https://img.shields.io/badge/coverage-100%25-green.svg
    :target: #

.. image:: https://img.shields.io/badge/pypi-v0.2.5-blue.svg
    :target: https://pypi.python.org/pypi/scalpl/

Outline
~~~~~~~

1. `Overview <https://github.com/ducdetronquito/scalpl#overview>`_
2. `Benefits <https://github.com/ducdetronquito/scalpl#benefits>`_
3. `Installation <https://github.com/ducdetronquito/scalpl#installation>`_
4. `Usage <https://github.com/ducdetronquito/scalpl#usage>`_
5. `Benchmark <https://github.com/ducdetronquito/scalpl#benchmark>`_
6. `Frequently Asked Questions <https://github.com/ducdetronquito/scalpl#frequently-asked-questions>`_
7. `License <https://github.com/ducdetronquito/scalpl#license>`_


Overview
~~~~~~~~


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

* ⚡ Fast
* 🚀 Powerful as the standard dict API
* 👌 Well tested

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

Usually, you will only need to use the ``Cut`` wrapper, but if you do
not need to operate through lists, you should work with the ``LightCut``
wrapper as its computation overhead is a bit smaller.

These two wrappers strictly follow the standard ``dict``
`API <https://docs.python.org/3/library/stdtypes.html#dict>`_, that
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
    proxy.update({
        'trainers[0].region': 'Kanto',
    })


Following its purpose in the standard API, the *setdefault* method allows
you to create any missing dictionary when you try to access a nested key.

.. code:: python

    proxy.setdefault('pokemons[2].moves.Scratch.power', 40)
    # 40


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

    # Let's teach these pokemons some sick moves !
    for pokemon in proxy.all('pokemons'):
        pokemon.setdefault('moves.Scratch.power', 40)

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

Benchmark
~~~~~~~~~

This humble benchmark is an attempt to give you an overview of the performances
of `Scalpl <https://github.com/ducdetronquito/scalpl>`_ compared to `Addict <https://github.com/mewwts/addict>`_,
`Box <https://github.com/cdgriffith/Box>`_ and the built-in ``dict`` on **Python 3.5.3**.

It will summarize the *number of operations per second* that each library is 
able to perform on the JSON dump of the `Python subreddit main page <https://www.reddit.com/r/Python.json>`_.

You can run this tests on your machine to see if the proportion are preserved::

    python3.5 ./performance_tests.py

Here are some results

**Addict**::

    instanciate:-------- 25,430  ops per second.
    get:---------------- 25,253  ops per second.
    get through list:--- 24,591  ops per second.
    set:---------------- 25,422  ops per second.


**Box**::

    instanciate:--------- 10,037,632  ops per second.
    get:-----------------  2,623,730  ops per second.
    get through list:----    197,536  ops per second.
    set:-----------------  2,428,157  ops per second.
    set through list:----    201,214  ops per second.


**Scalpl**::

    instanciate:-------- 182,837,640  ops per second.
    get:----------------  27,471,923  ops per second.
    get through list:---  15,867,600  ops per second.
    set:----------------  27,686,668  ops per second.
    set through list:---  15,670,857  ops per second.


**dict**::

    instanciate:--------- 231,210,310  ops per second.
    get:----------------- 202,719,825  ops per second.
    get through list:---- 178,902,610  ops per second.
    set:----------------- 200,070,024  ops per second.
    set through list :--- 174,726,407  ops per second.


As a conclusion and despite being ~10 times slower than the built-in
``dict``, **Scalpl** is ~10 times faster than Box on simple read/write
operations, and ~100 times faster when it traverse lists. **Scalpl** is
also ~1000 times faster than Addict.

Às a human, I make a lot of mistakes. If you find some in this humble benchmark,
do not hesitate to send me an email, or fill in an issue.


Frequently Asked Questions:
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **What if my keys contain dots ?**
    If your keys contain a lot of dots, you should use an other
    key separator when wrapping your data::

        proxy = Cut(data, sep='->')
        proxy['computer->network->127.0.0.1']

    Otherwise, split your key in two part::

        proxy = Cut(data)
        proxy['computer.network']['127.0.0.1']

* **What if my keys contain spaces ?**::
    
    proxy = Cut(data)
    proxy = ['it works. perfectly fine']


License
~~~~~~~

**Scalpl** is released into the **Public Domain**. 🎉

Ps: If we meet some day, and you think this small stuff worths it, you
can give me a beer, a coffee or a high-five in return: I would be really
happy to share a moment with you ! 🍻
