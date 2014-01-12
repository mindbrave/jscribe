# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""* HTMLDefaultGenerator module.
@module generators.html.htmldefaultgenerator
"""

import copy
import os
import codecs
import logging

from markdown import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from jscribe.utils.file import get_source_file_coding
from jscribe.conf import settings
from jscribe.core.jinjatemplaterenderer import JinjaTemplateRenderer
from jscribe.core.docstringparser import get_tag_type_property


class HTMLDefaultGenerator(object):
    def __init__(self, template_settings, doc_data, tag_settings, discovered_filepaths):
        self.doc_data = doc_data
        self.tag_settings = tag_settings
        self.template_settings = template_settings
        self.discovered_filepaths = discovered_filepaths
        self.renderer = self.create_renderer()

    def make_link(self, namepath):
        markdown_link = u'[{0}]({1} {0})'.format(namepath, namepath.replace('.', '_'))
        return markdown(markdown_link, output_format='html5')

    def get_template_for_element(self, tag_type_name):
        return self.template_settings['ELEMENT_TEMPLATES'].get(
            tag_type_name, self.template_settings['ELEMENT_TEMPLATES'].get('default')
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
            # check if element is defined in documentation
            if not self._is_element_defined(element):
                continue
            # check if element is separate, only then create file
            if element.get('is_separate'):
                self.generate_element_file(element)

    def _is_element_defined(self, element):
        if element.get('type') is None:
            return False
        return True

    def create_renderer(self):
        template_package = 'jscribe.templates.{}.{}'.format(settings.GENERATOR, settings.TEMPLATE)
        renderer = JinjaTemplateRenderer(
            template_package,
            {
                'tag_settings': self.tag_settings,
                'render_element': self.render_element,
                'FOOTER_TEXT': self.template_settings['FOOTER_TEXT'],
                'LOGO_PATH': self.template_settings['LOGO_PATH'],
            }
        )
        return renderer

    def build_template_data(self, doc_data):
        doc_data = copy.deepcopy(doc_data)
        lists = {}
        namepath = ''
        for prop, element in doc_data.get('properties').iteritems():
            # set namepath for element
            if element.get('name') is None:
                # if element is not defined but is used in namepath somewhere
                element['name'] = prop
            namepath = element.get('name')
            element['namepath'] = namepath
            element, lists = self._prepare_element_data(element, lists)
            self._get_element_template_data(element, namepath, lists)
        doc_data = {'root_element': doc_data, 'lists': lists}
        return doc_data

    def _get_element_template_data(self, data, namepath, lists):
        for prop, element in data.get('properties').iteritems():
            # set namepath for element
            if element.get('name') is None:
                # if element is not defined but is used in namepath somewhere
                element['name'] = prop
            _namepath = '.'.join([namepath, element.get('name')])
            element['namepath'] = _namepath
            element, lists = self._prepare_element_data(element, lists)
            self._get_element_template_data(element, _namepath, lists)

    def _prepare_element_data(self, element, lists):
        # get element tag type settings
        tag_type_name = element.get('type')
        # if element type is None then this element is not defined anywhere
        if tag_type_name is not None:
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
            # convert element description from markdown to html
            element['description_html'] = markdown(
                element['description'],
                output_format='html5',
            )
            # convert parameter descriptions if are set
            if element['attributes'].get('params') is not None:
                for param in element['attributes']['params']:
                    param['description_html'] = markdown(
                        param['description'],
                        output_format='html5',
                    )
            # convert return descriptions if are set
            if element['attributes'].get('return') is not None:
                element['attributes']['return']['description_html'] = markdown(
                    element['attributes']['return']['description'],
                    output_format='html5',
                )
            # convert example descriptions if are set, and convert code to html with pygments
            if element['attributes'].get('examples') is not None:
                for example in element['attributes']['examples']:
                    example['description_html'] = markdown(
                        example['description'],
                        output_format='html5',
                    )
                    langid = settings.LANGUAGE
                    if example.get('langid') is not None:
                        langid = example.get('langid')
                    example['langid'] = langid
                    lexer = get_lexer_by_name(langid, stripall=True)
                    formatter = HtmlFormatter(
                        linenos=self.template_settings['SHOW_LINE_NUMBER'],
                        cssclass="source"
                    )
                    result = highlight(example['code'], lexer, formatter)
                    example['code_html'] = result
            # check if element is separate
            is_separate = get_tag_type_property(self.tag_settings, tag_type, 'separate')
            element['is_separate'] = is_separate
        return element, lists

    def generate_element_file(self, element_data):
        for prop, element in element_data.get('properties').iteritems():
            # check if element is defined in documentation
            if not self._is_element_defined(element):
                continue
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
                linenos=self.template_settings['SHOW_LINE_NUMBER'],
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
