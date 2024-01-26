# Copyright (c) 2023 bedbad
from setuptools import setup, find_packages

setup(
    name='pyimports',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author='bedbad',
    author_email='antonyuk@bu.edu',
    description='Unconfuse your Py imports',
    long_description='''Resolve your Py imports - see all'''
                     '''Where are do those that you use sit, where'''
                     '''those that left, should be, see all dependencies,'''
                     '''and the way the were imported and defined - makes you adhere to'''
                     '''well defined Python project structure, and potentially automate build''',
    long_description_content_type='text/markdown',
    url='https://github.com/bedbad/justpyplot',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
)
