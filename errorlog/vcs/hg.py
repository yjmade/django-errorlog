# -*- coding: utf-8 -*-
from django.conf import settings
HG_CHANGESET = None
HG_REV = None


def _get_hg_changectx():
    from mercurial.hg import repository
    from mercurial.ui import ui
    repo = repository(ui(), settings.BASE_DIR)
    return repo[None].parents()[0]


def get_hg_changeset():
    global HG_CHANGESET
    if HG_CHANGESET is None:
        HG_CHANGESET = str(_get_hg_changectx())
    return HG_CHANGESET


def get_hg_rev():
    global HG_REV
    if HG_REV is None:
        HG_REV = _get_hg_changectx().rev()
    return HG_REV


get_hg_changeset()
get_hg_rev()
