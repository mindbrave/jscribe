TAG_SETTINGS = {
    "default": {
       "parent_type": None,
       "alias": [],
       "separate": False,
       "list": False,
       "list_order": 0,
       "name": ["default name"],
       "title": ["default plural name"],
       "source_visible": True,
       "callable": False,
       "attributes": {
           "access": "public",
           "example": None,
           "params": [],
           "return": None,
           "inherits": None,
           "default": None,
           "valtype": None,
           "author": None,
           "license": None,
           "version": None
       }
    },
    "article": {
        "parent_type": "default",
        "alias": ["a"],
        "name": "",
        "title": "manual",
        "separate": True,
        "source_visible": False,
        "list": True,
        "list_order": -1,
        "attributes": {
        }
    },
    "paragraph": {
        "parent_type": "default",
        "alias": ["p"],
        "name": "",
        "title": "paragraphs",
        "separate": False,
        "source_visible": False,
        "list": False,
        "attributes": {
        }
    },
    "package": {
        "parent_type": "default",
        "alias": ["pack"],
        "name": "package",
        "title": "packages",
        "separate": True,
        "list": True,
        "attributes": {
        }
    },
    "module": {
        "parent_type": "default",
        "alias": [],
        "name": "module",
        "separate": True,
        "list": True,
        "title": "modules",
        "attributes": {
        }
    },
    "class": {
        "parent_type": "default",
        "name": "class",
        "title": "classes",
        "list": True,
        "attributes": {
            "return": {
                "type": "instance",
                "description": None
            }
        }
    },
    "method": {
        "parent_type": "default",
        "name": "method",
        "title": "methods",
        "callable": True,
        "separate": False,
        "attributes": {
            "return": {
                "type": None,
                "description": None
            }
        }
    },
    "function": {
        "parent_type": "default",
        "name": "function",
        "title": "functions",
        "callable": True,
        "attributes": {
            "return": {
                "type": None,
                "description": None
            }
        }
    },
    "attribute": {
        "parent_type": "default",
        "alias": ["attr"],
        "name": "attribute",
        "ptitle": "attributes",
        "callable": False,
        "attributes": {
        }
    },
    "number": {
        "parent_type": "attribute",
        "alias": ["num"],
        "attributes": {
            "valtype": "number"
        }
    },
    "string": {
        "parent_type": "attribute",
        "alias": ["str"],
        "attributes": {
            "valtype": "string"
        }
    }
}