# -*- coding: utf-8 -*-
#!/usr/bin/env python


class Version(object):

    def __init__(self, *args):
        self.is_version_valid(args)
        self.version = tuple(args)
        self._create_repr()

    def __repr__(self):
        return self.repr

    def is_version_valid(self, version):
        if not version:
            raise ValueError('Version must have at least one number part')
        for i in version:
            try:
                int(i)
            except:
                raise ValueError('Version parts must be an integer')

    def _create_repr(self):
        self.repr = '.'.join((str(i) for i in self.version))
