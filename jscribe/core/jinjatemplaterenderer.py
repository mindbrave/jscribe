# -*- coding: utf-8 -*-
#!/usr/bin/env python

from jinja2 import Environment, PackageLoader


class JinjaTemplateRenderer(object):
    def __init__(self, template_package, global_context):
        # setup jinja template engine
        self.env = Environment(
            loader=PackageLoader(template_package, 'templates'),
            extensions=['jinja2.ext.i18n']
        )
        self.env.globals = global_context

    def update_globals(self, new_globals):
        self.env.globals.update(new_globals)

    def render_to_file(self, template, context, filepath, encoding):
        self.env.get_template(template).stream(context).dump(filepath, encoding=encoding)

    def render(self, template, context):
        return self.env.get_template(template).render(context)
