# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""* Library generates documentation from source files.
@module jscribe
"""

import argparse
import logging

from utils.version import Version

from core.docgenerator import DocumentationGenerator
from core import settings

logging.basicConfig(format='%(message)s', level=logging.INFO)

version = Version(0, 0, 1)

parser = argparse.ArgumentParser(
    description='Generates documentation.'
)
parser.add_argument(
    '--settings',
    dest='settings_path',
    type=str,
    default=None,
    help='Settings file path.',
)
args = parser.parse_args()

logging.info('JScribe documentation generator v{}.'.format(repr(version)))

generator = DocumentationGenerator(settings_path=args.settings_path)
generator.generate_documentation()

logging.info('Documentation created in "{}".'.format(settings.DOCUMENTATION_OUTPUT_PATH))