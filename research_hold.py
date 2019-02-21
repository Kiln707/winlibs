from __future__ import print_function
from __future__ import absolute_import
from builtins import object
import sys
import datetime
import time
import types
import xml.dom.minidom as xml

# Since we're depending on ADSI, you have to be on windows...
if sys.platform != 'win32':
    raise Exception("Must be running Windows in order to use pyad.")

try:
    import win32api
    import pywintypes
    import win32com.client
except ImportError:
    raise Exception("pywin32 library required. Download from http://sourceforge.net/projects/pywin32/")

# Import constants and other common elements.
# from .pyadconstants import *
# from .pyadexceptions import *

_adsi_provider = win32com.client.Dispatch('ADsNameSpaces')

try:
    # Discover default domain and forest information
    __default_ldap_obj = _adsi_provider.GetObject('', "LDAP://rootDSE")
except:
    # If there was an error, this this computer might not be on a domain.
    print("WARN: unable to connect to default domain. Computer is likely not attached to an AD domain")
    __default_ldap_obj = None
    _default_detected_forest = None
    _default_detected_domain = None
else:
    # connecting to rootDSE will connect to the domain that the
    # current logged-in user belongs to.. which is generally the
    # domain under question and therefore becomes the default domain.
    #_default_detected_forest = __default_ldap_obj.Get("rootDomainNamingContext")
    _default_detected_domain = __default_ldap_obj.Get("defaultNamingContext")

# if _default_detected_domain:
#     _default_detected_ntdomain = '.'.join([ a[3:] for a in _default_detected_domain.split(',') ])
# else:
#     _default_detected_ntdomain = socket.gethostname()



class NTUser(object):
    def __init__(self, username, server=None):
        
        self._adsi_obj = None
        self._scheme_obj=None
        self._mandatory_attributes=None
        self._optional_attributes=None
        if not server:
            server = socket.gethostname()
        # temp = self._adsi.GetObject('', "LDAP://rootDSE")
        # print(temp.Get("defaultNamingContext"))
        # sch = temp.schema
        # for p in list(temp.MandatoryProperties) + list(temp.OptionalProperties):
        #     try:
        #         print(p, temp.Get(p))
        #     except:
        #         print(p, None)
        # print('done temp')
        self._adsi_obj = self._adsi.GetObject('', "WinNT://%s/%s,user"%(server, username))
        for prop in self.get_attributes():
            try:
                #print(prop, self._adsi_obj.Get(prop))
                setattr(self, prop, self._adsi_obj.Get(prop))
            except:
                #print(prop, None)
                setattr(self, prop, None)

    def __init_schema(self):
        if self._scheme_obj is None:
            self._adsi_obj.GetInfo()
            self._scheme_obj = self._adsi.GetObject('',self._adsi_obj.schema)

    def get_mandatory_attributes(self):
        #Return a list of mandatory attributes for object. Attributes are not guaranteed to be defined
        self.__init_schema()
        if not self._mandatory_attributes:
            self._mandatory_attributes = list(self._scheme_obj.MandatoryProperties)
        return self._mandatory_attributes

    def get_optional_attributes(self):
        #Return a list of optional attributes for object. Attributes are not guaranteed to be defined
        self.__init_schema()
        if not self._optional_attributes:
            self._optional_attributes = list(self._scheme_obj.OptionalProperties)
        return self._optional_attributes

    def get_attributes(self):
        #Get list of all allowed attributes for object. Attributes are not guaranteed to be defined
        return list(set( self.get_mandatory_attributes() + self.get_optional_attributes() ))

    def get(self, attrib):
        return self._adsi_obj.Get(attrib)

user = NTUser('sswanson', 'solano.cc.ca.us')

# for prop in user.get_attributes():
#     try:
#         print(prop, user.get(prop))
#     except:
#         print(prop, None)
