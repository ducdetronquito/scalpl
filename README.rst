.. image:: https://raw.githubusercontent.com/ducdetronquito/scalpl/master/assets/scalpl.png
    :target: https://github.com/ducdetronquito/scalpl

Scalpl
======

.. image:: https://img.shields.io/badge/license-public%20domain-ff69b4.svg
    :target: https://github.com/ducdetronquito/scalpl#license

.. image:: https://img.shields.io/badge/coverage-100%25-green.svg
    :target: #

.. image:: https://img.shields.io/badge/pypi-v0.4.1-blue.svg
    :target: https://pypi.python.org/pypi/scalpl/

.. image:: https://travis-ci.org/ducdetronquito/scalpl.svg?branch=master
     :target: https://travis-ci.org/ducdetronquito/scalpl


Outline
~~~~~~~

1. `Overview <https://github.com/ducdetronquito/scalpl#overview>`_
2. `Benefits <https://github.com/ducdetronquito/scalpl#benefits>`_
3. `Installation <https://github.com/ducdetronquito/scalpl#installation>`_
4. `Usage <https://github.com/ducdetronquito/scalpl#usage>`_
5. `Benchmark <https://github.com/ducdetronquito/scalpl#benchmark>`_
6. `Frequently Asked Questions <https://github.com/ducdetronquito/scalpl#frequently-asked-questions>`_
7. `How to Contribute <https://github.com/ducdetronquito/scalpl#how-to-contribute>`_
8. `License <https://github.com/ducdetronquito/scalpl#license>`_


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

* 🚀 Powerful as the standard dict API
* ⚡ Lightweight
* 👌 Well tested


Installation
~~~~~~~~~~~~

**Scalpl** is a Python3 library that you can install via ``pip``

.. code:: sh

    pip3 install scalpl


Usage
~~~~~

**Scalpl** provides a simple class named **Cut** that wraps around your dictionary
and handles operations on nested ``dict`` and that can cut accross ``list`` item.

This wrapper strictly follows the standard ``dict``
`API <https://docs.python.org/3/library/stdtypes.html#dict>`_, which
means you can operate seamlessly on ``dict``,
``collections.defaultdict`` or ``collections.OrderedDict`` by using their methods
with dot-separated keys.
 
Let's see what it looks like with an example ! 👇

.. code:: python

    from scalpl import Cut

    data = {
        'pokemon': [
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

    proxy['pokemon[0].name']
    # 'Bulbasaur'
    proxy.get('pokemon[1].sex', 'Unknown')
    # 'Unknown'
    'trainers[0].hometown' in proxy
    # True

By default, **Scalpl** uses dot as a key separator, but you are free to
use a different character that better suits your needs.

.. code:: python

    # You just have to provide one when you wrap your data.
    proxy = Cut(data, sep='->')
    # Yarrr!
    proxy['pokemon[0]->name']

You can also easily create or update any key/value pair.

.. code:: python

    proxy['pokemon[1].weaknesses'] = ['Ground', 'Rock', 'Water']
    proxy['pokemon[1].weaknesses']
    # ['Ground', 'Rock', 'Water']
    proxy.update({
        'trainers[0].region': 'Kanto',
    })


Following its purpose in the standard API, the *setdefault* method allows
you to create any missing dictionary when you try to access a nested key.

.. code:: python

    proxy.setdefault('pokemon[2].moves.Scratch.power', 40)
    # 40


And it is still possible to iterate over your data.

.. code:: python

    proxy.items()
    # [('pokemon', [...]), ('trainers', [...])]
    proxy.keys()
    # ['pokemon', 'trainers']
    proxy.values()
    # [[...], [...]]

By the way, if you have to operate on a list of dictionaries, the
``Cut.all`` method is what you are looking for.

.. code:: python

    # Let's teach these pokemon some sick moves !
    for pokemon in proxy.all('pokemon'):
        pokemon.setdefault('moves.Scratch.power', 40)

Also, you can remove a specific or an arbitrary key/value pair.

.. code:: python

    proxy.pop('pokemon[0].category')
    # 'Seed'
    proxy.popitem()
    # ('trainers', [...])
    del proxy['pokemon[1].type']

Because **Scalpl** is only a wrapper around your data, it means you can
get it back at will without any conversion cost. If you use an external
API that operates on dictionary, it will just work.

.. code:: python

    import json
    json.dumps(proxy.data)
    # "{'pokemon': [...]}"

Finally, you can retrieve a shallow copy of the inner dictionary or
remove all keys.

.. code:: python

    shallow_copy = proxy.copy()

    proxy.clear()


Benchmark
~~~~~~~~~

This humble benchmark is an attempt to give you an overview of the performance
of `Scalpl <https://github.com/ducdetronquito/scalpl>`_ compared to `Addict <https://github.com/mewwts/addict>`_,
`Box <https://github.com/cdgriffith/Box>`_ and the built-in ``dict``.

It will summarize the *number of operations per second* that each library is 
able to perform on a portion of the JSON dump of the `Python subreddit main page <https://www.reddit.com/r/Python.json>`_.

You can run this benchmark on your machine with the following command:

    python3 ./benchmarks/performance_comparison.py

Here are the results obtained on an Intel Core i5-7500U CPU (2.50GHz) with **Python 3.6.4**.


**Addict** 2.2.1::

    instantiate:-------- 271,132  ops per second.
    get:---------------- 276,090  ops per second.
    get through list:--- 293,773  ops per second.
    set:---------------- 300,324  ops per second.
    set through list:--- 282,149  ops per second.


**Box** 3.4.2::

    instantiate:--------- 4,093,439  ops per second.
    get:-----------------   957,069  ops per second.
    get through list:----   164,013  ops per second.
    set:-----------------   900,466  ops per second.
    set through list:----   165,522  ops per second.


**Scalpl** latest::

    instantiate:-------- 183,879,865  ops per second.
    get:----------------  14,941,355  ops per second.
    get through list:---  14,175,349  ops per second.
    set:----------------  11,320,968  ops per second.
    set through list:---  11,956,001  ops per second.


**dict**::

    instantiate:---------  37,816,714  ops per second.
    get:-----------------  84,317,032  ops per second.
    get through list:----  62,480,474  ops per second.
    set:----------------- 146,484,375  ops per second.
    set through list :--- 122,473,974  ops per second.


As a conclusion and despite being an order of magniture slower than the built-in
``dict``, **Scalpl** is faster than Box and Addict by an order of magnitude for any operations.
Besides, the gap increase in favor of **Scalpl** when wrapping large dictionaries.

Keeping in mind that this benchmark may vary depending on your use-case, it is very unlikely that
**Scalpl** will become a bottleneck of your application.


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
    proxy['it works perfectly'] = 'fine'


How to Contribute
~~~~~~~~~~~~~~~~~

Contributions are welcomed and anyone can feel free to submit a patch, report a bug or ask for a feature. Please open an issue first in order to encourage and keep tracks of potential discussions ✍️


License
~~~~~~~

**Scalpl** is released into the **Public Domain**. 🎉

Ps: If we meet some day, and you think this small stuff worths it, you
can give me a beer, a coffee or a high-five in return: I would be really
happy to share a moment with you ! 🍻
