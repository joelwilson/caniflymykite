try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Can I Fly My Kite web application',
    'author': 'Joel Wilson',
    'url': 'https://github.com/elbinray',
    'download_url': 'https://github.com/elbinray',
    'author_email': 'elbinray@gmail.com',
    'version': '0.1',
    'install_requires': ['nose', 'suds'],
    'packages': ['caniflymykite'],
    'scripts': [],
    'name': 'caniflymykite'
}

setup(**config)