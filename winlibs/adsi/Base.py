from __future__ import print_function
from __future__ import absolute_import
from abc import abstractmethod
from builtins import object
import sys, socket

# Since we're depending on ADSI, you have to be on windows...
if sys.platform != 'win32':
    raise Exception("Must be running Windows in order to use pyad.")
try:
    import win32api
    import pywintypes
    import win32com.client
    import win32net
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
        ("default_protocol", "protocol"),
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
        self._scheme_obj=None
        self._adsi_path=None
        self._server=None
        self._port=None
        self._username=None
        self._password=None
        self._protocol=None
        self._authentication_flag=None
        self._domain=None
        self._mandatory_attributes=[]
        self._optional_attributes=[]
        if adsi_com_object:
            self._adsi_obj = adsi_com_object
        elif identifier:
            self._apply_options(options)
            self._adsi_path = self._generate_adsi_path(identifier)
            self._set_adsi_obj()
        else:
            raise Exception("COM Object or Identifier is required to create an ADSIBaseObject")
        self._set_attributes()

    def _set_adsi_obj(self):
        raise NotImplementedError()

    def _generate_adsi_path(self, identifier):
        raise NotImplementedError()

    def _apply_options(self, options={}):
        opts = ['server','port','username','password','protocol','authentication_flag','domain']
        for op in opts:
            if op in options:
                # print("Applying %s:"%op, options[op])
                setattr(self, '_'+op, options[op])
            else:
                # print("Applying default to %s"%op, getattr(self, 'default_'+op))
                setattr(self, '_'+op, getattr(self, 'default_'+op))

    def _valid_protocol(self, protocol):
        if not protocol.isupper() and protocol != 'WinNT':
            protocol = protocol.upper()
        if protocol == 'WINNT':
            self._protocol =  'WinNT'
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

    def _set_attributes(self):
        for attr in self.get_attributes():
            setattr(self, attr, self.get(attr))

    def _adsi_obj(self):
        return self._adsi_obj

    def __init_schema(self):
        if self._scheme_obj is None:
            self._adsi_obj.GetInfo()
            self._scheme_obj = self.adsi_provider.GetObject('',self._adsi_obj.schema)

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
        try:
            return self._adsi_obj.Get(attrib)
        except:
            return None

    def save(self):
        self._adsi_obj.SetInfo()

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

###################################
#   Common ADSI Interfaces
###################################
class I_Container(ADSIBaseObject):
    def copy_here(self, obj_path, new_name=None):
        self._adsi_obj.CopyHere(obj_path, new_name)
    def create(self, class_type, name):
        print("Creating %s with name %s"%(class_type, name))
        return self._adsi_obj.Create(class_type, name)
    def delete(self, class_type, name):
        self._adsi_obj.Delete(class_type, name)
    def get_object(self, class_type, name):
        return self._adsi_obj.GetObject(class_type, name)
    def move_here(self, source, new_name=None):
        self._adsi_obj.MoveHere(source, new_name)
    def __iter__(self):
        for obj in self._adsi_obj:
            yield obj

class I_User(ADSIBaseObject):
    def change_password(self, old_password, new_password):
        assert type(old_password) is str and type(new_password) is str, "new and old passwords must be of type string"
        self._adsi_obj.ChangePassword(old_password, new_password)
    def _groups(self):
        return self._adsi_obj.Groups()
    def set_password(self, password):
        assert type(password) is str, "Password must be string"
        self._adsi_obj.SetPassword(password)

class I_Group(ADSIBaseObject):
    def _add(self, obj):
        self._adsi_obj.Add(obj)
    def _is_member(self, obj):
        return self._adsi_obj.IsMember(obj)
    def _members(self):
        return self._adsi_obj.Members()
    def _remove(self, obj):
        self._adsi_obj.Remove(obj)
    def add(self, obj):
        self._add(obj._adsi_obj())
    def remove(self, obj):
        self._remove(obj._adsi_obj())

class I_Members(ADSIBaseObject):
    def __iter__(self):
        for obj in self._adsi_obj:
            yield obj

class I_OpenDSObject(ADSIBaseObject):
    def _openDSObject(self, adsi_path, username, password):
        return self._adsi_obj.OpenDSObject(adsi_path, username, password, 0)

class I_PrintQueueOperations(ADSIBaseObject):
    def pause(self):
        self._adsi_obj.Pause()
    def printJobs(self):
        return self._adsi_obj.PrintJobs()
    def purge(self):
        self._adsi_obj.Purge()
    def resume(self):
        self._adsi_obj.Resume()
