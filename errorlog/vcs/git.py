# -*- coding: utf-8 -*-
import git
from django.conf import settings

GIT_REV = None


def get_git_rev():
    global GIT_REV
    if GIT_REV is None:
        GIT_REV = git.Repo(settings.BASE_DIR).head.commit.name_rev
    return GIT_REV
