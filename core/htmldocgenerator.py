# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""* HTMLDocumentationGenerator module file.
@module core.htmldocgenerator
@author Rafał Łużyński
"""

import json
import os
import importlib

from core import settings


class HTMLDocumentationGenerator(object):
    """* This class creates documentation in HTML format.
    @class .HTMLDocumentationGenerator
    """

    def __init__(self, doc_data, tag_settings, filepaths):
        self.doc_data = doc_data
        self.filepaths = filepaths
        self.tag_settings = tag_settings
        self._load_template_settings()

    def _load_template_settings(self):
        with open(os.path.join(
                    'templates', settings.GENERATOR, settings.TEMPLATE, 'defaultsettings.json'
                ), 'r') as f:
            template_settings = json.load(f)
            f.close()
        template_settings['ELEMENT_TEMPLATES'].update(
            settings.TEMPLATE_SETTINGS.get('ELEMENT_TEMPLATES', {})
        )
        settings.TEMPLATE_SETTINGS['ELEMENT_TEMPLATES'] = template_settings['ELEMENT_TEMPLATES']
        template_settings.update(settings.TEMPLATE_SETTINGS)
        settings.TEMPLATE_SETTINGS = template_settings

    def generate_documentation(self):
        # import template generator
        template_generator_class = getattr(
            importlib.import_module(
                'templates.{}.{}.generate'.format(settings.GENERATOR, settings.TEMPLATE)
            ),
            'HTMLGeneratorTemplate'
        )
        template_generator = template_generator_class(
            self.doc_data, self.tag_settings, self.filepaths
        )
        template_generator.generate_documentation()
