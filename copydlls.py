__author__ = 'hari.jayaram'
import os

dlllist = [r'C:\windows\system32\OLEAUT32.dll' ,r'C:\windows\system32\USER32.dll',r'C:\windows\system32\SHELL32.dll',r'C:\windows\system32\ole32.dll',r'C:\windows\system32\WINMM.dll',r'C:\windows\system32\WSOCK32.dll',r'C:\windows\system32\COMCTL32.dll',r'C:\windows\system32\ADVAPI32.dll',r'C:\windows\system32\WS2_32.dll', r'c:\Python27_32\lib\site-packages\wx-2.8-msw-unicode\wx\gdiplus.dll',r'C:\windows\system32\GDI32.dll',r'C:\windows\system32\KERNEL32.dll', r'C:\windows\system32\WINSPOOL.DRV',r'C:\windows\system32\COMDLG32.dll',r'C:\windows\system32\RPCRT4.dll']

PWD = os.getcwd()
import shutil
for dll in dlllist:
    print "Copying ", dll , " to" , os.path.join(os.curdir,"dist")
    shutil.copy(dll,os.path.join(os.curdir,"dist"))
