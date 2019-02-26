from .Base import *
from .utils import escape_path
import socket

class NTObject(ADSIBaseObject):
    _class = None
    default_protocol='WinNT'
    default_domain=ADSIBaseObject.default_ntdomain
    default_server=ADSIBaseObject.default_ntdomain
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        if 'protocol' in options:
            del options['protocol']
        super().__init__(identifier, adsi_com_object, options)

    def _set_adsi_obj(self):
        #Create connection to ADSI
        if not self._valid_protocol(self._protocol):
            raise Exception("Invalid protocol. Valid Protocols: LDAP, GC, WinNT")
        self._adsi_obj = self.adsi_provider.getObject('', self._adsi_path)

    def valid_protocol(self, protocol):
        return protocol == 'WinNT'

    def _generate_adsi_path(self, identifier):
        if not self.valid_protocol(self._protocol):
            raise Exception("Invalid Protocol for. Protocol is required to be WinNT")
        adsi_path = ''.join((self._protocol, '://'))
        if self._server:
            adsi_path =''.join((adsi_path,self._server))
            if self._port:
                adsi_path = ':'.join((adsi_path, str(self._port)))
        else:
            adsi_path = ''.join((adsi_path,socket.gethostname()))
        adsi_path =''.join((adsi_path, '/'))
        adsi_path = ''.join((adsi_path, escape_path(identifier)))
        if self._class:
            adsi_path = ','.join((adsi_path,self._class))
        return adsi_path

######################################
#   Common Interfaces for NT Objects
######################################
class I_NTCollection(ADSIBaseObject):
    def _add(self, obj):
        self._adsi_obj.Add(obj)
    def _remove(self, obj):
        self._adsi_obj.Remove(obj)
    def _get_enum(self):
        return self._adsi_obj.get_NewEnum()
    def _get_object(self, adsi_path):
        return self._adsi_obj.GetObject(adsi_path)

class I_NTFileServiceOperations(ADSIBaseObject):
    def _resources(self):
        return self._adsi_obj.Resources()
    def _sessions(self):
        return self._adsi_obj.Sessions()
######################################
#   NT Objects
######################################
class NTDomain(NTObject, I_Container):
    _class = 'Domain'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTComputer(NTObject, I_Container):
    _class = 'Computer'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)
    def shutdown(self, reboot=False):
        self._adsi_obj.Shutdown(reboot)
    def status(self):
        return self._adsi_obj.Status()
    def _get_groups(self):
        return win32net.NetGroupEnum(self._server, 2, 0)

class NTUser(NTObject, I_User):
    _class='User'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTFileService(NTObject, I_NTFileServiceOperations):
    _class = 'FileService'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTFileShare(NTObject):
    _class = 'FileShare'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTGroup(NTObject, I_Group):
    _class = 'Group'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTGroupCollection(NTObject, I_Members):
    _class='GroupCollection'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTLocalGroup(NTObject, I_Group):
    _class='LocalGroup'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTNamespace(NTObject, I_Container, I_OpenDSObject):
    _class='Namespace'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTPrintJob(NTObject):
    _class='PrintJob'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)
    def pause(self):
        self._adsi_obj.Pause()
    def resume(self):
        self._adsi_obj.Resume()

class NTPrintJobsCollection(NTObject, I_NTCollection):
    _class='PrintJobsCollection'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTPrintQueue(NTObject, I_PrintQueueOperations):
    _class='PrintQueue'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTProperty(NTObject):
    _class='Property'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)
    def qualifiers(self):
        return self._adsi_obj.Qualifiers()

class NTResource(NTObject):
    _class='Resource'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTResourcesCollection(NTObject, I_NTCollection):
    _class='ResourcesCollection'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTSchema(NTObject, I_Container):
    _class='Schema'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTService(NTObject):
    _class='Service'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

    def resume(self):
        self._adsi_obj.Continue()
    def pause(self):
        self._adsi_obj.Pause()
    def start(self):
        self._adsi_obj.Start()
    def stop(self):
        self._adsi_obj.Stop()
    def set_password(self, new_password):
        self._adsi_obj.SetPassword(new_password)

class NTSession(NTObject):
    _class='Session'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTSessionsCollection(NTObject):
    _class='SessionsCollection'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTSyntax(NTObject):
    _class='Syntax'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTUserGroupCollection(NTObject, I_Members):
    _class='UserGroupCollection'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)
