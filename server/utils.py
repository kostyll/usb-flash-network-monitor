# -*- coding:utf-8 -*-
# from __future__ import unicode_literals

def clean_up_double_spaces(line):
    while line.find('  ') >-1:
        line = line.replace('  ',' ')
    return line

# in future will be gettext function
def _(x):
    return x
