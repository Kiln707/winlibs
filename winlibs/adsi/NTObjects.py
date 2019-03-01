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

    def _schema(self):
        return NTSchema(self.__class__.__name__, adsi_com_object=self._scheme_obj)

    @classmethod
    def set_NTObj(cls, obj):
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
    def resources(self):
        for obj in self._resources():
            yield NTObject.set_NTObj(obj)
    def sessions(self):
        for obj in self._sessions():
            yield NTObject.set_NTObj(obj)
class I_NTContainer(I_Container):
    def __iter__(self):
        for obj in self._adsi_obj:
            yield NTObject.set_NTObj(obj)
    def get_object(self, class_type, name):
        return NTObject.set_NTObj(self._get_object(class_type, name))
class I_NTPrintQueueOperations(I_PrintQueueOperations):
    def pause(self):
        self._adsi_obj.Pause()
    def print_jobs(self):
        for i in self._print_jobs():
            yield NTPrintJob(adsi_com_object=i)
class Lanman_adsi_obj(NTObject):
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
        adsi_path = ''.join((adsi_path, '/LanmanServer'))
        if identifier:
            adsi_path =''.join((adsi_path, '/'))
            adsi_path = ''.join((adsi_path, escape_path(identifier)))
            if self._class:
                adsi_path = ','.join((adsi_path,self._class))
        return adsi_path
    def __iter__(self):
        for obj in self._adsi_obj:
            yield NTObject.set_NTObj(obj)

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
    def get_user(self, name):
        return NTUser(adsi_com_object=self._get_object(class_type=NTUser._class, name=name))
    def get_group(self, name):
        return NTGroup(adsi_com_object=self._get_object(class_type=NTGroup._class, name=name))
    def get_printer(self, name):
        return NTPrintQueue(adsi_com_object=self._get_object(class_type=NTPrintQueue._class, name=name))
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
        if identifier and self._server:
            adsi_path =''.join((adsi_path, '/'))
            adsi_path = ''.join((adsi_path, escape_path(identifier)))
            if self._class:
                adsi_path = ','.join((adsi_path,self._class))
        print(adsi_path)
        return adsi_path
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

class NTFileService(Lanman_adsi_obj, I_NTFileServiceOperations):
    _class = 'FileService'
    _attributes=set(['Name', 'CurrentUserCount', 'HostComputer', 'Description', 'MaxUserCount', 'Path'])
    def __init__(self, identifier=None,computer=None, adsi_com_object=None, options={}):
        if computer:
            options['server']=computer
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTFileShare(Lanman_adsi_obj):
    _class = 'FileShare'
    _attributes=set(['Name', 'HostComputer', 'Path', 'CurrentUserCount', 'Description', 'MaxUserCount'])
    def __init__(self, identifier=None,computer=None, adsi_com_object=None, options={}):
        if computer:
            options['server']=computer
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTGroup(NTObject, I_Group):
    _class = 'Group'
    _attributes=set(['groupType', 'Name', 'objectSid', 'Description'])
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)
    def members(self):
        for obj in self._members():
            yield NTObject.set_NTObj(obj)

class NTPrintJob(NTObject):
    _class='PrintJob'
    _attributes=set(['TimeElapsed', 'UntilTime', 'Name', 'TotalPages', 'StartTime', 'Notify', 'HostPrintQueue', 'Priority', 'Position', 'PagesPrinted', 'TimeSubmitted', 'Description', 'Size', 'User'])
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)
        
class NTPrintQueue(NTObject, I_NTPrintQueueOperations):
    _class='PrintQueue'
    _attributes=set(['PrinterName', 'Priority', 'Model', 'Description', 'StartTime', 'ObjectGUID', 'Location', 'PrintDevices', 'UntilTime', 'Datatype', 'Attributes', 'DefaultJobPriority', 'HostComputer', 'JobCount', 'Action', 'Name', 'BannerPage', 'PrintProcessor'])
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTResource(NTObject):
    _class='Resource'
    _attributes=set(['User', 'Name', 'Path', 'LockCount'])
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

    def __repr__(self):
        return "< %(class)s User: %(name)s >"%{'class':self.__class__.__name__, 'name':self.User}

class NTSchema(NTObject, I_NTContainer):
    _class='Schema'
    def __init__(self, schema_class, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)
        self._schema_class=schema_class
    def __iter__(self):
        return I_NTMembers.__iter__(self)
    def _init_schema(self):
        if self._scheme_obj is None:
            self._scheme_obj = self._adsi_obj
    def __repr__(self):
        return "< %(class)s for Class: %(name)s >"%{'class':self.__class__.__name__, 'name':self._schema_class}

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
    _attributes=set(['Name', 'User', 'ConnectTime', 'IdleTime', 'Computer'])
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

NTObject._obj_map={NTDomain._class:NTDomain, NTComputer._class:NTComputer, NTUser._class:NTUser, NTFileService._class:NTFileService,
NTFileShare._class:NTFileShare, NTGroup._class:NTGroup, NTPrintJob._class:NTPrintJob, NTPrintQueue._class:NTPrintQueue,
NTResource._class:NTResource, NTService._class:NTService, NTSession._class:NTSession}
