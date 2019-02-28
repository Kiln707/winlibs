from .Base import *
from .utils import escape_path
import socket

class NTObject(ADSIBaseObject):
    _class = None
    default_protocol='WinNT'
    default_domain=ADSIBaseObject.default_ntdomain
    default_server=ADSIBaseObject.default_ntdomain
    _attributes=None
    _obj_map={}
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
        if identifier:
            adsi_path =''.join((adsi_path, '/'))
            adsi_path = ''.join((adsi_path, escape_path(identifier)))
            if self._class:
                adsi_path = ','.join((adsi_path,self._class))
        return adsi_path

    @classmethod
    def get_object(cls, obj):
        o = NTObject(adsi_com_object=obj)
        fingerprint = set( o.get_attributes() )
        for c,k in cls._obj_map.items():
            if k._attributes:
                if not fingerprint ^ k._attributes:
                    o.__class__ = k
        if o.__class__ == NTObject or o.__class__ == NTComputer:
            print( o.get_attributes() )
        return o

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
class I_NTContainer(I_Container):
    def __iter__(self):
        for obj in self._adsi_obj:
            yield NTObject.get_object(obj)
class I_NTMembers(I_Members):
    def __iter__(self):
        for obj in self._adsi_obj:
            if obj is None:
                continue
            try:
                if obj.Get('Name') == None:
                    continue
            except:
                continue
            yield NTObject.get_object(obj)
    def get_object(self, objclass, name):
        raise NotImplementedError()
######################################
#   NT Objects
######################################
class NTDomain(NTObject, I_NTContainer):
    _class = 'Domain'
    _attributes=set(['MaxBadPasswordsAllowed', 'Name', 'LockoutObservationInterval', 'MaxPasswordAge', 'AutoUnlockInterval', 'MinPasswordAge', 'MinPasswordLength', 'PasswordHistoryLength'])
    def __init__(self, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier=None, adsi_com_object=adsi_com_object, options=options)
    def __iter__(self):
        return I_NTMembers.__iter__(self)
    def get_user(self, name):
        return NTUser(adsi_com_object=self._get_object(class_type=NTUser._class, name=name))
    def get_group(self, name):
        return NTGroup(adsi_com_object=self._get_object(class_type=NTGroup._class, name=name))
    def get_computer(self, name):
        return NTComputer(adsi_com_object=self._get_object(class_type=NTComputer._class, name=name))

class NTComputer(NTObject, I_NTContainer):
    _class = 'Computer'
    _attributes=set(['OperatingSystemVersion', 'Processor', 'Owner', 'Name', 'OperatingSystem', 'ProcessorCount', 'Division'])
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)
    def shutdown(self, reboot=False):
        self._adsi_obj.Shutdown(reboot)
    def status(self):
        return self._adsi_obj.Status()
    def _get_groups(self):
        return win32net.NetGroupEnum(self._server, 2, 0)
    def __iter__(self):
        return I_NTMembers.__iter__(self)

class NTUser(NTObject, I_User):
    _class='User'
    _attributes=set(['HomeDirectory', 'PrimaryGroupID', 'UserFlags', 'FullName', 'Parameters', 'Name', 'MinPasswordAge', 'LoginHours',
    'HomeDirDrive', 'Description', 'AccountExpirationDate', 'BadPasswordAttempts', 'PasswordExpired', 'LoginScript', 'MaxLogins',
    'PasswordHistoryLength', 'LastLogin', 'LastLogoff', 'PasswordAge', 'MinPasswordLength', 'MaxPasswordAge', 'objectSid',
    'LoginWorkstations', 'MaxStorage', 'Profile'])
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

    def groups(self):
        for g in self._adsi_obj.Groups():
            yield NTGroup(adsi_com_object=g)

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
    _attributes=set(['groupType', 'Name', 'objectSid', 'Description'])
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)
    def members(self):
        for obj in self._members():
            yield NTObject.get_object(obj)

class NTGroupCollection(NTObject, I_NTMembers):
    _class='GroupCollection'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTLocalGroup(NTObject, I_Group):
    _class='LocalGroup'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTNamespace(NTObject, I_NTContainer, I_OpenDSObject):
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

class NTSchema(NTObject, I_NTContainer):
    _class='Schema'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)
    def __iter__(self):
        return I_NTMembers.__iter__(self)

class NTService(NTObject):
    _class='Service'
    _attributes=set(['StartType', 'ServiceType', 'DisplayName', 'Path', 'ErrorControl', 'HostComputer', 'LoadOrderGroup', 'ServiceAccountName', 'Dependencies', 'Name'])
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

class NTUserGroupCollection(NTObject, I_NTMembers):
    _class='UserGroupCollection'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

NTObject._obj_map={NTDomain._class:NTDomain, NTComputer._class:NTComputer, NTUser._class:NTUser, NTFileService._class:NTFileService,
NTFileShare._class:NTFileShare, NTGroup._class:NTGroup, NTGroupCollection._class:NTGroupCollection, NTLocalGroup._class:NTLocalGroup,
NTNamespace._class:NTNamespace, NTPrintJob._class:NTPrintJob, NTPrintJobsCollection._class:NTPrintJobsCollection, NTPrintQueue._class:NTPrintQueue,
NTProperty._class:NTProperty, NTResource._class:NTResource, NTResourcesCollection._class:NTResourcesCollection, NTSchema._class:NTSchema,
NTService._class:NTService, NTSession._class:NTSession, NTSessionsCollection._class:NTSessionsCollection, NTSyntax._class:NTSyntax,
NTUserGroupCollection._class:NTUserGroupCollection}
