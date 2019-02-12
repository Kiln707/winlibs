from builtins import object
import sys, socket

if sys.platform != 'win32':
    raise Exception("Must be running Windows in order to use WinLibs!")

try:
    import win32api
    import pywintypes
    import win32com.client
except ImportError:
    raise Exception("pywin32 library required. Download from https://pypi.org/project/pywin32/")

class NTUser(object):
    def __init__(self, username, server=None):
        adsi = win32com.client.Dispatch('ADs:')
        winnt =adsi.getobject('','WINNT:')
