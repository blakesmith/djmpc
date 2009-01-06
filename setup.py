#!/usr/bin/env python

from distutils.core import setup
import os

def get_head_commit():
    head = open(".git/HEAD").read()[5:-1]
    head_commit = open(".git/" + head).read()[:10]
    return head_commit

def get_recent_tag():
    return os.popen("git tag | tail -n 1").read().rsplit("-")[1][:-1]

setup(name='djmpc',
        version=get_recent_tag(),
        description='An ncurses MPD client with cuesheet support',
        author='Blake Smith',
        author_email='blakesmith0@gmail.com',
        url='http://djblithe.com/page/djmpc',
        license='GPLv2',
        packages=['djmpclib'],
        scripts=['djmpclib/djmpc'],
        data_files=[('share/djmpc', ['djmpclib/djmpc_config.py'])],
        )
