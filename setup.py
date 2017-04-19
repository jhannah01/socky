import os.path
import codecs
import pkg_resources
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

try:
    with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except:
    long_description = None

from socky import __version__ as socky_version

setup(
    name='socky',
    version=socky_version,
    description='Wraps the Python socket module with extended functionality to provide support \
    for anonymized connectivity using SOCKS/Tor or HTTP proxies'
    long_description=long_description,
    url='https://github.com/jhannah01/socky',
    license='GNU',
    classifiers=[
        'Topic :: Software Development :: Libraries',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
    ],
    keywords='tor socket socks proxy',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
)
