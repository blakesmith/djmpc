#!/usr/bin/env python

from distutils.core import setup

setup(name='djmpc',
        version='beta-0.4',
        description='An ncurses MPD client with cuesheet support',
        author='Blake Smith',
        author_email='blakesmith0@gmail.com',
        url='http://djblithe.com/page/djmpc',
        license='GPLv2',
        packages=['djmpclib'],
        scripts=['djmpclib/djmpc'],
        data_files=[('share/djmpc', ['djmpclib/djmpc_config.py'])],
        )
