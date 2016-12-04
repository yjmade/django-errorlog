# -*- coding: utf-8 -*-
from django.contrib import admin
# Register your models here.
from .models import Error


@admin.register(Error)
class ErrorAdmin(admin.ModelAdmin):
    list_filter = [
        "fixed",
    ]
    list_display = [
        "name",
        "error_message",
        "occur_time"
    ]
