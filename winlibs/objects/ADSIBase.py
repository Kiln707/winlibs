from __future__ import print_function
from __future__ import absolute_import
from builtins import object
import sys

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
    _default_detected_domain = None
else:
    # connecting to rootDSE will connect to the domain that the
    # current logged-in user belongs to.. which is generally the
    # domain under question and therefore becomes the default domain.
    _default_detected_domain = __default_ldap_obj.Get("defaultNamingContext")
if _default_detected_domain:
    _default_detected_ntdomain = '.'.join([ a[3:] for a in _default_detected_domain.split(',') ])
else:
    _default_detected_ntdomain = socket.gethostname()

class ADSIBaseObject():

    DEFAULTS_OPTIONS_MAPPINGS = [
        ("default_server", "server"),
        ("default_port", "port"),
        ("default_username", "username"),
        ("default_password", "password"),
        ("default_protocol", "protocol")
        ("default_authentication_flag", "authentication_flag"),
        ("default_ssl", "ssl")
    ]
    #Settings
    default_ssl = False
    default_server = None
    default_port = None
    default_username = None
    default_password = None
    default_protocol = ''
    default_authentication_flag = 0  # No credentials
    default_domain = _default_detected_domain
    default_ntdomain = _default_detected_ntdomain
    adsi_provider = _adsi_provider

    #Need to move _SET_ADSI_OBJ, Different between NT and LDAP
    # def __set_adsi_obj(self):
    #     #Create connection to ADSI
    #     if not self._valid_protocol():
    #         raise Exception("Invalid protocol. Valid Protocols: LDAP, GC, WinNT")
    #     if self.default_username and self.default_password:
    #         _ds = self.adsi_provider.getObject('',"%s:"%self.default_protocol)
    #     #NEED TO SETUP ENCRYPTION
    #     self._adsi_obj = _ds.OpenDSObject()

    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        self._adsi_obj=None
        self._adsi_path=None
        if adsi_com_object:
            self._adsi_obj = adsi_com_object
        elif identifier:
            self._apply_options(options)
            self._adsi_path = self._generate_adsi_path(identifier)
            self.__set_adsi_obj()
        else:
            raise Exception("COM Object or Identifier is required to create an ADSIBaseObject")

    def __set_adsi_obj(self):
        raise NotImplementedError()

    def _set_identifier(self):
        raise NotImplementedError()

    def _apply_options(self, options={}):
        self._server=options['server'] if 'server' in options else self._server = self.default_server
        self._port=options['port'] if 'port' in options else self._port = self.default_port
        self._username=options['username'] if 'username' in options else self._username = self.default_username
        self._password=options['password'] if 'password' in options else self._password = self.default_password
        self._protocol=options['protocol'] if 'protocol' in options else self._protocol = self.default_protocol
        self._authentication_flag=options['authentication_flag'] if 'authentication_flag' in options else self._authentication_flag = self.default_authentication_flag
        self._domain=options['domain'] if 'domain' in options else self._domain = self.default_domain

    def _valid_protocol(self, protocol=self.default_protocol):
        if not protocol.isupper() and protocol != 'WinNT':
            protocol = protocol.upper()
        if protocol == 'WINNT':
            protocol = 'WinNT'
        return ( protocol == 'LDAP' or protocol == 'GC' or protocol == 'WinNT' )

    def _set_defaults(self, options):
        for (default, key) in ADBase.DEFAULTS_OPTIONS_MAPPINGS:
            if key in options:
                setattr(self, default, options[key])

    def _make_options(self):
        options = dict()
        for (default, key) in ADBase.DEFAULTS_OPTIONS_MAPPINGS:
            val = getattr(self, default)
            if val:
                options[key] = val
        return options

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

    @property
    def _safe_default_domain(self):
        if self.default_domain:
            return self.default_domain
        raise Exception("Unable to detect default domain. Must specify search base.")

    @property
    def _safe_default_ntdomain(self):
        if self.default_ntdomain:
            return self.default_ntdomain
        raise Exception("Unable to detect default NT domain Must specify search base.")

def set_defaults(**kwargs):
    for k, v in kwargs.items():
        setattr(WinBase, '_'.join(('default', k)), v)
