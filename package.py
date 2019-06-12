#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kerlomz <kerlomz@gmail.com>
import os
from PyInstaller.__main__ import run
import config as server

PUBLISH = True

if __name__ == '__main__':

    opts = ['server_release.spec', '--distpath=dist/server']
    run(opts)
