# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Printer

@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    pass
