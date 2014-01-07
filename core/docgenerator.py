# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""* DocumentationGenerator module file.
@module core.docgenerator
@author Rafał Łużyński
"""

import json

from utils.file import discover_files

from core import settings
from core.docstringparser import DocStringParser
from core.htmldocgenerator import HTMLDocumentationGenerator


class DocumentationGenerator(object):
    """* This class is a controller class that creates documentation.
    @class .DocumentationGenerator
    """
    class InvalidGeneratorException(Exception):
        pass
    GENERATORS = {
        'html': HTMLDocumentationGenerator,
    }
    def __init__(self, settings_path=None):
        """* Initialization takes optional parameter "settings_path". Usually you should pass your
        own settings path there.
        @method ..__init__
        @param self
        @param settings_path=None {str} Path to settings json file.
        """
        self.doc_data = {}
        self.tag_settings = {}
        """* List that containts paths of source files discovered using data from settings.
        Input paths, ignore paths and regexes.
        @attr ..discovered_filepaths
        @valtype {list}
        """
        self.discovered_filepaths = []
        if settings_path is not None:
            settings.load(settings_path)
        self._load_tag_settings()
        self._get_doc_data()

    def _load_tag_settings(self):
        """* Load tag settings from file given in settings and save it on this instance.
        @method .._load_tag_settings
        @private
        """
        with open(settings.TAG_SETTINGS_PATH, 'r') as f:
            self.tag_settings = json.load(f)
            f.close()

    def _get_doc_data(self):
        self.discovered_filepaths = discover_files(
            settings.INPUT_PATHS, settings.FILE_REGEX,
            ignore_paths_regex=settings.IGNORE_PATHS_REGEX,
            ignore_regex=settings.FILE_IGNORE_REGEX
        )
        dsp = DocStringParser(
            settings.TAG_SETTINGS_PATH, settings.DOC_STRING_REGEX, settings.TAG_REGEX,
            settings.DOC_STRING_LINE_PREFIX, settings.IGNORE_INVALID_TAGS, settings.NEW_LINE_REPLACE
        )
        for filepath in self.discovered_filepaths:
            dsp.parse_file(filepath)
        self.doc_data = dsp.data

    def generate_documentation(self):
        # get generator
        generator_class = self.GENERATORS.get(settings.GENERATOR)
        if generator_class is None:
            raise self.InvalidGeneratorException(
                'Invalid generator "{}". Maybe not supported yet.'.format(settings.GENERATOR)
            )
        generator = generator_class(self.doc_data, self.tag_settings, self.discovered_filepaths)
        generator.generate_documentation()

