<p align="center">
    <img src="scalpl.png">
    <h1 align="center">Scalpl</h1>
</p>

**Scalpl** provides a **lightweight wrapper** that helps you to operate on
**nested dictionaries** seamlessly **through the built-in** `dict` **API**, 
by using colon-separated string keys.

It's not a drop-in replacement for your dictionnaries, just syntactic sugar
to avoid `this['annoying']['kind']['of']['things']` and `prefer['a:different:approach']`.

No conversion cost, a thin computation overhead: that's **Scalpl**
in a nutshell.

### Installation

**Scalpl** is a Python3-only module that you can install via `pip`

```sh
pip3 install scalpl
``` 

### Usage
**Scalpl** strictly follows the standard `dict` 
[API](https://docs.python.org/3/library/stdtypes.html#dict).
Do not hesitate to take a look at it : you might find some cool 
features you didn't know about :)

**Scalpl** can wrap around your `dict`, `collections.defaultdict` or `collections.OrderedDict`.
By default, it uses colon as a key separator, but you are free to use
a different character that better suits your needs.

Let's see what it looks like with a toy dictionary ! 👇

```Python
from scalpl import Cut

data = {
    'pokemons': {
        'Bulbasaur': {
            'type': ['Grass', 'Poison'],
            'category': 'Seed',
            'ability': 'Overgrow'
        },
        'Charmander': {
            'type': 'Fire',
            'category': 'Lizard',
            'ability': 'Blaze',
        },
        'Squirtle': {
            'type': 'Water',
            'category': 'Tiny Turtle',
            'ability': 'Torrent',
        }
    },
    'trainers': {
        'Ash': {
            'hometown': 'Pallet Town'
        }
    }
}
# Just wrap your data, and you're ready to go deeper !
proxy = Cut(data)
```

You can use the built-in `dict` API to access its values.

```Python
proxy['pokemons:Bulbasaur:ability']
# 'Overgrow'
proxy.get('pokemons:MissingNo', 'Not Found')
# 'Not Found'
'trainers:Ash:hometown' in proxy
# True
```

You can also easily create or update any key/value pair.

```Python
proxy['pokemons:Charmander:weaknesses'] = ['Ground', 'Rock', 'Water']
proxy['pokemons:Charmander:weaknesses']
# ['Ground', 'Rock', 'Water']
proxy.setdefault('pokemons:Squirtle:ability', 'Torrent')
# 'Torrent'
proxy.update({
    'trainers:Ash:region': 'Kanto',
})
```

And it is still possible to iterate over your data.
```Python
proxy.items()
# [('pokemons', {...}), ('trainers', {...})]
proxy.keys()
# ['pokemons', 'trainers']
proxy.values()
# [{...}, {...}]
```

By the way, if you have to operate on a list of dictionaries,
the `Cut.all` method is what you are looking for.

```Python
pokemons = proxy['pokemons'].values()
# Let's teach these pokemons some sick moves !
for pokemon in Cut.all(pokemons):
    pokemon['moves:Scratch:power'] = 40
```

Also, you can remove a specific or an arbitrary key/value pair.

```Python
proxy.pop('pokemons:Bulbasaur:category')
# 'Seed'
proxy.popitem()
# ('trainers', {...})
del proxy['pokemons:Charmander:type']
```

Because **Scalpl** is only a wrapper around your data, it means you can get 
it back at will without any conversion cost. If you use an external API
that operates on dictionary, it will just work.

```Python
import json
json.dumps(proxy.data)
# "{'pokemons': {...}}"
```


Finally, you can retrieve a shallow copy of the inner dictionary
or remove all keys.

```Python
shallow_copy = proxy.copy()

proxy.clear()
```

### License

**Scalpl** is released into the **Public Domain**. 🎉

Ps: If we meet some day, and you think this small stuff worths it,
you can give me a beer, a coffee or a high-five in return:
I would be really happy to share a moment with you ! 🍻
