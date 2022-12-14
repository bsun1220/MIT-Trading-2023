#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 23:08:15 2022

@author: stanley
"""

from os.path import dirname, basename, isfile, join
import glob

# need this code to import competitor bots properly

modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]