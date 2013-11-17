#!/usr/bin/env python

import sys; sys.path.insert(0, 'lib') # this line is necessary for the rest
import os                             # of the imports to work!

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

class sql_page:
    def prepareQueryForRender(self,result):
        inRows = result.list()
        inCols = []
        if inRows:
            inCols = inRows[0].keys()
        return {'rows':inRows,'cols':inCols}
# helper method to render a template in the templates/ directory
#
# `template_name': name of template file to render
#
# `**context': a dictionary of variable names mapped to values
# that is passed to Jinja2's templating engine
#
# See curr_time's `GET' method for sample usage
    def render_template(self,template_name, **context):
        extensions = context.pop('extensions', [])
        globals = context.pop('globals', {})

        jinja_env = Environment(autoescape=True,
                loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
                extensions=extensions,
                )
        jinja_env.globals.update(globals)

        web.header('Content-Type','text/html; charset=utf-8', unique=True)

        return jinja_env.get_template(template_name).render(context)