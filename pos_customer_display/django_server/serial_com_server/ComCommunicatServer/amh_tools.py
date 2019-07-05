# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os, sys
import win32api
import win32print

def open_cash_drawer(printerName) :   
       printerHandler = win32print.OpenPrinter(printerName)
       cashDraweOpenCommand = chr(27)+chr(112)+chr(0)+chr(25)+chr(250)
       win32print.StartDocPrinter(printerHandler, 1, ('Cash Drawer Open',None,'RAW')) 
       win32print.WritePrinter( printerHandler, cashDraweOpenCommand)
       win32print.EndDocPrinter(printerHandler)
       win32print.ClosePrinter(printerHandler)



def get_all_printers_from_os():
    printers = win32print.EnumPrinters(
            win32print.PRINTER_ENUM_CONNECTIONS
            + win32print.PRINTER_ENUM_LOCAL)
    #LIST OF:#(8388608, 'NCR 7197 Receipt,NCR 7197 Receipt,' , 'NCR 7197 Receipt', 'NCR POS Printer Driver')
    res = {}
    for p in printers:
        res[p[2]] = p
    # use key to call the printer
    return res


if __name__ == '__main__':
    open_cash_drawer("NCR 7197 Receipt")
    for p in get_all_printers_from_os():
        print(p)
