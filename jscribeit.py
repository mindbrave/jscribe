# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""* Library generates documentation from source files.
@module jscribeit
"""

import argparse
import logging

from jscribe.utils.version import Version

from jscribe.core.docgenerator import DocumentationGenerator
from jscribe.conf import settings

logging.basicConfig(format='%(message)s', level=logging.INFO)

version = Version(0, 0, 2, 'dev')

parser = argparse.ArgumentParser(
    description='Generates documentation.'
)
parser.add_argument(
    'settings',
    type=str,
    help='Settings file path.',
)
args = parser.parse_args()

logging.info('JScribe documentation generator v{}.'.format(repr(version)))

generator = DocumentationGenerator(args.settings)
generator.generate_documentation()

logging.info('Documentation created in "{}".'.format(settings.DOCUMENTATION_OUTPUT_PATH))
