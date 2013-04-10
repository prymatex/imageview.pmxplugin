#!/usr/bin/env python
# -*- coding: utf-8 -*-

from imageview.viewers import PMXImageViewer

def registerPlugin(manager):
    manager.registerComponent(PMXImageViewer)
    
def unregisterPlugin(manager):
    pass
