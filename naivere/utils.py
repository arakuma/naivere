# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Utilities
# Purpose:
#
# Author:      Arakuma
#
# Created:     17/01/2013
#-------------------------------------------------------------------------------

#Class definitions
class BaseObject(object):
    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)

    def __getattr__(self, name):
        try:
            return object.__getattribute__(name)
        except:
            return name + ' not found!'

class Map(dict):
    def add(self, key, value):
        if not key in self or not isinstance(self[key], list):
            self[key] = []
        self[key].append(value)
