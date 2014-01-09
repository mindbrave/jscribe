INPUT_PATHS = ["./"]
IGNORE_PATHS_REGEX = []
FILE_REGEX = ".*?[.]js$"
FILE_IGNORE_REGEX = None
DOCUMENTATION_OUTPUT_PATH = "./"
DOC_STRING_REGEX = ["[/][*][*]", "[*][/]"]
DOC_STRING_LINE_PREFIX = "*"
TAG_REGEX = "[@](?P<tag>.*?)\\s"
IGNORE_INVALID_TAGS = False
NEW_LINE_REPLACE = "<br/>"
TEMPLATE = "default"
TEMPLATE_SETTINGS = {
        "SHOW_LINE_NUMBER": True,
        "FOOTER_TEXT": "JSCRIBE",
        "LOGO_PATH": "",
        "ELEMENT_TEMPLATES": {},
}
TAG_SETTINGS_PATH = "jscribe.conf.pythontagsettings"
OUTPUT_ENCODING = "utf-8"
LANGUAGE = "javascript"
GENERATOR = "html"