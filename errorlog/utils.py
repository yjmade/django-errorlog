# -*- coding: utf-8 -*-
from django.views.debug import ExceptionReporter
from django.template import loader


class Reporter(ExceptionReporter):

    def __init__(self, exc_type, exc_value, tb):
        super(Reporter, self).__init__(request=None, exc_type=exc_type, exc_value=exc_value, tb=tb, is_email=False)

    def get_traceback_data(self):
        data = super(Reporter, self).get_traceback_data()
        del data["settings"]
        return data

    def get_traceback_html(self):
        "Return HTML version of debug 500 HTTP error page."
        return loader.render_to_string("TECHNICAL_500_TEMPLATE.html", self.get_traceback_data())


class class_property(property):  # noqa

    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()
