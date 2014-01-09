# -*- coding: utf-8 -*-
#!/usr/bin/env python

import sys
import json

from jscribe.conf.defaults import *


def load(path):
    with open(path, 'r') as f:
        _settings = json.load(f)
        f.close()
    for attr, value in _settings.iteritems():
        setattr(sys.modules[__name__], attr, value)