# -*- coding: utf-8 -*-
"""
Created on 2026-04-11

@author: Lukypu

Description: 
    utility functions for songparser script
    Intended to become obsolete in the futere

Todo: 
"""

import re

def chord_pattern():
    # return r"[A-H][\w#b\d/]{0,5}"
    return r'[A-H](#|b)?(m|mi|maj|min|dim|aug|sus|add)?(\d){0,2}(/[A-H](#|b)?)?.?'

def is_chord(string):
    pattern = re.compile(r"^" + chord_pattern() + r"$")
    return re.match(pattern, string) is not None
