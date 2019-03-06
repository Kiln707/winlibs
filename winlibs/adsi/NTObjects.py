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
        self._adsi_obj = self.adsi_provider.getObject('', self._adsi_path)
    def _set_attributes(self):
        for attr in self.get_attributes():
            #print(self.get(attr).isSingleValued())
            setattr(self, attr, self.get(attr))
    def _valid_protocol(self, protocol):
        return protocol == 'WinNT'
    def _generate_adsi_path(self, identifier):
        if not self._valid_protocol(self._protocol):
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
    def save(self):
        for attr in self.get_attributes():
            if self.get(attr) != getattr(self, attr):
                self.update(attr, getattr(self, attr))
        self._flush()
    @classmethod
    def set_NTObj(cls, obj):
        o = NTObject(adsi_com_object=obj)
        fingerprint = set( o.get_attributes() )
        for c,k in cls._obj_map.items():
            if k._attributes:
                if not fingerprint ^ k._attributes:
                    o.__class__ = k
        return o
######################################
#   Common Interfaces for NT Objects
######################################
class I_NTContainer(I_Container):
    def __iter__(self):
        for obj in self._adsi_obj:
            yield NTObject.set_NTObj(obj)
    def get_object(self, class_type, name):
        return NTObject.set_NTObj(self._get_object(class_type, name))
    def _get_list(self, classType):
        for i in self:
            if i._class == classType:
                yield i
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
        if identifier:
            adsi_path =''.join((adsi_path, '/'))
            adsi_path = ''.join((adsi_path, escape_path(identifier)))
        adsi_path = ''.join((adsi_path, '/LanmanServer'))
        if self._class:
            adsi_path = ','.join((adsi_path,self._class))
        return adsi_path
######################################
#   NT Objects
######################################
class NTDomain(NTObject, I_NTContainer):
    _class = 'Domain'
    _attributes=set(['MaxBadPasswordsAllowed', 'Name', 'LockoutObservationInterval', 'MaxPasswordAge', 'AutoUnlockInterval', 'MinPasswordAge', 'MinPasswordLength', 'PasswordHistoryLength'])
    def __init__(self, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier=None, adsi_com_object=adsi_com_object, options=options)
    def user(self, name):
        return NTUser(adsi_com_object=self._get_object(class_type=NTUser._class, name=name))
    def group(self, name):
        return NTGroup(adsi_com_object=self._get_object(class_type=NTGroup._class, name=name))
    def computer(self, name):
        return NTComputer(adsi_com_object=self._get_object(class_type=NTComputer._class, name=name))
    def get_users(self):
        return self._get_list(NTUser._class)
    def get_groups(self):
        return self._get_list(NTGroup._class)
    def get_computers(self):
        return self._get_list(NTComputer._class)
    def get_printers(self):
        return self._get_list(NTPrintQueue._class)

class NTComputer(NTObject, I_NTContainer):
    _class = 'Computer'
    _attributes=set(['OperatingSystemVersion', 'Processor', 'Owner', 'Name', 'OperatingSystem', 'ProcessorCount', 'Division'])
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)
        self._file_service=None
    def shutdown(self, reboot=False):
        self._adsi_obj.Shutdown(reboot)
    def status(self):
        return self._adsi_obj.Status()
    def user(self, name):
        return NTUser(adsi_com_object=self._get_object(class_type=NTUser._class, name=name))
    def group(self, name):
        return NTGroup(adsi_com_object=self._get_object(class_type=NTGroup._class, name=name))
    def printer(self, name):
        return NTPrintQueue(adsi_com_object=self._get_object(class_type=NTPrintQueue._class, name=name))
    def service(self, name):
        return NTService(adsi_com_object=self._get_object(class_type=NTService._class, name=name))
    def get_users(self):
        return self._get_list(NTUser._class)
    def get_groups(self):
        return self._get_list(NTGroup._class)
    def get_printers(self):
        return self._get_list(NTPrintQueue._class)
    def get_services(self):
        return self._get_list(NTService._class)
    def get_shares(self):
        self._init_file_service()
        return self._file_service.__iter__()
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
        return adsi_path
    def _init_file_service(self):
        if self._file_service is None:
            self._file_service = NTFileService(computer=self.Name.lower())
    def get_fileservice(self):
        self._init_file_service()
        return self._file_service
    def __iter__(self):
        return super().__iter__()
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

