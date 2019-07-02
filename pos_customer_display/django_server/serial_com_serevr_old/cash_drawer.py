
#pip install wxPython
#pip install pypiwin32
import wx
import win32api
import win32print
class ComboBoxFrame(wx.Frame):
    def __init__(self):
        # creates a drop down with the list of printers available
        wx.Frame.__init__(self, None, -1, 'Printers', size=(350, 300))
        panel = wx.Panel(self, -1)
        liste=[]
        #Enum printers returns the list of printers available in the network
        printers = win32print.EnumPrinters(
            win32print.PRINTER_ENUM_CONNECTIONS
            + win32print.PRINTER_ENUM_LOCAL)
        for i in printers:
            liste.append(i[2])
        sampleList = liste
        wx.StaticText(panel, -1, "Please select one printer from the list of printers to print:", (15, 15))
        self.combo =wx.ComboBox(panel, -1, "printers", (15, 40), wx.DefaultSize,sampleList, wx.CB_READONLY )
        btn2 = wx.Button(panel, label="Print", pos=(15, 60))
        btn2.Bind(wx.EVT_BUTTON, self.Onmsgbox)
        self.Centre()
        self.Show()

    def Onmsgbox(self, event):
        filename='manage.py'
        # here the user selected printer value will be given as input
        #print(win32print.GetDefaultPrinter ())
        win32api.ShellExecute (
          0,
          "printto",
          filename,
          '"%s"' % self.combo.GetValue(),
          ".",
          0
        )
        print(self.combo.GetValue())


if __name__ =='__main__':
    app = wx.App()
    ComboBoxFrame().Show()
    app.MainLoop()

