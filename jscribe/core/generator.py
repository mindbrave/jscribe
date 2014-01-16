# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""* Generator module.
@module jscribe.core.generator
"""


class Generator(object):
    """* Abstract Generator class.
    @class jscribe.core.generator.Generator
    """
    class GeneratorException(Exception):
        pass
    class InvalidGeneratorException(Exception):
        pass