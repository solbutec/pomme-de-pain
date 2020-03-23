Set oShell = CreateObject ("Wscript.Shell") 
Dim strArgs
strArgs = "cmd /c C:\serial_com_server\start.bat"
oShell.Run strArgs, 0, false