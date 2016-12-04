# -*- coding: utf-8 -*-
import sys
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin
from .models import Error


class ErrorLogMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        try:
            exc_type, exc, tb = sys.exc_info()
            if exc_type is not Http404:
                Error.from_except_with_request(request.path, tb, exception, request).save()
        finally:
            del exc_type, exc, tb
