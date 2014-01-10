# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""* DocumentationGenerator module file.
@module core.docgenerator
@author Rafał Łużyński
"""

import json
import importlib

from jscribe.utils.file import discover_files
from jscribe.conf import settings
from jscribe.core.docstringparser import DocStringParser
from jscribe.core.htmldocgenerator import HTMLDocumentationGenerator


class DocumentationGenerator(object):
    """* This class is a *controller* class that creates documentation.
    @class .DocumentationGenerator
    """
    class InvalidGeneratorException(Exception):
        pass
    GENERATORS = {
        'html': HTMLDocumentationGenerator,
    }
    def __init__(self, settings_path):
        """* Initialization.
        @method ..__init__
        @param self
        @param settings_path {str} Path to settings **json** file.
        @example Doc generation usage. {
            doc_generator = DocumentationGenerator(path_to_settings)
            doc_generator.generate_documentation()
        } This is how you generate docs.
        @example Javascript test example. #javascript {
            var docs = docGenerator();
            docs.run();
        } javascript decsription.
        """
        self.doc_data = {}
        self.tag_settings = {}
        """* List that containts paths of source files discovered using data from settings.
        Input paths, ignore paths and regexes.
        @attr ..discovered_filepaths
        @valtype {list}
        """
        self.discovered_filepaths = []
        settings.load(settings_path)
        self.load_tag_settings(settings.TAG_SETTINGS)
        self._get_doc_data()

    def load_tag_settings(self, tag_settings_path):
        """* Load tag settings from json file given in settings or python module and save
        it on this instance.
        @method ..load_tag_settings
        @private
        """
        if tag_settings_path.split('.')[-1] == 'json':
            with open(tag_settings_path, 'r') as f:
                self.tag_settings = json.load(f)
                f.close()
        else:
            self.tag_settings = getattr(
                importlib.import_module(
                    tag_settings_path
                ),
                'TAG_SETTINGS'
            )

    def _get_doc_data(self):
        self.discovered_filepaths = discover_files(
            settings.INPUT_PATHS, settings.FILE_REGEX,
            ignore_paths_regex=settings.IGNORE_PATHS_REGEX,
            ignore_regex=settings.FILE_IGNORE_REGEX
        )
        dsp = DocStringParser(
            self.tag_settings, settings.DOC_STRING_REGEX, settings.TAG_REGEX,
            settings.DOC_STRING_LINE_PREFIX, settings.IGNORE_INVALID_TAGS
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

