"""* Default settings for jscribe.
@module jscribe.conf.defaults
"""

# MANUAL - SETTINGS FILE
"""* # Settings file #
@a settings
"""

INPUT_PATHS = ["./"]
IGNORE_PATHS_REGEX = []
FILE_REGEX = ".*?[.]js$"
FILE_IGNORE_REGEX = None
DOCUMENTATION_OUTPUT_PATH = "./"
DOC_STRING_REGEX = ["[/][*][*]", "[*][/]"]
TAG_REGEX = "[@](?P<tag>.*?)\\s"
IGNORE_INVALID_TAGS = False
TEMPLATE = "default"
TEMPLATE_SETTINGS = {
        "SHOW_LINE_NUMBER": True,
        "FOOTER_TEXT": "Footer text",
        "TITLE": "My Docs Title",
        "ELEMENT_TEMPLATES": {},
}
TAG_SETTINGS_PATH = "jscribe.conf.pythontagsettings"
OUTPUT_ENCODING = "utf-8"
LANGUAGE = "javascript"
GENERATOR = "html"
ALL_SOURCE_FILES = False
