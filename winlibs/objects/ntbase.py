from builtins import object
import sys

if sys.platform != 'win32':
    raise Exception("Must be running Windows in order to use WinLibs!")

try:
    import win32api
    import pywintypes
    import win32com.client
except ImportError:
    raise Exception("pywin32 library required. Download from https://pypi.org/project/pywin32/")

class NTBase(object):
    pass
