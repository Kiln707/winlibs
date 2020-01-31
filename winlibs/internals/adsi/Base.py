from __future__ import print_function
from __future__ import absolute_import
from builtins import object
from enum import Enum
import sys, socket

# Since we're depending on ADSI, you have to be on windows...
if sys.platform != 'win32':
    raise Exception("Must be running Windows in order to use pyad.")
try:
    import win32api
    import pywintypes
    import win32com
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
    _default_detected_domain = None
    _default_detected_forest=None
else:
    # connecting to rootDSE will connect to the domain that the
    # current logged-in user belongs to.. which is generally the
    # domain under question and therefore becomes the default domain.
    _default_detected_domain = __default_ldap_obj.Get("defaultNamingContext")
    _default_detected_forest = __default_ldap_obj.Get("rootDomainNamingContext")

if _default_detected_domain:
    _default_detected_ntdomain = '.'.join([ a[3:] for a in _default_detected_domain.split(',') ])
else:
    _default_detected_ntdomain = socket.gethostname()

class ADSIBaseObject(object):

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
    default_forest = _default_detected_forest
    default_ntdomain = _default_detected_ntdomain
    adsi_provider = _adsi_provider

    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        self._adsi_obj=None
        self._scheme_obj=None
        self._adsi_path=None
        self._server=None
        self._port=None
        self._username=None
        self._password=None
        self._authentication_flag=None
        self._domain=None
        self._ssl=None
        self._mandatory_attributes=[]
        self._optional_attributes=[]
        if adsi_com_object:
            self._adsi_obj = adsi_com_object
        else:
            self._apply_options(options)
            self._adsi_path = self._generate_adsi_path(identifier)
            self._set_adsi_obj()
        # else:
        #     raise Exception("COM Object or Identifier is required to create an ADSIBaseObject")
        self._set_attributes()

    def _set_adsi_obj(self):
        raise NotImplementedError()

    def _generate_adsi_path(self, identifier):
        raise NotImplementedError()

    def _schema(self):
        raise NotImplementedError()

    def _apply_options(self, options={}):
        opts = ['server','port','username','password','authentication_flag','domain']
        for op in opts:
            if op in options:
                # print("Applying %s:"%op, options[op])
                setattr(self, '_'+op, options[op])
            else:
                # print("Applying default to %s"%op, getattr(self, 'default_'+op))
                setattr(self, '_'+op, getattr(self, 'default_'+op))

    def _set_defaults(self, options):
        for (default, key) in ADSIBaseObject.DEFAULTS_OPTIONS_MAPPINGS:
            if key in options:
                setattr(self, default, options[key])

    def _make_options(self):
        options = dict()
        for (default, key) in ADSIBaseObject.DEFAULTS_OPTIONS_MAPPINGS:
            val = getattr(self, default)
            if val:
                options[key] = val
        return options

    def _set_attributes(self):
        raise NotImplementedError()

    def _adsi_obj(self):
        return self._adsi_obj

    def get_schema(self):
        self._init_schema()
        return self._schema()

    def _init_schema(self):
        if self._scheme_obj is None:
            try:
                self._scheme_obj = self.adsi_provider.GetObject('',self._adsi_obj.schema)
            except:
                pass

    def get_mandatory_attributes(self):
        #Return a list of mandatory attributes for object. Attributes are not guaranteed to be defined
        self._init_schema()
        if not self._mandatory_attributes:
            try:
                self._mandatory_attributes = list(self._scheme_obj.MandatoryProperties)
            except:
                pass
        return self._mandatory_attributes

    def get_optional_attributes(self):
        #Return a list of optional attributes for object. Attributes are not guaranteed to be defined
        self._init_schema()
        if not self._optional_attributes:
            try:
                self._optional_attributes = list(self._scheme_obj.OptionalProperties)
            except:
                pass
        return self._optional_attributes

    def get_attributes(self):
        #Get list of all allowed attributes for object. Attributes are not guaranteed to be defined
        return list(set(self.get_mandatory_attributes() + self.get_optional_attributes() ))

    def _flush(self):
        self._adsi_obj.SetInfo()

    #######################
    #   Manage Attributes
    #######################
    def has_attribute(self, attribute):
        return hasattr(self._adsi_obj, attribute)

    #   Normally for Multivalue attributes.
    #   Might start to use for Multi-value attributes only in the future
    def _set_attribute(self, attribute, action, value):
        assert isinstance(action, IADS_ACTION), "Action must be instance of IADS_ACTION"
        if not self.has_attribute(attribute):
            raise InvalidAttribute(self, attribute)
        try:
            self._adsi_obj.putEx(action.value, attribute, self.__generate_list(value))
        except:
            raise Exception("Failed to set attribute %s"%attribute)
    #
    # def _set_attribute(self, attribute, value):
    #     if not self.has_attribute(attribute):
    #         raise InvalidAttribute(self, attribute)
    #     try:
    #         self._adsi_obj.put(attribute, value)
    #     except:
    #         raise Exception("Failed to set attribute %s"%attribute)

    def get(self, attrib):
        try:
            return self._adsi_obj.Get(attrib)
        except:
            return None

    def set(self, attribute, value):
        self._set_attribute(attribute, IADS_ACTION.UPDATE, value)

    def update(self, attribute, value):
        if value in ((),[],None,''):
            self.delete(attribute)
        else:
            self.set(attribute, value)

    def append(self, attribute, values):
        difference = list( set(self.__generate_list(values)) - set(self.get(attribute)) )
        if len(difference) != 0:
            self._set_attribute(attribute, IADS_ACTION.APPEND, difference)

    def remove(self, attribute, values):
        difference = list( set(self.__generate_list(values)) & set(self.get(attribute)) )
        if len(difference) != 0:
            self._set_attribute(attribute, IADS_ACTION.DELETE, difference)

    def delete(self, attribute):
        if self.get(attribute) != None:
            self._set_attribute(attribute, IADS_ACTION.CLEAR, [])

    def save(self):
        self._flush()

    def _convert_datetime(self, adsi_time_com_obj):
        # Converts 64-bit integer COM object representing time into a python datetime object.
        # credit goes to John Nielsen who documented this at
        # http://docs.activestate.com/activepython/2.6/pywin32/html/com/help/active_directory.html.

        high_part = int(adsi_time_com_obj.highpart) << 32
        low_part = int(adsi_time_com_obj.lowpart)
        date_value = ((high_part + low_part) - 116444736000000000) // 10000000
        #
        # The "fromtimestamp" function in datetime cannot take a
        # negative value, so if the resulting date value is negative,
        # explicitly set it to 18000. This will result in the date
        # 1970-01-01 00:00:00 being returned from this function
        #
        if date_value < 0:
            date_value = 18000
        return datetime.datetime.fromtimestamp(date_value)

    def convert_bigint(self, obj):
        # based on http://www.selfadsi.org/ads-attributes/user-usnChanged.htm
        h, l = obj.HighPart, obj.LowPart
        if l < 0:
            h += 1
        return (h << 32) + l

