# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""* #JScribe package#

Thanks to this lib you generate documentation from "doc strings" in your code.

@author Rafał Łużyński
@package jscribe
"""

# INDEX DOC

"""* ##generates documentation for you from your "doc strings" placed in code.##

@a index "JScribe"
"""

"""* #### when there is a lot of other doc generators? ####

From the beggining.

I wanted to create javascript library and document it well. Unfortunately
doc generators, that are out there for javascript, are not that great as it would seem.

In example, I don't use *constructors* in javascript and I don't try to emulate *class*.
What I use are *factories* (I won't be discussing why since it's not an issue here).

Most (dunno if any) js doc generators doesn't support things like *factory* or *prototype*, but
I wanted it to be named *factory* and not *class* in documentation.

Alright, but creating new generator just for a few new *doc elements* is not worth it, I thought.
So I decided that it should present some new values in doc generators area.

In the end it became something similiar to
[SphinxDocumentation](http://sphinx-doc.org/ "SphinxDocumentation") for Python.

@p .WhyIMadeIt "Why I made it"
"""

"""* ##  Features: ##

- you can create your own *doc elements* (tags) with ease
- it can be used in every langauge
    (in fact, every that pygments library supports, which is most of known languages, full list
    here: [http://pygments.org/languages/](http://pygments.org/languages/)).
- supports [markdown](http://daringfireball.net/projects/markdown/syntax) markup in descriptions
- what is documented must be set explicitly by user, JScribe does not use lexers so it does not
    document things without your will. For some it might be disadvantage, for me it's a plus.
    What does it mean is that you can create documentation even without a bit of code,
    just by defining elements that are not really there (this document is made that way).
- you can reference any defined *doc element* anywhere in docs
- attaches source files to documentation with colored syntax
- you can place code snippets for every supported langauge in descriptions
- ability to create your own templates, or even whole generators (for now there is only HTML
    generator)
- of course support for standard tags, like: param, author, access, return etc. and few new

@p .WhatItBecame "What it became"
"""