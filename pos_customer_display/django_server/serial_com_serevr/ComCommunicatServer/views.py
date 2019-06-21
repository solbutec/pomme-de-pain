# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import json
import serial
from pprint import pprint



@csrf_exempt
def send_message(request):
    msg_res = "OK"
    #pprint(request)
    if request.method == 'POST':
        port = request.POST.get('port')
        band = request.POST.get('band')
        msg = request.POST.get('msg')
        msg = msg.strip().encode()
        print("INFOS: ", port,band,msg)
        if True:
            com6 = serial.Serial(
                port = port, 
                baudrate = int(band), 
                parity = serial.PARITY_NONE,
                bytesize = serial.EIGHTBITS,
                stopbits = serial.STOPBITS_ONE,
            )
            print("=== IS OPEN COM: ", com6.is_open)
            if not com6.is_open:
                com6.open()
            msg = msg.encode('utf-8')
            com6.write(("%40s"%'').encode())
            com6.write(("%40s"%msg).encode())
        #except Exception as e:
            #msg_res = str(e)
        
        return HttpResponse(json.dumps({'OK': True, 'msg': msg_res}), content_type="application/json")
    else :
        return HttpResponse(json.dumps({'OK': False, 'msg': 'AJAX CALL REQUIRED'}), content_type="application/json")

@csrf_exempt
def test_com(request):
    return render(request, 'ComCommunicatServer/index.html')
