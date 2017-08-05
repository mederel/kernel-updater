"""
A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='kernelupdater',
    version='1.0.1',
    description='Project to update kernel in Gentoo after new sources were merged',
    long_description=long_description,
    url='https://github.com/mederel/kernel-updater',
    author='Emile de Weerd',
    author_email='emile@deweerd.fr',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: System :: Operating System Kernels :: Linux',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    keywords='gentoo kernel linux',
    packages=find_packages(exclude=['contrib', 'tests']),
    entry_points={
        'console_scripts': [
            'kernel-updater=kernelupdater.cli:main',
        ],
    }
)