#################################################################################################################
#   TODO: Implement xml dump
#################################################################################################################
    def dump_to_xml(self, whitelist_attributes=[], blacklist_attributes=[]):
        raise NotImplementedError()
        """Dumps object and all human-readable attributes to an xml document which is returned as a string."""
        if len(whitelist_attributes) == 0:
            whitelist_attributes = self.get_attributes()
        attributes = list(set(whitelist_attributes) - set(blacklist_attributes))

        doc = xml.Document()
        adobj_xml_doc = doc.createElement("ADObject")
        adobj_xml_doc.setAttribute("objectGUID", str(self.guid).lstrip('{').rstrip('}'))
        adobj_xml_doc.setAttribute("pyADType", self.type)
        doc.appendChild(adobj_xml_doc)

        for attribute in attributes:
            node = doc.createElement("attribute")
            node.setAttribute("name", attribute)
            value = self.get(attribute)
            if str(type(value)).split("'",2)[1] not in ('buffer','instance') and value is not None:
                if type(value) is not list:
                    try:
                        ok_elem=True
                        node.setAttribute("type", str(type(value)).split("'",2)[1])
                        try:
                            text = doc.createTextNode(str(value))
                        except:
                            text = doc.createTextNode(value.encode("latin-1", 'replace'))
                        node.appendChild(text)
                    except:
                        print('attribute: %s not xml-able' % attribute)
                else:
                    node.setAttribute("type", "multiValued")
                    ok_elem = False
                    try:
                        for item in value:
                            if str(type(item)).split("'",2)[1] not in ('buffer','instance') and value is not None:
                                valnode = doc.createElement("value")
                                valnode.setAttribute("type", str(type(item)).split("'",2)[1])
                                text = doc.createTextNode(str(item))
                                valnode.appendChild(text)
                                node.appendChild(valnode)
                                ok_elem=True
                    except:
                        print('attribute: %s not xml-able' % attribute)
                if ok_elem: adobj_xml_doc.appendChild(node)
        return doc.toxml(encoding="UTF-8")
    #################################################################################################################

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

    def __generate_list(self, input):
        if type(input) is list:
            return input
        elif type(input) in (set,tuple):
            return list(input)
        else:
            return [input,]

    def __repr__(self):
        try:
            return "<%(class)s Name: '%(name)s'>"%{'class':self.__class__.__name__, 'name':self._adsi_obj.Get('Name')}
        except:
            return "<%(class)s>"%{'class':self.__class__.__name__}

    def __str__(self):
        print(self.__repr__())
        return self.__repr__()

def set_defaults(**kwargs):
    for k, v in kwargs.items():
        setattr(WinBase, '_'.join(('default', k)), v)

####################################
#   ADSI Enumerations
####################################
class IADS_ACTION(Enum):
    CLEAR = 1
    UPDATE = 2
    APPEND = 3
    DELETE = 4

###################################
#   Common ADSI Interfaces
###################################
class I_Container(ADSIBaseObject):
    def _copy_here(self, obj_path, new_name=None):
        self._adsi_obj.CopyHere(obj_path, new_name)
    def _create(self, class_type, name):
        return self._adsi_obj.Create(class_type, name)
    def _delete(self, class_type, name):
        self._adsi_obj.Delete(class_type, name)
    def _get_object(self, class_type, name):
        return self._adsi_obj.GetObject(class_type, name)
    def _move_here(self, source, new_name=None):
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
    def is_member(self, obj):
        return self._is_member(obj._adsi_obj())
    def add(self, obj):
        self._add(obj._adsi_obj())
    def remove(self, obj):
        self._remove(obj._adsi_obj())

class I_OpenDSObject(ADSIBaseObject):
    def _openDSObject(self, adsi_path, username, password):
        return self._adsi_obj.OpenDSObject(adsi_path, username, password, 0)

class I_PrintQueueOperations(ADSIBaseObject):
    def pause(self):
        self._adsi_obj.Pause()
    def _print_jobs(self):
        return self._adsi_obj.PrintJobs()
    def purge(self):
        self._adsi_obj.Purge()
    def resume(self):
        self._adsi_obj.Resume()
    def __iter__(self):
        raise NotImplementedError()
