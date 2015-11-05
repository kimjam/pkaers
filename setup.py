"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))


setup(
    name='pkaers',

    version='0.0.2',

    description='Python Khan Academy ELO Rating System',
    long_description='Utilizes ELO Rating system to predict',
                     'a student\'s RIT score and to update',
                     'a Khan exercise\'s item difficulty on',
                     'the RIT scale.'

    url='https://github.com/kimjam/pkaers',

    author='James Kim',
    author_email='jamesykim10@gmail.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',

        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Topic :: Education'

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2.7'
    ],

    keywords='education khan',

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    install_requires=['numpy', 'pandas', 'PyYAML'],

    # Entry points for command line integration
    entry_points="",

    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
)