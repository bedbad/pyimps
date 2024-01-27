# Copyright (c) 2023 bedbad
from setuptools import setup, find_packages

setup(
    name='pyimps',
    version='0.0.5',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'pyimps = pyimps.pyimps:main',
        ],
    },
    author='bedbad',
    author_email='antonyuk@bu.edu',
    description='Unconfuse your Py imports',
    long_description='''Resolve your Py imports - see entire listing \r\n'''
                     '''Where all tha you have sit; \r\n'''
                     '''Where all tha you don't, should be; \r\n'''
                     '''See all transitives the way the were imported and defined. \r\n'''
                     '''All of it - right in your terminal \r\n''',
    long_description_content_type='text/markdown',
    url='https://github.com/bedbad/pyimps',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
)
