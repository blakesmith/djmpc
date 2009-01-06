#!/usr/bin/env python

from distutils.core import setup

def get_head_commit():
    head = open(".git/HEAD").read()[5:-1]
    head_commit = open(".git/" + head).read()[:10]
    return head_commit

setup(name='djmpc',
        version=get_head_commit(),
        description='An ncurses MPD client with cuesheet support',
        author='Blake Smith',
        author_email='blakesmith0@gmail.com',
        url='http://djblithe.com/page/djmpc',
        license='GPLv2',
        packages=['djmpclib'],
        scripts=['djmpclib/djmpc'],
        data_files=[('share/djmpc', ['djmpclib/djmpc_config.py'])],
        )
