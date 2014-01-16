# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""* HTMLDocumentationGenerator module file.
@module jscribe.core.htmldocgenerator
@author Rafał Łużyński
"""

import importlib

from jscribe.conf import settings


class HTMLDocumentationGenerator(object):
    """* This class creates documentation in HTML format.
    @class .HTMLDocumentationGenerator
    """

    def __init__(self, doc_data, tag_settings, filepaths):
        self.doc_data = doc_data
        self.filepaths = filepaths
        self.tag_settings = tag_settings
        self._template_settings = {}
        self._template_generator = None
        self._load_template_settings()

    def _load_template_settings(self):
        # load template settings from python module in template
        template_settings = importlib.import_module(
            'jscribe.templates.{}.{}.settings'.format(settings.GENERATOR, settings.TEMPLATE)
        )
        # first update default element templates with user element templates
        template_settings.TEMPLATE_SETTINGS['ELEMENT_TEMPLATES'].update(
            settings.TEMPLATE_SETTINGS.get('ELEMENT_TEMPLATES', {})
        )
        settings.TEMPLATE_SETTINGS['ELEMENT_TEMPLATES'] = template_settings.TEMPLATE_SETTINGS[
            'ELEMENT_TEMPLATES'
        ]
        template_settings.TEMPLATE_SETTINGS.update(settings.TEMPLATE_SETTINGS)
        self._template_settings = template_settings.TEMPLATE_SETTINGS
        self._template_generator = template_settings.GENERATOR

    def generate_documentation(self):
        # import template generator
        module = importlib.import_module(
            self._template_generator[0]
        )
        # get class attr from attr path, i.e. foo.bar.HTMLGenerator where foo and bar are also
        # classes
        current_attr = module
        for attr in self._template_generator[1].split('.'):
            current_attr = getattr(
                current_attr,
                attr
            )
        template_generator_class = current_attr
        template_generator = template_generator_class(
            self._template_settings, self.doc_data, self.tag_settings, self.filepaths
        )
        template_generator.generate_documentation()
