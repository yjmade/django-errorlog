#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import six
import traceback
import json
from contextlib import contextmanager

from django.db import models
from django.utils import timezone
from django.views.debug import ExceptionReporter
from django.conf import settings
from django.utils.timezone import now
from .utils import Reporter, class_property


def get_vcs_rev():
    vcs = getattr(settings, "VCS_SYSTEM", None)
    if vcs == "hg":
        from .vcs.hg import get_hg_rev
        return get_hg_rev()
    elif vcs == "git":
        from .vcs.git import get_git_rev
        return get_git_rev()


class BaseError(models.Model):

    class Meta(object):
        ordering = ["-occur_time"]
        abstract = True

    fixed = models.BooleanField(default=False)
    occur_time = models.DateTimeField(default=now)
    fix_time = models.DateTimeField(null=True)
    error_type = models.TextField()
    error_args_json = models.TextField(null=True)
    stack_list_json = models.TextField(null=True)
    stack_hash = models.TextField(db_index=True)
    error_html = models.TextField(null=True)
    vcs_rev = models.TextField(null=True, default=get_vcs_rev)

    @property
    def stack_list(self):
        return json.loads(self.stack_list_json) if self.stack_list_json else None

    @stack_list.setter
    def stack_list(self, new_value):
        self.stack_list_json = json.dumps(new_value)

    @property
    def error_args(self):
        return json.loads(self.error_args_json) if self.error_args_json else None

    @error_args.setter
    def error_args(self, new_value):
        self.error_args_json = json.dumps(new_value)

    def __unicode__(self):
        if hasattr(self, "_same_count"):
            return "%5d - %s" % (self._same_count, self._name)
        return self._name

    @property
    def error_message(self):
        return "%s: %s" % (self.error_type, ", ".join("%s" % arg for arg in self.error_args))

    @property
    def format_stack(self):
        return "".join(traceback.format_list(self.stack_list))

    @classmethod
    def _normalize_file_python(cls, src_path):
        rel_path = os.path.relpath(src_path, start=settings.BASE_DIR)
        return rel_path if not rel_path.startswith("../") else src_path

    @classmethod
    def _get_stack_hash(cls, stack_list):
        return hash(tuple((path, func_name, src_code) for path, lineno, func_name, src_code in stack_list))

    @classmethod
    def _get_except_cls_name(cls, exception_cls):
        return ".".join([exception_cls.__name__] if exception_cls.__module__ == "exceptions" else [exception_cls.__module__, exception_cls.__name__])

    @property
    def same_errors(self):
        cls = type(self)
        return cls.objects.filter(
            stack_hash=self.stack_hash,
            fixed=False,
        )

    def ignore(self):
        self.same_errors.update(fixed=True, fix_time=timezone.now())

    @classmethod
    def get_distinct_filter(cls, field_name, value):
        if not value:
            return models.Q()
        return models.Q(id__in=cls.objects.filter(fixed=False).order_by().values(field_name).annotate(max_id=models.Max("id")).values_list("max_id", flat=True))

    @classmethod
    def get_same_attr(cls, field_name, id):
        value = cls.objects.filter(id=id).values_list(field_name, flat=True)[0]
        return models.Q(**{field_name: value})

    @property
    def _name(self):
        return "%s - %s" % (getattr(self, self.name_property), self.error_message)

    @classmethod
    def from_except(cls, name, tb, exception, error_html_getter=None, error_html_getter_params={}, **data):
        try:
            from celery.exceptions import Retry
        except ImportError:
            pass
        else:
            if isinstance(exception, Retry):
                six.reraise(Retry, exception, tb)
        tb_stacks = traceback.extract_tb(tb)
        stack_list = [
            (cls._normalize_file_python(src_path), lineno, func_name, src_code)
            for src_path, lineno, func_name, src_code in tb_stacks
        ]
        error_html_getter = error_html_getter or (lambda exc_type, exc_value, tb, **kwargs: Reporter(exc_type, exc_value, tb).get_traceback_html())
        data[cls.name_property] = name
        res = cls(
            stack_hash=cls._get_stack_hash(stack_list),
            error_type=cls._get_except_cls_name(type(exception)),
            error_html=error_html_getter(exc_type=type(exception), exc_value=exception, tb=tb, **error_html_getter_params),
            **data
        )
        res.stack_list = stack_list
        res.error_args = [repr(arg) for arg in exception.args]
        return res

    @classmethod
    def from_except_with_request(cls, name, tb, exception, request, **data):
        return super(Error, cls).from_except(
            name,
            tb,
            exception,
            error_html_getter=lambda exc_type, exc_value, tb, request: ExceptionReporter(request, exc_type, exc_value, tb).get_traceback_html(),
            error_html_getter_params={"request": request},
            **data
        )

    @classmethod
    @contextmanager
    def log_exception(cls, name, reraise=True, **data):
        exc_type, exc, tb = None, None, None
        try:
            yield
        except Exception:
            exc_type, exc, tb = sys.exc_info()
            # traceback.print_exc()
            cls.from_except(name, tb, exc, **data).save()
            reraise and six.reraise(exc_type, exc, tb=tb)
        finally:
            del exc_type, exc, tb

    @property
    def prints(self):
        print "Traceback (most recent call last):"
        print self.format_stack,
        print self.error_message

    @class_property
    @classmethod
    def unfixed_errors(cls):
        unique_errors_id_ct = dict(cls.objects.filter(fixed=False).values("error_type", "stack_hash").annotate(max_id=models.Max("id"), ct=models.Count("id")).values_list("max_id", "ct"))
        query = cls.objects.filter(id__in=unique_errors_id_ct.keys())
        for obj in query:
            obj._same_count = unique_errors_id_ct[obj.id]
        return {i: item for i, item in enumerate(query)}


class Error(BaseError):
    name = models.TextField()
    name_property = "name"
