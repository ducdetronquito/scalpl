from setuptools import setup

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='scalpl',
    py_modules=['scalpl'],
    version='0.2.6',
    description=(
        'A lightweight wrapper to operate on nested '
        'dictionaries seamlessly.'
    ),
    long_description=readme,
    author='Guillaume Paulet',
    author_email='guillaume.paulet@giome.fr',
    license='Public Domain',
    url='https://github.com/ducdetronquito/scalpl',
    download_url=(
        'https://github.com/ducdetronquito/scalpl/archive/'
        '0.2.6.tar.gz'
    ),
    tests_require=[
        'addict', 'mypy', 'pytest', 'pytest-cov',
        'python-box', 'requests',
    ],
    keywords=[
        'dict', 'nested', 'proxy', 'traversable',
        'dictionary', 'box', 'addict', 'munch',
        'scalpl', 'scalpel', 'wrapper',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
