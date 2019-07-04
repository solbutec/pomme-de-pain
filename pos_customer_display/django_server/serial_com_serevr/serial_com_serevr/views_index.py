# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import json
import serial
import unicodedata
from pprint import pprint




@csrf_exempt
def index(request):
    return render(request, 'ComCommunicatServer/index.html')

