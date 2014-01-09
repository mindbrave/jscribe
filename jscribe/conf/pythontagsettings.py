TAG_SETTINGS = {
    "default": {
       "parent_type": None,
       "alias": [],
       "separate": False,
       "list": False,
       "name": ["default name"],
       "plural_name": ["default plural name"],
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
    "package": {
        "parent_type": "default",
        "alias": ["pack"],
        "name": "package",
        "plural": "packages",
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
        "plural": "modules",
        "attributes": {
        }
    },
    "class": {
        "parent_type": "default",
        "name": "class",
        "plural": "classes",
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
        "plural": "methods",
        "callable": True,
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
        "plural": "functions",
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
        "plural": "attributes",
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