class NTFileService(Lanman_adsi_obj):
    _class = 'FileService'
    _attributes=set(['Name', 'CurrentUserCount', 'HostComputer', 'Description', 'MaxUserCount', 'Path'])
    def __init__(self, identifier=None,computer=None, adsi_com_object=None, options={}):
        if computer:
            options['server']=computer
        super(NTObject, self).__init__(identifier, adsi_com_object, options)
    def host(self):
        return NTComputer(adsi_com_obj=self.HostComputer)
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
    def __iter__(self):
        for obj in self._adsi_obj:
            yield NTObject.set_NTObj(obj)

class NTFileShare(Lanman_adsi_obj):
    _class = 'FileShare'
    _attributes=set(['Name', 'HostComputer', 'Path', 'CurrentUserCount', 'Description', 'MaxUserCount'])
    def __init__(self, identifier=None,computer=None, adsi_com_object=None, options={}):
        if computer:
            options['server']=computer
        super(NTObject, self).__init__(identifier, adsi_com_object, options)
    def host(self):
        return NTComputer(adsi_com_obj=self.HostComputer)

class NTGroup(NTObject, I_Group):
    _class = 'Group'
    _attributes=set(['groupType', 'Name', 'objectSid', 'Description'])
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)
    def members(self):
        for obj in self._members():
            yield NTObject.set_NTObj(obj)
    def __iter__(self):
        return self.members()

class NTPrintQueue(NTObject, I_PrintQueueOperations):
    _class='PrintQueue'
    _attributes=set(['PrinterName', 'Priority', 'Model', 'Description', 'StartTime', 'ObjectGUID', 'Location', 'PrintDevices', 'UntilTime', 'Datatype', 'Attributes', 'DefaultJobPriority', 'HostComputer', 'JobCount', 'Action', 'Name', 'BannerPage', 'PrintProcessor'])
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)
    def host(self):
        return NTComputer(adsi_com_obj=self.HostComputer)
    def print_jobs(self):
        for i in self._print_jobs():
            yield NTPrintJob(adsi_com_object=i)
    def __iter__(self):
        return self.print_jobs()

class NTPrintJob(NTObject):
    _class='PrintJob'
    _attributes=set(['TimeElapsed', 'UntilTime', 'Name', 'TotalPages', 'StartTime', 'Notify', 'HostPrintQueue', 'Priority', 'Position', 'PagesPrinted', 'TimeSubmitted', 'Description', 'Size', 'User'])
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)
    def user(self):
        return NTUser(adsi_com_obj=self.User)
    def printer(self):
        return NTPrintQueue(adsi_com_obj=self.HostPrintQueue)

class NTResource(NTObject):
    _class='Resource'
    _attributes=set(['User', 'Name', 'Path', 'LockCount'])
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)
    def user(self):
        return NTUser(adsi_com_obj=self.User)
    def __repr__(self):
        return "< %(class)s User: %(name)s >"%{'class':self.__class__.__name__, 'name':self.User}

class NTSchema(NTObject, I_NTContainer):
    _class='Schema'
    def __init__(self, schema_class, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)
        self._schema_class=schema_class
    def __iter__(self):
        return super().__iter__(self)
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
    def host(self):
        return NTComputer(adsi_com_obj=self.HostComputer)
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
    def user(self):
        return NTUser(adsi_com_obj=self.User)
    def computer(self):
        return NTComputer(adsi_com_obj=self.Computer)

NTObject._obj_map={NTDomain._class:NTDomain, NTComputer._class:NTComputer, NTUser._class:NTUser, NTFileService._class:NTFileService,
NTFileShare._class:NTFileShare, NTGroup._class:NTGroup, NTPrintJob._class:NTPrintJob, NTPrintQueue._class:NTPrintQueue,
NTResource._class:NTResource, NTService._class:NTService, NTSession._class:NTSession}
