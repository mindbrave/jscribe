# -*- coding: utf-8 -*-
#!/usr/bin/env python

import copy
import os
import codecs
import logging

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from utils.file import get_source_file_coding

from core import settings
from core.jinjatemplaterenderer import JinjaTemplateRenderer
from core.docstringparser import get_tag_type_property


class HTMLGeneratorTemplate(object):
    def __init__(self, doc_data, tag_settings, discovered_filepaths):
        self.doc_data = doc_data
        self.tag_settings = tag_settings
        self.discovered_filepaths = discovered_filepaths
        self.renderer = self.create_renderer()

    def get_template_for_element(self, tag_type_name):
        return settings.TEMPLATE_SETTINGS['ELEMENT_TEMPLATES'].get(
            tag_type_name, settings.TEMPLATE_SETTINGS['ELEMENT_TEMPLATES'].get('default')
        )

    def get_path_to_element_file(self, element):
        return os.path.join(
            settings.DOCUMENTATION_OUTPUT_PATH,
            '.'.join([element.get('namepath').replace('.', '_'), 'html'])
        )

    def get_path_to_sourcefile(self, filepath):
        return os.path.join(
            settings.DOCUMENTATION_OUTPUT_PATH,
            '.'.join([filepath.replace(os.path.sep, '_')[1:], 'html'])
        )

    def get_path_to_list_file(self, list_type):
        return os.path.join(
            settings.DOCUMENTATION_OUTPUT_PATH,
            '.'.join(['list_{}'.format(list_type), 'html'])
        )

    def generate_documentation(self):
        # get documentation data for templates
        doc_data = self.build_template_data(self.doc_data)
        # add lists to the global context so its always available to mainframe
        self.renderer.update_globals({'lists': doc_data['lists']})
        # create source doc files (source code with line numbers and anchors)
        self.generate_source_files_for_documentation()
        # create list files
        self.generate_list_files(doc_data)
        # create files for every element with separate type
        for prop, element in doc_data['root_element'].get('properties').iteritems():
            # check if element is separate
            if element.get('is_separate'):
                self.generate_element_file(element)

    def create_renderer(self):
        template_package = 'templates.{}.{}'.format(settings.GENERATOR, settings.TEMPLATE)
        renderer = JinjaTemplateRenderer(
            template_package,
            {
                'tag_settings': self.tag_settings,
                'render_element': self.render_element,
                'FOOTER_TEXT': settings.TEMPLATE_SETTINGS['FOOTER_TEXT'],
                'LOGO_PATH': settings.TEMPLATE_SETTINGS['LOGO_PATH'],
            }
        )
        return renderer

    def build_template_data(self, doc_data):
        doc_data = copy.deepcopy(doc_data)
        lists = {}
        namepath = ''
        for prop, element in doc_data.get('properties').iteritems():
            # set namepath for element
            namepath = element.get('name')
            element['namepath'] = namepath
            # get element tag type settings
            tag_type_name = element.get('type')
            # add element to its element list
            if lists.get(tag_type_name) is None:
                lists[tag_type_name] = {
                    'path': self.get_path_to_list_file(tag_type_name), 'elements': []
                }
            lists[tag_type_name]['elements'].append(element)
            tag_type = self.tag_settings.get(tag_type_name)
            # remove beginnig dot from filepath
            element['filepath'] = element['filepath'][1:]
            # set element path to sourcefile
            element['sourcepath'] = self.get_path_to_sourcefile(element.get('filepath'))
            # add element doc file path
            output_path = self.get_path_to_element_file(element)
            element['doc_element_path'] = output_path
            # check if element is separate
            is_separate = get_tag_type_property(self.tag_settings, tag_type, 'separate')
            element['is_separate'] = is_separate
            if is_separate:
                self._get_element_template_data(element, namepath, lists)
        doc_data = {'root_element': doc_data, 'lists': lists}
        return doc_data

    def _get_element_template_data(self, data, namepath, lists):
        for prop, element in data.get('properties').iteritems():
            # set namepath for element
            _namepath = '.'.join([namepath, element.get('name')])
            element['namepath'] = _namepath
            # get element tag type settings
            tag_type_name = element.get('type')
            # add element to its element list
            if lists.get(tag_type_name) is None:
                lists[tag_type_name] = {
                    'path': self.get_path_to_list_file(tag_type_name), 'elements': []
                }
            lists[tag_type_name]['elements'].append(element)
            tag_type = self.tag_settings.get(tag_type_name)
            # remove beginnig dot from filepath
            element['filepath'] = element['filepath'][1:]
            # set element path to sourcefile
            element['sourcepath'] = self.get_path_to_sourcefile(element.get('filepath'))
            # add element doc file path
            output_path = self.get_path_to_element_file(element)
            element['doc_element_path'] = output_path
            # check if element is separate
            is_separate = get_tag_type_property(self.tag_settings, tag_type, 'separate')
            element['is_separate'] = is_separate
            if is_separate:
                self._get_element_template_data(element, _namepath, lists)

    def generate_element_file(self, element_data):
        for prop, element in element_data.get('properties').iteritems():
            if element.get('is_separate'):
                self.generate_element_file(element)
        result = self.render_element(element_data)
        self.renderer.render_to_file(
            'element.html',
            {'element_rendered': result, },
            element_data['doc_element_path'],
            settings.OUTPUT_ENCODING
        )
        logging.info('Created: {}'.format(element_data['doc_element_path']))

    def generate_list_files(self, doc_data):
        for list_type, _list in doc_data['lists'].iteritems():
            self.renderer.render_to_file(
                'list.html',
                {'list': _list, 'list_type': list_type, },
                self.get_path_to_list_file(list_type),
                settings.OUTPUT_ENCODING
            )

    def generate_source_files_for_documentation(self):
        for filepath in self.discovered_filepaths:
            encoding = get_source_file_coding(filepath)
            with codecs.open(filepath, 'r', encoding) as f:
                code = f.read()
                f.close()
            output_path = self.get_path_to_sourcefile(filepath[1:])
            lexer = get_lexer_by_name(settings.LANGUAGE, stripall=True)
            formatter = HtmlFormatter(
                linenos=settings.TEMPLATE_SETTINGS['SHOW_LINE_NUMBER'],
                cssclass="source"
            )
            result = highlight(code, lexer, formatter)
            self.renderer.render_to_file(
                'sourcefile.html',
                {'source': result, },
                output_path,
                settings.OUTPUT_ENCODING
            )
            logging.info('Created: {}'.format(output_path))

    def render_element(self, element):
        template = self.get_template_for_element(element.get('type'))
        return self.renderer.render(template, {'element': element, })
