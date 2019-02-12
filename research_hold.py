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
        adsi = win32com.client.Dispatch('ADsNameSpaces')
        if not server:
            server = socket.gethostname()
        user = adsi.GetObject("", "WinNT://%s/%s,user"%(server, username) )
        user.GetInfo()
        userScheme = adsi.GetObject('', user.schema)
        attrib = list(userScheme.OptionalProperties)
        print(user.Get('PrimaryGroupID'))

NTUser('sswanson', 'solano.cc.ca.us')
