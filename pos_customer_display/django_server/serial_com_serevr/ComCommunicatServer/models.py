# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Printer(models.Model):
	name = models.CharField('Imprimente', max_length=200)