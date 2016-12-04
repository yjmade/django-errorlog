# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^1/', views.test_error1),
    url(r'^2/', views.test_error2),
]
