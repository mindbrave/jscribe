# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""* Doc string parser module file.
@module core.docstringparser
@author Rafał Łużyński
"""

import re
from collections import OrderedDict
import codecs
import json

from utils.file import get_source_file_coding


class DocStringParser(object):
    """* This class generates doc data from source files.
    @class .DocStringParser
    """

    class TagValueException(Exception):
        pass

    class InvalidDocStringException(Exception):
        pass

    class InvalidTagException(Exception):
        pass

    class InvalidElementPathException(Exception):
        pass

    class TagSettingsException(Exception):
        pass

    def __init__(
            self, tag_settings_path, doc_string_regex, tag_regex, line_prefix='',
            ignore_invalid_tags=False, new_line_sign='<br/>'
        ):
        """* Initialization.
        @method ..__init__
        @param self
        @param tag_settings_path {str} - Path to tag settings json file.
        @param doc_string_regex {regex} - Regex that matches doc strings.
        @param tag_regex {regex} - Regex that matches tags in doc strings.
        @param line_prefix='' {str} - Prefix that will be escaped from every line in doc string.
        Whitespaces at the line begining are always ommited.
        @param ignore_invalid_tags=False {boolean} - If True then invalid tag name won't raise
        error.
        @param new_line_sign='&lt;br/&gt;' {str} - New line characters in descriptions will be replaced
        with value of this parameter.
        """

        self.PROPERTY_TAGS = {
            'return': self.get_return_from_tag_string,
            'param': self.get_param_from_tag_string,
            'author': self.get_author_from_tag_string,
            'valtype': self.get_valtype_from_tag_string,
            'default': self.get_default_from_tag_string,
            'inherits': self.get_inherits_from_tag_string,
            'access': self.get_access_from_tag_string,
            'version': self.get_version_from_tag_string,
            'license': self.get_license_from_tag_string,
            'example': self.get_example_from_tag_string,
            'private': lambda ts: ('access', 'private'),
        }

        self._doc_string_regex = None
        self._doc_string_regex_obj = None
        self.doc_string_regex = doc_string_regex
        self._tag_regex = None
        self._tag_regex_obj = None
        self.tag_regex = tag_regex
        self.line_prefix = line_prefix
        self.new_line_sign = new_line_sign
        self.ignore_invalid_tags = ignore_invalid_tags
        self._tag_settings = None
        self._tag_alias_map = {}
        self.load_tag_settings(tag_settings_path)
        self.data = OrderedDict({'properties': OrderedDict({})})
        self._temp_data = OrderedDict({})

    @property
    def doc_string_regex(self):
        return self._doc_string_regex

    @doc_string_regex.setter
    def doc_string_regex(self, doc_string_regex):
        self._doc_string_regex = doc_string_regex
        # only whitespaces before opening tag
        no_whitespace_regex = r'^\s*?'
        self._doc_string_open_regex_obj = re.compile(no_whitespace_regex + doc_string_regex[0])
        self._doc_string_close_regex_obj = re.compile(doc_string_regex[1])

    @property
    def tag_regex(self):
        return self._tag_regex

    @tag_regex.setter
    def tag_regex(self, tag_regex):
        self._tag_regex = tag_regex
        self._tag_regex_obj = re.compile(tag_regex)

    @property
    def tag_settings(self):
        return self._tag_settings

    @tag_settings.setter
    def tag_settings(self, tag_settings):
        self._tag_settings = tag_settings
        self._create_tag_alias_map(tag_settings)

    def load_tag_settings(self, path):
        with open(path, 'r') as f:
            self.tag_settings = json.load(f)
            f.close()

    def _create_tag_alias_map(self, tag_settings):
        for tag, settings in tag_settings.iteritems():
            aliases = get_tag_type_property(tag_settings, settings, 'alias')
            if aliases is None:
                continue
            for alias in aliases:
                self._tag_alias_map[alias] = tag

    def parse_file(self, path):
        # get coding of source file
        source_coding = get_source_file_coding(path)
        doc_strings = self._get_doc_strings(path, source_coding)
        previous_elements_paths = []
        for doc_string in doc_strings:
            doc_string_data = self._parse_doc_string(doc_string)
            if doc_string_data is None:
                # that doc string is not a proper doc string
                continue
            doc_string_data['filepath'] = path
            previous_elements_paths = self._add_temp_data(doc_string_data, previous_elements_paths)
        self._assemble_data()

    def _assemble_data(self):
        for path, data in self._temp_data.iteritems():
            path_parts = path.split('.')
            current_element = self.data
            for part in path_parts:
                if current_element['properties'].get(part) is None:
                    current_element['properties'][part] = {
                        'properties': OrderedDict({}),
                        'name': None,
                        'type': None,
                        'startline': None,
                        'endline': None,
                        'filepath': None,
                    }
                current_element = current_element['properties'].get(part)
            for prop in data:
                current_element[prop] = data[prop]

    def _add_temp_data(self, doc_string_data, previous_elements_paths):
        name_parts = doc_string_data['name'].split('.')
        element_true_name = name_parts.pop(-1)
        if element_true_name == '':
            raise self.InvalidElementPathException('Invalid element path: {}'.format(
                doc_string_data['name']
            ))
        current_element_path = ''
        level = -1
        if len(name_parts) > 0 and name_parts[0] == '':
            # relative to previously defined elements
            for level, part in enumerate(name_parts):
                if part == '':
                    # relative
                    try:
                        current_element_path = previous_elements_paths[level]
                    except IndexError:
                        raise self.InvalidElementPathException('No parent element, path: {}'.format(
                            doc_string_data['name']
                        ))
                else:
                    # from here is the element path
                    ## check if rest of the path is valid
                    for part in name_parts[level:]:
                        if part == '':
                            raise self.InvalidElementPathException(
                                'Invalid element path: {}'.format(doc_string_data['name'])
                            )
                        current_element_path = '.'.join([current_element_path, part])
                    break
        elif len(name_parts) > 0 and name_parts[0] != '':
            # absolute path to element
            ## check if path is valid
            for part in name_parts:
                if part == '':
                    raise self.InvalidElementPathException('Invalid element path: {}'.format(
                        doc_string_data['name']
                    ))
            current_element_path = '.'.join(name_parts)
        # add element true name to path
        if current_element_path != '':
            current_element_path = '.'.join([current_element_path, element_true_name])
        else:
            current_element_path = element_true_name
        # add doc string data to temp data
        doc_string_data['name'] = element_true_name
        self._temp_data[current_element_path] = doc_string_data

        previous_elements_paths = previous_elements_paths [:level + 1]
        previous_elements_paths.append(current_element_path)
        return previous_elements_paths

    def _parse_doc_string(self, doc_string):
        doc_string_data = {
            'startline': doc_string[0],
            'endline': doc_string[1],
            'name': None,
            'type': None,
            'attributes': {},
        }
        # get description and tag strings
        tag_strings = []
        position_end = 0
        position_start = 0
        while position_end < len(doc_string[2]):
            match_inst = self._tag_regex_obj.search(doc_string[2], position_end)
            if match_inst is None:
                # end of doc string
                position_end = len(doc_string[2])
                tag_strings.append(doc_string[2][position_start:])
            else:
                # found tag
                tag_strings.append(doc_string[2][position_start:match_inst.start()])
                position_start = match_inst.start()
                position_end = match_inst.end()
                # if tag has no value and is last in doc string
                if position_end >= len(doc_string[2]):
                    tag_strings.append(doc_string[2][position_start:position_end])

        # if tag_strings has only one element or less, then it's not a doc string (no tags in there)
        if len(tag_strings) < 2:
            return None
        # first element of tag_strings is a description of an element
        doc_string_data['description'] = tag_strings.pop(0).strip('\n').strip(' ').replace(
            '\n', self.new_line_sign
        )
        # indicates if doc string has element tag, it must have exactly one to be a valid doc string
        has_element_tag = False

        for tag_string in tag_strings:
            match_inst = self._tag_regex_obj.search(tag_string)
            tag_name = match_inst.group('tag')
            # check if tag type is valid
            ## check if tag is an element tag, check also aliases
            if self.tag_settings.get(tag_name) is not None or \
                    self._tag_alias_map.get(tag_name) is not None:
                if has_element_tag:
                    raise self.InvalidDocStringException(
                        'Two or more element tags in one doc string, docstring: {}.'.format(
                            doc_string
                        )
                    )
                has_element_tag = True
                if self.tag_settings.get(tag_name) is not None:
                    doc_string_data['type'] = tag_name
                elif self._tag_alias_map.get(tag_name) is not None:
                    doc_string_data['type'] = self._tag_alias_map.get(tag_name)
                # first word after tag name is an element name
                element_name = self._get_element_name(tag_string)
                doc_string_data['name'] = element_name
            ## check if tag is a property tag
            elif self.PROPERTY_TAGS.get(tag_name) is not None:
                # get value of property from tag string
                tag_type, value = self.PROPERTY_TAGS.get(tag_name)(
                    tag_string[match_inst.end():]
                )
                # special case if tag is param
                if tag_type == 'param':
                    if doc_string_data['attributes'].get('params') is None:
                        doc_string_data['attributes']['params'] = []
                    doc_string_data['attributes']['params'].append(value)
                else:
                    doc_string_data['attributes'][tag_type] = value
            ## tag type is invalid, raise exception if ignore invalid tags setting is not True
            elif not self.ignore_invalid_tags:
                raise self.InvalidTagException(
                    'Invalid tag "{}" in doc string.'.format(tag_name)
                )

        if not has_element_tag:
            raise self.InvalidDocStringException(
                'No element tag in doc string.'
            )

        return doc_string_data

    def _get_element_name(self, tag_string):
        tag_string = tag_string.strip('\n').strip(' ').replace('\n', ' ').split(' ')
        try:
            element_name = tag_string[1]
        except IndexError:
            raise self.TagValueException('No element name.')
        if element_name == '':
            raise self.TagValueException('No element name.')
        return element_name

    def _get_doc_strings(self, path, encoding):
        doc_strings = []
        in_tag = False
        doc_string_text = ''
        with codecs.open(path, 'r', encoding) as f:
            for line_number, line in enumerate(f.readlines(), start=1):
                position = 0
                if not in_tag:
                    match_inst = self._doc_string_open_regex_obj.search(line, position)
                    if match_inst is not None:
                        in_tag = True
                        start_line = line_number
                        position = match_inst.end()
                    else:
                        continue
                if in_tag:
                    match_inst = self._doc_string_close_regex_obj.search(line, position)
                    if match_inst is not None:
                        in_tag = False
                        end_line = line_number
                        text_line = line[position:match_inst.start()].strip(' \t')
                        text_line = text_line.strip(self.line_prefix)
                        text_line = text_line.strip(' \t')
                        doc_string_text += text_line
                        doc_strings.append((start_line, end_line, doc_string_text))
                        doc_string_text = ''
                    else:
                        text_line = line[position:].strip(' \t')
                        text_line = text_line.strip(self.line_prefix)
                        text_line = text_line.strip(' \t')
                        doc_string_text += text_line
                        continue
            f.close()
        return doc_strings

    def clear_data(self):
        self._temp_data = OrderedDict({})
        self.data = OrderedDict({})

    def data_json(self):
        return json.dumps(self.data)

    def get_author_from_tag_string(self, tag_string):
        re_inst = re.search(r'\s*?(?P<author>.*?)$', tag_string, flags=re.DOTALL)
        if re_inst is not None:
            return 'author', re_inst.group('author').strip('\n').strip(' ')
        else:
            return 'author', ''

    def get_return_from_tag_string(self, tag_string):
        re_inst = re.search(
            r'\s*?[{](?P<return_type>.*?)[}]\s-?[ ]?(?P<description>.*?)$',
            tag_string,
            flags=re.DOTALL
        )
        if re_inst is not None:
            return 'return', {
                'type': re_inst.group('return_type'),
                'description': re_inst.group('description').replace('\n', self.new_line_sign)
            }
        else:
            return 'return', None

    def get_param_from_tag_string(self, tag_string):
        re_inst = re.search(
            r'\s*?(?P<name>\w+)(?:(?:=(?P<default>[^.]+?)\s)|(?:(?P<seq>[.]{3}))|(?:))(?:[{](?P<type>.+?)[}])?\s?-?[ ]?(?P<desc>.*?)$',
            tag_string,
            flags=re.DOTALL
        )
        if re_inst is not None:
            return 'param', {
                'name': re_inst.group('name'),
                'default': re_inst.group('default'),
                'is_sequenced': re_inst.group('seq'),
                'type': re_inst.group('type'),
                'description': re_inst.group('desc'),
            }
        else:
            raise self.TagValueException('Wrong data passed to param tag: "{}"'.format(tag_string))

    def get_valtype_from_tag_string(self, tag_string):
        re_inst = re.search(r'\s*?[{](?P<valtype>.*?)[}](\s|$)', tag_string)
        if re_inst is not None:
            return 'valtype', re_inst.group('valtype')
        else:
            return 'valtype', None

    def get_default_from_tag_string(self, tag_string):
        re_inst = re.search(r'\s*?(?P<default>.*?)(\s|$)', tag_string)
        if re_inst is not None:
            return 'default', re_inst.group('default')
        else:
            return 'default', None

    def get_inherits_from_tag_string(self, tag_string):
        re_inst = re.search(r'\s*?[{](?P<inherits>.*?)[}](\s|$)', tag_string)
        if re_inst is not None:
            return 'inherits', re_inst.group('inherits')
        else:
            return 'inherits', None

    def get_access_from_tag_string(self, tag_string):
        re_inst = re.search(r'\s*?(?P<access>.*?)(\s|$)', tag_string)
        if re_inst is not None:
            return 'access', re_inst.group('access')
        else:
            return 'access', None

    def get_version_from_tag_string(self, tag_string):
        re_inst = re.search(r'\s*?(?P<version>.*?)$', tag_string, flags=re.DOTALL)
        if re_inst is not None:
            return 'version', re_inst.group('version').strip('\n').strip(' ').replace(
                '\n', self.new_line_sign
            )
        else:
            return 'version', None

    def get_license_from_tag_string(self, tag_string):
        re_inst = re.search(r'\s*?(?P<license>.*?)$', tag_string, flags=re.DOTALL)
        if re_inst is not None:
            return 'license', re_inst.group('license').strip('\n').strip(' ').replace(
                '\n', self.new_line_sign
            )
        else:
            return 'license', None

    def get_example_from_tag_string(self, tag_string):
        re_inst = re.search(r'\s*?(?P<example>.*?)$', tag_string, flags=re.DOTALL)
        if re_inst is not None:
            return 'example', re_inst.group('example').strip('\n').strip(' ').replace(
                '\n', self.new_line_sign
            )
        else:
            return 'example', None


def get_tag_type_property(tag_settings, tag_type, property_name):
    prop = tag_type.get(property_name)
    while prop is None:
        parent_type = get_tag_parent_type(tag_settings, tag_type)
        if parent_type is None:
            raise DocStringParser.TagSettingsException(
                'No {} property on tag.'.format(property_name)
            )
        prop = parent_type.get(property_name)
    return prop


def get_tag_parent_type(tag_settings, tag_type):
    parent_type_name = tag_type.get('parent_type')
    if parent_type_name is None:
        return None
    else:
        parent_type = tag_settings.get(parent_type_name)
        if parent_type is None:
            raise DocStringParser.TagSettingsException('Parent type "{}" doesn\'t exist'.format(
                parent_type_name
            ))
        return parent_type
