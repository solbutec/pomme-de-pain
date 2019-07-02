# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os, sys
import win32api
import win32print
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from . import amh_tools
import json
import serial
import unicodedata
from pprint import pprint



@csrf_exempt
def send_message(request):
    msg_res = "OK"
    #pprint(request)
    if request.method == 'POST':
        port = request.POST.get('port')
        band = request.POST.get('band')
        msg = request.POST.get('msg')
        msg = msg.strip()
        msg_clean = ' ' * 40
        msg = unicodedata.normalize('NFKD', msg).encode('ascii','ignore')
        msg_clean = unicodedata.normalize('NFKD', msg_clean
                                          ).encode('ascii','ignore')
        #print("INFOS: ", port,band,msg)
        if True:
            com6 = serial.Serial(
                port = port, 
                baudrate = int(band), 
                parity = serial.PARITY_NONE,
                bytesize = serial.EIGHTBITS,
                stopbits = serial.STOPBITS_ONE,
            )
            if not com6.is_open:
                com6.open()
            com6.write(msg_clean)
            com6.write(msg)
        #except Exception as e:
            #msg_res = str(e)
        
        return HttpResponse(json.dumps({'OK': True, 'msg': msg_res}), content_type="application/json")
    else :
        return HttpResponse(json.dumps({'OK': False, 'msg': 'AJAX CALL REQUIRED'}), content_type="application/json")

@csrf_exempt
def open_cash_drawer(request):
    printer_name = ""
    ok, res = False, ""
    if not printer_name:
        printer_name = "NCR 7197 Receipt"
    try:
        amh_tools.open_cash_drawer(printer_name)
        res = "Success"
        ok = True
    except Exception as e:
        res = str(e)
    return HttpResponse(json.dumps({'OK': ok, 'msg': res}), content_type="application/json")


@csrf_exempt
def test_com(request):
    return render(request, 'ComCommunicatServer/test_com.html')

