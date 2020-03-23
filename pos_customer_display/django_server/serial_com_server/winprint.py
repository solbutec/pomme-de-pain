import os, sys
import win32print

printer_name = "NCR 7197 Receipt"
##printer_rec = win32print.OpenPrinter(printer_name)
##job = win32print.StartDocPrinter(printer_rec, 1, ("test of raw data", None, "RAW"))
##win32print.StartPagePrinter(printer_rec)
##win32print.WritePrinter(printer_rec, "data to print")
##win32print.EndPagePrinter(printer_rec)
#print(p)

def OpenCashDrawer(printerName) :   
       printerHandler = win32print.OpenPrinter(printerName)
       cashDraweOpenCommand = chr(27)+chr(112)+chr(0)+chr(25)+chr(250)
       win32print.StartDocPrinter(printerHandler, 1, ('Cash Drawer Open',None,'RAW')) 
       win32print.WritePrinter( printerHandler, cashDraweOpenCommand)
       win32print.EndDocPrinter(printerHandler)
       win32print.ClosePrinter(printerHandler)

OpenCashDrawer(printer_name)
